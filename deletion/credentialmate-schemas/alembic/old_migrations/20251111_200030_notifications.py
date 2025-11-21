"""notifications

Revision ID: 20251111_200030
Revises: 20251111_200020
Create Date: 2025-11-11 20:00:30

Session ID: 20251111-185816
Agent: Agent 2 (Data - Migration Generator)

Creates notification infrastructure:
- notification_settings: User notification preferences (email, SMS, in-app)
- notification_queue: Outbound notification queue with delivery tracking

Supports automated alerts for license expirations, CME deadlines, etc.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = "20251111_200030"
down_revision = "20251111_200020"
branch_labels = None
depends_on = None


def upgrade():
    # Create notification_settings table
    op.create_table(
        "notification_settings",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "prefer_email", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column(
            "prefer_sms", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column(
            "prefer_inapp", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column(
            "timezone",
            sa.String(length=50),
            server_default="America/Chicago",
            nullable=False,
        ),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_foreign_key(
        "fk_notification_settings_user",
        "notification_settings",
        "users",
        ["user_id"],
        ["id"],
    )

    # Create notification_queue table
    op.create_table(
        "notification_queue",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("template_id", sa.String(length=50), nullable=True),
        sa.Column("payload", postgresql.JSON(), nullable=True),
        sa.Column(
            "status", sa.String(length=30), server_default="queued", nullable=False
        ),
        sa.Column("sent_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("delivery_status", sa.String(length=30), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_foreign_key(
        "fk_notification_queue_user", "notification_queue", "users", ["user_id"], ["id"]
    )


def downgrade():
    op.drop_constraint(
        "fk_notification_queue_user", "notification_queue", type_="foreignkey"
    )
    op.drop_table("notification_queue")
    op.drop_constraint(
        "fk_notification_settings_user", "notification_settings", type_="foreignkey"
    )
    op.drop_table("notification_settings")
