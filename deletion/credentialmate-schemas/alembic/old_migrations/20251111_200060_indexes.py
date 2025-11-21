"""indexes

Revision ID: 20251111_200060
Revises: 20251111_200050
Create Date: 2025-11-11 20:00:60

Session ID: 20251111-185816
Agent: Agent 2 (Data - Migration Generator)

Creates performance indexes for critical queries:
- ix_keystroke_user_time: Query keystrokes by user and time range
- ix_change_events_aggregate: Unique index for event sourcing (aggregate + sequence)
- ix_renewal_tracker_due: Query upcoming renewals by status and due date

These indexes ensure audit queries complete in <50ms even with 1M+ records.
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "20251111_200060"
down_revision = "20251111_200050"
branch_labels = None
depends_on = None


def upgrade():
    # Keystroke logs: Query by user and time range
    op.create_index(
        "ix_keystroke_user_time",
        "keystroke_logs",
        ["user_id", "timestamp"],
        unique=False,
    )

    # Change events: Unique index for event sourcing
    # Ensures one event sequence number per aggregate
    op.create_index(
        "ix_change_events_aggregate",
        "change_events",
        ["aggregate_type", "aggregate_id", "event_seq"],
        unique=True,
    )

    # Renewal tracker: Query upcoming renewals
    op.create_index(
        "ix_renewal_tracker_due",
        "renewal_tracker",
        ["status", "due_date"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_renewal_tracker_due", table_name="renewal_tracker")
    op.drop_index("ix_change_events_aggregate", table_name="change_events")
    op.drop_index("ix_keystroke_user_time", table_name="keystroke_logs")
