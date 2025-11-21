"""
Link all Blueshift admins to ALL providers in the database.

This script ensures that every admin has delegation access to every provider,
including both seed data and manually created providers.
"""

import sys
import uuid
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.delegation import Delegation


def link_admins_to_all_providers():
    """Link all admins to all providers"""
    db = SessionLocal()

    try:
        print(f"\n{'='*70}")
        print(f"LINKING ADMINS TO ALL PROVIDERS")
        print(f"{'='*70}\n")

        # Get all admins
        admins = db.query(User).filter(User.role == UserRole.ADMIN).all()
        print(f"Found {len(admins)} admin users:")
        for admin in admins:
            print(f"  - {admin.email}")

        # Get all providers
        providers = db.query(User).filter(User.role == UserRole.PROVIDER).all()
        print(f"\nFound {len(providers)} provider users")

        # Admin permissions (full access)
        admin_permissions = [
            "view_licenses",
            "manage_cme",
            "upload_documents",
            "view_compliance",
            "receive_notifications",
        ]

        created_count = 0
        skipped_count = 0

        # Create delegations for each admin to every provider
        for admin in admins:
            for provider in providers:
                # Check if delegation already exists
                existing = (
                    db.query(Delegation)
                    .filter_by(provider_id=provider.id, delegate_email=admin.email)
                    .first()
                )

                if existing:
                    skipped_count += 1
                    continue

                # Create new delegation
                delegation = Delegation(
                    id=uuid.uuid4(),
                    provider_id=provider.id,
                    delegate_email=admin.email,
                    delegate_name=f"{admin.first_name} {admin.last_name}",
                    permissions=admin_permissions,
                    created_at=datetime.utcnow()
                    - timedelta(days=random.randint(90, 365)),
                )

                db.add(delegation)
                created_count += 1

            print(f"OK Linked {admin.email} to all {len(providers)} providers")

        db.commit()

        print(f"\n{'='*70}")
        print(f"SUMMARY")
        print(f"{'='*70}")
        print(f"Created: {created_count} new delegations")
        print(f"Skipped: {skipped_count} existing delegations")
        print(
            f"Total: {len(admins)} admins x {len(providers)} providers = {len(admins) * len(providers)} delegations"
        )
        print(f"{'='*70}\n")

        return True

    except Exception as e:
        db.rollback()
        print(f"\nERROR: {str(e)}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = link_admins_to_all_providers()
    sys.exit(0 if success else 1)
