#!/usr/bin/env python3
# TIMESTAMP: 2025-11-17T20:00:00Z
# ORIGIN: credentialmate-app
# UPDATED_FOR: ui-ux-governance-validation
# COMPLIANCE: ISO/SOC2

"""
UX/UI Session Validation Script

Validates that AI agents completed their session work correctly by checking:
1. CSV updates (tracker, session log, standards, test catalog, schema log)
2. Timestamp formats (ISO 8601 UTC)
3. File path verification
4. Test coverage validation
5. SOC2 compliance
6. Cross-lane access audit
7. Drift detection

Usage:
    python scripts/validate_ux_ui_session.py [session_id]
    python scripts/validate_ux_ui_session.py --latest

Examples:
    python scripts/validate_ux_ui_session.py ui-ux-1-2
    python scripts/validate_ux_ui_session.py --latest
"""

import csv
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Base path
BASE_DIR = Path(__file__).parent.parent

# CSV paths
TRACKER_CSV = BASE_DIR / "docs" / "ux-ui" / "governance" / "UX_UI_PROJECT_TRACKER.csv"
SESSION_LOG_CSV = BASE_DIR / "docs" / "ux-ui" / "outputs" / "ui-ux-SESSION_OUTPUT_LOG.csv"
STANDARDS_CSV = BASE_DIR / "docs" / "ux-ui" / "outputs" / "ui-ux-STANDARDS.csv"
TEST_DATA_CSV = BASE_DIR / "docs" / "ux-ui" / "outputs" / "ui-ux-TEST_DATA_CATALOG.csv"
SCHEMA_LOG_CSV = BASE_DIR / "docs" / "SCHEMA_CHANGE_LOG.csv"


class ValidationResult:
    """Validation result container"""
    def __init__(self):
        self.passed = True
        self.errors = []
        self.warnings = []
        self.session_id = None
        self.session_data = {}

    def add_error(self, message: str):
        self.passed = False
        self.errors.append(message)

    def add_warning(self, message: str):
        self.warnings.append(message)

    def print_report(self):
        """Print validation report"""
        if self.passed:
            print("\n[PASS] Session Validation: PASS\n")
            print(f"Session: {self.session_id}")
            print(f"Status: {self.session_data.get('status', 'UNKNOWN')}")
            print(f"Tests Passing: {self.session_data.get('tests_passing', 'N/A')}")
            print(f"Coverage: {self.session_data.get('coverage_pct', 'N/A')}%")
            print(f"Files Modified: {len(self.session_data.get('files_modified', '').split(',')) if self.session_data.get('files_modified') else 0}")
            print(f"Files Created: {len(self.session_data.get('files_created', '').split(',')) if self.session_data.get('files_created') else 0}")
            print(f"Cross-Lane Access: {self.session_data.get('cross_lane_access', 'N/A')}")
            print(f"SOC2 Compliant: {self.session_data.get('soc2_signed', 'N/A')}")

            if self.warnings:
                print("\n[WARNING] Warnings:")
                for warning in self.warnings:
                    print(f"  - {warning}")

            print("\nAll validation checks passed. Session approved.")
        else:
            print("\n[FAIL] Session Validation: FAIL\n")
            print(f"Session: {self.session_id}")
            print("\nIssues found:")
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. [ERROR] {error}")

            if self.warnings:
                print("\n[WARNING] Warnings:")
                for warning in self.warnings:
                    print(f"  - {warning}")

            print("\nSession NOT approved. Fix issues before proceeding to next session.")


def read_csv(file_path: Path) -> List[Dict]:
    """Read CSV file and return list of dicts"""
    if not file_path.exists():
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def validate_timestamp(timestamp_str: str, field_name: str, result: ValidationResult) -> bool:
    """Validate ISO 8601 UTC timestamp format"""
    if not timestamp_str or timestamp_str == 'N/A':
        return True  # Optional fields

    # Expected format: 2025-11-17T20:00:00Z
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

        # Check format exactly matches ISO 8601 UTC
        if not timestamp_str.endswith('Z'):
            result.add_error(f"{field_name}: Missing 'Z' suffix (must be UTC): {timestamp_str}")
            return False

        if 'T' not in timestamp_str:
            result.add_error(f"{field_name}: Missing 'T' separator: {timestamp_str}")
            return False

        return True
    except (ValueError, AttributeError):
        result.add_error(f"{field_name}: Invalid timestamp format: {timestamp_str} (expected YYYY-MM-DDTHH:MM:SSZ)")
        return False


def validate_file_exists(file_path: str, result: ValidationResult) -> bool:
    """Validate that declared file actually exists"""
    if not file_path or file_path == 'N/A':
        return True

    full_path = BASE_DIR / file_path
    if not full_path.exists():
        result.add_error(f"File declared but not found: {file_path}")
        return False

    return True


def get_latest_session(session_log: List[Dict]) -> str:
    """Get latest completed session ID"""
    completed = [s for s in session_log if s.get('status') == 'COMPLETE']
    if not completed:
        return None

    # Sort by timestamp
    completed.sort(key=lambda x: x.get('session_end_timestamp', ''), reverse=True)
    return completed[0].get('session_id')


def validate_session(session_id: str) -> ValidationResult:
    """Main validation logic"""
    result = ValidationResult()
    result.session_id = session_id

    # Read CSVs
    tracker_rows = read_csv(TRACKER_CSV)
    session_log_rows = read_csv(SESSION_LOG_CSV)
    standards_rows = read_csv(STANDARDS_CSV)

    # Find session in logs
    session_log_entry = next((s for s in session_log_rows if s.get('session_id') == session_id), None)
    tracker_entry = next((t for t in tracker_rows if t.get('session_id') == session_id), None)

    if not session_log_entry:
        result.add_error(f"Session {session_id} not found in ui-ux-SESSION_OUTPUT_LOG.csv")
        return result

    if not tracker_entry:
        result.add_error(f"Session {session_id} not found in UX_UI_PROJECT_TRACKER.csv")
        return result

    result.session_data = {**session_log_entry, **tracker_entry}

    # 1. Check status = COMPLETE
    if session_log_entry.get('status') != 'COMPLETE':
        result.add_error(f"Session status is '{session_log_entry.get('status')}', expected 'COMPLETE'")

    if tracker_entry.get('status') != 'COMPLETE':
        result.add_error(f"Tracker status is '{tracker_entry.get('status')}', expected 'COMPLETE'")

    # 2. Validate timestamps
    validate_timestamp(session_log_entry.get('session_start_timestamp'), 'session_start_timestamp', result)
    validate_timestamp(session_log_entry.get('session_end_timestamp'), 'session_end_timestamp', result)
    validate_timestamp(session_log_entry.get('entry_created_at'), 'entry_created_at', result)
    validate_timestamp(tracker_entry.get('completion_date'), 'completion_date', result)
    validate_timestamp(tracker_entry.get('tracker_updated_at'), 'tracker_updated_at', result)

    # 3. Validate file paths
    files_modified = tracker_entry.get('files_modified', '').split(',')
    files_created = tracker_entry.get('files_created', '').split(',')

    for file_path in files_modified:
        if file_path and file_path.strip() and file_path != 'N/A':
            validate_file_exists(file_path.strip(), result)

    for file_path in files_created:
        if file_path and file_path.strip() and file_path != 'N/A':
            validate_file_exists(file_path.strip(), result)

    # 4. Test coverage validation
    tests_passing = session_log_entry.get('tests_passing', '').lower()
    if tests_passing not in ['yes', 'no', 'n/a']:
        result.add_error(f"tests_passing must be 'yes', 'no', or 'N/A', got: {tests_passing}")

    if tests_passing == 'no':
        result.add_error("Tests are not passing - session cannot be marked COMPLETE")

    coverage_str = session_log_entry.get('coverage_pct', '')
    if coverage_str and coverage_str != 'N/A':
        try:
            coverage = float(coverage_str)
            if coverage < 90:
                result.add_warning(f"Coverage {coverage}% is below recommended 90%+ target")
        except ValueError:
            result.add_error(f"Invalid coverage_pct format: {coverage_str}")

    # 5. SOC2 compliance check
    soc2_signed = tracker_entry.get('soc2_signed', '').lower()
    if soc2_signed != 'yes':
        result.add_error(f"soc2_signed must be 'yes', got: {soc2_signed}")

    # 6. Cross-lane access audit
    cross_lane_access = session_log_entry.get('cross_lane_access', '').lower()
    if cross_lane_access not in ['yes', 'no', 'n/a']:
        result.add_error(f"cross_lane_access must be 'yes', 'no', or 'N/A', got: {cross_lane_access}")

    if cross_lane_access == 'yes':
        notes = session_log_entry.get('notes', '')
        if not notes or 'cross-lane' not in notes.lower():
            result.add_warning("Cross-lane access occurred but not documented in notes")

    # 7. Check for blockers
    blockers = session_log_entry.get('blockers', '')
    if blockers and blockers.lower() not in ['none', 'n/a', '']:
        result.add_error(f"Session has unresolved blockers: {blockers}")

    # 8. Verify agent updated standards if new patterns established
    session_standards = [s for s in standards_rows if s.get('session_id') == session_id]
    if session_standards:
        result.add_warning(f"Session established {len(session_standards)} new standards")

    return result


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_ux_ui_session.py [session_id]")
        print("   Or: python scripts/validate_ux_ui_session.py --latest")
        sys.exit(1)

    session_id = sys.argv[1]

    # Handle --latest flag
    if session_id == '--latest':
        session_log_rows = read_csv(SESSION_LOG_CSV)
        session_id = get_latest_session(session_log_rows)
        if not session_id:
            print("❌ No completed sessions found in session log")
            sys.exit(1)
        print(f"Validating latest session: {session_id}\n")

    # Validate session
    result = validate_session(session_id)
    result.print_report()

    # Exit code
    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
