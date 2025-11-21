"""
Script to create easy-to-remember demo users for testing.

All users have the same password: Passtest123

Run this after migrations to set up demo accounts.
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


def create_demo_users():
    """Create easy demo users with consistent password."""
    db = SessionLocal()

    # Common password for all demo accounts
    common_password = "Passtest123"
    hashed_password = hash_password(common_password)

    demo_users = [
        {
            "email": "admin@example.com",
            "npi": "1111111111",
            "first_name": "Admin",
            "last_name": "User",
            "role": UserRole.ADMIN,
        },
        {
            "email": "delegate@example.com",
            "npi": "2222222222",
            "first_name": "Delegate",
            "last_name": "User",
            "role": UserRole.DELEGATE,
        },
        {
            "email": "provider@example.com",
            "npi": "3333333333",
            "first_name": "Provider",
            "last_name": "User",
            "role": UserRole.PROVIDER,
        },
    ]

    try:
        created_count = 0
        updated_count = 0

        for user_data in demo_users:
            email = user_data["email"]
            existing_user = db.query(User).filter(User.email == email).first()

            if not existing_user:
                # Create new user
                user = User(
                    id=uuid.uuid4(),
                    email=email,
                    npi=user_data["npi"],
                    hashed_password=hashed_password,
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    role=user_data["role"],
                    is_active=True,
                    is_verified=True,
                )
                db.add(user)
                created_count += 1
                print(f"[OK] Created {user_data['role'].value} user: {email}")
            else:
                # Update existing user's password and role
                existing_user.hashed_password = hashed_password
                existing_user.role = user_data["role"]
                existing_user.npi = user_data["npi"]
                existing_user.is_active = True
                existing_user.is_verified = True
                updated_count += 1
                print(f"[OK] Updated {user_data['role'].value} user: {email}")

        db.commit()

        print("\n" + "=" * 70)
        print("DEMO USER CREDENTIALS (All users have the same password)")
        print("=" * 70)
        print("")
        print("ADMIN USER:")
        print(f"  Email:    admin@example.com")
        print(f"  Password: Passtest123")
        print(f"  Role:     admin")
        print("")
        print("DELEGATE USER:")
        print(f"  Email:    delegate@example.com")
        print(f"  Password: Passtest123")
        print(f"  Role:     delegate")
        print("")
        print("PROVIDER USER:")
        print(f"  Email:    provider@example.com")
        print(f"  Password: Passtest123")
        print(f"  Role:     provider")
        print("")
        print("=" * 70)
        print(f"Summary: {created_count} created, {updated_count} updated")
        print("=" * 70)

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error creating demo users: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_demo_users()
