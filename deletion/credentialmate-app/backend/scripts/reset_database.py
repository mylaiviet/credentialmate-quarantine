"""
Drop and recreate database schema for clean slate.
Session: 20251111-234532
Agent: Claude Code (Backend)
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


def reset_database():
    """Drop all tables and recreate clean schema"""
    print("Dropping public schema...")

    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        print("OK - Schema dropped")

        conn.execute(text("CREATE SCHEMA public"))
        print("OK - Schema recreated")

        # Grant permissions
        conn.execute(text("GRANT ALL ON SCHEMA public TO credentialmate"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
        print("OK - Permissions granted")

    print("\nDatabase reset complete!")
    print("Next step: Run 'alembic upgrade head' to create tables\n")


if __name__ == "__main__":
    reset_database()
