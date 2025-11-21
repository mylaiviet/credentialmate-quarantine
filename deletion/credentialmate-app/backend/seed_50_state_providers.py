#!/usr/bin/env python3
"""
Seed 20 Providers with Multi-State Licenses Spanning All 50 States

Creates providers with 3+ licenses each, ensuring coverage across all 50 states.
50% of providers will have state-specific CME requirements to analyze overlap.

Focus: Demonstrate CME requirement variation across states, especially:
- States with specific requirements (cultural competency, opioid training, etc.)
- States with different credit hour requirements
- States with different renewal cycles

Author: Claude Code
Date: 2025-11-18
"""

import sys
import os
from datetime import datetime, date, timedelta
from decimal import Decimal
import random
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.license import License, LicenseStatus
from app.models.cme_activity import CMEActivity


# All 50 US states
ALL_50_STATES = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
]

# States with specific CME requirements (beyond general requirements)
STATES_WITH_SPECIFIC_REQUIREMENTS = {
    'CA': ['cultural_competency', 'pain_management', 'human_trafficking'],
    'FL': ['hiv_aids', 'domestic_violence', 'medical_errors'],
    'TX': ['ethics', 'controlled_substances', 'human_trafficking'],
    'NY': ['infection_control', 'pain_management', 'cultural_competency'],
    'IL': ['sexual_harassment', 'implicit_bias', 'cultural_competency'],
    'OH': ['opioid_prescribing', 'pain_management', 'controlled_substances'],
    'PA': ['patient_safety', 'risk_management', 'opioid_prescribing'],
    'GA': ['opioid_education', 'controlled_substances', 'pain_management'],
    'NC': ['risk_management', 'professional_boundaries', 'controlled_substances'],
    'MI': ['pain_management', 'opioid_prescribing', 'ethics'],
    'NJ': ['cultural_competency', 'end_of_life_care', 'opioid_prescribing'],
    'VA': ['opioid_prescribing', 'human_trafficking', 'controlled_substances'],
    'WA': ['suicide_prevention', 'opioid_prescribing', 'pain_management'],
    'MA': ['risk_management', 'end_of_life_care', 'cultural_competency'],
    'AZ': ['opioid_prescribing', 'controlled_substances', 'pain_management'],
    'TN': ['controlled_substances', 'opioid_prescribing', 'pain_management'],
    'IN': ['opioid_prescribing', 'controlled_substances', 'pain_management'],
    'MO': ['controlled_substances', 'opioid_prescribing', 'ethics'],
    'MD': ['cultural_competency', 'implicit_bias', 'opioid_prescribing'],
    'WI': ['opioid_prescribing', 'controlled_substances', 'pain_management']
}

# Provider names for variety
PROVIDER_DATA = [
    ('Sarah', 'Mitchell', 'MD', 'Family Medicine'),
    ('David', 'Chen', 'DO', 'Internal Medicine'),
    ('Maria', 'Rodriguez', 'MD', 'Pediatrics'),
    ('James', 'Thompson', 'DO', 'Emergency Medicine'),
    ('Jennifer', 'Lee', 'MD', 'Psychiatry'),
    ('Michael', 'Williams', 'DO', 'Cardiology'),
    ('Lisa', 'Anderson', 'MD', 'Dermatology'),
    ('Robert', 'Martinez', 'DO', 'Orthopedics'),
    ('Emily', 'Taylor', 'MD', 'Obstetrics/Gynecology'),
    ('Daniel', 'Brown', 'DO', 'Neurology'),
    ('Amanda', 'Davis', 'MD', 'Anesthesiology'),
    ('Christopher', 'Garcia', 'DO', 'Radiology'),
    ('Jessica', 'Wilson', 'MD', 'Oncology'),
    ('Matthew', 'Moore', 'DO', 'Gastroenterology'),
    ('Ashley', 'Jackson', 'MD', 'Endocrinology'),
    ('Joshua', 'White', 'DO', 'Pulmonology'),
    ('Lauren', 'Harris', 'MD', 'Rheumatology'),
    ('Andrew', 'Martin', 'DO', 'Nephrology'),
    ('Rachel', 'Thompson', 'MD', 'Infectious Disease'),
    ('Brandon', 'Clark', 'DO', 'Physical Medicine')
]


def create_multi_state_provider(
    db: Session,
    first_name: str,
    last_name: str,
    suffix: str,
    specialty: str,
    states: list,
    has_specific_requirements: bool,
    provider_index: int
):
    """Create a provider with licenses in multiple states."""

    email = f"provider.multistate{provider_index}@example.com"

    # Create user
    user = User(
        email=email,
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU0Nlk6u8rQC",  # "password"
        first_name=first_name,
        last_name=last_name,
        role="provider",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow() - timedelta(days=random.randint(180, 1095)),
        last_login=datetime.utcnow() - timedelta(days=random.randint(1, 30))
    )
    db.add(user)
    db.flush()

    print(f"  Created user: {first_name} {last_name} ({email})")

    # Create licenses for each state
    licenses_created = []
    for state in states:
        license_number = f"{state}{random.randint(100000, 999999)}"
        issue_date = date.today() - timedelta(days=random.randint(365, 3650))

        # Vary renewal cycles: 1, 2, or 3 years
        renewal_months = random.choice([12, 24, 36])
        expiration_date = issue_date + timedelta(days=renewal_months * 30)

        # Make some licenses expiring soon for variety
        if random.random() < 0.15:  # 15% expiring soon
            expiration_date = date.today() + timedelta(days=random.randint(30, 89))

        license_obj = License(
            user_id=user.id,
            state=state,
            license_number=license_number,
            license_type=suffix,
            issue_date=issue_date,
            expiration_date=expiration_date,
            status=LicenseStatus.ACTIVE,
            renewal_cycle_months=renewal_months,
            created_at=datetime.utcnow() - timedelta(days=random.randint(60, 365)),
            updated_at=datetime.utcnow()
        )
        db.add(license_obj)
        licenses_created.append((state, license_number))

    db.flush()
    print(f"    Added {len(licenses_created)} licenses: {', '.join([s for s, _ in licenses_created])}")

    # Create CME activities - both general and state-specific
    total_cme_credits = 0
    cme_count = 0

    # General CME (Category 1 - AMA PRA)
    general_topics = [
        'Advanced Cardiac Life Support',
        'Clinical Practice Guidelines Update',
        'Evidence-Based Medicine',
        'Medical Ethics and Professionalism',
        'Quality Improvement in Healthcare',
        'Electronic Health Records Best Practices',
        'Patient Safety and Risk Management',
        'Diagnostic Imaging Updates',
        'Pharmacology Updates',
        'Clinical Research Methods'
    ]

    # Add 10-15 general CME activities
    for i in range(random.randint(10, 15)):
        credits = round(random.uniform(0.5, 4.0), 1)
        completion_date = date.today() - timedelta(days=random.randint(30, 730))

        activity = CMEActivity(
            user_id=user.id,
            title=random.choice(general_topics),
            credits=Decimal(str(credits)),
            completion_date=completion_date,
            activity_type=random.choice(['Course', 'Conference', 'Webinar', 'Workshop', 'Self-Study']),
            category='category_1',
            provider='AMA PRA Category 1',
            state=None,  # General, not state-specific
            compliance_status='compliant',
            created_at=datetime.utcnow()
        )
        db.add(activity)
        total_cme_credits += credits
        cme_count += 1

    # If provider has specific requirements, add state-specific CME
    if has_specific_requirements:
        # Pick states with specific requirements from their license states
        specific_states = [s for s in states if s in STATES_WITH_SPECIFIC_REQUIREMENTS]

        if specific_states:
            for state in specific_states[:3]:  # Add specific CME for up to 3 states
                requirements = STATES_WITH_SPECIFIC_REQUIREMENTS[state]

                # Add 2-4 activities per specific requirement
                for req_type in requirements:
                    num_activities = random.randint(1, 2)
                    for _ in range(num_activities):
                        credits = round(random.uniform(1.0, 3.0), 1)
                        completion_date = date.today() - timedelta(days=random.randint(30, 730))

                        # Format requirement type as title
                        title = req_type.replace('_', ' ').title()
                        if req_type == 'opioid_prescribing':
                            title = f"{state} Opioid Prescribing Education"
                        elif req_type == 'cultural_competency':
                            title = f"{state} Cultural Competency Training"
                        elif req_type == 'controlled_substances':
                            title = f"{state} Controlled Substances Education"
                        elif req_type == 'pain_management':
                            title = f"{state} Pain Management and Addiction"
                        else:
                            title = f"{state} {title}"

                        activity = CMEActivity(
                            user_id=user.id,
                            title=title,
                            credits=Decimal(str(credits)),
                            completion_date=completion_date,
                            activity_type=random.choice(['Course', 'Webinar', 'Workshop']),
                            category='category_1',
                            provider=f'{state} State Medical Board',
                            state=state,  # State-specific
                            compliance_status='compliant',
                            created_at=datetime.utcnow()
                        )
                        db.add(activity)
                        total_cme_credits += credits
                        cme_count += 1

    print(f"    Added {cme_count} CME activities ({total_cme_credits:.1f} total credits)")
    if has_specific_requirements:
        print(f"    ✓ Includes state-specific requirements")

    return user


def distribute_states_across_providers(num_providers: int, min_licenses: int = 3, max_licenses: int = 7):
    """
    Distribute all 50 states across providers, ensuring good coverage.

    Returns a list of state lists, one per provider.
    """
    states_pool = ALL_50_STATES.copy()
    random.shuffle(states_pool)

    provider_states = []

    # First pass: give each provider their minimum licenses
    for i in range(num_providers):
        num_licenses = random.randint(min_licenses, max_licenses)
        selected_states = []

        # Take from pool first
        while len(selected_states) < num_licenses and states_pool:
            selected_states.append(states_pool.pop(0))

        # If pool is empty but we need more, pick from states with specific requirements
        while len(selected_states) < num_licenses:
            selected_states.append(random.choice(list(STATES_WITH_SPECIFIC_REQUIREMENTS.keys())))

        provider_states.append(selected_states)

    # Second pass: ensure all 50 states are covered
    # Add any remaining states to random providers
    if states_pool:
        for state in states_pool:
            random_provider = random.randint(0, num_providers - 1)
            if state not in provider_states[random_provider]:
                provider_states[random_provider].append(state)

    # Third pass: ensure states with specific requirements have good coverage
    # Make sure at least 50% of providers with those states have specific requirements
    specific_req_states = set(STATES_WITH_SPECIFIC_REQUIREMENTS.keys())
    for state in specific_req_states:
        # Find providers with this state
        providers_with_state = [i for i, states in enumerate(provider_states) if state in states]
        if len(providers_with_state) < 2:
            # Add to random providers
            for _ in range(2 - len(providers_with_state)):
                random_provider = random.randint(0, num_providers - 1)
                if state not in provider_states[random_provider]:
                    provider_states[random_provider].append(state)

    # Fourth pass: remove duplicates from each provider's state list
    for i in range(len(provider_states)):
        provider_states[i] = list(set(provider_states[i]))

    return provider_states


def main():
    """Seed 20 providers with multi-state licenses."""
    db = SessionLocal()

    try:
        print("="*70)
        print("SEEDING 20 MULTI-STATE PROVIDERS")
        print("="*70)
        print()

        # Distribute states across 20 providers
        num_providers = 20
        provider_states_list = distribute_states_across_providers(num_providers, min_licenses=3, max_licenses=7)

        # 50% will have specific requirements
        providers_with_specific_req = random.sample(range(num_providers), num_providers // 2)

        # Create providers
        created_count = 0
        for i, provider_data in enumerate(PROVIDER_DATA[:num_providers]):
            first_name, last_name, suffix, specialty = provider_data
            states = provider_states_list[i]
            has_specific_req = i in providers_with_specific_req

            print(f"\n{i+1}. Creating provider: {first_name} {last_name}, {suffix}")
            print(f"   Specialty: {specialty}")
            print(f"   States ({len(states)}): {', '.join(sorted(states))}")

            user = create_multi_state_provider(
                db,
                first_name,
                last_name,
                suffix,
                specialty,
                states,
                has_specific_req,
                i + 1
            )

            created_count += 1

        # Commit all changes
        db.commit()

        print()
        print("="*70)
        print("SEEDING COMPLETE")
        print("="*70)
        print(f"✅ Created {created_count} multi-state providers")
        print(f"✅ Total licenses created: {sum(len(s) for s in provider_states_list)}")
        print(f"✅ States covered: {len(set([s for states in provider_states_list for s in states]))}/50")
        print(f"✅ Providers with state-specific CME: {len(providers_with_specific_req)} (50%)")
        print()
        print("State-specific CME requirement states covered:")
        specific_covered = set()
        for i in providers_with_specific_req:
            specific_covered.update([s for s in provider_states_list[i] if s in STATES_WITH_SPECIFIC_REQUIREMENTS])
        print(f"  {', '.join(sorted(specific_covered))}")
        print()

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
