"""create_licensing_tables

Revision ID: 20251111_200020
Revises: 20251111_200010
Create Date: 2025-11-11 20:00:20

Session ID: 20251111-185816
Agent: Agent 2 (Data - Migration Generator)

Creates multi-state licensing support and renewal tracking:
- license_states: Multi-state license instances (one license can be valid in multiple states)
- renewal_tracker: Automated renewal tracking with notification flags

Enables providers to track licenses across multiple states with different
expiration dates and renewal requirements.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = "20251111_200020"
down_revision = "20251111_200010"
branch_labels = None
depends_on = None


def upgrade():
    # Create license_states table (multi-state support)
    op.create_table(
        "license_states",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column("license_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("state_code", sa.CHAR(length=2), nullable=False),
        sa.Column("expiration_date", sa.Date(), nullable=False),
        sa.Column(
            "renewal_status",
            sa.String(length=30),
            server_default="active",
            nullable=False,
        ),
        sa.Column("last_renewed_at", sa.Date(), nullable=True),
        sa.Column("next_renewal_due", sa.Date(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_foreign_key(
        "fk_license_states_license",
        "license_states",
        "licenses",
        ["license_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Create renewal_tracker table
    op.create_table(
        "renewal_tracker",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("license_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status", sa.String(length=30), server_default="pending", nullable=False
        ),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column(
            "notified_90_days",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "notified_60_days",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "notified_30_days",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_foreign_key(
        "fk_renewal_tracker_user", "renewal_tracker", "users", ["user_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_renewal_tracker_license",
        "renewal_tracker",
        "licenses",
        ["license_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        "fk_renewal_tracker_license", "renewal_tracker", type_="foreignkey"
    )
    op.drop_constraint("fk_renewal_tracker_user", "renewal_tracker", type_="foreignkey")
    op.drop_table("renewal_tracker")
    op.drop_constraint(
        "fk_license_states_license", "license_states", type_="foreignkey"
    )
    op.drop_table("license_states")
