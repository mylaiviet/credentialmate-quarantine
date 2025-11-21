"""
Discrepancy Pattern Analysis Script (Direct SQL Version)

Analyzes 127 field accuracy log entries using direct SQL queries via docker exec.
"""

import subprocess
import json
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any
import os

from discrepancy_taxonomy import DiscrepancyClassifier, ErrorType


def run_sql(query: str) -> List[tuple]:
    """Execute SQL query via docker exec"""
    cmd = [
        'docker', 'exec', 'credentialmate-postgres',
        'psql', '-U', 'credentialmate_dev', '-d', 'credentialmate_dev',
        '-t', '-A', '-F', '|', '-c', query
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

    if result.returncode != 0:
        print(f"SQL Error: {result.stderr}")
        return []

    lines = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
    rows = [tuple(line.split('|')) for line in lines if line]

    return rows


def analyze_overall_accuracy() -> Dict[str, Any]:
    """Analyze overall extraction accuracy"""
    query = """
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct
        FROM field_accuracy_logs;
    """

    rows = run_sql(query)

    if not rows:
        return {'total_fields': 0, 'correct': 0, 'incorrect': 0, 'accuracy_pct': 0.0}

    total, correct = int(rows[0][0]), int(rows[0][1])
    incorrect = total - correct
    accuracy_pct = (correct / total * 100) if total > 0 else 0

    return {
        'total_fields': total,
        'correct': correct,
        'incorrect': incorrect,
        'accuracy_pct': round(accuracy_pct, 1)
    }


def analyze_by_field_name() -> List[Dict[str, Any]]:
    """Analyze accuracy by field name"""
    query = """
        SELECT
            field_name,
            COUNT(*) as total,
            SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct
        FROM field_accuracy_logs
        GROUP BY field_name
        ORDER BY
            CAST(SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) ASC,
            COUNT(*) DESC;
    """

    rows = run_sql(query)

    field_stats = []
    for field_name, total, correct in rows:
        total = int(total)
        correct = int(correct)
        incorrect = total - correct
        accuracy_pct = (correct / total * 100) if total > 0 else 0

        field_stats.append({
            'field_name': field_name,
            'total': total,
            'correct': correct,
            'incorrect': incorrect,
            'accuracy_pct': round(accuracy_pct, 1)
        })

    return field_stats


def analyze_by_document_type() -> List[Dict[str, Any]]:
    """Analyze accuracy by document type"""
    query = """
        SELECT
            document_type,
            COUNT(*) as total,
            SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct
        FROM field_accuracy_logs
        GROUP BY document_type
        ORDER BY CAST(SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) ASC;
    """

    rows = run_sql(query)

    doc_stats = []
    for doc_type, total, correct in rows:
        total = int(total)
        correct = int(correct)
        accuracy_pct = (correct / total * 100) if total > 0 else 0

        doc_stats.append({
            'document_type': doc_type,
            'total': total,
            'correct': correct,
            'incorrect': total - correct,
            'accuracy_pct': round(accuracy_pct, 1)
        })

    return doc_stats


def get_all_incorrect_extractions() -> List[Dict[str, Any]]:
    """Get all incorrect extractions for error classification"""
    query = """
        SELECT
            document_type,
            field_name,
            field_category,
            ai_value::text,
            ground_truth_value::text,
            test_file_name
        FROM field_accuracy_logs
        WHERE is_correct = false
        ORDER BY field_name, document_type;
    """

    rows = run_sql(query)

    extractions = []
    for doc_type, field_name, field_cat, ai_val, gt_val, test_file in rows:
        # Handle null values
        if ai_val == '':
            ai_val = None
        if gt_val == '':
            gt_val = None

        extractions.append({
            'document_type': doc_type,
            'field_name': field_name,
            'field_category': field_cat,
            'ai_value': ai_val,
            'ground_truth_value': gt_val,
            'test_file_name': test_file
        })

    return extractions


def classify_all_errors(incorrect_extractions: List[Dict[str, Any]]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """Classify all errors using taxonomy"""
    error_patterns = defaultdict(lambda: defaultdict(list))

    for extraction in incorrect_extractions:
        error_type, reason = DiscrepancyClassifier.classify_error(
            field_name=extraction['field_name'],
            ai_value=extraction['ai_value'],
            ground_truth_value=extraction['ground_truth_value'],
            field_category=extraction['field_category'],
            document_type=extraction['document_type']
        )

        error_patterns[extraction['field_name']][error_type.value].append({
            'test_file': extraction['test_file_name'],
            'document_type': extraction['document_type'],
            'ai_value': extraction['ai_value'],
            'ground_truth': extraction['ground_truth_value'],
            'reason': reason
        })

    return dict(error_patterns)


def analyze_problem_fields(field_names: List[str]) -> Dict[str, Any]:
    """Deep dive analysis for specific problem fields"""
    problem_analysis = {}

    for field_name in field_names:
        query = f"""
            SELECT
                test_file_name,
                document_type,
                ai_value::text,
                ground_truth_value::text,
                is_correct
            FROM field_accuracy_logs
            WHERE field_name = '{field_name}';
        """

        rows = run_sql(query)

        total = len(rows)
        correct = sum(1 for row in rows if row[4] == 't')
        incorrect = total - correct

        incorrect_examples = [
            {
                'test_file': row[0],
                'document_type': row[1],
                'ai_value': row[2] if row[2] else None,
                'ground_truth': row[3] if row[3] else None
            }
            for row in rows if row[4] == 'f'
        ]

        problem_analysis[field_name] = {
            'total': total,
            'correct': correct,
            'incorrect': incorrect,
            'accuracy_pct': round((correct / total * 100), 1) if total > 0 else 0,
            'incorrect_examples': incorrect_examples
        }

    return problem_analysis


def generate_recommendations(
    field_stats: List[Dict[str, Any]],
    error_patterns: Dict[str, Dict[str, List[Dict[str, Any]]]],
    problem_fields: Dict[str, Any]
) -> List[str]:
    """Generate actionable recommendations"""
    recommendations = []

    # Recommendation 1: Zero accuracy fields
    zero_accuracy_fields = [f for f in field_stats if f['accuracy_pct'] == 0.0]
    if zero_accuracy_fields:
        field_list = ', '.join([f['field_name'] for f in zero_accuracy_fields])
        recommendations.append(
            f"**CRITICAL**: Fix {len(zero_accuracy_fields)} fields with 0% accuracy: {field_list}"
        )

    # Recommendation 2: Missing data errors
    missing_data_fields = []
    for field_name, errors in error_patterns.items():
        if 'missing_data' in errors and len(errors['missing_data']) > 2:
            missing_data_fields.append(field_name)

    if missing_data_fields:
        recommendations.append(
            f"**HIGH PRIORITY**: Fields frequently returning null: {', '.join(missing_data_fields)}. "
            "Review extraction prompts to ensure these fields are explicitly requested."
        )

    # Recommendation 3: Format mismatches
    format_fields = []
    for field_name, errors in error_patterns.items():
        if 'format_mismatch' in errors:
            format_fields.append(field_name)

    if format_fields:
        recommendations.append(
            f"**MEDIUM PRIORITY**: Standardize output format for: {', '.join(format_fields)}. "
            "Update prompts to specify exact format requirements."
        )

    # Recommendation 4: Punctuation/ordering
    punctuation_fields = []
    for field_name, errors in error_patterns.items():
        if 'punctuation_variance' in errors:
            punctuation_fields.append(field_name)

    if punctuation_fields:
        recommendations.append(
            f"**LOW PRIORITY**: Consider fuzzy matching for: {', '.join(punctuation_fields)}. "
            "These extractions are semantically correct but differ in formatting."
        )

    # Recommendation 5: Title field
    if 'title' in problem_fields and problem_fields['title']['accuracy_pct'] < 50:
        recommendations.append(
            "**TITLE FIELD**: 35.7% accuracy suggests systematic issue. "
            "Many CME documents may not have explicit 'title' field. "
            "Consider: (1) Making title optional for CME documents, or "
            "(2) Extract activity description as title fallback."
        )

    # Recommendation 6: Date range field
    if 'date_range' in problem_fields and problem_fields['date_range']['accuracy_pct'] == 0:
        recommendations.append(
            "**DATE_RANGE FIELD**: 0% accuracy indicates extraction failure. "
            "Review prompt to ensure date range is requested. "
            "Consider extracting from completion_date or activity_date as fallback."
        )

    return recommendations


def generate_markdown_report(
    overall: Dict[str, Any],
    field_stats: List[Dict[str, Any]],
    doc_stats: List[Dict[str, Any]],
    error_patterns: Dict[str, Dict[str, List[Dict[str, Any]]]],
    problem_fields: Dict[str, Any],
    recommendations: List[str]
) -> str:
    """Generate comprehensive Markdown report"""

    md = f"""# Phase 2, Session 2: Discrepancy Pattern Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Session ID:** ui-ux-2-2
**Analysis Scope:** {overall['total_fields']} field accuracy log entries

---

## Executive Summary

### Overall Accuracy
- **Total Fields Analyzed:** {overall['total_fields']}
- **Correct Extractions:** {overall['correct']} ({overall['accuracy_pct']}%)
- **Incorrect Extractions:** {overall['incorrect']} ({100 - overall['accuracy_pct']:.1f}%)

### Key Findings
1. **Perfect Performers (100% accuracy):** {len([f for f in field_stats if f['accuracy_pct'] == 100.0])} fields
2. **Problem Fields (<50% accuracy):** {len([f for f in field_stats if f['accuracy_pct'] < 50.0])} fields
3. **Critical Fields (0% accuracy):** {len([f for f in field_stats if f['accuracy_pct'] == 0.0])} fields

### Most Common Error Types
"""

    # Count error types
    error_type_counts = defaultdict(int)
    for field_name, errors in error_patterns.items():
        for error_type, examples in errors.items():
            error_type_counts[error_type] += len(examples)

    for error_type, count in sorted(error_type_counts.items(), key=lambda x: -x[1])[:5]:
        md += f"- **{error_type}:** {count} occurrences\n"

    md += "\n---\n\n## 1. Accuracy by Field Name\n\n"
    md += "| Field Name | Total | Correct | Incorrect | Accuracy % |\n"
    md += "|------------|-------|---------|-----------|------------|\n"

    for field in field_stats:
        md += f"| {field['field_name']} | {field['total']} | {field['correct']} | {field['incorrect']} | {field['accuracy_pct']}% |\n"

    md += "\n---\n\n## 2. Accuracy by Document Type\n\n"
    md += "| Document Type | Total Fields | Correct | Incorrect | Accuracy % |\n"
    md += "|---------------|--------------|---------|-----------|------------|\n"

    for doc in doc_stats:
        md += f"| {doc['document_type']} | {doc['total']} | {doc['correct']} | {doc['incorrect']} | {doc['accuracy_pct']}% |\n"

    md += "\n---\n\n## 3. Error Pattern Analysis\n\n"

    for field_name in sorted(error_patterns.keys()):
        errors = error_patterns[field_name]
        total_errors = sum(len(examples) for examples in errors.values())

        md += f"### {field_name} ({total_errors} errors)\n\n"

        for error_type, examples in sorted(errors.items(), key=lambda x: -len(x[1])):
            md += f"#### {error_type} ({len(examples)} occurrences)\n\n"

            # Show up to 3 examples
            for example in examples[:3]:
                md += f"- **{example['test_file']}** ({example['document_type']})\n"
                md += f"  - AI: `{example['ai_value']}`\n"
                md += f"  - GT: `{example['ground_truth']}`\n"
                md += f"  - Reason: {example['reason']}\n\n"

            if len(examples) > 3:
                md += f"  *(+{len(examples) - 3} more examples)*\n\n"

    md += "\n---\n\n## 4. Root Cause Analysis: Problem Fields\n\n"

    for field_name, analysis in problem_fields.items():
        md += f"### {field_name}\n\n"
        md += f"- **Accuracy:** {analysis['accuracy_pct']}% ({analysis['correct']}/{analysis['total']})\n"
        md += f"- **Failure Rate:** {100 - analysis['accuracy_pct']:.1f}%\n\n"

        md += "**Root Causes:**\n\n"

        if field_name in error_patterns:
            for error_type, examples in error_patterns[field_name].items():
                md += f"- **{error_type}:** {len(examples)} cases\n"

        md += "\n**Failed Extractions:**\n\n"

        for i, example in enumerate(analysis['incorrect_examples'][:5], 1):
            md += f"{i}. **{example['test_file']}** ({example['document_type']})\n"
            md += f"   - AI: `{example['ai_value']}`\n"
            md += f"   - GT: `{example['ground_truth']}`\n\n"

        if len(analysis['incorrect_examples']) > 5:
            md += f"   *(+{len(analysis['incorrect_examples']) - 5} more failures)*\n\n"

    md += "\n---\n\n## 5. Actionable Recommendations\n\n"

    for i, rec in enumerate(recommendations, 1):
        md += f"{i}. {rec}\n\n"

    md += "\n---\n\n## 6. Next Steps for Session 2-3\n\n"
    md += "### Immediate Actions\n"
    md += "1. Update extraction prompts for fields with missing_data errors\n"
    md += "2. Implement fuzzy matching for punctuation_variance cases\n"
    md += "3. Review ground truth for format_mismatch fields\n"
    md += "4. Consider making 'title' optional for CME documents\n\n"

    md += "### Testing Requirements\n"
    md += "1. Re-run field extraction tests after prompt updates\n"
    md += "2. Target: >90% accuracy for all fields except 'title'\n"
    md += "3. Validate date_range extraction with updated prompts\n"
    md += "4. Measure improvement in problem fields\n\n"

    md += "### Success Criteria for Session 2-3\n"
    md += "- ✅ Zero fields with 0% accuracy\n"
    md += "- ✅ 'title' field accuracy >50%\n"
    md += "- ✅ 'date_range' field accuracy >80%\n"
    md += "- ✅ Overall accuracy >85%\n\n"

    md += "---\n\n"
    md += "**Analysis Complete**\n"
    md += f"**Total Discrepancies Analyzed:** {overall['incorrect']}\n"
    md += f"**Error Types Identified:** {len(error_type_counts)}\n"
    md += f"**Recommendations Generated:** {len(recommendations)}\n"

    return md


def main():
    """Main analysis execution"""
    print("Phase 2, Session 2: Discrepancy Pattern Analysis")
    print("=" * 60)

    # Overall accuracy
    print("\n1. Analyzing overall accuracy...")
    overall = analyze_overall_accuracy()
    print(f"   Total: {overall['total_fields']}, Accuracy: {overall['accuracy_pct']}%")

    # By field name
    print("2. Analyzing by field name...")
    field_stats = analyze_by_field_name()
    print(f"   Analyzed {len(field_stats)} unique fields")

    # By document type
    print("3. Analyzing by document type...")
    doc_stats = analyze_by_document_type()
    print(f"   Analyzed {len(doc_stats)} document types")

    # Get incorrect extractions
    print("4. Fetching incorrect extractions...")
    incorrect_extractions = get_all_incorrect_extractions()
    print(f"   Retrieved {len(incorrect_extractions)} incorrect extractions")

    # Classify errors
    print("5. Classifying error patterns...")
    error_patterns = classify_all_errors(incorrect_extractions)
    total_errors = sum(
        sum(len(examples) for examples in errors.values())
        for errors in error_patterns.values()
    )
    print(f"   Classified {total_errors} errors across {len(error_patterns)} fields")

    # Problem fields
    print("6. Analyzing problem fields...")
    problem_field_names = ['title', 'date_range']
    problem_fields = analyze_problem_fields(problem_field_names)
    print(f"   Deep dive on {len(problem_fields)} problem fields")

    # Recommendations
    print("7. Generating recommendations...")
    recommendations = generate_recommendations(field_stats, error_patterns, problem_fields)
    print(f"   Generated {len(recommendations)} recommendations")

    # Generate report
    print("8. Generating Markdown report...")
    report = generate_markdown_report(
        overall, field_stats, doc_stats, error_patterns, problem_fields, recommendations
    )

    # Save report
    output_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'docs',
        'ux-ui',
        'outputs',
        'SESSION-2-2-DISCREPANCY-ANALYSIS-REPORT.md'
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"   Report saved to: {output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Total Fields: {overall['total_fields']}")
    print(f"Accuracy: {overall['accuracy_pct']}%")
    print(f"Problem Fields: {len(problem_fields)}")
    print(f"Recommendations: {len(recommendations)}")
    print(f"Report: SESSION-2-2-DISCREPANCY-ANALYSIS-REPORT.md")


if __name__ == "__main__":
    main()
