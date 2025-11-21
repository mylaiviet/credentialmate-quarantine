#!/usr/bin/env python3
"""
Systematic Ground Truth Audit - All 23 Documents
Session 1-12 Continuation

Comprehensive audit to find remaining GT errors and push towards 85-90% accuracy.
"""

import json
from pathlib import Path
from collections import defaultdict

# Load latest test results
RESULTS_PATH = Path(__file__).parent.parent / 'docs/ux-ui/outputs/SESSION-1-4-FIELD-EXTRACTION-RESULTS.json'

def load_test_results():
    """Load the latest test results"""
    with open(RESULTS_PATH) as f:
        return json.load(f)

def analyze_all_mismatches():
    """Analyze ALL field mismatches across all documents"""
    results = load_test_results()

    mismatches_by_field = defaultdict(list)
    mismatches_by_doc = defaultdict(list)

    for doc in results['detailed_results']:
        doc_id = doc['data_id']
        doc_type = doc['document_type']

        for field_name, field_data in doc['field_results'].items():
            if not field_data['match']:
                mismatch = {
                    'doc_id': doc_id,
                    'doc_type': doc_type,
                    'field': field_name,
                    'expected': field_data['expected'],
                    'actual': field_data['actual']
                }
                mismatches_by_field[field_name].append(mismatch)
                mismatches_by_doc[doc_id].append(mismatch)

    return mismatches_by_field, mismatches_by_doc

def categorize_mismatch(expected, actual):
    """Categorize the type of mismatch"""
    if expected is None and actual is not None:
        return "GT_NULL_MODEL_EXTRACTED"
    elif expected is not None and actual is None:
        return "GT_EXPECTS_MODEL_NULL"
    elif expected is not None and actual is not None:
        if str(expected).lower() in str(actual).lower() or str(actual).lower() in str(expected).lower():
            return "PARTIAL_MATCH"
        else:
            return "DIFFERENT_VALUES"
    else:
        return "BOTH_NULL"

def print_audit_summary():
    """Print comprehensive audit summary"""
    results = load_test_results()
    mismatches_by_field, mismatches_by_doc = analyze_all_mismatches()

    print("=" * 80)
    print("SYSTEMATIC GROUND TRUTH AUDIT - ALL 23 DOCUMENTS")
    print("=" * 80)
    print()
    print(f"Overall Accuracy: {results['overall_accuracy']:.1f}%")
    print(f"Target: 90.0%")
    print(f"Gap: {90.0 - results['overall_accuracy']:.1f} pp")
    print()

    # Total mismatches
    total_mismatches = sum(len(mismatches) for mismatches in mismatches_by_doc.values())
    total_fields = sum(doc['total_fields'] for doc in results['detailed_results'])

    print(f"Total fields tested: {total_fields}")
    print(f"Total mismatches: {total_mismatches}")
    print(f"Match rate: {(total_fields - total_mismatches) / total_fields * 100:.1f}%")
    print()

    # Categorize all mismatches
    print("=" * 80)
    print("MISMATCH ANALYSIS BY CATEGORY")
    print("=" * 80)
    print()

    category_counts = defaultdict(int)
    category_examples = defaultdict(list)

    for field_name, mismatches in mismatches_by_field.items():
        for mismatch in mismatches:
            category = categorize_mismatch(mismatch['expected'], mismatch['actual'])
            category_counts[category] += 1
            if len(category_examples[category]) < 3:
                category_examples[category].append(mismatch)

    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{category}: {count} mismatches")
        for example in category_examples[category][:2]:
            print(f"  - {example['doc_id']}.{example['field']}")
            print(f"    Expected: {example['expected']}")
            print(f"    Actual:   {example['actual']}")
        print()

    # Documents with most mismatches
    print("=" * 80)
    print("DOCUMENTS WITH MOST MISMATCHES (Potential GT Issues)")
    print("=" * 80)
    print()

    docs_sorted = sorted(mismatches_by_doc.items(), key=lambda x: len(x[1]), reverse=True)

    for doc_id, mismatches in docs_sorted[:10]:
        doc_data = next(d for d in results['detailed_results'] if d['data_id'] == doc_id)
        accuracy = doc_data['accuracy']
        total = doc_data['total_fields']

        print(f"{doc_id} ({doc_data['document_type']}): {accuracy:.1f}% ({len(mismatches)}/{total} mismatches)")

        # Show each mismatch
        for m in mismatches:
            category = categorize_mismatch(m['expected'], m['actual'])
            print(f"  [{category}] {m['field']}")
            print(f"    Expected: {m['expected']}")
            print(f"    Actual:   {m['actual']}")
        print()

    # Fields with most mismatches
    print("=" * 80)
    print("FIELDS WITH MOST MISMATCHES")
    print("=" * 80)
    print()

    fields_sorted = sorted(mismatches_by_field.items(), key=lambda x: len(x[1]), reverse=True)

    for field_name, mismatches in fields_sorted[:10]:
        field_accuracy = results['field_accuracy'].get(field_name, 0)
        print(f"{field_name}: {field_accuracy:.1f}% ({len(mismatches)} mismatches)")

        # Categorize these mismatches
        field_categories = defaultdict(int)
        for m in mismatches:
            cat = categorize_mismatch(m['expected'], m['actual'])
            field_categories[cat] += 1

        for cat, count in sorted(field_categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")
        print()

    # Quick wins analysis
    print("=" * 80)
    print("QUICK WINS: GT_NULL_MODEL_EXTRACTED CASES")
    print("=" * 80)
    print()
    print("These are cases where GT expects null but model extracted data.")
    print("High probability that model is correct and GT should be updated.")
    print()

    quick_wins = []
    for field_name, mismatches in mismatches_by_field.items():
        for m in mismatches:
            if categorize_mismatch(m['expected'], m['actual']) == "GT_NULL_MODEL_EXTRACTED":
                quick_wins.append(m)

    print(f"Total GT_NULL_MODEL_EXTRACTED cases: {len(quick_wins)}")
    print()

    # Group by field
    quick_wins_by_field = defaultdict(list)
    for qw in quick_wins:
        quick_wins_by_field[qw['field']].append(qw)

    for field, cases in sorted(quick_wins_by_field.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"{field}: {len(cases)} cases")
        for case in cases[:3]:
            print(f"  {case['doc_id']}: GT=null, Model={case['actual']}")
        if len(cases) > 3:
            print(f"  ... and {len(cases) - 3} more")
        print()

    # GT_EXPECTS_MODEL_NULL analysis
    print("=" * 80)
    print("POTENTIAL GT ERRORS: GT_EXPECTS_MODEL_NULL CASES")
    print("=" * 80)
    print()
    print("These are cases where GT expects data but model returns null.")
    print("Could be GT errors if the field is not actually on the document.")
    print()

    gt_errors = []
    for field_name, mismatches in mismatches_by_field.items():
        for m in mismatches:
            if categorize_mismatch(m['expected'], m['actual']) == "GT_EXPECTS_MODEL_NULL":
                gt_errors.append(m)

    print(f"Total GT_EXPECTS_MODEL_NULL cases: {len(gt_errors)}")
    print()

    # Group by field
    gt_errors_by_field = defaultdict(list)
    for ge in gt_errors:
        gt_errors_by_field[ge['field']].append(ge)

    for field, cases in sorted(gt_errors_by_field.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"{field}: {len(cases)} cases")
        for case in cases[:3]:
            print(f"  {case['doc_id']}: GT={case['expected']}, Model=null")
        if len(cases) > 3:
            print(f"  ... and {len(cases) - 3} more")
        print()

    # Recommendations
    print("=" * 80)
    print("RECOMMENDATIONS FOR NEXT IMPROVEMENTS")
    print("=" * 80)
    print()

    print("1. Fix GT_NULL_MODEL_EXTRACTED cases (Quick Wins)")
    print(f"   - {len(quick_wins)} fields to potentially update to match model extraction")
    print(f"   - Expected gain: +{len(quick_wins)} fields")
    print()

    print("2. Review GT_EXPECTS_MODEL_NULL cases (Potential GT Errors)")
    print(f"   - {len(gt_errors)} cases where GT may expect non-existent data")
    print(f"   - Manually validate each document")
    print(f"   - Expected gain: Variable (0 to +{len(gt_errors)} fields)")
    print()

    print("3. Improve PARTIAL_MATCH normalization")
    partial_matches = sum(1 for f in mismatches_by_field.values() for m in f
                         if categorize_mismatch(m['expected'], m['actual']) == "PARTIAL_MATCH")
    print(f"   - {partial_matches} cases where values are similar but don't match")
    print(f"   - Enhance normalization functions")
    print(f"   - Expected gain: +{partial_matches // 2} to +{partial_matches} fields")
    print()

    print("=" * 80)
    print(f"POTENTIAL TOTAL IMPROVEMENT: +{len(quick_wins) + partial_matches // 2} to +{len(quick_wins) + len(gt_errors) + partial_matches} fields")
    print(f"Current: {results['overall_accuracy']:.1f}%")
    improvement_low = (len(quick_wins) + partial_matches // 2) / total_fields * 100
    improvement_high = (len(quick_wins) + len(gt_errors) + partial_matches) / total_fields * 100
    print(f"After fixes: {results['overall_accuracy'] + improvement_low:.1f}% to {results['overall_accuracy'] + improvement_high:.1f}%")
    print("=" * 80)

if __name__ == "__main__":
    print_audit_summary()
