"""add_immutability_triggers

Prevents UPDATE/DELETE on audit tables to ensure HIPAA compliance.

Revision ID: 8c414c598b42
Revises: 20251111_200070
Create Date: 2025-11-11 20:45:32.675873

Session ID: 20251111-203249
Agent: Claude Backend+Security Agent
Task: AUDIT-001-P3 (Phase 3: Immutability Triggers)

CRITICAL: This migration implements immutability for audit logs as required by
HIPAA 45 CFR 164.312(b). Once applied, audit_logs, change_events, and
keystroke_logs tables cannot be modified or deleted - only INSERT is allowed.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8c414c598b42"
down_revision: Union[str, None] = "20251111_200070"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create immutability triggers for audit tables.

    Creates a reusable trigger function that prevents UPDATE and DELETE operations
    on audit tables, then applies this function to all three audit tables.
    """

    # Create the trigger function (reusable for all audit tables)
    op.execute(
        """
        CREATE OR REPLACE FUNCTION prevent_audit_modification()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'Cannot modify audit logs (HIPAA 45 CFR 164.312(b) requirement)';
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    # Apply trigger to audit_logs table
    op.execute(
        """
        CREATE TRIGGER prevent_audit_logs_update
        BEFORE UPDATE OR DELETE ON audit_logs
        FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();
    """
    )

    # Apply trigger to change_events table
    op.execute(
        """
        CREATE TRIGGER prevent_change_events_update
        BEFORE UPDATE OR DELETE ON change_events
        FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();
    """
    )

    # Apply trigger to keystroke_logs table
    op.execute(
        """
        CREATE TRIGGER prevent_keystroke_logs_update
        BEFORE UPDATE OR DELETE ON keystroke_logs
        FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();
    """
    )

    # Immutability triggers created successfully


def downgrade() -> None:
    """
    Remove immutability triggers.

    WARNING: This should only be done in development/testing environments.
    Production audit logs should NEVER have these triggers removed.
    """

    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS prevent_keystroke_logs_update ON keystroke_logs")
    op.execute("DROP TRIGGER IF EXISTS prevent_change_events_update ON change_events")
    op.execute("DROP TRIGGER IF EXISTS prevent_audit_logs_update ON audit_logs")

    # Drop function
    op.execute("DROP FUNCTION IF EXISTS prevent_audit_modification")

    # Immutability triggers removed
