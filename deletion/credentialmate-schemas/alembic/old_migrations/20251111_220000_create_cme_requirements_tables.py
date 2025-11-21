"""create_cme_requirements_tables

Revision ID: 20251111_220000
Revises: f855a1bf370b
Create Date: 2025-11-11 22:00:00.000000

Session ID: 20251111-220000
Agent: Claude Code
Task: Create CME requirements tracking system

This migration creates 5 tables to track state-specific CME requirements:

1. state_cme_base_requirements - Core hour requirements by state
2. content_specific_cme - Topic-specific requirements (opioid, ethics, etc.)
3. exemptions_equivalents - Board certification and other exemptions
4. special_population_requirements - Conditional requirements (specialty, patient demographics)
5. state_board_contacts - Reference data for state medical boards

Data Source: Federation of State Medical Boards (FSMB) CME requirements document
Coverage: All 50 states + DC + territories (67 medical boards total)

Purpose: Enable tracking of provider compliance with state-specific CME requirements
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20251111_220000"
down_revision: Union[str, None] = "f855a1bf370b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create CME requirements tables.
    """

    # Table 1: State CME Base Requirements
    op.create_table(
        "state_cme_base_requirements",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column(
            "state_code",
            sa.String(10),
            nullable=False,
            unique=True,
            index=True,
            comment="State/territory code with board designation (e.g., CA-M, CA-O, TX)",
        ),
        sa.Column(
            "state_name", sa.String(50), nullable=False, comment="Full state name"
        ),
        sa.Column(
            "board_type",
            sa.String(20),
            nullable=False,
            comment="MEDICAL, OSTEOPATHIC, or COMBINED",
        ),
        sa.Column(
            "provider_type", sa.String(10), nullable=False, comment="MD, DO, or BOTH"
        ),
        sa.Column(
            "substantial_cme_required",
            sa.Boolean,
            nullable=False,
            default=True,
            comment="Whether state requires substantial CME (>=15 hrs/year)",
        ),
        sa.Column(
            "cme_equivalent_accepted",
            sa.Boolean,
            nullable=False,
            default=False,
            comment="Whether board certification/equivalents accepted",
        ),
        sa.Column(
            "total_hours_required",
            sa.Integer,
            nullable=True,
            comment="Total CME hours required per cycle",
        ),
        sa.Column(
            "renewal_period_months",
            sa.Integer,
            nullable=True,
            comment="License renewal period in months (12, 24, 36, 48)",
        ),
        sa.Column(
            "hours_per_year_equivalent",
            sa.Numeric(5, 2),
            nullable=True,
            comment="Calculated: total_hours / (renewal_period_months / 12)",
        ),
        sa.Column(
            "min_category1_hours",
            sa.Integer,
            nullable=True,
            comment="Minimum Category 1 hours required",
        ),
        sa.Column(
            "category1_percentage",
            sa.Numeric(5, 2),
            nullable=True,
            comment="Percentage of total that must be Category 1",
        ),
        sa.Column(
            "max_category2_hours",
            sa.Integer,
            nullable=True,
            comment="Maximum Category 2 hours allowed",
        ),
        sa.Column(
            "rollover_allowed",
            sa.Boolean,
            nullable=False,
            default=False,
            comment="Whether excess credits can roll over to next cycle",
        ),
        sa.Column(
            "max_rollover_hours",
            sa.Integer,
            nullable=True,
            comment="Maximum hours that can roll over",
        ),
        sa.Column(
            "accreditation_required",
            sa.String(200),
            nullable=True,
            comment="Required accrediting bodies (e.g., 'AMA, AOA, ACCME')",
        ),
        sa.Column(
            "effective_date",
            sa.Date,
            nullable=True,
            comment="When requirement became effective",
        ),
        sa.Column(
            "last_updated",
            sa.Date,
            nullable=False,
            server_default=sa.func.current_date(),
            comment="When this record was last updated",
        ),
        sa.Column(
            "statute_citation",
            sa.Text,
            nullable=True,
            comment="Legal reference (statute, regulation, admin code)",
        ),
        sa.Column(
            "board_guidance_url",
            sa.String(500),
            nullable=True,
            comment="Link to official board guidance",
        ),
        sa.Column(
            "notes",
            sa.Text,
            nullable=True,
            comment="Additional context, exemptions, and edge cases",
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB,
            nullable=True,
            comment="Extensible metadata for future requirements",
        ),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        # Constraints
        sa.CheckConstraint(
            "board_type IN ('MEDICAL', 'OSTEOPATHIC', 'COMBINED')", name="ck_board_type"
        ),
        sa.CheckConstraint(
            "provider_type IN ('MD', 'DO', 'BOTH')", name="ck_provider_type"
        ),
        sa.CheckConstraint(
            "total_hours_required IS NULL OR total_hours_required >= 0",
            name="ck_total_hours_non_negative",
        ),
        sa.CheckConstraint(
            "renewal_period_months IS NULL OR renewal_period_months IN (12, 24, 36, 48)",
            name="ck_valid_renewal_period",
        ),
    )

    # Indexes for state_cme_base_requirements
    op.create_index(
        "idx_state_base_state_code", "state_cme_base_requirements", ["state_code"]
    )
    op.create_index(
        "idx_state_base_board_type", "state_cme_base_requirements", ["board_type"]
    )
    op.create_index(
        "idx_state_base_provider_type", "state_cme_base_requirements", ["provider_type"]
    )

    # Table 2: Content-Specific CME Requirements
    op.create_table(
        "content_specific_cme",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column(
            "requirement_id",
            sa.String(50),
            nullable=False,
            unique=True,
            index=True,
            comment="Unique identifier (e.g., AL-MD-OPIOID-001)",
        ),
        sa.Column(
            "state_code",
            sa.String(10),
            sa.ForeignKey("state_cme_base_requirements.state_code", ondelete="CASCADE"),
            nullable=False,
            index=True,
            comment="Links to state base requirements",
        ),
        sa.Column(
            "board_type",
            sa.String(20),
            nullable=False,
            comment="MEDICAL, OSTEOPATHIC, or COMBINED",
        ),
        sa.Column(
            "provider_type", sa.String(10), nullable=False, comment="MD, DO, or BOTH"
        ),
        sa.Column(
            "topic_category",
            sa.String(50),
            nullable=False,
            index=True,
            comment="Standardized topic (OPIOID_PRESCRIBING, MEDICAL_ETHICS, etc.)",
        ),
        sa.Column(
            "topic_subcategory",
            sa.String(100),
            nullable=True,
            comment="Specific focus within category",
        ),
        sa.Column(
            "hours_required",
            sa.Numeric(4, 2),
            nullable=False,
            comment="Hours required for this topic",
        ),
        sa.Column(
            "requirement_type",
            sa.String(20),
            nullable=False,
            comment="ONE_TIME, PER_RENEWAL, PER_YEAR, EVERY_N_YEARS",
        ),
        sa.Column(
            "frequency_months",
            sa.Integer,
            nullable=True,
            comment="How often required in months (for recurring requirements)",
        ),
        sa.Column(
            "frequency_description",
            sa.String(100),
            nullable=True,
            comment="Human-readable frequency (e.g., 'Every 2 years')",
        ),
        sa.Column(
            "conditional",
            sa.Boolean,
            nullable=False,
            default=False,
            comment="Whether this requirement has conditions",
        ),
        sa.Column(
            "condition_type",
            sa.String(50),
            nullable=True,
            comment="Type of condition (DEA_REGISTRATION, SPECIALTY, PATIENT_AGE, etc.)",
        ),
        sa.Column(
            "condition_description",
            sa.Text,
            nullable=True,
            comment="Full description of conditions that trigger this requirement",
        ),
        sa.Column(
            "applies_to_new_licensees",
            sa.Boolean,
            nullable=False,
            default=False,
            comment="Whether this is a new licensee requirement",
        ),
        sa.Column(
            "new_licensee_timeframe",
            sa.Integer,
            nullable=True,
            comment="Months for new licensees to complete",
        ),
        sa.Column(
            "effective_date",
            sa.Date,
            nullable=True,
            comment="When requirement became effective",
        ),
        sa.Column(
            "statute_citation", sa.Text, nullable=True, comment="Legal reference"
        ),
        sa.Column(
            "notes",
            sa.Text,
            nullable=True,
            comment="Additional details, exceptions, and edge cases",
        ),
        sa.Column(
            "metadata", postgresql.JSONB, nullable=True, comment="Extensible metadata"
        ),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        # Constraints
        sa.CheckConstraint(
            "requirement_type IN ('ONE_TIME', 'PER_RENEWAL', 'PER_YEAR', 'EVERY_N_YEARS')",
            name="ck_requirement_type",
        ),
        sa.CheckConstraint("hours_required > 0", name="ck_hours_positive"),
    )

    # Indexes for content_specific_cme
    op.create_index("idx_content_state_code", "content_specific_cme", ["state_code"])
    op.create_index(
        "idx_content_topic_category", "content_specific_cme", ["topic_category"]
    )
    op.create_index(
        "idx_content_provider_type", "content_specific_cme", ["provider_type"]
    )
    op.create_index("idx_content_conditional", "content_specific_cme", ["conditional"])

    # Table 3: Exemptions and Equivalents
    op.create_table(
        "exemptions_equivalents",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column(
            "exemption_id",
            sa.String(50),
            nullable=False,
            unique=True,
            index=True,
            comment="Unique identifier (e.g., AL-EQUIV-ABMS-001)",
        ),
        sa.Column(
            "state_code",
            sa.String(10),
            sa.ForeignKey("state_cme_base_requirements.state_code", ondelete="CASCADE"),
            nullable=False,
            index=True,
            comment="Links to state base requirements",
        ),
        sa.Column(
            "board_type",
            sa.String(20),
            nullable=False,
            comment="MEDICAL, OSTEOPATHIC, or COMBINED",
        ),
        sa.Column(
            "exemption_type",
            sa.String(50),
            nullable=False,
            index=True,
            comment="BOARD_CERTIFICATION, RESIDENCY_TRAINING, MOC_PARTICIPATION, etc.",
        ),
        sa.Column(
            "exemption_category",
            sa.String(50),
            nullable=False,
            comment="SPECIALTY_BOARD, TRAINING, SERVICE, etc.",
        ),
        sa.Column(
            "description",
            sa.Text,
            nullable=False,
            comment="What qualifies for this exemption",
        ),
        sa.Column(
            "credit_hours_granted",
            sa.Integer,
            nullable=True,
            comment="Hours credited (NULL if full exemption)",
        ),
        sa.Column(
            "full_exemption",
            sa.Boolean,
            nullable=False,
            default=False,
            comment="Whether this exempts all CME requirements",
        ),
        sa.Column(
            "conditions",
            sa.Text,
            nullable=True,
            comment="Requirements to qualify for exemption",
        ),
        sa.Column(
            "documentation_required",
            sa.Text,
            nullable=True,
            comment="What must be submitted to board",
        ),
        sa.Column(
            "board_organizations",
            sa.String(200),
            nullable=True,
            comment="Recognized boards (e.g., 'ABMS, AOA, RCPSC')",
        ),
        sa.Column(
            "statute_citation", sa.Text, nullable=True, comment="Legal reference"
        ),
        sa.Column(
            "notes", sa.Text, nullable=True, comment="Additional details and exceptions"
        ),
        sa.Column(
            "metadata", postgresql.JSONB, nullable=True, comment="Extensible metadata"
        ),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # Indexes for exemptions_equivalents
    op.create_index(
        "idx_exemption_state_code", "exemptions_equivalents", ["state_code"]
    )
    op.create_index("idx_exemption_type", "exemptions_equivalents", ["exemption_type"])

    # Table 4: Special Population Requirements
    op.create_table(
        "special_population_requirements",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column(
            "requirement_id",
            sa.String(50),
            nullable=False,
            unique=True,
            index=True,
            comment="Unique identifier",
        ),
        sa.Column(
            "state_code",
            sa.String(10),
            sa.ForeignKey("state_cme_base_requirements.state_code", ondelete="CASCADE"),
            nullable=False,
            index=True,
            comment="Links to state base requirements",
        ),
        sa.Column(
            "provider_type", sa.String(10), nullable=False, comment="MD, DO, or BOTH"
        ),
        sa.Column(
            "specialty_type",
            sa.String(100),
            nullable=True,
            comment="Specialty affected (e.g., 'General Internal Medicine, Family Practice')",
        ),
        sa.Column(
            "population_criteria",
            sa.String(200),
            nullable=True,
            comment="Population definition (e.g., '25% of patients ≥65 years')",
        ),
        sa.Column(
            "hours_required",
            sa.Numeric(4, 2),
            nullable=True,
            comment="Additional hours required (NULL if percentage-based)",
        ),
        sa.Column(
            "percentage_of_total",
            sa.Numeric(5, 2),
            nullable=True,
            comment="Percentage of total CME (NULL if fixed hours)",
        ),
        sa.Column(
            "topic_area",
            sa.String(100),
            nullable=False,
            comment="Subject matter required (e.g., 'Geriatric Medicine')",
        ),
        sa.Column(
            "statute_citation", sa.Text, nullable=True, comment="Legal reference"
        ),
        sa.Column(
            "notes", sa.Text, nullable=True, comment="Additional details and exceptions"
        ),
        sa.Column(
            "metadata", postgresql.JSONB, nullable=True, comment="Extensible metadata"
        ),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # Indexes for special_population_requirements
    op.create_index(
        "idx_special_state_code", "special_population_requirements", ["state_code"]
    )
    op.create_index(
        "idx_special_specialty", "special_population_requirements", ["specialty_type"]
    )

    # Table 5: State Board Contacts
    op.create_table(
        "state_board_contacts",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column(
            "state_code",
            sa.String(10),
            nullable=False,
            unique=True,
            index=True,
            comment="State/territory code (links to base requirements)",
        ),
        sa.Column(
            "board_name", sa.String(200), nullable=False, comment="Official board name"
        ),
        sa.Column(
            "board_abbreviation",
            sa.String(20),
            nullable=True,
            comment="Common abbreviation (e.g., 'ALBME')",
        ),
        sa.Column(
            "website_url", sa.String(500), nullable=True, comment="Official website URL"
        ),
        sa.Column(
            "cme_guidance_url",
            sa.String(500),
            nullable=True,
            comment="CME-specific guidance page URL",
        ),
        sa.Column(
            "contact_email", sa.String(100), nullable=True, comment="Contact email"
        ),
        sa.Column("phone", sa.String(20), nullable=True, comment="Contact phone"),
        sa.Column(
            "last_verified",
            sa.Date,
            nullable=False,
            server_default=sa.func.current_date(),
            comment="When contact info was last verified",
        ),
        sa.Column("notes", sa.Text, nullable=True, comment="Additional information"),
        sa.Column(
            "metadata", postgresql.JSONB, nullable=True, comment="Extensible metadata"
        ),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # Indexes for state_board_contacts
    op.create_index("idx_board_state_code", "state_board_contacts", ["state_code"])


def downgrade() -> None:
    """
    Drop CME requirements tables.
    """
    op.drop_table("state_board_contacts")
    op.drop_table("special_population_requirements")
    op.drop_table("exemptions_equivalents")
    op.drop_table("content_specific_cme")
    op.drop_table("state_cme_base_requirements")
