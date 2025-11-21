"""create_base_tables

Revision ID: 20251111_200000
Revises: None
Create Date: 2025-11-11 20:00:00

Session ID: 20251111-185816
Agent: Agent 2 (Data - Migration Generator - REDO)

Creates BASE tables that existed before (users, licenses, cme_activities, documents, delegations).
This is a clean-slate deployment - recreating the original schema.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = "20251111_200000"
down_revision = None  # First migration
branch_labels = None
depends_on = None


def upgrade():
    # Create UserRole enum (with exception handling for idempotency)
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE userrole AS ENUM ('provider', 'delegate', 'admin');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """
    )

    # Create users table
    op.create_table(
        "users",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column(
            "role",
            postgresql.ENUM(
                "provider", "delegate", "admin", name="userrole", create_type=False
            ),
            nullable=False,
            server_default="provider",
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("last_login", sa.TIMESTAMP(), nullable=True),
        sa.Column("user_metadata", postgresql.JSONB(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # Create LicenseStatus enum (with exception handling for idempotency)
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE licensestatus AS ENUM ('active', 'expired', 'pending', 'suspended');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """
    )

    # Create licenses table
    op.create_table(
        "licenses",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("license_number", sa.String(length=100), nullable=False),
        sa.Column("issuing_board", sa.String(length=100), nullable=True),
        sa.Column("issued_at", sa.Date(), nullable=True),
        sa.Column("state_code", sa.CHAR(length=2), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_foreign_key(
        "fk_licenses_user", "licenses", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )

    # Create cme_activities table
    op.create_table(
        "cme_activities",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("provider", sa.String(length=255), nullable=True),
        sa.Column("credits", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("date_completed", sa.Date(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_foreign_key(
        "fk_cme_activities_user",
        "cme_activities",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Create DocumentType and DocumentStatus enums (with exception handling for idempotency)
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE documenttype AS ENUM ('license', 'cme_certificate', 'other');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """
    )
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE documentstatus AS ENUM ('uploaded', 'processing', 'completed', 'failed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """
    )

    # Create documents table
    op.create_table(
        "documents",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=50), nullable=True),
        sa.Column("s3_key", sa.String(length=512), nullable=True),
        sa.Column(
            "uploaded_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column("retention_until", sa.TIMESTAMP(), nullable=True),
        sa.Column(
            "is_redacted", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_foreign_key(
        "fk_documents_user",
        "documents",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_documents_uploader", "documents", "users", ["uploaded_by"], ["id"]
    )

    # Create delegations table
    op.create_table(
        "delegations",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column("delegator_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delegate_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scope", postgresql.JSONB(), nullable=True),
        sa.Column("expires_at", sa.TIMESTAMP(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_foreign_key(
        "fk_delegations_delegator",
        "delegations",
        "users",
        ["delegator_user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_delegations_delegate",
        "delegations",
        "users",
        ["delegate_user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # NOTE: notification_settings table moved to migration 20251111_200030 (enhanced version with more fields)

    # Create audit_logs table (from old schema)
    op.create_table(
        "audit_logs",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("target_table", sa.String(length=100), nullable=True),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("details", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_foreign_key(
        "fk_audit_logs_actor", "audit_logs", "users", ["actor_id"], ["id"]
    )

    # Create token_blacklist table (from old schema)
    op.create_table(
        "token_blacklist",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column("token_jti", sa.String(length=255), nullable=False, unique=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "revoked_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("expires_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("revocation_reason", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_jti"),
    )
    op.create_foreign_key(
        "fk_token_blacklist_user",
        "token_blacklist",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_table("token_blacklist")
    op.drop_table("audit_logs")
    # notification_settings dropped in migration 20251111_200030
    op.drop_table("delegations")
    op.drop_table("documents")
    op.drop_table("cme_activities")
    op.drop_table("licenses")
    op.drop_table("users")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS userrole CASCADE")
    op.execute("DROP TYPE IF EXISTS licensestatus CASCADE")
    op.execute("DROP TYPE IF EXISTS documenttype CASCADE")
    op.execute("DROP TYPE IF EXISTS documentstatus CASCADE")
