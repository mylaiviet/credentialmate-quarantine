"""immutable_keystrokes_and_events

Revision ID: 20251111_200050
Revises: 20251111_200040
Create Date: 2025-11-11 20:00:50

Session ID: 20251111-185816
Agent: Agent 2 (Data - Migration Generator)

⚠️ CRITICAL: Immutable audit trail for HIPAA/SOC2 compliance

Creates three tables for tamper-evident audit logging:
- keystroke_logs: Immutable keystroke-level audit trail (encrypted)
- change_events: Event sourcing for all data changes
- audit_immutable_index: Integrity verification with Merkle roots

SECURITY REQUIREMENTS:
1. These tables are APPEND-ONLY - no UPDATE or DELETE allowed
2. payload_encrypted uses KMS envelope encryption
3. integrity_hash creates hash chain to detect tampering
4. event_seq provides strict ordering for change_events

COMPLIANCE: HIPAA 45 CFR 164.312(b), SOC2 CC6.1
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = "20251111_200050"
down_revision = "20251111_200040"
branch_labels = None
depends_on = None


def upgrade():
    # Create keystroke_logs table (immutable, encrypted)
    op.create_table(
        "keystroke_logs",
        sa.Column(
            "event_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("timestamp", sa.TIMESTAMP(), nullable=False),
        sa.Column("target_table", sa.String(length=100), nullable=True),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action_type", sa.String(length=30), nullable=True),
        sa.Column("field_name", sa.String(length=255), nullable=True),
        sa.Column(
            "payload_encrypted", sa.LargeBinary(), nullable=False
        ),  # BYTEA for encrypted payload
        sa.Column("client_ip", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column(
            "integrity_hash", sa.String(length=128), nullable=False
        ),  # Hash chaining
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_foreign_key(
        "fk_keystroke_user", "keystroke_logs", "users", ["user_id"], ["id"]
    )

    # Create change_events table (event sourcing, append-only)
    op.create_table(
        "change_events",
        sa.Column(
            "event_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
        ),
        sa.Column("aggregate_type", sa.String(length=100), nullable=False),
        sa.Column("aggregate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "event_seq", sa.BigInteger(), nullable=False
        ),  # Monotonic sequence per aggregate
        sa.Column(
            "event_type", sa.String(length=100), nullable=False
        ),  # CREATED, UPDATED, DELETED
        sa.Column("event_payload", postgresql.JSON(), nullable=False),  # Minimal diff
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_foreign_key(
        "fk_change_events_actor", "change_events", "users", ["actor_id"], ["id"]
    )

    # Create audit_immutable_index table (integrity verification)
    op.create_table(
        "audit_immutable_index",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column("snapshot_time", sa.TIMESTAMP(), nullable=False),
        sa.Column("aggregate_counts", postgresql.JSON(), nullable=True),
        sa.Column(
            "merkle_root", sa.String(length=128), nullable=False
        ),  # Merkle tree root hash
        sa.Column(
            "storage_pointer", sa.String(length=512), nullable=True
        ),  # S3/cold storage pointer
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    # CRITICAL: These tables should rarely be dropped in production
    # Dropping audit logs may violate compliance requirements
    op.drop_table("audit_immutable_index")
    op.drop_constraint("fk_change_events_actor", "change_events", type_="foreignkey")
    op.drop_table("change_events")
    op.drop_constraint("fk_keystroke_user", "keystroke_logs", type_="foreignkey")
    op.drop_table("keystroke_logs")
