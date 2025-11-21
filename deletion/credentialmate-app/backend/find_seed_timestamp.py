"""
Find the actual timestamp when data was seeded to the database.
"""

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import User
from datetime import datetime

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # List all available tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print("\n" + "="*100)
    print("ALL AVAILABLE TABLES IN DATABASE")
    print("="*100)
    for table in sorted(tables):
        print(f"  - {table}")

    # Get earliest user created_at (simulated date)
    earliest_simulated = db.query(User).order_by(User.created_at).first()
    latest_simulated = db.query(User).order_by(User.created_at.desc()).first()

    print("\n" + "="*100)
    print("USER CREATION TIMESTAMPS (Simulated for Dashboard)")
    print("="*100)
    print(f"Earliest Simulated User: {earliest_simulated.created_at} ({earliest_simulated.email})")
    print(f"Latest Simulated User: {latest_simulated.created_at} ({latest_simulated.email})")

    # Check updated_at timestamps
    earliest_updated = db.query(User).order_by(User.updated_at).first()
    print(f"\nEarliest Updated At: {earliest_updated.updated_at}")

    # Check if there are any timestamps in system tables
    result = db.execute(text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """))

    print("\n" + "="*100)
    print("CHECKING FOR SEED TIMESTAMP IN VARIOUS TABLES")
    print("="*100)

    all_tables = [row[0] for row in result]

    # Try to find most recent activity
    for table in all_tables[:5]:
        try:
            result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"{table}: {count} rows")
        except:
            pass

    # Check if there's a seed log or system table
    print("\n" + "="*100)
    print("FILE MODIFICATION TIMESTAMPS (Source Code)")
    print("="*100)
    import os
    seed_script = "/app/app/scripts/seed_all_data.py"
    if os.path.exists(seed_script):
        mtime = os.path.getmtime(seed_script)
        mtime_dt = datetime.fromtimestamp(mtime)
        print(f"seed_all_data.py modified: {mtime_dt}")

finally:
    db.close()
