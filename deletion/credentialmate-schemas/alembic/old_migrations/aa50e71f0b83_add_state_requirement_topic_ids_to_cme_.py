"""add_state_requirement_topic_ids_to_cme_activities

Revision ID: aa50e71f0b83
Revises: 20251111_220000
Create Date: 2025-11-11 22:40:22.413695

Adds external state requirement tracking to CME activities.

This migration prepares the schema for integration with an external
state requirements API by adding a JSONB field to store references
to external requirement topic IDs.

Schema changes:
- Add state_requirement_topic_ids JSONB field to cme_activities
- Add compliance_last_checked timestamp for tracking validation state
- Add compliance_status for caching compliance state

Purpose:
- Link CME activities to specific state requirement topics (external API)
- Track compliance validation state
- Enable gap analysis and compliance reporting
- Maintain flexibility for external data source integration
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = "aa50e71f0b83"
down_revision: Union[str, None] = "20251111_220000"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add JSONB field for external state requirement topic IDs
    op.add_column(
        "cme_activities",
        sa.Column(
            "state_requirement_topic_ids",
            JSONB,
            nullable=True,
            comment="External state requirement topic IDs (references external API)",
        ),
    )

    # Add compliance tracking fields
    op.add_column(
        "cme_activities",
        sa.Column(
            "compliance_last_checked",
            sa.DateTime,
            nullable=True,
            comment="Last time compliance was validated against state requirements",
        ),
    )

    op.add_column(
        "cme_activities",
        sa.Column(
            "compliance_status",
            sa.String(50),
            nullable=True,
            comment="Cached compliance status: pending, valid, expired, needs_review",
        ),
    )

    # Create index for compliance queries
    op.create_index(
        "idx_cme_compliance_status",
        "cme_activities",
        ["user_id", "compliance_status"],
        unique=False,
    )


def downgrade() -> None:
    # Drop index first
    op.drop_index("idx_cme_compliance_status", table_name="cme_activities")

    # Drop columns
    op.drop_column("cme_activities", "compliance_status")
    op.drop_column("cme_activities", "compliance_last_checked")
    op.drop_column("cme_activities", "state_requirement_topic_ids")
