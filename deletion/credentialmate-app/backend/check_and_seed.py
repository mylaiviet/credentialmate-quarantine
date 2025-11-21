"""Quick script to check database and seed if needed"""
import sys

sys.path.insert(0, ".")

from app.database import SessionLocal
from app.models.user import User
from app.services.auth_service import AuthService


def main():
    db = SessionLocal()

    # Check if users exist
    user_count = db.query(User).count()
    print(f"✅ Database connected")
    print(f"📊 Total users in database: {user_count}")

    if user_count == 0:
        print("\n❌ No users found! Database needs seeding.")
        print("\nRun this command:")
        print("  python scripts/seed_all.py")
        return

    # List first 5 users
    users = db.query(User).limit(5).all()
    print(f"\n📋 First {len(users)} users:")
    for user in users:
        print(f"  - {user.email} ({user.role}) - Active: {user.is_active}")

    # Check for lauren.chen@example.com
    lauren = db.query(User).filter(User.email == "lauren.chen@example.com").first()
    if lauren:
        print(f"\n✅ Test user 'lauren.chen@example.com' exists!")
        print(f"   Role: {lauren.role}, Active: {lauren.is_active}")
    else:
        print(f"\n❌ Test user 'lauren.chen@example.com' NOT FOUND")
        print("   Available emails:")
        for user in users:
            print(f"     - {user.email}")

    db.close()


if __name__ == "__main__":
    main()
