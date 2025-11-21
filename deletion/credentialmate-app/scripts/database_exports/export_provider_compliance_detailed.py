#!/usr/bin/env python3
"""
Export Detailed Provider Compliance Report

Creates a comprehensive CSV report with:
- All provider attributes
- All licenses by state (Medical, DEA, Controlled Substance)
- CME compliance by state-specific requirements
- Granular compliance status for each requirement type
- State-by-state breakdown

Output: One row per provider with all compliance details

Location: scripts/database_exports/export_provider_compliance_detailed.py
"""

import requests
import csv
import os
from datetime import datetime
from collections import defaultdict

# Configuration
API_BASE = "http://localhost:8000/api"
EMAIL = "admin@blueshift.com"
PASSWORD = "BlueShift2024!"
EXPORT_DIR = "database_export/provider_compliance_reports"

def login():
    """Login and return auth headers"""
    print("🔐 Logging in...")
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    token = response.json()["access_token"]
    print("✅ Logged in")
    return {"Authorization": f"Bearer {token}"}

def fetch_table_data(headers, table_name):
    """Fetch all data from a table"""
    print(f"📥 Fetching {table_name}...", end=" ")
    response = requests.get(
        f"{API_BASE}/admin/database/tables/{table_name}/data?limit=10000",
        headers=headers
    )
    data = response.json()['data']
    print(f"✅ ({len(data)} rows)")
    return data

def generate_compliance_report(headers):
    """Generate comprehensive provider compliance report"""

    print()
    print("=" * 80)
    print("Fetching Data")
    print("=" * 80)
    print()

    # Fetch all required data
    users = fetch_table_data(headers, "users")
    licenses = fetch_table_data(headers, "licenses")
    cme_activities = fetch_table_data(headers, "cme_activities")

    # Try to fetch additional tables (may not all exist)
    try:
        providers = fetch_table_data(headers, "providers")
    except:
        providers = []
        print("ℹ️  No providers table found, using users table")

    try:
        cme_requirements = fetch_table_data(headers, "state_cme_base_requirements")
    except:
        cme_requirements = []
        print("ℹ️  No CME requirements table found")

    try:
        dea_registrations = fetch_table_data(headers, "dea_registrations")
    except:
        dea_registrations = []
        print("ℹ️  No DEA registrations table found")

    try:
        board_certifications = fetch_table_data(headers, "board_certifications")
    except:
        board_certifications = []
        print("ℹ️  No board certifications table found")

    print()
    print("=" * 80)
    print("Processing Provider Compliance")
    print("=" * 80)
    print()

    # Filter to providers only
    providers_users = [u for u in users if u.get('role') == 'provider']
    print(f"📊 Found {len(providers_users)} providers to analyze")
    print()

    # Organize data by provider
    licenses_by_user = defaultdict(list)
    for lic in licenses:
        if lic.get('user_id'):
            licenses_by_user[lic['user_id']].append(lic)

    cme_by_user = defaultdict(list)
    for cme in cme_activities:
        if cme.get('user_id'):
            cme_by_user[cme['user_id']].append(cme)

    dea_by_user = defaultdict(list)
    for dea in dea_registrations:
        if dea.get('user_id'):
            dea_by_user[dea['user_id']].append(dea)

    certs_by_user = defaultdict(list)
    for cert in board_certifications:
        if cert.get('user_id'):
            certs_by_user[cert['user_id']].append(cert)

    # Build requirements lookup by state
    cme_requirements_by_state = {}
    for req in cme_requirements:
        if req.get('state'):
            cme_requirements_by_state[req['state']] = req

    # Generate compliance report
    report_data = []

    for i, provider in enumerate(providers_users, 1):
        user_id = provider['id']

        print(f"[{i}/{len(providers_users)}] Processing {provider.get('first_name')} {provider.get('last_name')}...")

        # Get user metadata
        metadata = provider.get('user_metadata', {}) or {}

        # Get all licenses for this provider
        user_licenses = licenses_by_user.get(user_id, [])
        user_cmes = cme_by_user.get(user_id, [])
        user_deas = dea_by_user.get(user_id, [])
        user_certs = certs_by_user.get(user_id, [])

        # Get unique states where provider is licensed
        licensed_states = set()
        for lic in user_licenses:
            if lic.get('state'):
                licensed_states.add(lic['state'])

        # Calculate state-by-state compliance
        state_compliance = {}
        for state in licensed_states:
            # Medical License Status
            state_licenses = [l for l in user_licenses if l.get('state') == state]
            active_licenses = [l for l in state_licenses if l.get('status') == 'active']
            expired_licenses = [l for l in state_licenses if l.get('status') == 'expired']

            # CME Compliance
            state_cmes = [c for c in user_cmes if c.get('state') == state]
            total_cme_credits = sum(c.get('credits', 0) for c in state_cmes)

            state_req = cme_requirements_by_state.get(state, {})
            required_cme = state_req.get('required_hours', 0) or 0

            cme_compliant = total_cme_credits >= required_cme if required_cme > 0 else None

            # DEA Status for this state
            state_deas = [d for d in user_deas if d.get('state') == state]
            has_active_dea = any(d.get('status') == 'active' for d in state_deas)

            state_compliance[state] = {
                'medical_license_count': len(state_licenses),
                'active_medical_licenses': len(active_licenses),
                'expired_medical_licenses': len(expired_licenses),
                'medical_license_compliant': len(active_licenses) > 0,
                'total_cme_credits': total_cme_credits,
                'required_cme_credits': required_cme,
                'cme_compliant': cme_compliant,
                'has_dea': len(state_deas) > 0,
                'dea_active': has_active_dea,
                'dea_count': len(state_deas),
            }

        # Overall compliance summary
        total_licenses = len(user_licenses)
        active_license_count = len([l for l in user_licenses if l.get('status') == 'active'])
        expired_license_count = len([l for l in user_licenses if l.get('status') == 'expired'])

        total_cme_all_states = sum(c.get('credits', 0) for c in user_cmes)

        # Determine overall compliance status
        if total_licenses == 0:
            overall_status = "NON_COMPLIANT"
        elif expired_license_count > 0:
            overall_status = "NON_COMPLIANT"
        elif active_license_count == total_licenses:
            overall_status = "COMPLIANT"
        else:
            overall_status = "AT_RISK"

        # Build base provider row
        row = {
            # Provider Identity
            'provider_id': user_id,
            'email': provider.get('email'),
            'first_name': provider.get('first_name'),
            'last_name': provider.get('last_name'),
            'license_type': metadata.get('license_type', ''),
            'specialty': metadata.get('specialty', ''),
            'organization': metadata.get('organization', ''),
            'phone': metadata.get('phone', ''),

            # Account Status
            'is_active': provider.get('is_active'),
            'is_verified': provider.get('is_verified'),
            'created_at': provider.get('created_at'),
            'last_login': provider.get('last_login'),

            # Overall Compliance Summary
            'overall_compliance_status': overall_status,
            'total_states_licensed': len(licensed_states),
            'licensed_states': ', '.join(sorted(licensed_states)),
            'total_licenses': total_licenses,
            'active_licenses': active_license_count,
            'expired_licenses': expired_license_count,
            'total_cme_credits_all_states': total_cme_all_states,
            'total_cme_activities': len(user_cmes),
            'total_dea_registrations': len(user_deas),
            'total_board_certifications': len(user_certs),
        }

        # Add state-by-state compliance columns
        for state in sorted(licensed_states):
            comp = state_compliance.get(state, {})
            prefix = f"{state}_"

            row[f"{prefix}medical_license_count"] = comp.get('medical_license_count', 0)
            row[f"{prefix}active_medical_licenses"] = comp.get('active_medical_licenses', 0)
            row[f"{prefix}expired_medical_licenses"] = comp.get('expired_medical_licenses', 0)
            row[f"{prefix}medical_license_compliant"] = comp.get('medical_license_compliant', False)

            row[f"{prefix}total_cme_credits"] = comp.get('total_cme_credits', 0)
            row[f"{prefix}required_cme_credits"] = comp.get('required_cme_credits', 0)

            cme_comp = comp.get('cme_compliant')
            if cme_comp is None:
                row[f"{prefix}cme_compliant"] = 'UNKNOWN'
            elif cme_comp:
                row[f"{prefix}cme_compliant"] = 'COMPLIANT'
            else:
                row[f"{prefix}cme_compliant"] = 'NON_COMPLIANT'

            row[f"{prefix}cme_deficit"] = max(0, comp.get('required_cme_credits', 0) - comp.get('total_cme_credits', 0))

            row[f"{prefix}has_dea"] = comp.get('has_dea', False)
            row[f"{prefix}dea_active"] = comp.get('dea_active', False)
            row[f"{prefix}dea_count"] = comp.get('dea_count', 0)

            # Determine state-level overall compliance
            if comp.get('medical_license_compliant'):
                if cme_comp is False:
                    row[f"{prefix}overall_compliance"] = 'NON_COMPLIANT_CME'
                elif cme_comp is True:
                    row[f"{prefix}overall_compliance"] = 'COMPLIANT'
                else:
                    row[f"{prefix}overall_compliance"] = 'COMPLIANT_UNKNOWN_CME'
            else:
                row[f"{prefix}overall_compliance"] = 'NON_COMPLIANT_LICENSE'

        report_data.append(row)

    return report_data

def export_to_csv(report_data, export_path):
    """Export report data to CSV"""

    if not report_data:
        print("❌ No data to export")
        return

    # Get all unique column names (since state columns vary)
    all_columns = set()
    for row in report_data:
        all_columns.update(row.keys())

    # Order columns: provider info first, then overall metrics, then state-specific
    base_columns = [
        'provider_id', 'email', 'first_name', 'last_name', 'license_type',
        'specialty', 'organization', 'phone', 'is_active', 'is_verified',
        'created_at', 'last_login', 'overall_compliance_status',
        'total_states_licensed', 'licensed_states', 'total_licenses',
        'active_licenses', 'expired_licenses', 'total_cme_credits_all_states',
        'total_cme_activities', 'total_dea_registrations', 'total_board_certifications'
    ]

    # Get state-specific columns
    state_columns = sorted([col for col in all_columns if col not in base_columns])

    # Final column order
    columns = base_columns + state_columns

    # Write CSV
    filename = os.path.join(export_path, "provider_compliance_detailed.csv")

    print()
    print("=" * 80)
    print("Writing CSV Report")
    print("=" * 80)
    print()

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(report_data)

    print(f"✅ Report exported: {filename}")
    print(f"   • Providers: {len(report_data)}")
    print(f"   • Columns: {len(columns)}")
    print(f"   • File size: {os.path.getsize(filename):,} bytes")

    # Create summary report
    summary_file = os.path.join(export_path, "compliance_summary.txt")
    with open(summary_file, 'w') as f:
        f.write("Provider Compliance Report Summary\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Providers: {len(report_data)}\n\n")

        # Count by status
        status_counts = {}
        for row in report_data:
            status = row.get('overall_compliance_status', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1

        f.write("Compliance Status Breakdown:\n")
        for status, count in sorted(status_counts.items()):
            pct = (count / len(report_data) * 100) if report_data else 0
            f.write(f"  {status}: {count} ({pct:.1f}%)\n")

        f.write("\n")

        # State coverage
        all_states = set()
        for row in report_data:
            states = row.get('licensed_states', '')
            if states:
                all_states.update(s.strip() for s in states.split(','))

        f.write(f"Total States Covered: {len(all_states)}\n")
        f.write(f"States: {', '.join(sorted(all_states))}\n")

    print(f"📄 Summary saved: {summary_file}")

def main():
    print()
    print("=" * 80)
    print("Provider Compliance Detailed Report")
    print("=" * 80)
    print()

    # Create export directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = os.path.join(EXPORT_DIR, timestamp)
    os.makedirs(export_path, exist_ok=True)

    print(f"📁 Export directory: {export_path}")
    print()

    # Login
    headers = login()

    # Generate report
    report_data = generate_compliance_report(headers)

    # Export to CSV
    export_to_csv(report_data, export_path)

    print()
    print("=" * 80)
    print("🎉 Complete!")
    print("=" * 80)
    print()
    print(f"📂 Open: {os.path.abspath(export_path)}")
    print()

if __name__ == "__main__":
    main()
