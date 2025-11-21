"""seed_reference_data

Revision ID: 20251111_200070
Revises: 20251111_200060
Create Date: 2025-11-11 20:00:70

Session ID: 20251111-185816
Agent: Agent 2 (Data - Migration Generator)

Seeds production reference data for:
- specialties: 10 common medical specialties
- license_types: 8 license types (MD, DO, NP, PA, RN, DDS, PharmD, Psychologist)
- cme_credit_types: 5 CME credit categories
- state_license_requirements: All 50 US states with CME requirements

This data is required for the application to function correctly.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Boolean, Interval


# revision identifiers, used by Alembic.
revision = "20251111_200070"
down_revision = "20251111_200060"
branch_labels = None
depends_on = None


def upgrade():
    # Define table references for bulk insert
    specialties = table(
        "specialties",
        column("name", String),
        column("description", String),
        column("cme_modifier", Integer),
    )

    license_types = table(
        "license_types",
        column("code", String),
        column("description", String),
        column("requires_cme", Boolean),
        column("renewal_period", Interval),
    )

    cme_credit_types = table(
        "cme_credit_types",
        column("credit_type", String),
        column("description", String),
        column("accrediting_body", String),
        column("is_mandatory", Boolean),
    )

    state_license_requirements = table(
        "state_license_requirements",
        column("state_code", String),
        column("renewal_period", Interval),
        column("required_cme_hours", Integer),
        column("controlled_substance_hours", Integer),
    )

    # Seed specialties
    op.bulk_insert(
        specialties,
        [
            {
                "name": "Family Medicine",
                "description": "Primary care for all ages",
                "cme_modifier": 0,
            },
            {
                "name": "Internal Medicine",
                "description": "Adult primary and specialty care",
                "cme_modifier": 0,
            },
            {
                "name": "Pediatrics",
                "description": "Child and adolescent care",
                "cme_modifier": 0,
            },
            {
                "name": "Emergency Medicine",
                "description": "Acute care and emergency services",
                "cme_modifier": 5,
            },
            {
                "name": "Surgery",
                "description": "Surgical specialties",
                "cme_modifier": 10,
            },
            {
                "name": "Psychiatry",
                "description": "Mental health care",
                "cme_modifier": 0,
            },
            {
                "name": "Obstetrics & Gynecology",
                "description": "Women's health",
                "cme_modifier": 5,
            },
            {
                "name": "Anesthesiology",
                "description": "Anesthesia and pain management",
                "cme_modifier": 5,
            },
            {"name": "Radiology", "description": "Medical imaging", "cme_modifier": 0},
            {
                "name": "Pathology",
                "description": "Laboratory medicine",
                "cme_modifier": 0,
            },
        ],
    )

    # Seed license types (renewal_period set to NULL, typically varies by state)
    op.bulk_insert(
        license_types,
        [
            {
                "code": "MD",
                "description": "Doctor of Medicine",
                "requires_cme": True,
                "renewal_period": None,
            },
            {
                "code": "DO",
                "description": "Doctor of Osteopathic Medicine",
                "requires_cme": True,
                "renewal_period": None,
            },
            {
                "code": "NP",
                "description": "Nurse Practitioner",
                "requires_cme": True,
                "renewal_period": None,
            },
            {
                "code": "PA",
                "description": "Physician Assistant",
                "requires_cme": True,
                "renewal_period": None,
            },
            {
                "code": "RN",
                "description": "Registered Nurse",
                "requires_cme": True,
                "renewal_period": None,
            },
            {
                "code": "DDS",
                "description": "Doctor of Dental Surgery",
                "requires_cme": True,
                "renewal_period": None,
            },
            {
                "code": "PharmD",
                "description": "Doctor of Pharmacy",
                "requires_cme": True,
                "renewal_period": None,
            },
            {
                "code": "PsyD",
                "description": "Doctor of Psychology",
                "requires_cme": True,
                "renewal_period": None,
            },
        ],
    )

    # Seed CME credit types
    op.bulk_insert(
        cme_credit_types,
        [
            {
                "credit_type": "AMA PRA Category 1",
                "description": "American Medical Association Category 1 Credits",
                "accrediting_body": "AMA",
                "is_mandatory": True,
            },
            {
                "credit_type": "AMA PRA Category 2",
                "description": "AMA Category 2 Self-Directed CME",
                "accrediting_body": "AMA",
                "is_mandatory": False,
            },
            {
                "credit_type": "AOA Category 1-A",
                "description": "American Osteopathic Association Category 1-A",
                "accrediting_body": "AOA",
                "is_mandatory": True,
            },
            {
                "credit_type": "ANCC Contact Hours",
                "description": "American Nurses Credentialing Center Contact Hours",
                "accrediting_body": "ANCC",
                "is_mandatory": True,
            },
            {
                "credit_type": "AAPA Category 1",
                "description": "American Academy of Physician Assistants Category 1",
                "accrediting_body": "AAPA",
                "is_mandatory": True,
            },
        ],
    )

    # Seed state license requirements (all 50 states)
    # Format: {state, renewal_period, required_cme_hours, controlled_substance_hours}
    state_data = [
        # Format: (state_code, years, cme_hours, cs_hours)
        ("AL", 2, 25, 2),
        ("AK", 2, 50, 0),
        ("AZ", 2, 40, 0),
        ("AR", 2, 20, 0),
        ("CA", 2, 50, 0),
        ("CO", 2, 0, 0),
        ("CT", 2, 50, 0),
        ("DE", 2, 40, 0),
        ("FL", 2, 40, 2),
        ("GA", 2, 40, 0),
        ("HI", 2, 40, 0),
        ("ID", 2, 40, 0),
        ("IL", 3, 150, 0),
        ("IN", 2, 0, 0),
        ("IA", 3, 60, 0),
        ("KS", 2, 50, 0),
        ("KY", 3, 60, 0),
        ("LA", 2, 20, 0),
        ("ME", 2, 100, 0),
        ("MD", 2, 50, 0),
        ("MA", 2, 0, 0),
        ("MI", 3, 150, 0),
        ("MN", 1, 75, 0),
        ("MS", 2, 40, 0),
        ("MO", 2, 50, 0),
        ("MT", 2, 0, 0),
        ("NE", 2, 50, 0),
        ("NV", 2, 40, 0),
        ("NH", 2, 50, 0),
        ("NJ", 2, 100, 0),
        ("NM", 3, 75, 0),
        ("NY", 3, 0, 0),
        ("NC", 1, 60, 0),
        ("ND", 1, 60, 0),
        ("OH", 2, 100, 0),
        ("OK", 2, 60, 0),
        ("OR", 2, 60, 0),
        ("PA", 2, 100, 0),
        ("RI", 2, 40, 0),
        ("SC", 2, 40, 0),
        ("SD", 2, 0, 0),
        ("TN", 2, 40, 0),
        ("TX", 2, 48, 0),
        ("UT", 2, 40, 0),
        ("VT", 2, 30, 0),
        ("VA", 2, 60, 0),
        ("WA", 1, 200, 0),
        ("WV", 2, 50, 0),
        ("WI", 2, 30, 0),
        ("WY", 3, 60, 0),
    ]

    # Build state records (renewal_period set to NULL - varies by license type)
    state_records = []
    for state_code, years, cme_hours, cs_hours in state_data:
        state_records.append(
            {
                "state_code": state_code,
                "renewal_period": None,  # Varies by license type
                "required_cme_hours": cme_hours,
                "controlled_substance_hours": cs_hours,
            }
        )

    op.bulk_insert(state_license_requirements, state_records)


def downgrade():
    # Clear seeded data in reverse order (respecting FK constraints)
    op.execute("DELETE FROM state_license_requirements")
    op.execute("DELETE FROM cme_credit_types")
    op.execute("DELETE FROM license_types")
    op.execute("DELETE FROM specialties")
