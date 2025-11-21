"""
Standalone script to measure document classification accuracy.

This script runs classification tests with real AWS Bedrock API calls
and generates a comprehensive accuracy report.

Author: Claude Code
Session: ui-ux-1-3 (Phase 1 Session 3 - Accuracy Improvement)
Created: 2025-11-18
"""

import sys
import json
import csv
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.document_type_detector import DocumentTypeDetector

# Paths
TEST_DATA_CATALOG = Path("../docs/ux-ui/outputs/ui-ux-TEST_DATA_CATALOG.csv")
GROUND_TRUTH_DIR = Path("tests/fixtures/ground_truth")
UPLOADS_DIR = Path("uploads/2025/11")


def load_test_catalog() -> List[Dict[str, str]]:
    """Load test data catalog CSV."""
    with open(TEST_DATA_CATALOG, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [row for row in reader if row['approved_for_use'] == 'yes']


def load_ground_truth(data_id: str) -> Dict[str, Any]:
    """Load ground truth JSON for a data ID."""
    gt_file = GROUND_TRUTH_DIR / f"{data_id}_ground_truth.json"
    with open(gt_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_document(file_path: str) -> bytes:
    """Load document bytes from file path."""
    # Handle both relative and absolute paths
    if file_path.startswith('backend/'):
        file_path = file_path.replace('backend/', '')

    path = Path(file_path)
    with open(path, 'rb') as f:
        return f.read()


def run_accuracy_test() -> Dict[str, Any]:
    """
    Run accuracy test across all approved documents.

    Returns:
        Dictionary with accuracy metrics and failure details
    """
    print("=" * 80)
    print("DOCUMENT CLASSIFICATION ACCURACY TEST")
    print("Session: ui-ux-1-3 (Phase 1 Session 3)")
    print("Mode: REAL AWS Bedrock API calls (use_mock=False)")
    print("=" * 80)
    print()

    # Initialize detector with REAL AWS Bedrock
    print("Initializing DocumentTypeDetector with AWS Bedrock...")
    detector = DocumentTypeDetector(use_mock=False, enable_two_stage=True)
    print("✓ Detector initialized")
    print()

    # Load test catalog
    print("Loading test data catalog...")
    catalog = load_test_catalog()
    print(f"✓ Loaded {len(catalog)} approved test documents")
    print()

    # Track results
    results_by_type = {}
    correct = 0
    total = 0
    failures = []

    print("Running classification tests...")
    print("-" * 80)

    for i, row in enumerate(catalog, 1):
        data_id = row['data_id']
        file_path = row['file_path']
        expected_type = row['expected_document_type']

        print(f"\n[{i}/{len(catalog)}] Testing {data_id}: {Path(file_path).name}")
        print(f"    Expected: {expected_type}")

        try:
            # Load document and ground truth
            doc_bytes = load_document(file_path)
            ground_truth = load_ground_truth(data_id)

            # Classify document
            result = detector.classify_document_type(doc_bytes)

            # Check if correct
            is_correct = result.document_type == expected_type

            # Track by type
            if expected_type not in results_by_type:
                results_by_type[expected_type] = {'correct': 0, 'total': 0, 'tests': []}

            results_by_type[expected_type]['total'] += 1
            results_by_type[expected_type]['tests'].append({
                'data_id': data_id,
                'file': Path(file_path).name,
                'expected': expected_type,
                'actual': result.document_type,
                'confidence': result.confidence,
                'correct': is_correct
            })

            total += 1

            if is_correct:
                correct += 1
                results_by_type[expected_type]['correct'] += 1
                print(f"    ✓ PASS - Actual: {result.document_type} (confidence: {result.confidence:.2f})")
            else:
                failures.append({
                    'data_id': data_id,
                    'file': Path(file_path).name,
                    'expected': expected_type,
                    'actual': result.document_type,
                    'confidence': result.confidence,
                    'reasoning': result.reasoning[:150] if result.reasoning else None
                })
                print(f"    ✗ FAIL - Actual: {result.document_type} (confidence: {result.confidence:.2f})")
                print(f"    Reasoning: {result.reasoning[:100]}...")

        except Exception as e:
            print(f"    ✗ ERROR: {str(e)}")
            failures.append({
                'data_id': data_id,
                'file': Path(file_path).name,
                'expected': expected_type,
                'actual': 'ERROR',
                'confidence': 0.0,
                'reasoning': str(e)
            })
            total += 1

    print()
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print()

    # Calculate overall accuracy
    overall_accuracy = (correct / total * 100) if total > 0 else 0

    print(f"Overall Accuracy: {overall_accuracy:.1f}% ({correct}/{total} documents)")
    print()

    # Per-type accuracy
    print("Accuracy by Document Type:")
    print("-" * 80)
    for doc_type in sorted(results_by_type.keys()):
        stats = results_by_type[doc_type]
        type_accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        status = "✓" if type_accuracy >= 90 else "✗"
        print(f"  {status} {doc_type:25s}: {type_accuracy:5.1f}% ({stats['correct']}/{stats['total']})")

    print()

    # Failures
    if failures:
        print(f"Failures ({len(failures)}):")
        print("-" * 80)
        for failure in failures:
            print(f"  ✗ {failure['data_id']} ({failure['file']})")
            print(f"    Expected: {failure['expected']}, Got: {failure['actual']} (confidence: {failure['confidence']:.2f})")
            print(f"    Reason: {failure['reasoning']}")
            print()
    else:
        print("✓ No failures!")
        print()

    # Session 1-2 baseline comparison
    session_1_2_baseline = 36.4
    improvement = overall_accuracy - session_1_2_baseline

    print("Comparison to Session 1-2 Baseline:")
    print("-" * 80)
    print(f"  Session 1-2 Baseline: {session_1_2_baseline:.1f}%")
    print(f"  Session 1-3 Result:   {overall_accuracy:.1f}%")
    print(f"  Improvement:          +{improvement:.1f} percentage points")
    print()

    # Target check
    target_accuracy = 95.0
    if overall_accuracy >= target_accuracy:
        print(f"✓ SUCCESS: Achieved target accuracy of {target_accuracy}%")
    else:
        gap = target_accuracy - overall_accuracy
        print(f"✗ BELOW TARGET: Need +{gap:.1f} percentage points to reach {target_accuracy}%")

    print()

    return {
        'timestamp': datetime.now().isoformat(),
        'overall_accuracy': overall_accuracy,
        'correct': correct,
        'total': total,
        'results_by_type': results_by_type,
        'failures': failures,
        'session_1_2_baseline': session_1_2_baseline,
        'improvement': improvement
    }


if __name__ == '__main__':
    try:
        results = run_accuracy_test()

        # Save results to JSON
        output_file = Path("../docs/ux-ui/outputs/SESSION-1-3-ACCURACY-RESULTS.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

        print(f"Results saved to: {output_file}")
        print()

        # Exit with code based on target achievement
        sys.exit(0 if results['overall_accuracy'] >= 95.0 else 1)

    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
