"""Script to check database tables."""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(
        text(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
        )
    )
    tables = [row[0] for row in result]
    print("Database tables:")
    for table in tables:
        print(f"  - {table}")
    print(f"\nTotal: {len(tables)} tables")

    # Check for critical HIPAA tables
    critical_tables = ["audit_logs", "token_blacklist", "users"]
    print("\nCritical HIPAA tables:")
    for table in critical_tables:
        status = "[OK]" if table in tables else "[MISSING]"
        print(f"  {status} {table}")
