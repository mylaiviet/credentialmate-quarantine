#!/usr/bin/env python3
"""
Restore Title Fields and Create Validation Report

This script:
1. Restores title fields from backups (where we incorrectly set them to null)
2. Extracts what the parser actually found for each title
3. Creates a validation report for manual review

Session: ui-ux-1-8
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


def get_latest_backup(data_id: str, ground_truth_dir: Path) -> Path:
    """Find the most recent backup for a ground truth file"""
    backup_dir = ground_truth_dir / "backups"
    if not backup_dir.exists():
        return None

    # Find all backups for this data_id
    backups = list(backup_dir.glob(f"{data_id}_ground_truth_backup_*.json"))
    if not backups:
        return None

    # Return most recent (by filename timestamp)
    return sorted(backups)[-1]


def restore_title_from_backup(data_id: str, ground_truth_dir: Path) -> Tuple[bool, str, any]:
    """
    Restore title field from backup.

    Returns: (success, message, original_title_value)
    """
    current_file = ground_truth_dir / f"{data_id}_ground_truth.json"
    backup_file = get_latest_backup(data_id, ground_truth_dir)

    if not backup_file:
        return False, "No backup found", None

    # Load current and backup
    with open(current_file, 'r') as f:
        current_data = json.load(f)

    with open(backup_file, 'r') as f:
        backup_data = json.load(f)

    # Get title values
    current_title = current_data.get('expected_extraction', {}).get('credential_details', {}).get('title')
    backup_title = backup_data.get('expected_extraction', {}).get('credential_details', {}).get('title')

    # If current is null and backup had a value, restore it
    if current_title is None and backup_title is not None:
        current_data['expected_extraction']['credential_details']['title'] = backup_title

        # Save restored version
        with open(current_file, 'w') as f:
            json.dump(current_data, f, indent=2)

        return True, f"Restored title: '{backup_title}'", backup_title
    else:
        return False, f"No restoration needed (current={current_title}, backup={backup_title})", backup_title


def get_parser_extracted_title(data_id: str, results_file: Path) -> any:
    """Get what the parser actually extracted for this document's title"""
    if not results_file.exists():
        return "RESULTS_FILE_NOT_FOUND"

    with open(results_file, 'r') as f:
        results = json.load(f)

    # Find this document in results
    for result in results.get('detailed_results', []):
        if result['data_id'] == data_id:
            return result.get('field_results', {}).get('credential_details.title', {}).get('actual')

    return "NOT_IN_RESULTS"


def main():
    print("Title Field Restoration and Validation")
    print("=" * 80)
    print()

    ground_truth_dir = Path(__file__).parent / "tests/fixtures/ground_truth"
    results_file = Path(__file__).parent.parent / "docs/ux-ui/outputs/SESSION-1-4-FIELD-EXTRACTION-RESULTS.json"

    # Files that had title set to null in Session 1-7
    cme_files_to_restore = [
        'TD-001', 'TD-002', 'TD-003', 'TD-008',
        'TD-012', 'TD-014', 'TD-015', 'TD-016',
        'TD-017', 'TD-018', 'TD-019', 'TD-020'
    ]

    restoration_results = []
    validation_report = []

    print("PHASE 1: Restoring Title Fields from Backups")
    print("-" * 80)

    for data_id in cme_files_to_restore:
        success, message, original_title = restore_title_from_backup(data_id, ground_truth_dir)

        restoration_results.append({
            'data_id': data_id,
            'success': success,
            'message': message,
            'original_title': original_title
        })

        if success:
            print(f"[OK] {data_id}: {message}")
        else:
            print(f"[SKIP] {data_id}: {message}")

    print()
    print("PHASE 2: Creating Validation Report")
    print("-" * 80)
    print()

    # Create validation report comparing ground truth vs parser output
    for data_id in cme_files_to_restore:
        # Get current ground truth
        gt_file = ground_truth_dir / f"{data_id}_ground_truth.json"
        with open(gt_file, 'r') as f:
            gt_data = json.load(f)

        gt_title = gt_data.get('expected_extraction', {}).get('credential_details', {}).get('title')
        gt_issuer = gt_data.get('expected_extraction', {}).get('credential_details', {}).get('issuing_authority')

        # Get parser output
        parser_title = get_parser_extracted_title(data_id, results_file)

        # Determine validation status
        if gt_title == parser_title:
            status = "MATCH"
            recommendation = "No action needed - ground truth matches parser"
        elif gt_title is None and parser_title is None:
            status = "MATCH"
            recommendation = "Both null - correct"
        elif gt_title is None and parser_title:
            # Ground truth null, parser found something
            if parser_title == gt_issuer or (gt_issuer and parser_title in gt_issuer):
                status = "ACCEPTABLE"
                recommendation = f"Parser extracted issuer name as title. Consider setting ground truth to: '{parser_title}'"
            else:
                status = "NEEDS_REVIEW"
                recommendation = f"Parser found course title. UPDATE ground truth to: '{parser_title}'"
        elif gt_title and parser_title is None:
            status = "MISMATCH"
            recommendation = f"Ground truth has '{gt_title}' but parser returned null. Verify certificate."
        else:
            # Both have values but different
            status = "MISMATCH"
            recommendation = f"Values differ. Manual review needed."

        validation_entry = {
            'data_id': data_id,
            'ground_truth_title': gt_title,
            'parser_extracted_title': parser_title,
            'issuing_authority': gt_issuer,
            'status': status,
            'recommendation': recommendation
        }

        validation_report.append(validation_entry)

        # Print summary
        status_icon = {
            'MATCH': '[OK]',
            'ACCEPTABLE': '[*]',
            'NEEDS_REVIEW': '[!]',
            'MISMATCH': '[X]'
        }.get(status, '[?]')

        print(f"{status_icon} {data_id} ({status})")
        print(f"    Ground Truth: {gt_title}")
        print(f"    Parser Found: {parser_title}")
        print(f"    Issuer: {gt_issuer}")
        print(f"    Action: {recommendation}")
        print()

    # Save validation report
    report_path = Path(__file__).parent.parent / "docs/ux-ui/outputs/TITLE_VALIDATION_REPORT.json"
    with open(report_path, 'w') as f:
        json.dump({
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'total_files': len(cme_files_to_restore),
            'restoration_results': restoration_results,
            'validation_report': validation_report,
            'status_summary': {
                'MATCH': sum(1 for v in validation_report if v['status'] == 'MATCH'),
                'ACCEPTABLE': sum(1 for v in validation_report if v['status'] == 'ACCEPTABLE'),
                'NEEDS_REVIEW': sum(1 for v in validation_report if v['status'] == 'NEEDS_REVIEW'),
                'MISMATCH': sum(1 for v in validation_report if v['status'] == 'MISMATCH'),
            }
        }, f, indent=2)

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    restored_count = sum(1 for r in restoration_results if r['success'])
    print(f"Files restored: {restored_count}/{len(cme_files_to_restore)}")

    status_summary = {
        'MATCH': sum(1 for v in validation_report if v['status'] == 'MATCH'),
        'ACCEPTABLE': sum(1 for v in validation_report if v['status'] == 'ACCEPTABLE'),
        'NEEDS_REVIEW': sum(1 for v in validation_report if v['status'] == 'NEEDS_REVIEW'),
        'MISMATCH': sum(1 for v in validation_report if v['status'] == 'MISMATCH'),
    }

    print()
    print("Validation Status:")
    for status, count in status_summary.items():
        print(f"  {status:15} {count} files")

    needs_action = status_summary['NEEDS_REVIEW'] + status_summary['MISMATCH']
    print()
    print(f"Files needing manual updates: {needs_action}")

    print(f"\nValidation report saved to: {report_path}")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
