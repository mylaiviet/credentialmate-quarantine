#!/usr/bin/env python3
"""Quick check of database seed data"""
from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
try:
    count = db.query(User).count()
    print(f"Total users in database: {count}")

    if count == 0:
        print("\n❌ No users found! Database needs seeding.")
        print("\nRun this command to seed:")
        print("  python scripts/seed_all.py")
    else:
        # Check for Lauren
        lauren = db.query(User).filter(User.email == "lauren.chen@example.com").first()
        if lauren:
            print(f"\n✅ Lauren Chen exists!")
            print(f"   Email: {lauren.email}")
            print(f"   Active: {lauren.is_active}")
            print(f"   Verified: {lauren.is_verified}")
            print(f"   Role: {lauren.role}")
            print(f"   Has password: {bool(lauren.hashed_password)}")
        else:
            print(f"\n❌ Lauren Chen not found!")

        # Show first 5 users
        print(f"\nFirst 5 users in database:")
        users = db.query(User).limit(5).all()
        for user in users:
            print(f"  - {user.email} ({user.role}) - Active: {user.is_active}")

except Exception as e:
    print(f"❌ Error connecting to database: {e}")
    import traceback

    traceback.print_exc()
finally:
    db.close()
