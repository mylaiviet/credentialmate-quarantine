"""
Verify and create users for batch credential upload.

This script checks if users exist and creates them if needed before bulk upload.

Usage:
    python verify_and_create_users.py

Author: Claude Code
Created: 2025-11-06
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv()

from sqlalchemy.orm import Session
from app.core.database import engine
from app.models.user import User, UserRole
from app.core.security import hash_password
from uuid import UUID


def get_or_create_user(
    db: Session,
    email: str,
    first_name: str,
    last_name: str,
    npi: str = None,
    role: UserRole = UserRole.PROVIDER,
) -> tuple[User, bool]:
    """
    Get existing user or create new user.

    Args:
        db: Database session
        email: User email
        first_name: First name
        last_name: Last name
        npi: NPI number (optional)
        role: User role (default: provider)

    Returns:
        Tuple of (User, created) where created is True if new user was created
    """
    # Check if user exists by email
    user = db.query(User).filter(User.email == email).first()

    if user:
        print(f"[OK] User exists: {user.full_name} ({user.email})")
        print(f"   ID: {user.id}")
        print(f"   NPI: {user.npi or 'Not set'}")
        print(f"   Role: {user.role.value}")
        return user, False

    # Create new user
    print(f"[NEW] Creating new user: {first_name} {last_name} ({email})")

    # Generate a temporary password (user will need to reset)
    temp_password = "TempPass123!"  # This is just for batch upload, user will reset

    user = User(
        email=email,
        hashed_password=hash_password(temp_password),
        first_name=first_name,
        last_name=last_name,
        npi=npi,
        role=role,
        is_active=True,
        is_verified=True,  # Mark as verified since we're creating them
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    print(f"[OK] User created: {user.full_name}")
    print(f"   ID: {user.id}")
    print(f"   NPI: {user.npi or 'Not set'}")
    print(f"   Role: {user.role.value}")
    print(f"   Temp password: {temp_password} (user should reset)")

    return user, True


def main():
    """Main verification and creation logic."""
    print("=" * 80)
    print("USER VERIFICATION & CREATION")
    print("=" * 80)
    print()

    # Create database session
    db = Session(engine)

    try:
        # 1. Tricia Nguyen (primary test user with 16 documents)
        print("1. Verifying Tricia Nguyen...")
        print("-" * 80)
        tricia, tricia_created = get_or_create_user(
            db=db,
            email="tricia.nguyen@example.com",
            first_name="Tricia",
            last_name="Nguyen",
            npi="1600000001",  # Unique NPI for testing
            role=UserRole.PROVIDER,
        )
        print()

        # 2. Training data providers (3 providers with ~57 documents)
        print("2. Verifying training data providers...")
        print("-" * 80)

        dalawari, dalawari_created = get_or_create_user(
            db=db,
            email="dalawari@example.com",
            first_name="Unknown",  # Will be updated from documents
            last_name="Dalawari MD",
            role=UserRole.PROVIDER,
        )
        print()

        hilliard, hilliard_created = get_or_create_user(
            db=db,
            email="hilliard@example.com",
            first_name="Unknown",
            last_name="Hilliard MD",
            role=UserRole.PROVIDER,
        )
        print()

        sehgal, sehgal_created = get_or_create_user(
            db=db,
            email="sehgal@example.com",
            first_name="Unknown",
            last_name="Sehgal MD",
            role=UserRole.PROVIDER,
        )
        print()

        # Summary
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total users checked: 4")
        print(
            f"Existing users: {4 - sum([tricia_created, dalawari_created, hilliard_created, sehgal_created])}"
        )
        print(
            f"New users created: {sum([tricia_created, dalawari_created, hilliard_created, sehgal_created])}"
        )
        print()

        print("User IDs for batch processing:")
        print(f"  Tricia Nguyen: {tricia.id}")
        print(f"  Dalawari MD:   {dalawari.id}")
        print(f"  Hilliard MD:   {hilliard.id}")
        print(f"  Sehgal MD:     {sehgal.id}")
        print()

        print("[OK] All users ready for batch upload")
        print("=" * 80)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
