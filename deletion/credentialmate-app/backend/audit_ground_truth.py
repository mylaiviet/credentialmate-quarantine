#!/usr/bin/env python3
"""
Ground Truth Schema Audit Script

Scans all ground truth files to identify schema inconsistencies that cause
false negative test results.

Session: ui-ux-1-7
Phase: 1 (Ground Truth Audit)
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


def flatten_dict(d: Dict, prefix: str = '') -> Dict:
    """Flatten nested dictionary for field analysis"""
    items = []
    for key, value in d.items():
        new_key = f"{prefix}{key}" if prefix else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, f"{new_key}.").items())
        else:
            items.append((new_key, value))
    return dict(items)


def analyze_name_format(name: str) -> Dict[str, Any]:
    """Analyze provider name format"""
    if not name:
        return {'format': 'null', 'has_comma': False, 'all_caps': False}

    return {
        'format': 'LAST, FIRST' if ',' in name else 'First Last',
        'has_comma': ',' in name,
        'all_caps': name.isupper(),
        'has_title': name.startswith('Dr.') or name.startswith('DR.'),
        'value': name
    }


def analyze_jurisdiction_format(jurisdiction: str) -> Dict[str, Any]:
    """Analyze jurisdiction format"""
    if not jurisdiction:
        return {'format': 'null', 'length': 0}

    return {
        'format': '2-letter' if len(jurisdiction) == 2 else 'full-name',
        'length': len(jurisdiction),
        'value': jurisdiction
    }


def analyze_professional_designation(designation: str) -> Dict[str, Any]:
    """Analyze professional designation format"""
    if not designation:
        return {'format': 'null', 'length': 0}

    return {
        'format': 'abbreviated' if len(designation) <= 3 else 'full',
        'length': len(designation),
        'value': designation
    }


def find_field_value(data: Dict, field_name: str) -> Any:
    """Find field value in nested dict"""
    flat = flatten_dict(data)
    return flat.get(field_name)


def audit_ground_truth_file(file_path: Path) -> Dict[str, Any]:
    """Audit a single ground truth file"""
    with open(file_path, 'r') as f:
        data = json.load(f)

    data_id = data.get('data_id')
    doc_type = data.get('expected_classification', {}).get('document_type')
    extraction = data.get('expected_extraction', {})

    if not extraction:
        return {
            'data_id': data_id,
            'document_type': doc_type,
            'has_extraction': False,
            'issues': []
        }

    flat = flatten_dict(extraction)
    issues = []

    # Analyze provider name
    name = find_field_value(extraction, 'provider_info.name')
    name_analysis = analyze_name_format(name)

    # CME-specific check: name expected but not visible on certificate
    if doc_type == 'cme' and name and name != 'null':
        issues.append({
            'severity': 'WARNING',
            'field': 'provider_info.name',
            'issue': 'CME certificate may not show provider name',
            'expected': name,
            'recommendation': 'Verify name is actually visible on certificate, set to null if not'
        })

    # Check for "LAST, FIRST" format that should be normalized
    if name_analysis.get('has_comma'):
        issues.append({
            'severity': 'HIGH',
            'field': 'provider_info.name',
            'issue': 'Name in "LAST, FIRST" format but parser normalizes to "First Last"',
            'expected': name,
            'recommendation': f'Change to normalized format or update test to expect raw format'
        })

    # Analyze jurisdiction
    jurisdiction = find_field_value(extraction, 'credential_details.jurisdiction')
    state = find_field_value(extraction, 'credential_details.state')

    if state and not jurisdiction:
        issues.append({
            'severity': 'CRITICAL',
            'field': 'credential_details.state',
            'issue': 'Uses "state" field but parser uses "jurisdiction"',
            'expected': state,
            'recommendation': f'Rename "state" to "jurisdiction" OR add to FIELD_ALIASES'
        })

    if jurisdiction:
        jurisdiction_analysis = analyze_jurisdiction_format(jurisdiction)
        if jurisdiction_analysis['format'] == 'full-name':
            issues.append({
                'severity': 'HIGH',
                'field': 'credential_details.jurisdiction',
                'issue': 'Full state name but parser returns 2-letter code',
                'expected': jurisdiction,
                'recommendation': 'Change to 2-letter code (e.g., "Missouri" → "MO")'
            })

    # Analyze professional designation
    designation = find_field_value(extraction, 'provider_info.professional_designation')
    if designation:
        designation_analysis = analyze_professional_designation(designation)
        if designation_analysis['format'] == 'full':
            issues.append({
                'severity': 'MEDIUM',
                'field': 'provider_info.professional_designation',
                'issue': 'Full designation but parser may abbreviate',
                'expected': designation,
                'recommendation': f'Consider abbreviating (e.g., "MEDICAL DOCTOR" → "MD")'
            })

    # Check for drug_schedules location
    drug_schedules_top = find_field_value(extraction, 'credential_details.drug_schedules')
    drug_schedules_nested = find_field_value(extraction, 'credential_details.additional_info.drug_schedules')

    if drug_schedules_top and drug_schedules_nested:
        # Both locations (e.g., TD-022)
        if drug_schedules_top != drug_schedules_nested:
            issues.append({
                'severity': 'CRITICAL',
                'field': 'credential_details.drug_schedules',
                'issue': 'drug_schedules in BOTH top-level and nested with DIFFERENT values',
                'expected': f'Top: {drug_schedules_top}, Nested: {drug_schedules_nested}',
                'recommendation': 'Remove duplicate, keep only top-level'
            })

    # Check for license_number vs credential_number
    license_number = find_field_value(extraction, 'credential_details.license_number')
    credential_number = find_field_value(extraction, 'credential_details.credential_number')
    registration_number = find_field_value(extraction, 'credential_details.registration_number')

    if license_number and not credential_number:
        issues.append({
            'severity': 'CRITICAL',
            'field': 'credential_details.license_number',
            'issue': 'Uses "license_number" but parser uses "credential_number"',
            'expected': license_number,
            'recommendation': f'Rename to "credential_number" (already in FIELD_ALIASES)'
        })

    # CME-specific checks
    if doc_type == 'cme':
        title = find_field_value(extraction, 'credential_details.title')
        issuing_authority = find_field_value(extraction, 'credential_details.issuing_authority')

        # Check if title is actually issuing authority
        if title and issuing_authority:
            if title in issuing_authority or issuing_authority in title:
                issues.append({
                    'severity': 'CRITICAL',
                    'field': 'credential_details.title',
                    'issue': 'Title field contains issuing authority name, not course title',
                    'expected': title,
                    'recommendation': 'Set title to null if no course name visible, move issuer to issuing_authority'
                })

        # Check category format
        category = find_field_value(extraction, 'credential_details.category')
        if category:
            # Check if category needs normalization
            normalized_categories = ['AMA PRA Category 1', 'AMA PRA Category 2', 'Category 1', 'Category 2']
            if category not in normalized_categories:
                issues.append({
                    'severity': 'LOW',
                    'field': 'credential_details.category',
                    'issue': 'Category not in normalized format',
                    'expected': category,
                    'recommendation': f'Normalize to one of: {normalized_categories}'
                })

    return {
        'data_id': data_id,
        'document_type': doc_type,
        'has_extraction': True,
        'name_format': name_analysis,
        'jurisdiction_format': analyze_jurisdiction_format(jurisdiction or state),
        'designation_format': analyze_professional_designation(designation),
        'issues': issues,
        'field_count': len(flat),
        'uses_license_number': bool(license_number),
        'uses_credential_number': bool(credential_number),
        'uses_state': bool(state),
        'uses_jurisdiction': bool(jurisdiction),
    }


def main():
    print("Ground Truth Schema Audit")
    print("=" * 80)

    # Find all ground truth files
    ground_truth_dir = Path(__file__).parent / "tests/fixtures/ground_truth"
    gt_files = sorted(ground_truth_dir.glob("*_ground_truth.json"))

    print(f"\nFound {len(gt_files)} ground truth files")
    print()

    # Audit each file
    all_results = []
    issue_counts = defaultdict(int)
    severity_counts = defaultdict(int)

    for gt_file in gt_files:
        result = audit_ground_truth_file(gt_file)
        all_results.append(result)

        # Count issues by severity
        for issue in result.get('issues', []):
            severity_counts[issue['severity']] += 1
            issue_counts[result['data_id']] += 1

    # Print summary by document
    print("ISSUES BY DOCUMENT:")
    print("-" * 80)
    for result in all_results:
        data_id = result['data_id']
        doc_type = result['document_type']
        issue_count = len(result.get('issues', []))

        if issue_count > 0:
            print(f"\n{data_id} ({doc_type}): {issue_count} issue(s)")
            for issue in result['issues']:
                severity_icon = {
                    'CRITICAL': '[!]',
                    'HIGH': '[!]',
                    'MEDIUM': '[*]',
                    'LOW': '[-]',
                    'WARNING': '[?]'
                }.get(issue['severity'], '•')
                print(f"  {severity_icon} [{issue['severity']}] {issue['field']}")
                print(f"     Issue: {issue['issue']}")
                print(f"     Expected: {issue['expected']}")
                print(f"     Fix: {issue['recommendation']}")
        else:
            print(f"{data_id} ({doc_type}): [OK] No issues")

    # Print severity summary
    print("\n" + "=" * 80)
    print("ISSUE SUMMARY BY SEVERITY:")
    print("-" * 80)
    total_issues = sum(severity_counts.values())
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'WARNING']:
        count = severity_counts[severity]
        if count > 0:
            pct = (count / total_issues * 100) if total_issues > 0 else 0
            print(f"{severity:12} {count:3} issues ({pct:5.1f}%)")
    print(f"{'TOTAL':12} {total_issues:3} issues")

    # Print field usage patterns
    print("\n" + "=" * 80)
    print("FIELD NAMING PATTERNS:")
    print("-" * 80)

    license_count = sum(1 for r in all_results if r.get('uses_license_number'))
    credential_count = sum(1 for r in all_results if r.get('uses_credential_number'))
    state_count = sum(1 for r in all_results if r.get('uses_state'))
    jurisdiction_count = sum(1 for r in all_results if r.get('uses_jurisdiction'))

    print(f"credential_number: {credential_count} files")
    print(f"license_number:    {license_count} files  {'[X] INCONSISTENT' if license_count > 0 else '[OK]'}")
    print(f"jurisdiction:      {jurisdiction_count} files")
    print(f"state:             {state_count} files  {'[X] INCONSISTENT' if state_count > 0 else '[OK]'}")

    # Print name format patterns
    print("\n" + "=" * 80)
    print("NAME FORMAT PATTERNS:")
    print("-" * 80)

    name_formats = defaultdict(list)
    for result in all_results:
        if result.get('has_extraction') and result.get('name_format'):
            fmt = result['name_format'].get('format', 'null')
            name_formats[fmt].append(result['data_id'])

    for fmt, data_ids in sorted(name_formats.items()):
        print(f"{fmt:15} {len(data_ids)} files: {', '.join(data_ids[:5])}")
        if fmt == 'LAST, FIRST':
            print(f"                [!] Parser normalizes to 'First Last' - these will fail!")

    # Save detailed results to JSON
    output_path = Path(__file__).parent.parent / "docs/ux-ui/outputs/GROUND_TRUTH_AUDIT_RESULTS.json"
    with open(output_path, 'w') as f:
        json.dump({
            'timestamp': '2025-11-18T10:00:00Z',
            'total_files': len(gt_files),
            'total_issues': total_issues,
            'severity_counts': dict(severity_counts),
            'results': all_results
        }, f, indent=2)

    print(f"\n\nDetailed results saved to: {output_path}")

    # Generate fix recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDED FIXES (Priority Order):")
    print("=" * 80)

    # Group critical issues
    critical_issues = []
    for result in all_results:
        for issue in result.get('issues', []):
            if issue['severity'] == 'CRITICAL':
                critical_issues.append((result['data_id'], issue))

    if critical_issues:
        print(f"\n[!] CRITICAL ({len(critical_issues)} issues) - Fix FIRST:")
        for data_id, issue in critical_issues:
            print(f"   {data_id}: {issue['field']}")
            print(f"   -> {issue['recommendation']}")

    # High priority
    high_issues = []
    for result in all_results:
        for issue in result.get('issues', []):
            if issue['severity'] == 'HIGH':
                high_issues.append((result['data_id'], issue))

    if high_issues:
        print(f"\n[!] HIGH PRIORITY ({len(high_issues)} issues) - Fix SECOND:")
        for data_id, issue in high_issues[:5]:  # Show first 5
            print(f"   {data_id}: {issue['field']}")
            print(f"   -> {issue['recommendation']}")
        if len(high_issues) > 5:
            print(f"   ... and {len(high_issues) - 5} more")

    print("\n" + "=" * 80)
    print(f"Audit complete. Found {total_issues} issues across {len([r for r in all_results if r.get('issues')])}/{len(gt_files)} files.")
    print("=" * 80)

    return 0 if total_issues == 0 else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
