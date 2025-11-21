"""ai_and_audits

Revision ID: 20251111_200040
Revises: 20251111_200030
Create Date: 2025-11-11 20:00:40

Session ID: 20251111-185816
Agent: Agent 2 (Data - Migration Generator)

Creates AI document extraction audit trail:
- document_extraction_logs: Tracks all AI document parsing operations

Provides auditability for AI-assisted document classification and field extraction.
Includes model version, confidence scores, and human verification status.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = "20251111_200040"
down_revision = "20251111_200030"
branch_labels = None
depends_on = None


def upgrade():
    # Create document_extraction_logs table
    op.create_table(
        "document_extraction_logs",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_used", sa.String(length=100), nullable=True),
        sa.Column("extraction_status", sa.String(length=30), nullable=True),
        sa.Column("confidence_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("parsed_fields", postgresql.JSON(), nullable=True),
        sa.Column("verified_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("verified_at", sa.TIMESTAMP(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_foreign_key(
        "fk_doc_extract_doc",
        "document_extraction_logs",
        "documents",
        ["document_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_doc_extract_verifier",
        "document_extraction_logs",
        "users",
        ["verified_by"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        "fk_doc_extract_verifier", "document_extraction_logs", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_doc_extract_doc", "document_extraction_logs", type_="foreignkey"
    )
    op.drop_table("document_extraction_logs")
