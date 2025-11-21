"""update_users_add_specialty_and_encrypted

Revision ID: 20251111_200010
Revises: 20251111_200001
Create Date: 2025-11-11 20:00:10

Session ID: 20251111-185816
Agent: Agent 2 (Data - Migration Generator)

Enhances users table with:
- specialty_id: FK to specialties table
- npi_encrypted: BYTEA field for encrypted NPI (HIPAA compliance)
- ssn_encrypted: BYTEA field for encrypted SSN (HIPAA compliance)

SECURITY: npi_encrypted and ssn_encrypted use envelope encryption with KMS.
Raw values must NEVER be stored or logged.
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20251111_200010"
down_revision = "20251111_200001"
branch_labels = None
depends_on = None


def upgrade():
    # Add specialty_id FK column
    op.add_column("users", sa.Column("specialty_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_users_specialty", "users", "specialties", ["specialty_id"], ["id"]
    )

    # Add encrypted PHI fields (BYTEA for binary encrypted data)
    # These fields store KMS-encrypted data, never plaintext
    op.add_column("users", sa.Column("npi_encrypted", sa.LargeBinary(), nullable=True))
    op.add_column("users", sa.Column("ssn_encrypted", sa.LargeBinary(), nullable=True))


def downgrade():
    op.drop_column("users", "ssn_encrypted")
    op.drop_column("users", "npi_encrypted")
    op.drop_constraint("fk_users_specialty", "users", type_="foreignkey")
    op.drop_column("users", "specialty_id")
