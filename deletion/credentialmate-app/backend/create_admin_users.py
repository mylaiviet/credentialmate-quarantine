"""
Script to create admin and delegate test users.

Run this after migrations to set up test admin accounts.
"""

import sys
from pathlib import Path

# Add backend to path
BACKEND_DIR = Path(__file__).parent
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv

load_dotenv()

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password
import uuid


def create_admin_users():
    """Create admin and delegate test users."""
    db = SessionLocal()

    try:
        # Admin user
        admin_email = "admin@credentialmate.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()

        if not existing_admin:
            admin = User(
                id=uuid.uuid4(),
                email=admin_email,
                npi="9999999999",  # Special NPI for admin
                hashed_password=hash_password("Admin123!"),
                first_name="System",
                last_name="Administrator",
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True,
            )
            db.add(admin)
            print(f"[OK] Created admin user: {admin_email}")
        else:
            print(f"[INFO] Admin user already exists: {admin_email}")

        # Delegate user
        delegate_email = "delegate@credentialmate.com"
        existing_delegate = db.query(User).filter(User.email == delegate_email).first()

        if not existing_delegate:
            delegate = User(
                id=uuid.uuid4(),
                email=delegate_email,
                npi="8888888888",  # Special NPI for delegate
                hashed_password=hash_password("Delegate123!"),
                first_name="Office",
                last_name="Manager",
                role=UserRole.DELEGATE,
                is_active=True,
                is_verified=True,
            )
            db.add(delegate)
            print(f"[OK] Created delegate user: {delegate_email}")
        else:
            print(f"[INFO] Delegate user already exists: {delegate_email}")

        db.commit()

        print("\n" + "=" * 60)
        print("ADMIN CREDENTIALS")
        print("=" * 60)
        print(f"Email: admin@credentialmate.com")
        print(f"Password: Admin123!")
        print(f"Role: admin")
        print("")
        print("=" * 60)
        print("DELEGATE CREDENTIALS")
        print("=" * 60)
        print(f"Email: delegate@credentialmate.com")
        print(f"Password: Delegate123!")
        print(f"Role: delegate")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error creating admin users: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_users()
