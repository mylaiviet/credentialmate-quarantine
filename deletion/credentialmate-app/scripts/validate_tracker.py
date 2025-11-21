#!/usr/bin/env python3
"""
Project Tracker Validation Script

Validates PHASE1_PROJECT_TRACKER.csv for completeness and compliance.
Run daily to ensure SOC2 audit trail compliance.

Usage:
    python scripts/validate_tracker.py

Returns:
    Exit code 0 if validation passes
    Exit code 1 if validation fails
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

# Tracker file location
TRACKER_FILE = Path(__file__).parent.parent / "docs" / "governance" / "initiatives" / "PHASE1_PROJECT_TRACKER.csv"

# Required fields for COMPLETE tasks
REQUIRED_FIELDS_COMPLETE = [
    'completion_date',
    'ris_compliant',
    'soc2_signed',
    'tracker_updated_by',
    'tracker_updated_at'
]

def validate_tracker():
    """Main validation function"""

    if not TRACKER_FILE.exists():
        print(f"❌ TRACKER FILE NOT FOUND: {TRACKER_FILE}")
        return False

    errors = []
    warnings = []
    tasks = {
        'PENDING': 0,
        'IN_PROGRESS': 0,
        'COMPLETE': 0,
        'BLOCKED': 0,
        'DEFERRED': 0,
        'CANCELLED': 0
    }

    compliance_checks = {
        'complete_with_fields': True,
        'complete_ris_compliant': True,
        'complete_soc2_signed': True,
        'blocked_with_description': True
    }

    with open(TRACKER_FILE, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            task_id = row['task_id']
            status = row['status']

            # Count tasks by status
            if status in tasks:
                tasks[status] += 1
            else:
                errors.append(f"{task_id}: Invalid status '{status}'")

            # Validate COMPLETE tasks
            if status == 'COMPLETE':
                # Check required fields
                for field in REQUIRED_FIELDS_COMPLETE:
                    if not row.get(field) or row[field].strip() == '':
                        errors.append(f"{task_id}: COMPLETE but missing {field}")
                        compliance_checks['complete_with_fields'] = False

                # Check RIS compliance
                if row.get('ris_compliant') != 'TRUE':
                    errors.append(f"{task_id}: COMPLETE but ris_compliant != TRUE (value: '{row.get('ris_compliant')}')")
                    compliance_checks['complete_ris_compliant'] = False

                # Check SOC2 signed
                if row.get('soc2_signed') != 'TRUE':
                    errors.append(f"{task_id}: COMPLETE but soc2_signed != TRUE (value: '{row.get('soc2_signed')}')")
                    compliance_checks['complete_soc2_signed'] = False

                # Check tests_passing if applicable
                if row.get('tests_passing') and int(row['tests_passing']) == 0:
                    warnings.append(f"{task_id}: COMPLETE but 0 tests passing (is this correct?)")

            # Validate BLOCKED tasks
            if status == 'BLOCKED':
                if not row.get('blockers') or row['blockers'].strip() == '':
                    errors.append(f"{task_id}: BLOCKED but no blocker description")
                    compliance_checks['blocked_with_description'] = False
                else:
                    warnings.append(f"{task_id}: Task is BLOCKED - {row['blockers']}")

            # Validate IN_PROGRESS tasks for timeline
            if status == 'IN_PROGRESS':
                target_date = row.get('target_date')
                if target_date:
                    try:
                        target = datetime.strptime(target_date, '%Y-%m-%d')
                        today = datetime.now()
                        if target < today.replace(hour=0, minute=0, second=0, microsecond=0):
                            warnings.append(f"{task_id}: IN_PROGRESS but past target_date ({target_date})")
                    except ValueError:
                        errors.append(f"{task_id}: Invalid target_date format: {target_date}")

    # Print results
    print("\n" + "="*60)
    if errors:
        print("❌ TRACKER VALIDATION FAILED\n")
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ TRACKER VALIDATION PASSED\n")

    print("="*60)
    print("Summary:")
    print(f"  - Total tasks: {sum(tasks.values())}")
    for status, count in tasks.items():
        print(f"  - {status}: {count}")

    print("\nCompliance:")
    print(f"  - All COMPLETE tasks have required fields: {'YES' if compliance_checks['complete_with_fields'] else 'NO'}")
    print(f"  - All COMPLETE tasks RIS compliant: {'YES' if compliance_checks['complete_ris_compliant'] else 'NO'}")
    print(f"  - All COMPLETE tasks SOC2 signed: {'YES' if compliance_checks['complete_soc2_signed'] else 'NO'}")
    print(f"  - All BLOCKED tasks have description: {'YES' if compliance_checks['blocked_with_description'] else 'NO'}")

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")

    if tasks['BLOCKED'] > 0:
        print("\nActions required:")
        print(f"  - PM review BLOCKERS.md for {tasks['BLOCKED']} blocked task(s)")

    print("="*60 + "\n")

    return len(errors) == 0


if __name__ == '__main__':
    success = validate_tracker()
    sys.exit(0 if success else 1)
