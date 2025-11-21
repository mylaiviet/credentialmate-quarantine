"""
Check audit logs to find actual seed timestamp.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Get earliest audit log entry
    result = db.execute(text("""
        SELECT timestamp, user_id, endpoint, method
        FROM audit_logs
        ORDER BY timestamp ASC
        LIMIT 5
    """))

    print("\n" + "="*100)
    print("EARLIEST AUDIT LOG ENTRIES (Actual Seeding Timestamp)")
    print("="*100)

    rows = result.fetchall()
    if rows:
        for row in rows:
            print(f"\nTimestamp: {row[0]}")
            print(f"User ID: {row[1]}")
            print(f"Endpoint: {row[2]}")
            print(f"Method: {row[3]}")
    else:
        print("No audit logs found")

    # Check file_history to see when data was created
    result = db.execute(text("""
        SELECT timestamp, event_type, file_path
        FROM file_history_events
        ORDER BY timestamp ASC
        LIMIT 5
    """))

    print("\n" + "="*100)
    print("EARLIEST FILE HISTORY EVENTS")
    print("="*100)

    rows = result.fetchall()
    if rows:
        for row in rows:
            print(f"\nTimestamp: {row[0]}")
            print(f"Event Type: {row[1]}")
            print(f"File Path: {row[2]}")

    # Get the actual data statistics
    result = db.execute(text("""
        SELECT COUNT(*) as cnt FROM users
    """))
    user_count = result.scalar()

    result = db.execute(text("""
        SELECT COUNT(*) as cnt FROM licenses
    """))
    license_count = result.scalar()

    result = db.execute(text("""
        SELECT COUNT(*) as cnt FROM cme_activities
    """))
    cme_count = result.scalar()

    print("\n" + "="*100)
    print("DATA VOLUME")
    print("="*100)
    print(f"Total Users: {user_count}")
    print(f"Total Licenses: {license_count}")
    print(f"Total CME Activities: {cme_count}")

finally:
    db.close()
