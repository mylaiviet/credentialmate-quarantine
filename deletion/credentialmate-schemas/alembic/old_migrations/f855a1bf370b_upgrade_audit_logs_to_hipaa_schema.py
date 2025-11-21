"""upgrade_audit_logs_to_hipaa_schema

Revision ID: f855a1bf370b
Revises: 8c414c598b42
Create Date: 2025-11-11 21:43:38.495723

Session ID: 20251111-213231
Agent: Agent 6 (Schema Migration)
Task: INT-001 - Migrate audit_logs to HIPAA schema

CRITICAL: This migration resolves schema drift between database and HIPAA model.

HIPAA Requirement: 45 CFR 164.312(b) - Audit Controls
Must track who, what, when, where, and how for all PHI access events.

Changes:
1. Rename columns for clarity:
   - actor_id → user_id
   - event_type → action_type
   - target_table → resource_type
   - target_id → resource_id
   - details → changes_made
   - created_at → timestamp

2. Add CRITICAL PHI tracking columns:
   - phi_accessed (BOOLEAN NOT NULL DEFAULT FALSE) - Flag indicating PHI access
   - phi_fields (JSONB) - List of PHI fields accessed

3. Add user context columns:
   - user_email (VARCHAR(255)) - Email for audit trail
   - user_role (VARCHAR(50)) - User role at time of action

4. Add request tracing columns:
   - endpoint (VARCHAR(255)) - API endpoint accessed
   - http_method (VARCHAR(10)) - HTTP method (GET, POST, etc.)
   - request_id (VARCHAR(100), indexed) - Unique request ID

5. Add status tracking columns:
   - status (VARCHAR(20) DEFAULT 'success') - Action status
   - error_message (TEXT) - Error message if failed

6. Add performance indexes for HIPAA compliance queries:
   - idx_audit_timestamp_phi (timestamp, phi_accessed) - PHI access reports
   - idx_audit_user_action (user_id, action_type) - User activity
   - idx_audit_resource (resource_type, resource_id) - Resource audit trail
   - idx_audit_request_id (request_id) - Request tracing

TESTING:
- Run test_migration_audit_logs_hipaa.py before/after
- Expected: 11/11 tests PASS after migration

ROLLBACK SAFETY:
- Data is preserved (column renames only)
- Downgrade restores original schema
- Existing records backfilled with safe defaults
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "f855a1bf370b"
down_revision: Union[str, None] = "8c414c598b42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade audit_logs table to HIPAA-compliant schema.

    This migration transforms the simplified audit schema to the full
    HIPAA-compliant schema with PHI tracking, request tracing, and
    comprehensive audit context.
    """

    # Step 1: Rename existing columns for clarity and consistency
    # Note: Keeping nullable status as-is during rename (actor_id was NOT NULL)
    op.alter_column("audit_logs", "actor_id", new_column_name="user_id")
    op.alter_column("audit_logs", "event_type", new_column_name="action_type")
    op.alter_column("audit_logs", "target_table", new_column_name="resource_type")
    op.alter_column("audit_logs", "target_id", new_column_name="resource_id")
    op.alter_column("audit_logs", "details", new_column_name="changes_made")
    op.alter_column("audit_logs", "created_at", new_column_name="timestamp")

    # Step 1b: Make user_id nullable (allows unauthenticated/system actions)
    op.alter_column("audit_logs", "user_id", nullable=True)

    # Step 2: Add user context columns (email and role)
    op.add_column(
        "audit_logs",
        sa.Column(
            "user_email",
            sa.String(length=255),
            nullable=True,
            comment="Email of user (preserved even if user deleted)",
        ),
    )

    op.add_column(
        "audit_logs",
        sa.Column(
            "user_role",
            sa.String(length=50),
            nullable=True,
            comment="Role of user: admin, provider, delegate",
        ),
    )

    # Step 3: Add CRITICAL PHI tracking columns (HIPAA requirement)
    op.add_column(
        "audit_logs",
        sa.Column(
            "phi_accessed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
            comment="Flag indicating PHI was accessed (HIPAA requirement)",
        ),
    )

    op.add_column(
        "audit_logs",
        sa.Column(
            "phi_fields",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment='List of PHI fields accessed: ["npi", "ssn", "name", "dob"]',
        ),
    )

    # Step 4: Add request context columns (tracing)
    op.add_column(
        "audit_logs",
        sa.Column(
            "endpoint",
            sa.String(length=255),
            nullable=True,
            comment="API endpoint accessed: /api/documents/123",
        ),
    )

    op.add_column(
        "audit_logs",
        sa.Column(
            "http_method",
            sa.String(length=10),
            nullable=True,
            comment="HTTP method: GET, POST, PUT, DELETE, PATCH",
        ),
    )

    op.add_column(
        "audit_logs",
        sa.Column(
            "request_id",
            sa.String(length=100),
            nullable=True,
            comment="Unique request ID for tracing across services",
        ),
    )

    # Step 5: Add status tracking columns
    op.add_column(
        "audit_logs",
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=True,
            server_default="success",
            comment="Status: success, failure, denied",
        ),
    )

    op.add_column(
        "audit_logs",
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
            comment="Error message if status is failure or denied",
        ),
    )

    # Step 6: Create performance indexes for HIPAA compliance queries
    # These indexes are CRITICAL for fast compliance reporting

    # Index for PHI access queries (most common compliance query)
    # Supports: "Show all PHI access in last 30 days"
    op.create_index(
        "idx_audit_timestamp_phi",
        "audit_logs",
        ["timestamp", "phi_accessed"],
        unique=False,
    )

    # Index for user activity queries
    # Supports: "Show all actions by user X"
    op.create_index(
        "idx_audit_user_action", "audit_logs", ["user_id", "action_type"], unique=False
    )

    # Index for resource audit trail
    # Supports: "Show all changes to document Y"
    op.create_index(
        "idx_audit_resource",
        "audit_logs",
        ["resource_type", "resource_id"],
        unique=False,
    )

    # Index for request tracing
    # Supports: "Trace request ID across services"
    op.create_index("idx_audit_request_id", "audit_logs", ["request_id"], unique=False)

    # Note: The immutability trigger already exists from migration 8c414c598b42
    # No need to recreate it - it will continue to work with renamed columns


def downgrade() -> None:
    """
    Downgrade audit_logs table back to simplified schema.

    WARNING: This will lose the new columns (user_email, user_role, phi tracking, etc.)
    Only use this in development/testing, not in production.
    """

    # Drop indexes (in reverse order)
    op.drop_index("idx_audit_request_id", table_name="audit_logs")
    op.drop_index("idx_audit_resource", table_name="audit_logs")
    op.drop_index("idx_audit_user_action", table_name="audit_logs")
    op.drop_index("idx_audit_timestamp_phi", table_name="audit_logs")

    # Drop new columns
    op.drop_column("audit_logs", "error_message")
    op.drop_column("audit_logs", "status")
    op.drop_column("audit_logs", "request_id")
    op.drop_column("audit_logs", "http_method")
    op.drop_column("audit_logs", "endpoint")
    op.drop_column("audit_logs", "phi_fields")
    op.drop_column("audit_logs", "phi_accessed")
    op.drop_column("audit_logs", "user_role")
    op.drop_column("audit_logs", "user_email")

    # Make user_id NOT NULL again (restore original constraint)
    op.alter_column("audit_logs", "user_id", nullable=False)

    # Rename columns back to original names
    op.alter_column("audit_logs", "timestamp", new_column_name="created_at")
    op.alter_column("audit_logs", "changes_made", new_column_name="details")
    op.alter_column("audit_logs", "resource_id", new_column_name="target_id")
    op.alter_column("audit_logs", "resource_type", new_column_name="target_table")
    op.alter_column("audit_logs", "action_type", new_column_name="event_type")
    op.alter_column("audit_logs", "user_id", new_column_name="actor_id")
