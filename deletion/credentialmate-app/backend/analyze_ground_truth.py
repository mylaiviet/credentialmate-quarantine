#!/usr/bin/env python3
"""
Ground Truth Analysis Script
Analyzes ground truth files to identify issues affecting accuracy
"""

import json
from pathlib import Path
from typing import Dict, List, Any

# Low accuracy CME documents from baseline test
LOW_ACCURACY_DOCS = [
    ("TD-009", 50.0, "2/4 fields"),
    ("TD-010", 50.0, "2/4 fields"),
    ("TD-011", 50.0, "5/10 fields"),
    ("TD-012", 40.0, "4/10 fields"),  # LOWEST
    ("TD-013", 60.0, "6/10 fields"),
    ("TD-014", 70.0, "7/10 fields"),
    ("TD-015", 50.0, "5/10 fields"),
    ("TD-016", 50.0, "5/10 fields"),
    ("TD-017", 42.9, "3/7 fields"),
    ("TD-018", 42.9, "3/7 fields"),
    ("TD-019", 60.0, "6/10 fields"),
    ("TD-020", 50.0, "5/10 fields"),
]

def count_fields(data: Dict[str, Any], prefix: str = "") -> int:
    """Recursively count non-null fields in nested dict"""
    count = 0
    for key, value in data.items():
        current_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            count += count_fields(value, current_key)
        elif value is not None:
            count += 1
    return count

def analyze_ground_truth(data_id: str) -> Dict[str, Any]:
    """Analyze a single ground truth file"""
    gt_path = Path(__file__).parent / f"tests/fixtures/ground_truth/{data_id}_ground_truth.json"

    with open(gt_path, 'r') as f:
        gt_data = json.load(f)

    expected = gt_data.get('expected_extraction', {})

    # Count total expected fields
    total_fields = 0
    null_fields = []
    non_null_fields = []

    def analyze_dict(data, prefix=""):
        nonlocal total_fields
        for key, value in data.items():
            current_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                analyze_dict(value, current_key)
            else:
                total_fields += 1
                if value is None:
                    null_fields.append(current_key)
                else:
                    non_null_fields.append(current_key)

    analyze_dict(expected)

    return {
        "data_id": data_id,
        "total_expected_fields": total_fields,
        "null_fields_count": len(null_fields),
        "non_null_fields_count": len(non_null_fields),
        "null_percentage": (len(null_fields) / total_fields * 100) if total_fields > 0 else 0,
        "null_fields": null_fields,
        "non_null_fields": non_null_fields,
    }

def main():
    print("=" * 80)
    print("GROUND TRUTH ANALYSIS - Low Accuracy CME Documents")
    print("=" * 80)
    print()

    results = []

    for data_id, accuracy, correct in LOW_ACCURACY_DOCS:
        analysis = analyze_ground_truth(data_id)
        results.append({
            **analysis,
            "test_accuracy": accuracy,
            "test_correct": correct
        })

    # Summary table
    print(f"{'ID':<8} {'Accuracy':<10} {'Total':<8} {'Null':<8} {'Non-Null':<10} {'Null %':<10}")
    print("-" * 80)

    total_null = 0
    total_non_null = 0

    for r in results:
        print(f"{r['data_id']:<8} {r['test_accuracy']:<10.1f} {r['total_expected_fields']:<8} "
              f"{r['null_fields_count']:<8} {r['non_null_fields_count']:<10} "
              f"{r['null_percentage']:<10.1f}")
        total_null += r['null_fields_count']
        total_non_null += r['non_null_fields_count']

    print("-" * 80)
    total_fields = total_null + total_non_null
    print(f"{'TOTAL':<8} {'':<10} {total_fields:<8} {total_null:<8} {total_non_null:<10} "
          f"{(total_null/total_fields*100):<10.1f}")
    print()

    # Identify common null fields
    print("=" * 80)
    print("COMMON NULL FIELDS ACROSS LOW-ACCURACY DOCUMENTS")
    print("=" * 80)
    print()

    null_field_counts = {}
    for r in results:
        for field in r['null_fields']:
            null_field_counts[field] = null_field_counts.get(field, 0) + 1

    sorted_nulls = sorted(null_field_counts.items(), key=lambda x: x[1], reverse=True)

    print(f"{'Field Name':<50} {'Null Count':<15} {'% of Documents'}")
    print("-" * 80)
    for field, count in sorted_nulls:
        percentage = (count / len(results)) * 100
        print(f"{field:<50} {count:<15} {percentage:.1f}%")

    print()
    print("=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)
    print()

    # Calculate accuracy impact
    avg_null_pct = sum(r['null_percentage'] for r in results) / len(results)
    avg_accuracy = sum(r['test_accuracy'] for r in results) / len(results)

    print(f"Average null percentage: {avg_null_pct:.1f}%")
    print(f"Average test accuracy: {avg_accuracy:.1f}%")
    print()

    # Detailed analysis of worst performers
    print("WORST PERFORMERS (accuracy < 50%):")
    print()
    for r in results:
        if r['test_accuracy'] < 50:
            print(f"{r['data_id']} - {r['test_accuracy']}% accuracy")
            print(f"  Null fields: {', '.join(r['null_fields'])}")
            print()

if __name__ == "__main__":
    main()
