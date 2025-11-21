"""create_reference_tables

Revision ID: 20251111_200001
Revises: 20251111_183254
Create Date: 2025-11-11 20:00:01

Session ID: 20251111-185816
Agent: Agent 2 (Data - Migration Generator)

Creates reference tables for multi-state licensing and CME tracking:
- specialties: Medical specialty classifications
- license_types: License type codes (MD, DO, NP, PA, RN, etc.)
- cme_credit_types: CME credit categories (AMA PRA Category 1, etc.)
- state_license_requirements: State-specific CME requirements (all 50 states)

These tables must be created FIRST as they are referenced by other tables.
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20251111_200001"
down_revision = "20251111_200000"  # After base tables
branch_labels = None
depends_on = None


def upgrade():
    # Create specialties table
    op.create_table(
        "specialties",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("cme_modifier", sa.Integer(), server_default="0", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create license_types table
    op.create_table(
        "license_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=30), nullable=True),
        sa.Column("description", sa.String(length=100), nullable=True),
        sa.Column(
            "requires_cme",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("renewal_period", sa.Interval(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    # Create cme_credit_types table
    op.create_table(
        "cme_credit_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("credit_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("accrediting_body", sa.String(length=100), nullable=True),
        sa.Column(
            "is_mandatory",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create state_license_requirements table
    op.create_table(
        "state_license_requirements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("state_code", sa.CHAR(length=2), nullable=True),
        sa.Column("renewal_period", sa.Interval(), nullable=True),
        sa.Column("required_cme_hours", sa.Integer(), nullable=True),
        sa.Column("controlled_substance_hours", sa.Integer(), nullable=True),
        sa.Column("last_updated", sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("state_license_requirements")
    op.drop_table("cme_credit_types")
    op.drop_table("license_types")
    op.drop_table("specialties")
