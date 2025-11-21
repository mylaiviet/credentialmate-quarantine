"""
Query script to retrieve actual seed timestamp from user metadata.
"""

from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import User
import json

# Create database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Query users with their metadata
    users = db.query(User).all()

    print("\n" + "="*120)
    print("USER METADATA ANALYSIS - LOOKING FOR ACTUAL SEED TIMESTAMP")
    print("="*120 + "\n")

    # Check what metadata contains
    metadata_samples = []
    for user in users[:5]:
        if user.user_metadata:
            metadata_samples.append({
                "email": user.email,
                "metadata": user.user_metadata
            })

    if metadata_samples:
        print("Sample Metadata from Users:")
        for sample in metadata_samples:
            print(f"\nEmail: {sample['email']}")
            print(f"Metadata: {json.dumps(sample['metadata'], indent=2)}")
    else:
        print("No metadata found in first 5 users.")

    # Try to get any audit logs that might have seeding timestamp
    from app.models.audit_log import AuditLog
    audit_logs = db.query(AuditLog).order_by(AuditLog.timestamp).limit(10).all()

    if audit_logs:
        print("\n" + "="*120)
        print("EARLIEST AUDIT LOGS (May contain seed timestamp):")
        print("="*120)
        for log in audit_logs:
            print(f"\nTimestamp: {log.timestamp}")
            print(f"Action: {log.action}")
            print(f"Details: {log.details}")

    # Check for any system events or logs
    print("\n" + "="*120)
    print("DATABASE TABLE INFO:")
    print("="*120)
    print(f"Total Users: {db.query(func.count(User.id)).scalar()}")

    # Get earliest and latest created_at timestamps
    earliest_user = db.query(User).order_by(User.created_at).first()
    latest_user = db.query(User).order_by(User.created_at.desc()).first()

    if earliest_user:
        print(f"Earliest User Created At: {earliest_user.created_at}")
    if latest_user:
        print(f"Latest User Created At: {latest_user.created_at}")

finally:
    db.close()
