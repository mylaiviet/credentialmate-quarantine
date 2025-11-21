"""fix_licenses_schema_add_missing_columns

Revision ID: f97a3162ee67
Revises: aa50e71f0b83
Create Date: 2025-11-11 23:56:54.666389

Session ID: 20251111-234532
Agent: Claude Code (Backend)

Fixes schema drift between License model and database:
- Adds missing columns: state, license_type, issue_date, expiration_date, status, renewal_cycle_months, license_metadata
- Migrates existing data from state_code -> state, issued_at -> issue_date
- Preserves all existing seeded data
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f97a3162ee67"
down_revision: Union[str, None] = "aa50e71f0b83"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns (nullable first to avoid issues with existing data)
    op.add_column("licenses", sa.Column("state", sa.String(length=2), nullable=True))
    op.add_column(
        "licenses", sa.Column("license_type", sa.String(length=20), nullable=True)
    )
    op.add_column("licenses", sa.Column("issue_date", sa.Date(), nullable=True))
    op.add_column("licenses", sa.Column("expiration_date", sa.Date(), nullable=True))
    op.add_column("licenses", sa.Column("status", sa.String(length=20), nullable=True))
    op.add_column(
        "licenses", sa.Column("renewal_cycle_months", sa.Integer(), nullable=True)
    )
    op.add_column(
        "licenses", sa.Column("license_metadata", postgresql.JSONB(), nullable=True)
    )

    # Migrate existing data
    op.execute(
        """
        UPDATE licenses
        SET
            state = state_code,
            issue_date = issued_at,
            license_type = 'MD',  -- Default to MD, can be updated later
            expiration_date = COALESCE(issued_at, CURRENT_DATE) + INTERVAL '24 months',  -- Default 2-year expiration
            status = 'active',  -- Default to active
            renewal_cycle_months = 24  -- Default 24 months
        WHERE state_code IS NOT NULL
    """
    )

    # For records without state_code, set defaults
    op.execute(
        """
        UPDATE licenses
        SET
            state = 'CA',  -- Default state
            issue_date = COALESCE(issued_at, created_at::date),
            license_type = 'MD',
            expiration_date = COALESCE(issued_at, created_at::date, CURRENT_DATE) + INTERVAL '24 months',
            status = 'active',
            renewal_cycle_months = 24
        WHERE state_code IS NULL
    """
    )

    # Now make the new columns non-nullable
    op.alter_column("licenses", "state", nullable=False)
    op.alter_column("licenses", "license_type", nullable=False)
    op.alter_column("licenses", "issue_date", nullable=False)
    op.alter_column("licenses", "expiration_date", nullable=False)
    op.alter_column("licenses", "status", nullable=False)
    op.alter_column("licenses", "renewal_cycle_months", nullable=False)

    # Add indexes for the new columns
    op.create_index("idx_licenses_state", "licenses", ["state"])
    op.create_index("idx_licenses_expiration_date", "licenses", ["expiration_date"])

    # Add check constraint for dates
    op.create_check_constraint(
        "ck_license_dates", "licenses", "expiration_date > issue_date"
    )

    # Add unique constraint for user_id + state
    op.create_unique_constraint("uq_user_state", "licenses", ["user_id", "state"])

    # Keep old columns for now (can be dropped in a future migration if confirmed safe)
    # This allows rollback if needed


def downgrade() -> None:
    # Drop constraints and indexes
    op.drop_constraint("uq_user_state", "licenses", type_="unique")
    op.drop_constraint("ck_license_dates", "licenses", type_="check")
    op.drop_index("idx_licenses_expiration_date", "licenses")
    op.drop_index("idx_licenses_state", "licenses")

    # Drop new columns
    op.drop_column("licenses", "license_metadata")
    op.drop_column("licenses", "renewal_cycle_months")
    op.drop_column("licenses", "status")
    op.drop_column("licenses", "expiration_date")
    op.drop_column("licenses", "issue_date")
    op.drop_column("licenses", "license_type")
    op.drop_column("licenses", "state")
