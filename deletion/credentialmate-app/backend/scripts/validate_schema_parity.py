"""
Schema Validation Script - Prevents Schema Drift

Compares SQLAlchemy models against actual database schema to detect drift.
Run in CI/CD pipeline to catch mismatches before deployment.

Session: 20251111-234532
Agent: Claude Code (Backend)

Usage:
    python scripts/validate_schema_parity.py

Exit Codes:
    0 - Schema matches (success)
    1 - Schema drift detected (failure)
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import inspect
from app.core.database import engine
from app.models import Base


def validate_schema():
    """
    Validate that database schema matches SQLAlchemy models.

    Checks:
    - All model tables exist in database
    - All model columns exist in tables
    - Warns about extra columns in database (possible deprecated fields)

    Returns:
        bool: True if schema matches, False if drift detected
    """
    inspector = inspect(engine)
    errors = []
    warnings = []

    print("Validating schema parity...")
    print(f"Checking {len(Base.metadata.tables)} tables\n")

    for table_name, table in Base.metadata.tables.items():
        # Check table exists
        if not inspector.has_table(table_name):
            errors.append(f"Table '{table_name}' missing in database")
            continue

        # Get columns from database
        db_columns = {col["name"]: col for col in inspector.get_columns(table_name)}
        model_columns = {col.name: col for col in table.columns}

        # Check for missing columns (model has it, DB doesn't)
        for col_name, col in model_columns.items():
            if col_name not in db_columns:
                errors.append(
                    f"Column '{table_name}.{col_name}' missing in database "
                    f"(type: {col.type})"
                )

        # Check for extra columns (DB has it, model doesn't)
        for col_name in db_columns:
            if col_name not in model_columns:
                warnings.append(
                    f"Column '{table_name}.{col_name}' exists in DB but not in model "
                    f"(possibly deprecated)"
                )

    # Print results
    if errors:
        print("SCHEMA DRIFT DETECTED!\n")
        print("Errors:")
        for error in errors:
            print(f"  [ERROR] {error}")
        print()

    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  [WARN] {warning}")
        print()

    if not errors and not warnings:
        print("OK - Schema validation passed")
        print("Database schema matches SQLAlchemy models\n")
        return True
    elif errors:
        print(f"FAILED - {len(errors)} error(s), {len(warnings)} warning(s)")
        print("\nTo fix schema drift:")
        print("  1. Run: alembic revision --autogenerate -m 'Fix schema drift'")
        print("  2. Review the generated migration")
        print("  3. Run: alembic upgrade head")
        print("  4. Run this script again to verify\n")
        return False
    else:
        # Only warnings, not errors
        print(f"OK - {len(warnings)} warning(s) (deprecated columns in DB)")
        print("Consider creating a migration to drop deprecated columns\n")
        return True


if __name__ == "__main__":
    try:
        success = validate_schema()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERROR: Schema validation failed with exception: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
