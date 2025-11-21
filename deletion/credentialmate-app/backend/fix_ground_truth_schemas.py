#!/usr/bin/env python3
"""
Ground Truth Schema Fix Script

Automatically fixes schema inconsistencies identified by the audit.

Session: ui-ux-1-7
Phase: 1 (Ground Truth Fixes)
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def backup_file(file_path: Path) -> Path:
    """Create backup of original file"""
    backup_dir = file_path.parent / "backups"
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"

    shutil.copy2(file_path, backup_path)
    return backup_path


def fix_cme_title_field(data: Dict, data_id: str) -> tuple[Dict, List[str]]:
    """
    Fix CME title field - set to null if it contains issuer name.

    Issue: Title field contains issuing authority name instead of course title.
    Files affected: TD-001, TD-002, TD-003, TD-008, TD-012, TD-014, TD-015,
                    TD-016, TD-017, TD-018, TD-019, TD-020
    """
    changes = []

    if data.get('expected_classification', {}).get('document_type') != 'cme':
        return data, changes

    extraction = data.get('expected_extraction', {})
    if not extraction:
        return data, changes

    credential_details = extraction.get('credential_details', {})
    title = credential_details.get('title')
    issuing_authority = credential_details.get('issuing_authority', '')

    # Check if title appears to be an issuer name, not a course title
    issuer_keywords = ['UpToDate', 'NetCE', 'Pennsylvania', 'Nebraska', 'Wills Eye', 'Hospital']

    if title and any(keyword in str(title) for keyword in issuer_keywords):
        old_title = title
        credential_details['title'] = None
        changes.append(f"Set title to null (was: '{old_title}')")

    return data, changes


def fix_field_names(data: Dict, data_id: str) -> tuple[Dict, List[str]]:
    """
    Fix field name mismatches.

    Issues:
    - license_number → credential_number
    - state → jurisdiction (with value normalization)

    Files affected: TD-004, TD-007
    """
    changes = []

    extraction = data.get('expected_extraction', {})
    if not extraction:
        return data, changes

    credential_details = extraction.get('credential_details', {})

    # Fix license_number → credential_number
    if 'license_number' in credential_details:
        old_value = credential_details['license_number']
        # Add as credential_number (keep both for now to avoid breaking)
        if 'credential_number' not in credential_details:
            credential_details['credential_number'] = old_value
            changes.append(f"Added credential_number: {old_value} (from license_number)")
        # Remove license_number
        # del credential_details['license_number']
        # changes.append(f"Removed license_number (migrated to credential_number)")

    # Fix state → jurisdiction
    if 'state' in credential_details:
        old_state = credential_details['state']

        # Normalize state to 2-letter code
        state_map = {
            'Missouri': 'MO',
            'Pennsylvania': 'PA',
            'Nebraska': 'NE',
            'California': 'CA',
            'New York': 'NY',
            'Texas': 'TX',
            'Florida': 'FL',
        }

        new_jurisdiction = state_map.get(old_state, old_state)

        # Add jurisdiction field
        if 'jurisdiction' not in credential_details:
            credential_details['jurisdiction'] = new_jurisdiction
            changes.append(f"Added jurisdiction: {new_jurisdiction} (from state: {old_state})")

        # Remove state field
        # del credential_details['state']
        # changes.append(f"Removed state field (migrated to jurisdiction)")

    return data, changes


def fix_name_format(data: Dict, data_id: str) -> tuple[Dict, List[str]]:
    """
    Fix name format from "LAST, FIRST" to "First Last".

    Files affected: TD-004, TD-007
    """
    changes = []

    extraction = data.get('expected_extraction', {})
    if not extraction:
        return data, changes

    provider_info = extraction.get('provider_info', {})
    name = provider_info.get('name')

    if not name:
        return data, changes

    # Check if format is "LAST, FIRST"
    if ',' in name:
        parts = [p.strip() for p in name.split(',', 1)]
        if len(parts) == 2:
            last, first = parts
            # Normalize to "First Last" with proper casing
            normalized_name = f"{first.title()} {last.title()}"

            if normalized_name != name:
                old_name = name
                provider_info['name'] = normalized_name
                changes.append(f"Normalized name: '{old_name}' -> '{normalized_name}'")

    return data, changes


def fix_professional_designation(data: Dict, data_id: str) -> tuple[Dict, List[str]]:
    """
    Fix professional designation format (full to abbreviated).

    Example: "MEDICAL DOCTOR" → "MD"
    """
    changes = []

    extraction = data.get('expected_extraction', {})
    if not extraction:
        return data, changes

    provider_info = extraction.get('provider_info', {})
    designation = provider_info.get('professional_designation')

    if not designation:
        return data, changes

    # Abbreviation map
    abbrev_map = {
        'MEDICAL DOCTOR': 'MD',
        'Doctor of Medicine': 'MD',
        'Doctor of Osteopathic Medicine': 'DO',
        'Nurse Practitioner': 'NP',
        'Physician Assistant': 'PA',
        'Registered Nurse': 'RN',
    }

    if designation in abbrev_map:
        old_designation = designation
        provider_info['professional_designation'] = abbrev_map[designation]
        changes.append(f"Abbreviated designation: '{old_designation}' -> '{abbrev_map[designation]}'")

    return data, changes


def process_ground_truth_file(file_path: Path, apply_fixes: bool = False) -> Dict:
    """
    Process a single ground truth file and apply fixes.

    Args:
        file_path: Path to ground truth JSON file
        apply_fixes: If True, save changes; if False, dry run

    Returns:
        Dict with processing results
    """
    with open(file_path, 'r') as f:
        data = json.load(f)

    data_id = data.get('data_id')
    all_changes = []

    # Apply all fixes
    data, changes = fix_cme_title_field(data, data_id)
    all_changes.extend(changes)

    data, changes = fix_field_names(data, data_id)
    all_changes.extend(changes)

    data, changes = fix_name_format(data, data_id)
    all_changes.extend(changes)

    data, changes = fix_professional_designation(data, data_id)
    all_changes.extend(changes)

    # Save if changes were made and apply_fixes is True
    if all_changes and apply_fixes:
        # Backup original
        backup_path = backup_file(file_path)

        # Save fixed version
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    return {
        'data_id': data_id,
        'file_path': str(file_path),
        'changes_made': len(all_changes),
        'changes': all_changes,
        'modified': len(all_changes) > 0 and apply_fixes
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Fix ground truth schema issues')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying them')
    parser.add_argument('--apply', action='store_true', help='Apply fixes and save files')
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("ERROR: Must specify either --dry-run or --apply")
        print("\nUsage:")
        print("  python fix_ground_truth_schemas.py --dry-run   # Preview changes")
        print("  python fix_ground_truth_schemas.py --apply     # Apply fixes")
        return 1

    apply_fixes = args.apply

    print("Ground Truth Schema Fix Script")
    print("=" * 80)
    print(f"Mode: {'APPLY FIXES' if apply_fixes else 'DRY RUN (preview only)'}")
    print("=" * 80)
    print()

    # Find all ground truth files
    ground_truth_dir = Path(__file__).parent / "tests/fixtures/ground_truth"
    gt_files = sorted(ground_truth_dir.glob("*_ground_truth.json"))

    print(f"Found {len(gt_files)} ground truth files\n")

    # Process all files
    results = []
    total_changes = 0

    for gt_file in gt_files:
        result = process_ground_truth_file(gt_file, apply_fixes=apply_fixes)
        results.append(result)

        if result['changes_made'] > 0:
            total_changes += result['changes_made']
            print(f"{result['data_id']}: {result['changes_made']} change(s)")
            for change in result['changes']:
                print(f"  - {change}")
            print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    files_modified = sum(1 for r in results if r['changes_made'] > 0)
    print(f"Files processed:  {len(results)}")
    print(f"Files modified:   {files_modified}")
    print(f"Total changes:    {total_changes}")

    if apply_fixes:
        print(f"\nBackups saved to: {ground_truth_dir / 'backups'}")
        print("\n[OK] Fixes applied successfully!")
    else:
        print("\n[!] DRY RUN - No files were modified")
        print("Run with --apply to save changes")

    # Save results report
    report_path = Path(__file__).parent.parent / "docs/ux-ui/outputs/GROUND_TRUTH_FIX_REPORT.json"
    with open(report_path, 'w') as f:
        json.dump({
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'mode': 'apply' if apply_fixes else 'dry-run',
            'files_processed': len(results),
            'files_modified': files_modified,
            'total_changes': total_changes,
            'results': results
        }, f, indent=2)

    print(f"\nDetailed report saved to: {report_path}")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
