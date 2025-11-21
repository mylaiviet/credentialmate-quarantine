"""
Export comprehensive provider analysis to CSV
Generates a detailed CSV report of all providers and their related attributes.

Author: Claude Code
Date: 2025-11-18
"""

import csv
import json
from datetime import datetime
from sqlalchemy.orm import joinedload
from app.core.database import SessionLocal
from app.models.user import User
from app.models.provider import Provider, ProviderState, ProviderIdentifier, ProviderSetting, ProviderRole
from app.models.license import License
from app.models.dea_registration import DEARegistration
from app.models.board_certification import BoardCertification
from app.models.csr_certificate import CSRCertificate
from app.models.document import Document
from app.models.cme_tracking import CMECredit


def export_provider_analysis():
    """Export all provider data to CSV."""
    db = SessionLocal()

    try:
        # Query all providers with eager loading of relationships
        providers = db.query(Provider).options(
            joinedload(Provider.user),
            joinedload(Provider.states),
            joinedload(Provider.identifiers),
            joinedload(Provider.settings),
            joinedload(Provider.roles)
        ).all()

        print(f"Found {len(providers)} providers in database")

        # Prepare CSV data
        rows = []

        for provider in providers:
            # Get related data
            licenses = db.query(License).filter(
                License.provider_id == provider.id,
                License.is_deleted == False
            ).all()

            dea_regs = db.query(DEARegistration).filter(
                DEARegistration.provider_id == provider.id,
                DEARegistration.is_deleted == False
            ).all()

            board_certs = db.query(BoardCertification).filter(
                BoardCertification.provider_id == provider.id,
                BoardCertification.is_deleted == False
            ).all()

            csr_certs = db.query(CSRCertificate).filter(
                CSRCertificate.provider_id == provider.id,
                CSRCertificate.is_deleted == False
            ).all()

            documents = db.query(Document).filter(
                Document.provider_id == provider.id,
                Document.is_deleted == False
            ).all()

            cme_credits = db.query(CMECredit).filter(
                CMECredit.provider_id == provider.id
            ).all()

            # Build row data
            row = {
                # Provider Basic Info
                'provider_id': str(provider.id),
                'user_id': str(provider.user_id),
                'first_name': provider.first_name,
                'middle_name': provider.middle_name or '',
                'last_name': provider.last_name,
                'suffix': provider.suffix or '',
                'full_name': provider.full_name,
                'specialty': provider.specialty or '',

                # User Info
                'user_email': provider.user.email if provider.user else '',
                'user_is_active': provider.user.is_active if provider.user else False,
                'user_is_verified': provider.user.is_verified if provider.user else False,

                # Address
                'address': json.dumps(provider.address_json) if provider.address_json else '',

                # Provider States
                'states_count': len(provider.states),
                'states_list': ', '.join([ps.state for ps in provider.states]),
                'primary_state': next((ps.state for ps in provider.states if ps.is_primary), ''),

                # Identifiers
                'identifiers_count': len(provider.identifiers),
                'identifier_types': ', '.join([pi.id_type for pi in provider.identifiers]),

                # Settings
                'timezone': provider.settings.timezone if provider.settings else 'UTC',
                'prefers_list_view': provider.settings.prefers_list_view if provider.settings else True,
                'prefers_compact_view': provider.settings.prefers_compact_view if provider.settings else False,

                # Roles
                'roles': ', '.join([pr.role for pr in provider.roles]),

                # Medical Licenses
                'licenses_count': len(licenses),
                'license_states': ', '.join([lic.state for lic in licenses]),
                'license_numbers': ', '.join([lic.license_number for lic in licenses if lic.license_number]),
                'license_statuses': ', '.join([lic.status or 'unknown' for lic in licenses]),
                'license_types': ', '.join([lic.license_type or 'unknown' for lic in licenses]),
                'licenses_expiring_soon': sum(1 for lic in licenses if lic.expiration_date and (lic.expiration_date - datetime.utcnow().date()).days < 90),

                # DEA Registrations
                'dea_count': len(dea_regs),
                'dea_numbers': ', '.join([dea.registration_number for dea in dea_regs if dea.registration_number]),
                'dea_statuses': ', '.join([dea.status or 'unknown' for dea in dea_regs]),
                'dea_expiring_soon': sum(1 for dea in dea_regs if dea.expiration_date and (dea.expiration_date - datetime.utcnow().date()).days < 90),

                # Board Certifications
                'board_cert_count': len(board_certs),
                'board_cert_names': ', '.join([bc.certification_name for bc in board_certs if bc.certification_name]),
                'board_cert_statuses': ', '.join([bc.status or 'unknown' for bc in board_certs]),
                'board_cert_expiring_soon': sum(1 for bc in board_certs if bc.expiration_date and (bc.expiration_date - datetime.utcnow().date()).days < 90),

                # CSR Certificates
                'csr_count': len(csr_certs),
                'csr_states': ', '.join([csr.state for csr in csr_certs if csr.state]),
                'csr_statuses': ', '.join([csr.status or 'unknown' for csr in csr_certs]),
                'csr_expiring_soon': sum(1 for csr in csr_certs if csr.expiration_date and (csr.expiration_date - datetime.utcnow().date()).days < 90),

                # Documents
                'documents_count': len(documents),
                'document_types': ', '.join(list(set([doc.document_type for doc in documents if doc.document_type]))),
                'documents_pending_review': sum(1 for doc in documents if doc.review_status == 'pending'),
                'documents_reviewed': sum(1 for doc in documents if doc.review_status == 'reviewed'),

                # CME Credits
                'cme_credits_count': len(cme_credits),
                'cme_total_credits': sum(cme.credits_earned for cme in cme_credits if cme.credits_earned),
                'cme_category_1_credits': sum(cme.credits_earned for cme in cme_credits if cme.credits_earned and cme.category == 'category_1'),
                'cme_category_2_credits': sum(cme.credits_earned for cme in cme_credits if cme.credits_earned and cme.category == 'category_2'),

                # Audit Info
                'org_id': provider.org_id or '',
                'is_deleted': provider.is_deleted,
                'created_at': provider.created_at.isoformat() if provider.created_at else '',
                'updated_at': provider.updated_at.isoformat() if provider.updated_at else '',
            }

            rows.append(row)

        # Write to CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'provider_analysis_report_{timestamp}.csv'

        if rows:
            fieldnames = rows[0].keys()

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            print(f"\n✓ CSV report generated: {filename}")
            print(f"✓ Total providers: {len(rows)}")
            print(f"✓ Total columns: {len(fieldnames)}")

            # Print summary statistics
            print("\n=== SUMMARY STATISTICS ===")
            print(f"Total Providers: {len(rows)}")
            print(f"Total Licenses: {sum(row['licenses_count'] for row in rows)}")
            print(f"Total DEA Registrations: {sum(row['dea_count'] for row in rows)}")
            print(f"Total Board Certifications: {sum(row['board_cert_count'] for row in rows)}")
            print(f"Total CSR Certificates: {sum(row['csr_count'] for row in rows)}")
            print(f"Total Documents: {sum(row['documents_count'] for row in rows)}")
            print(f"Total CME Credits: {sum(row['cme_credits_count'] for row in rows)}")
            print(f"Total CME Hours: {sum(row['cme_total_credits'] for row in rows):.1f}")

            # State distribution
            all_states = []
            for row in rows:
                if row['states_list']:
                    all_states.extend(row['states_list'].split(', '))

            if all_states:
                from collections import Counter
                state_counts = Counter(all_states)
                print("\n=== STATE DISTRIBUTION ===")
                for state, count in state_counts.most_common(10):
                    print(f"{state}: {count} providers")

            # Specialty distribution
            specialties = [row['specialty'] for row in rows if row['specialty']]
            if specialties:
                from collections import Counter
                specialty_counts = Counter(specialties)
                print("\n=== SPECIALTY DISTRIBUTION ===")
                for specialty, count in specialty_counts.most_common(10):
                    print(f"{specialty}: {count} providers")

        else:
            print("No data to export")

        return filename

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    export_provider_analysis()