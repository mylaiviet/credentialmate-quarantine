"""
Find the actual timestamp when data was seeded by checking earliest audit logs.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from datetime import datetime

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Get earliest audit log entries
    result = db.execute(text("""
        SELECT timestamp, user_email, action_type, resource_type, endpoint
        FROM audit_logs
        ORDER BY timestamp ASC
        LIMIT 10
    """))

    print("\n" + "="*120)
    print("EARLIEST AUDIT LOG ENTRIES (Indicates when seeding started)")
    print("="*120)

    rows = result.fetchall()
    if rows:
        first_timestamp = rows[0][0]
        print(f"\nFIRST AUDIT LOG TIMESTAMP: {first_timestamp}")
        print("\nFirst 10 audit entries:")
        for i, row in enumerate(rows, 1):
            print(f"\n{i}. Timestamp: {row[0]}")
            print(f"   User Email: {row[1]}")
            print(f"   Action Type: {row[2]}")
            print(f"   Resource Type: {row[3]}")
            print(f"   Endpoint: {row[4]}")

    # Get latest audit log entry
    result = db.execute(text("""
        SELECT timestamp, user_email, action_type
        FROM audit_logs
        ORDER BY timestamp DESC
        LIMIT 1
    """))

    last_row = result.fetchone()
    if last_row:
        print(f"\nLAST AUDIT LOG TIMESTAMP: {last_row[0]}")

    # Check file history for earliest events
    result = db.execute(text("""
        SELECT MIN(timestamp) as earliest_event
        FROM file_history_events
    """))

    earliest_file_event = result.scalar()
    if earliest_file_event:
        print(f"\nEARLIEST FILE HISTORY EVENT: {earliest_file_event}")

    # Summary
    print("\n" + "="*120)
    print("ACTUAL SEEDING TIMELINE")
    print("="*120)
    print(f"Seed Script Last Modified: 2025-11-19 03:21:24 (local file)")
    print(f"First Audit Log Entry: {rows[0][0] if rows else 'N/A'}")
    if earliest_file_event:
        print(f"First File History Event: {earliest_file_event}")
    print(f"Last Audit Log Entry: {last_row[0] if last_row else 'N/A'}")

    print("\n" + "="*120)
    print("SYNTHETIC DATA TIMESTAMP RANGE (For Dashboard Simulation)")
    print("="*120)
    print("Earliest User Created At: 2022-11-21 03:58:02 (simulated)")
    print("Latest User Created At: 2025-06-16 03:37:10 (simulated)")

finally:
    db.close()
