#!/usr/bin/env python3
"""
CME Requirement Overlap Analysis

Analyzes CME requirements across states to show:
1. Which providers have licenses in multiple states
2. State-specific CME requirements vs general requirements
3. Overlap of CME requirements across states
4. Providers affected by multiple state-specific requirements

Author: Claude Code
Date: 2025-11-18
"""

import csv
import json
from collections import defaultdict
from datetime import datetime


def main():
    """Analyze CME overlap across states."""

    # Load data
    print("Loading data...")
    with open('provider_summary.csv', 'r', encoding='utf-8') as f:
        providers = list(csv.DictReader(f))

    with open('provider_licenses.csv', 'r', encoding='utf-8') as f:
        licenses = list(csv.DictReader(f))

    with open('provider_cme.csv', 'r', encoding='utf-8') as f:
        cme_activities = list(csv.DictReader(f))

    print(f"Loaded {len(providers)} providers, {len(licenses)} licenses, {len(cme_activities)} CME activities\n")

    # Analysis 1: Multi-state license distribution
    print("=" * 80)
    print("MULTI-STATE LICENSE DISTRIBUTION")
    print("=" * 80)

    state_counts = defaultdict(list)
    for provider in providers:
        if provider['license_states']:
            states = [s.strip() for s in provider['license_states'].split(',')]
            num_states = len(states)
            state_counts[num_states].append({
                'name': f"{provider['first_name']} {provider['last_name']}",
                'states': states
            })

    for count in sorted(state_counts.keys(), reverse=True):
        prov_list = state_counts[count]
        print(f"\nProviders with {count} state license(s): {len(prov_list)}")
        for prov in prov_list[:5]:  # Show first 5
            print(f"  - {prov['name']}: {', '.join(sorted(prov['states']))}")
        if len(prov_list) > 5:
            print(f"  ... and {len(prov_list) - 5} more")

    # Analysis 2: State coverage
    print("\n" + "=" * 80)
    print("STATE COVERAGE ANALYSIS")
    print("=" * 80)

    state_provider_count = defaultdict(set)
    for license_rec in licenses:
        if license_rec['state']:
            state_provider_count[license_rec['state']].add(license_rec['email'])

    print(f"\nTotal states with licenses: {len(state_provider_count)}")
    print(f"\nTop 20 states by number of providers:")
    for state, providers_set in sorted(state_provider_count.items(), key=lambda x: len(x[1]), reverse=True)[:20]:
        print(f"  {state}: {len(providers_set)} providers")

    # Analysis 3: CME Activity Analysis - General vs State-Specific
    print("\n" + "=" * 80)
    print("CME ACTIVITIES: GENERAL VS STATE-SPECIFIC")
    print("=" * 80)

    general_cme = []
    state_specific_cme = defaultdict(list)

    for activity in cme_activities:
        if activity['cme_state']:  # State-specific
            state = activity['cme_state'].strip()
            state_specific_cme[state].append(activity)
        else:  # General
            general_cme.append(activity)

    print(f"\nGeneral CME Activities (no state specified): {len(general_cme)}")
    print(f"State-Specific CME Activities: {len(cme_activities) - len(general_cme)}")
    print(f"States with specific CME requirements: {len(state_specific_cme)}")

    # Analysis 4: State-Specific CME Requirements Detail
    print("\n" + "=" * 80)
    print("STATE-SPECIFIC CME REQUIREMENTS BY STATE")
    print("=" * 80)

    for state in sorted(state_specific_cme.keys()):
        activities = state_specific_cme[state]
        total_credits = sum(float(a['credits'] or 0) for a in activities)

        # Get unique requirement types from activity titles
        requirement_types = defaultdict(int)
        for activity in activities:
            title = activity['title'].lower()
            if 'opioid' in title:
                requirement_types['Opioid Prescribing'] += 1
            elif 'cultural competency' in title or 'cultural' in title:
                requirement_types['Cultural Competency'] += 1
            elif 'controlled substance' in title:
                requirement_types['Controlled Substances'] += 1
            elif 'pain management' in title or 'addiction' in title:
                requirement_types['Pain Management/Addiction'] += 1
            elif 'ethics' in title:
                requirement_types['Ethics'] += 1
            elif 'human trafficking' in title:
                requirement_types['Human Trafficking'] += 1
            elif 'implicit bias' in title:
                requirement_types['Implicit Bias'] += 1
            elif 'suicide prevention' in title:
                requirement_types['Suicide Prevention'] += 1
            else:
                requirement_types['Other State-Specific'] += 1

        print(f"\n{state}:")
        print(f"  Total activities: {len(activities)}")
        print(f"  Total credits: {total_credits:.1f}")
        print(f"  Providers affected: {len(set(a['email'] for a in activities))}")
        print(f"  Requirement types:")
        for req_type, count in sorted(requirement_types.items(), key=lambda x: x[1], reverse=True):
            print(f"    - {req_type}: {count} activities")

    # Analysis 5: Providers with Multiple State-Specific Requirements
    print("\n" + "=" * 80)
    print("PROVIDERS AFFECTED BY MULTIPLE STATE-SPECIFIC REQUIREMENTS")
    print("=" * 80)

    provider_state_reqs = defaultdict(set)
    for state, activities in state_specific_cme.items():
        for activity in activities:
            provider_state_reqs[activity['email']].add(state)

    multi_state_req_providers = {email: states for email, states in provider_state_reqs.items() if len(states) >= 2}

    print(f"\nProviders with state-specific CME in 2+ states: {len(multi_state_req_providers)}")
    for email, states in sorted(multi_state_req_providers.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
        # Get provider name
        prov = next((p for p in providers if p['email'] == email), None)
        if prov:
            name = f"{prov['first_name']} {prov['last_name']}"
        else:
            name = email

        print(f"  {name}: {', '.join(sorted(states))} ({len(states)} states)")

    # Analysis 6: CME Requirement Overlap Matrix
    print("\n" + "=" * 80)
    print("CME REQUIREMENT TYPE OVERLAP ACROSS STATES")
    print("=" * 80)

    # Build requirement type by state matrix
    state_req_matrix = defaultdict(set)
    for state, activities in state_specific_cme.items():
        for activity in activities:
            title = activity['title'].lower()
            if 'opioid' in title:
                state_req_matrix['Opioid Prescribing'].add(state)
            if 'cultural' in title:
                state_req_matrix['Cultural Competency'].add(state)
            if 'controlled substance' in title:
                state_req_matrix['Controlled Substances'].add(state)
            if 'pain management' in title or 'addiction' in title:
                state_req_matrix['Pain Management'].add(state)
            if 'ethics' in title:
                state_req_matrix['Ethics'].add(state)
            if 'human trafficking' in title:
                state_req_matrix['Human Trafficking'].add(state)
            if 'implicit bias' in title:
                state_req_matrix['Implicit Bias'].add(state)
            if 'suicide' in title:
                state_req_matrix['Suicide Prevention'].add(state)

    print("\nRequirement Type Coverage:")
    for req_type in sorted(state_req_matrix.keys(), key=lambda x: len(state_req_matrix[x]), reverse=True):
        states = state_req_matrix[req_type]
        print(f"\n{req_type} ({len(states)} states):")
        print(f"  States: {', '.join(sorted(states))}")

        # Find providers affected by this requirement in multiple states
        affected_providers = defaultdict(set)
        for state in states:
            for activity in state_specific_cme[state]:
                if req_type.lower().replace(' ', '') in activity['title'].lower().replace(' ', ''):
                    affected_providers[activity['email']].add(state)

        multi_state_affected = {email: st for email, st in affected_providers.items() if len(st) >= 2}
        if multi_state_affected:
            print(f"  Providers affected in 2+ states: {len(multi_state_affected)}")
            for email, st in sorted(multi_state_affected.items(), key=lambda x: len(x[1]), reverse=True)[:3]:
                prov = next((p for p in providers if p['email'] == email), None)
                name = f"{prov['first_name']} {prov['last_name']}" if prov else email
                print(f"    - {name}: {', '.join(sorted(st))}")

    # Create CSV export of overlap analysis
    print("\n" + "=" * 80)
    print("GENERATING OVERLAP ANALYSIS CSV")
    print("=" * 80)

    overlap_rows = []
    for email in provider_state_reqs.keys():
        prov = next((p for p in providers if p['email'] == email), None)
        if not prov:
            continue

        # Get all licenses for this provider
        prov_licenses = [lic for lic in licenses if lic['email'] == email]
        all_states = [lic['state'] for lic in prov_licenses]

        # Get state-specific CME states
        cme_states = provider_state_reqs[email]

        # Get requirement types per state
        state_reqs = defaultdict(set)
        for state in cme_states:
            for activity in state_specific_cme[state]:
                if activity['email'] == email:
                    title = activity['title'].lower()
                    if 'opioid' in title:
                        state_reqs[state].add('Opioid')
                    if 'cultural' in title:
                        state_reqs[state].add('Cultural')
                    if 'controlled' in title:
                        state_reqs[state].add('Controlled Substances')
                    if 'pain' in title:
                        state_reqs[state].add('Pain Mgmt')
                    if 'ethics' in title:
                        state_reqs[state].add('Ethics')
                    if 'trafficking' in title:
                        state_reqs[state].add('Trafficking')

        overlap_rows.append({
            'provider_name': f"{prov['first_name']} {prov['last_name']}",
            'email': email,
            'total_licenses': len(all_states),
            'all_license_states': ', '.join(sorted(all_states)),
            'states_with_specific_cme': len(cme_states),
            'specific_cme_states': ', '.join(sorted(cme_states)),
            'total_cme_activities': int(prov.get('cme_count', 0)),
            'total_cme_credits': float(prov.get('total_cme_credits', 0)),
            'state_requirements': ' | '.join([f"{s}: {', '.join(sorted(state_reqs[s]))}" for s in sorted(cme_states)])
        })

    # Sort by states with specific CME
    overlap_rows.sort(key=lambda x: x['states_with_specific_cme'], reverse=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    overlap_file = f'cme_state_overlap_analysis_{timestamp}.csv'

    with open(overlap_file, 'w', newline='', encoding='utf-8') as f:
        if overlap_rows:
            writer = csv.DictWriter(f, fieldnames=overlap_rows[0].keys())
            writer.writeheader()
            writer.writerows(overlap_rows)

    print(f"\n✅ Created CME overlap analysis: {overlap_file}")
    print(f"   {len(overlap_rows)} providers with state-specific CME requirements")
    print()


if __name__ == "__main__":
    main()
