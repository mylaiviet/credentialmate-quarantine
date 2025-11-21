#!/usr/bin/env python3
"""
Discrepancy Pattern Analysis Script

Performs comprehensive root cause analysis of field extraction errors.
Classifies errors by type, identifies problem fields, and generates actionable
recommendations for improving extraction accuracy.

Key Features:
- Error type classification using DiscrepancyClassifier
- Field-level accuracy analysis
- Document type breakdown
- Confidence calibration analysis
- Problem field identification (<70% accuracy)

Author: Claude Code
Session: Phase 2, Session 2 - Discrepancy Analysis
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
from datetime import datetime

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.models.field_accuracy_log import FieldAccuracyLog
from discrepancy_taxonomy import DiscrepancyClassifier, ErrorType


class DiscrepancyAnalyzer:
    """Analyzes field extraction discrepancies and generates comprehensive reports"""

    def __init__(self):
        """Initialize database connection and tracking variables"""
        self.db = SessionLocal()
        self.entries = []
        self.field_stats = {}
        self.error_classifications = []
        self.problem_fields = []
        self.document_type_analysis = {}
        self.confidence_patterns = {}


    def analyze_all(self) -> None:
        """
        Main analysis method - orchestrates all analysis steps.

        Steps:
        1. Load field accuracy log entries from database
        2. Calculate per-field statistics (accuracy, confidence)
        3. Classify all errors using DiscrepancyClassifier
        4. Analyze error patterns by field
        5. Identify problem fields (<70% accuracy)
        6. Analyze by document type
        7. Analyze confidence calibration patterns
        """
        print("Starting comprehensive discrepancy analysis...")
        print("=" * 60)

        # Step 1: Load data
        print("Step 1/7: Loading field accuracy log entries...")
        self._load_entries()
        print(f"  Loaded {len(self.entries)} total entries")

        # Step 2: Calculate statistics
        print("\nStep 2/7: Calculating per-field statistics...")
        self._calculate_statistics()
        print(f"  Analyzed {len(self.field_stats)} unique fields")

        # Step 3: Classify errors
        print("\nStep 3/7: Classifying errors by type...")
        self._classify_errors()
        print(f"  Classified {len(self.error_classifications)} errors")

        # Step 4: Analyze patterns
        print("\nStep 4/7: Analyzing field-level error patterns...")
        self._analyze_field_patterns()

        # Step 5: Identify problem fields
        print("\nStep 5/7: Identifying problem fields (<70% accuracy)...")
        self._identify_problem_fields()
        print(f"  Found {len(self.problem_fields)} problem fields")

        # Step 6: Analyze by document type
        print("\nStep 6/7: Analyzing by document type...")
        self._analyze_by_document_type()
        print(f"  Analyzed {len(self.document_type_analysis)} document types")

        # Step 7: Analyze confidence patterns
        print("\nStep 7/7: Analyzing confidence calibration patterns...")
        self._analyze_confidence_patterns()

        print("\n" + "=" * 60)
        print("Analysis complete!")

    def _load_entries(self) -> None:
        """Query all field_accuracy_logs from database"""
        self.entries = self.db.query(FieldAccuracyLog).all()

    def _calculate_statistics(self) -> None:
        """
        Calculate per-field statistics including:
        - Total extractions
        - Correct extractions
        - Accuracy percentage
        - Average confidence score
        - Confidence bucket distribution
        """
        field_data = defaultdict(lambda: {
            'total': 0,
            'correct': 0,
            'incorrect': 0,
            'confidence_scores': [],
            'confidence_buckets': defaultdict(int)
        })

        for entry in self.entries:
            field_name = entry.field_name
            field_data[field_name]['total'] += 1

            if entry.is_correct:
                field_data[field_name]['correct'] += 1
            else:
                field_data[field_name]['incorrect'] += 1

            if entry.confidence_score is not None:
                field_data[field_name]['confidence_scores'].append(entry.confidence_score)

            if entry.confidence_bucket:
                field_data[field_name]['confidence_buckets'][entry.confidence_bucket] += 1

        # Calculate derived statistics
        for field_name, data in field_data.items():
            accuracy = (data['correct'] / data['total'] * 100) if data['total'] > 0 else 0
            avg_confidence = (
                sum(data['confidence_scores']) / len(data['confidence_scores'])
                if data['confidence_scores'] else None
            )

            self.field_stats[field_name] = {
                'total': data['total'],
                'correct': data['correct'],
                'incorrect': data['incorrect'],
                'accuracy_pct': round(accuracy, 1),
                'avg_confidence': round(avg_confidence, 3) if avg_confidence else None,
                'confidence_buckets': dict(data['confidence_buckets'])
            }

    def _classify_errors(self) -> None:
        """
        Classify all incorrect extractions using DiscrepancyClassifier.

        Creates list of error classifications with:
        - Error type (ErrorType enum)
        - Field name
        - Reason
        - AI value vs Ground truth value
        """
        incorrect_entries = [e for e in self.entries if not e.is_correct]

        for entry in incorrect_entries:
            error_type, reason = DiscrepancyClassifier.classify_error(
                field_name=entry.field_name,
                ai_value=entry.ai_value,
                ground_truth_value=entry.ground_truth_value,
                field_category=entry.field_category,
                document_type=entry.document_type
            )

            self.error_classifications.append({
                'field_name': entry.field_name,
                'error_type': error_type,
                'reason': reason,
                'ai_value': entry.ai_value,
                'ground_truth_value': entry.ground_truth_value,
                'document_type': entry.document_type,
                'test_file': entry.test_file_name,
                'confidence_score': entry.confidence_score
            })

    def _analyze_field_patterns(self) -> None:
        """
        Analyze error patterns per field.

        Counts error types per field to identify systematic issues.
        Updates field_stats with error_type_distribution.
        """
        for field_name in self.field_stats:
            # Count error types for this field
            error_counts = defaultdict(int)
            field_errors = [e for e in self.error_classifications if e['field_name'] == field_name]

            for error in field_errors:
                error_type_str = error['error_type'].value
                error_counts[error_type_str] += 1

            self.field_stats[field_name]['error_type_distribution'] = dict(error_counts)

    def _identify_problem_fields(self) -> None:
        """
        Find fields with <70% accuracy.

        Problem fields are prioritized for improvement efforts.
        Includes error type distribution and top error examples.
        """
        for field_name, stats in self.field_stats.items():
            if stats['accuracy_pct'] < 70.0:
                # Get top error examples for this field
                field_errors = [e for e in self.error_classifications if e['field_name'] == field_name][:3]

                self.problem_fields.append({
                    'field_name': field_name,
                    'accuracy_pct': stats['accuracy_pct'],
                    'total_extractions': stats['total'],
                    'incorrect_count': stats['incorrect'],
                    'avg_confidence': stats['avg_confidence'],
                    'error_distribution': stats.get('error_type_distribution', {}),
                    'sample_errors': field_errors
                })

        # Sort by accuracy (worst first)
        self.problem_fields.sort(key=lambda x: x['accuracy_pct'])

    def _analyze_by_document_type(self) -> None:
        """
        Group analysis by document type (cme, dea, etc.).

        Calculates accuracy and error distribution per document type.
        """
        doc_type_data = defaultdict(lambda: {
            'total': 0,
            'correct': 0,
            'incorrect': 0
        })

        for entry in self.entries:
            doc_type = entry.document_type
            doc_type_data[doc_type]['total'] += 1

            if entry.is_correct:
                doc_type_data[doc_type]['correct'] += 1
            else:
                doc_type_data[doc_type]['incorrect'] += 1

        # Calculate accuracy per document type
        for doc_type, data in doc_type_data.items():
            accuracy = (data['correct'] / data['total'] * 100) if data['total'] > 0 else 0

            self.document_type_analysis[doc_type] = {
                'total': data['total'],
                'correct': data['correct'],
                'incorrect': data['incorrect'],
                'accuracy_pct': round(accuracy, 1)
            }

    def _analyze_confidence_patterns(self) -> None:
        """
        Analyze confidence calibration to identify over/under-confidence.

        Groups by confidence bucket and calculates actual accuracy vs expected.
        Identifies calibration gaps.
        """
        bucket_data = defaultdict(lambda: {
            'total': 0,
            'correct': 0,
            'confidence_scores': []
        })

        for entry in self.entries:
            if entry.confidence_bucket:
                bucket = entry.confidence_bucket
                bucket_data[bucket]['total'] += 1

                if entry.is_correct:
                    bucket_data[bucket]['correct'] += 1

                if entry.confidence_score is not None:
                    bucket_data[bucket]['confidence_scores'].append(entry.confidence_score)

        # Calculate calibration metrics
        for bucket, data in bucket_data.items():
            accuracy = (data['correct'] / data['total'] * 100) if data['total'] > 0 else 0
            avg_confidence = (
                sum(data['confidence_scores']) / len(data['confidence_scores'])
                if data['confidence_scores'] else None
            )

            calibration_gap = (
                (avg_confidence * 100 - accuracy)
                if avg_confidence else None
            )

            self.confidence_patterns[bucket] = {
                'total': data['total'],
                'correct': data['correct'],
                'accuracy_pct': round(accuracy, 1),
                'avg_confidence': round(avg_confidence, 3) if avg_confidence else None,
                'calibration_gap': round(calibration_gap, 1) if calibration_gap else None
            }

    def generate_report(self) -> str:
        """
        Generate comprehensive Markdown report.

        Returns:
            Markdown-formatted report string
        """
        report_lines = [
            "# Field Extraction Discrepancy Analysis Report",
            "",
            f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "---",
            "",
            "## Executive Summary",
            ""
        ]

        # Calculate overall statistics
        total_entries = len(self.entries)
        total_correct = sum(1 for e in self.entries if e.is_correct)
        total_incorrect = total_entries - total_correct
        overall_accuracy = (total_correct / total_entries * 100) if total_entries > 0 else 0

        report_lines.extend([
            f"- **Total Field Extractions:** {total_entries}",
            f"- **Correct Extractions:** {total_correct}",
            f"- **Incorrect Extractions:** {total_incorrect}",
            f"- **Overall Accuracy:** {overall_accuracy:.1f}%",
            f"- **Fields Analyzed:** {len(self.field_stats)}",
            f"- **Problem Fields (<70% accuracy):** {len(self.problem_fields)}",
            "",
            "---",
            "",
            "## Error Type Distribution",
            ""
        ])

        # Count error types globally
        error_type_counts = defaultdict(int)
        for error in self.error_classifications:
            error_type_counts[error['error_type'].value] += 1

        report_lines.append("| Error Type | Count | Percentage |")
        report_lines.append("|------------|-------|------------|")

        for error_type, count in sorted(error_type_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_incorrect * 100) if total_incorrect > 0 else 0
            report_lines.append(f"| {error_type} | {count} | {percentage:.1f}% |")

        report_lines.extend([
            "",
            "---",
            "",
            "## Problem Fields (<70% Accuracy)",
            ""
        ])

        if self.problem_fields:
            for problem in self.problem_fields:
                report_lines.extend([
                    f"### {problem['field_name']} - {problem['accuracy_pct']:.1f}% Accuracy",
                    "",
                    f"- **Total Extractions:** {problem['total_extractions']}",
                    f"- **Incorrect:** {problem['incorrect_count']}",
                    f"- **Average Confidence:** {problem['avg_confidence'] if problem['avg_confidence'] else 'N/A'}",
                    "",
                    "**Error Type Distribution:**",
                    ""
                ])

                if problem['error_distribution']:
                    for error_type, count in sorted(problem['error_distribution'].items(), key=lambda x: x[1], reverse=True):
                        report_lines.append(f"- {error_type}: {count} occurrences")
                    report_lines.append("")

                if problem['sample_errors']:
                    report_lines.extend([
                        "**Sample Errors:**",
                        ""
                    ])

                    for i, error in enumerate(problem['sample_errors'], 1):
                        report_lines.extend([
                            f"{i}. **{error['error_type'].value}** - {error['reason']}",
                            f"   - AI: `{error['ai_value']}`",
                            f"   - GT: `{error['ground_truth_value']}`",
                            f"   - Document: {error['test_file']} ({error['document_type']})",
                            ""
                        ])

                report_lines.append("---")
                report_lines.append("")
        else:
            report_lines.append("No problem fields identified - all fields have >=70% accuracy!")
            report_lines.append("")

        report_lines.extend([
            "## Field-by-Field Summary",
            ""
        ])

        report_lines.append("| Field Name | Total | Correct | Incorrect | Accuracy | Avg Confidence |")
        report_lines.append("|------------|-------|---------|-----------|----------|----------------|")

        for field_name, stats in sorted(self.field_stats.items(), key=lambda x: x[1]['accuracy_pct']):
            conf_str = f"{stats['avg_confidence']}" if stats['avg_confidence'] else "N/A"
            report_lines.append(
                f"| {field_name} | {stats['total']} | {stats['correct']} | "
                f"{stats['incorrect']} | {stats['accuracy_pct']:.1f}% | {conf_str} |"
            )

        report_lines.extend([
            "",
            "---",
            "",
            "## Analysis by Document Type",
            ""
        ])

        report_lines.append("| Document Type | Total | Correct | Incorrect | Accuracy |")
        report_lines.append("|---------------|-------|---------|-----------|----------|")

        for doc_type, data in sorted(self.document_type_analysis.items(), key=lambda x: x[1]['accuracy_pct'], reverse=True):
            report_lines.append(
                f"| {doc_type} | {data['total']} | {data['correct']} | "
                f"{data['incorrect']} | {data['accuracy_pct']:.1f}% |"
            )

        report_lines.extend([
            "",
            "---",
            "",
            "## Confidence Calibration Analysis",
            ""
        ])

        report_lines.append("| Confidence Bucket | Total | Accuracy | Avg Confidence | Calibration Gap |")
        report_lines.append("|-------------------|-------|----------|----------------|-----------------|")

        for bucket in ['high', 'medium', 'low']:
            if bucket in self.confidence_patterns:
                data = self.confidence_patterns[bucket]
                gap_str = f"{data['calibration_gap']:+.1f}%" if data['calibration_gap'] is not None else "N/A"
                conf_str = f"{data['avg_confidence']}" if data['avg_confidence'] else "N/A"

                bucket_label = bucket.capitalize()
                if bucket == 'high':
                    bucket_label += " (>=0.85)"
                elif bucket == 'medium':
                    bucket_label += " (0.70-0.84)"
                else:
                    bucket_label += " (<0.70)"

                report_lines.append(
                    f"| {bucket_label} | {data['total']} | {data['accuracy_pct']:.1f}% | "
                    f"{conf_str} | {gap_str} |"
                )

        report_lines.extend([
            "",
            "**Calibration Gap Interpretation:**",
            "- **Positive gap** (e.g., +10%): Model is over-confident (confidence higher than actual accuracy)",
            "- **Negative gap** (e.g., -10%): Model is under-confident (confidence lower than actual accuracy)",
            "- **Near zero** (±5%): Well-calibrated",
            "",
            "---",
            "",
            "## Root Cause Summary",
            ""
        ])

        # Group errors by type and provide recommendations
        error_type_summaries = {
            ErrorType.MISSING_DATA: {
                'description': 'AI failed to extract field that exists in document',
                'recommendation': 'Review extraction prompts to ensure field is explicitly requested. Check OCR quality.'
            },
            ErrorType.FORMAT_MISMATCH: {
                'description': 'Correct data extracted but in wrong format (e.g., date format)',
                'recommendation': 'Add format normalization step in post-processing. Update prompt with format examples.'
            },
            ErrorType.PUNCTUATION_VARIANCE: {
                'description': 'Content correct but punctuation/word order differs',
                'recommendation': 'Use fuzzy matching for validation. Consider normalizing before comparison.'
            },
            ErrorType.NUMERIC_TYPO: {
                'description': 'Single digit OCR errors in numeric fields',
                'recommendation': 'Implement checksum validation. Flag for manual review if available.'
            },
            ErrorType.PARTIAL_EXTRACTION: {
                'description': 'AI extracted only part of the full field value',
                'recommendation': 'Improve prompts to request complete values. Add validation for truncated fields.'
            },
            ErrorType.INFERENCE_ERROR: {
                'description': 'AI completely misinterpreted the field',
                'recommendation': 'Add field-specific examples to prompts. Consider few-shot learning.'
            },
            ErrorType.SCHEMA_MISMATCH: {
                'description': 'AI extracted field that does not exist in document',
                'recommendation': 'Review schema definitions. Add explicit null handling in prompts.'
            },
            ErrorType.OCR_FAILURE: {
                'description': 'Text not readable due to poor image quality',
                'recommendation': 'Improve document preprocessing. Flag low-quality images for manual review.'
            }
        }

        for error_type in ErrorType:
            if error_type.value in error_type_counts:
                count = error_type_counts[error_type.value]
                summary = error_type_summaries.get(error_type, {})

                report_lines.extend([
                    f"### {error_type.value.replace('_', ' ').title()} ({count} occurrences)",
                    "",
                    f"**Description:** {summary.get('description', 'N/A')}",
                    "",
                    f"**Recommendation:** {summary.get('recommendation', 'N/A')}",
                    ""
                ])

        report_lines.extend([
            "---",
            "",
            "## Next Steps",
            "",
            "1. **Address Problem Fields:** Focus improvement efforts on fields with <70% accuracy",
            "2. **Fix Format Mismatches:** Implement post-processing normalization for dates and formats",
            "3. **Improve Prompts:** Add field-specific examples for fields with high inference error rates",
            "4. **Calibrate Confidence:** Adjust confidence thresholds based on calibration gaps",
            "5. **Implement Fuzzy Matching:** Use fuzzy comparison for punctuation variance errors",
            "",
            f"**Report End** - Generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            ""
        ])

        return "\n".join(report_lines)

    def close(self) -> None:
        """Close database connection"""
        self.db.close()


def main():
    """Main function - instantiate analyzer, run analysis, generate report"""
    analyzer = DiscrepancyAnalyzer()

    try:
        # Run analysis
        analyzer.analyze_all()

        # Generate report
        print("\nGenerating comprehensive report...")
        report = analyzer.generate_report()

        # Save to file
        # In Docker container, __file__ is /app/analyze_discrepancies.py
        # So parent is /app, and we need /app/docs/ux-ui/outputs
        backend_path = Path(__file__).parent  # /app
        output_dir = backend_path / "docs/ux-ui/outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "SESSION-2-2-DISCREPANCY-ANALYSIS-REPORT.md"

        with open(output_file, 'w') as f:
            f.write(report)

        print(f"\n{'=' * 60}")
        print(f"Report saved to: {output_file}")
        print(f"{'=' * 60}\n")

        # Print summary statistics
        print("SUMMARY STATISTICS")
        print("=" * 60)
        print(f"Total Entries: {len(analyzer.entries)}")
        print(f"Total Fields: {len(analyzer.field_stats)}")
        print(f"Total Errors Classified: {len(analyzer.error_classifications)}")
        print(f"Problem Fields (<70%): {len(analyzer.problem_fields)}")
        print(f"Document Types: {len(analyzer.document_type_analysis)}")
        print("=" * 60)

        # Print problem fields
        if analyzer.problem_fields:
            print("\nPROBLEM FIELDS (<70% accuracy):")
            for problem in analyzer.problem_fields:
                print(f"  - {problem['field_name']}: {problem['accuracy_pct']:.1f}% ({problem['incorrect_count']} errors)")

        print("\nAnalysis complete - review report for detailed recommendations.")

    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        analyzer.close()


if __name__ == "__main__":
    main()
