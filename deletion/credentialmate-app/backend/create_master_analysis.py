#!/usr/bin/env python3
"""
Create Master Provider Analysis CSV

Combines all provider data (summary, licenses, CME, documents) into a single
comprehensive CSV with one row per provider and aggregated attributes.

Author: Claude Code
Date: 2025-11-18
"""

import os
import sys
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def get_database_url() -> str:
    """Get database URL from environment or use default"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Default for docker environment
        db_password = os.getenv("DB_PASSWORD", "sHAw4kmnJefRRy3FtaawwDKFr/21gJFiM7sLbjbKTbQ=")
        db_url = f"postgresql://credentialmate:{db_password}@postgres:5432/credentialmate_dev"
    return db_url


def query_comprehensive_provider_data(session):
    """
    Query comprehensive provider data with all attributes.

    Returns one row per provider with aggregated license, CME, and document data.
    """
    query = text("""
        WITH license_agg AS (
            SELECT
                user_id,
                COUNT(*) as license_count,
                STRING_AGG(DISTINCT state, ', ' ORDER BY state) as license_states,
                STRING_AGG(DISTINCT license_type, ', ' ORDER BY license_type) as license_types,
                STRING_AGG(DISTINCT status::text, ', ' ORDER BY status::text) as license_statuses,
                STRING_AGG(license_number, ', ' ORDER BY license_number) as license_numbers,
                MIN(expiration_date) as earliest_expiration,
                MAX(expiration_date) as latest_expiration,
                STRING_AGG(
                    CASE
                        WHEN expiration_date < CURRENT_DATE THEN 'EXPIRED: ' || state || ' (' || expiration_date::text || ')'
                        WHEN expiration_date < CURRENT_DATE + INTERVAL '90 days' THEN 'EXPIRING: ' || state || ' (' || expiration_date::text || ')'
                        ELSE NULL
                    END,
                    ', '
                ) as expiration_alerts,
                COUNT(*) FILTER (WHERE status = 'active') as active_licenses,
                COUNT(*) FILTER (WHERE status = 'expired') as expired_licenses,
                COUNT(*) FILTER (WHERE expiration_date < CURRENT_DATE + INTERVAL '90 days') as expiring_soon_count
            FROM licenses
            GROUP BY user_id
        ),
        cme_agg AS (
            SELECT
                user_id,
                COUNT(*) as cme_activity_count,
                COALESCE(SUM(credits), 0) as total_cme_credits,
                COALESCE(SUM(CASE WHEN category = 'category_1' THEN credits ELSE 0 END), 0) as cat1_credits,
                COALESCE(SUM(CASE WHEN category = 'category_2' THEN credits ELSE 0 END), 0) as cat2_credits,
                STRING_AGG(DISTINCT activity_type, ', ' ORDER BY activity_type) as cme_activity_types,
                STRING_AGG(DISTINCT state, ', ' ORDER BY state) as cme_states,
                MIN(completion_date) as earliest_cme_date,
                MAX(completion_date) as latest_cme_date,
                COUNT(DISTINCT EXTRACT(YEAR FROM completion_date)) as cme_years_covered
            FROM cme_activities
            GROUP BY user_id
        ),
        doc_agg AS (
            SELECT
                user_id,
                COUNT(*) as document_count,
                COUNT(*) FILTER (WHERE document_type = 'license') as license_docs,
                COUNT(*) FILTER (WHERE document_type = 'cme') as cme_docs,
                COUNT(*) FILTER (WHERE document_type = 'certification') as cert_docs,
                COUNT(*) FILTER (WHERE document_status = 'pending_review') as pending_docs,
                COUNT(*) FILTER (WHERE document_status = 'reviewed') as reviewed_docs,
                COUNT(*) FILTER (WHERE document_status = 'verified') as verified_docs,
                AVG(confidence_score) as avg_confidence_score,
                COUNT(*) FILTER (WHERE confidence_score >= 0.95) as high_confidence_docs,
                COUNT(*) FILTER (WHERE confidence_score < 0.80) as low_confidence_docs,
                STRING_AGG(DISTINCT document_type, ', ' ORDER BY document_type) as document_types,
                MAX(uploaded_at) as last_document_upload
            FROM documents
            GROUP BY user_id
        ),
        cme_credits_agg AS (
            SELECT
                user_id,
                COUNT(*) as cme_credit_entries,
                COALESCE(SUM(credits_earned), 0) as total_credits_earned,
                STRING_AGG(DISTINCT state, ', ' ORDER BY state) as cme_credit_states
            FROM cme_credits
            GROUP BY user_id
        )
        SELECT
            -- User Basic Info
            u.id as user_id,
            u.email,
            u.first_name,
            u.last_name,
            u.first_name || ' ' || u.last_name as full_name,
            u.npi_encrypted as npi,
            u.role,
            u.is_active,
            u.is_verified,
            u.created_at as user_created_at,
            u.last_login,
            u.user_metadata,

            -- License Summary
            COALESCE(l.license_count, 0) as license_count,
            l.license_states,
            l.license_types,
            l.license_statuses,
            l.license_numbers,
            l.earliest_expiration,
            l.latest_expiration,
            l.expiration_alerts,
            COALESCE(l.active_licenses, 0) as active_licenses,
            COALESCE(l.expired_licenses, 0) as expired_licenses,
            COALESCE(l.expiring_soon_count, 0) as licenses_expiring_soon,

            -- CME Activity Summary
            COALESCE(c.cme_activity_count, 0) as cme_activity_count,
            COALESCE(c.total_cme_credits, 0) as total_cme_credits,
            COALESCE(c.cat1_credits, 0) as category_1_credits,
            COALESCE(c.cat2_credits, 0) as category_2_credits,
            c.cme_activity_types,
            c.cme_states as cme_activity_states,
            c.earliest_cme_date,
            c.latest_cme_date,
            COALESCE(c.cme_years_covered, 0) as cme_years_covered,

            -- CME Credits Summary (from cme_credits table)
            COALESCE(cc.cme_credit_entries, 0) as cme_credit_entries,
            COALESCE(cc.total_credits_earned, 0) as total_credits_earned_alt,
            cc.cme_credit_states,

            -- Document Summary
            COALESCE(d.document_count, 0) as document_count,
            COALESCE(d.license_docs, 0) as license_documents,
            COALESCE(d.cme_docs, 0) as cme_documents,
            COALESCE(d.cert_docs, 0) as certification_documents,
            COALESCE(d.pending_docs, 0) as pending_review_docs,
            COALESCE(d.reviewed_docs, 0) as reviewed_docs,
            COALESCE(d.verified_docs, 0) as verified_docs,
            ROUND(COALESCE(d.avg_confidence_score, 0)::numeric, 3) as avg_document_confidence,
            COALESCE(d.high_confidence_docs, 0) as high_confidence_docs,
            COALESCE(d.low_confidence_docs, 0) as low_confidence_docs,
            d.document_types,
            d.last_document_upload,

            -- Compliance Status Indicators
            CASE
                WHEN l.expiring_soon_count > 0 THEN 'WARNING: ' || l.expiring_soon_count || ' license(s) expiring soon'
                WHEN l.expired_licenses > 0 THEN 'CRITICAL: ' || l.expired_licenses || ' expired license(s)'
                WHEN l.license_count = 0 THEN 'NO LICENSES'
                ELSE 'OK'
            END as license_compliance_status,

            CASE
                WHEN COALESCE(c.total_cme_credits, 0) = 0 THEN 'NO CME CREDITS'
                WHEN COALESCE(c.total_cme_credits, 0) < 10 THEN 'LOW CME CREDITS'
                ELSE 'OK'
            END as cme_compliance_status,

            CASE
                WHEN COALESCE(d.document_count, 0) = 0 THEN 'NO DOCUMENTS'
                WHEN COALESCE(d.pending_docs, 0) > 0 THEN 'PENDING REVIEW: ' || d.pending_docs || ' document(s)'
                ELSE 'OK'
            END as document_compliance_status

        FROM users u
        LEFT JOIN license_agg l ON l.user_id = u.id
        LEFT JOIN cme_agg c ON c.user_id = u.id
        LEFT JOIN doc_agg d ON d.user_id = u.id
        LEFT JOIN cme_credits_agg cc ON cc.user_id = u.id

        ORDER BY u.last_name, u.first_name
    """)

    result = session.execute(query)
    rows = result.fetchall()

    columns = result.keys()
    return [dict(zip(columns, row)) for row in rows]


def serialize_value(value):
    """Convert value to JSON-serializable format"""
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, (dict, list)):
        return json.dumps(value)
    elif value is None:
        return ""
    else:
        return str(value)


def main():
    """Generate comprehensive provider analysis CSV"""
    try:
        db_url = get_database_url()
        engine = create_engine(db_url, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()

        print("🔍 Querying comprehensive provider data...")
        data = query_comprehensive_provider_data(session)

        print(f"✅ Retrieved {len(data)} providers")

        # Export to CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'provider_master_analysis_{timestamp}.csv'

        if data:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()

                for row in data:
                    serialized_row = {k: serialize_value(v) for k, v in row.items()}
                    writer.writerow(serialized_row)

            print(f"✅ Exported comprehensive analysis to: {output_file}")
            print(f"📊 Total columns: {len(data[0].keys())}")

            # Print summary statistics
            print("\n" + "="*60)
            print("PROVIDER DATA SUMMARY")
            print("="*60)
            print(f"Total Providers: {len(data)}")
            print(f"Active Providers: {sum(1 for r in data if r['is_active'])}")
            print(f"Verified Providers: {sum(1 for r in data if r['is_verified'])}")
            print(f"\nTotal Licenses: {sum(r['license_count'] for r in data)}")
            print(f"Active Licenses: {sum(r['active_licenses'] for r in data)}")
            print(f"Expired Licenses: {sum(r['expired_licenses'] for r in data)}")
            print(f"Licenses Expiring Soon: {sum(r['licenses_expiring_soon'] for r in data)}")
            print(f"\nTotal CME Activities: {sum(r['cme_activity_count'] for r in data)}")
            print(f"Total CME Credits: {sum(r['total_cme_credits'] for r in data):.1f}")
            print(f"Total CME Credit Entries: {sum(r['cme_credit_entries'] for r in data)}")
            print(f"\nTotal Documents: {sum(r['document_count'] for r in data)}")
            print(f"Pending Review: {sum(r['pending_review_docs'] for r in data)}")
            print(f"Reviewed: {sum(r['reviewed_docs'] for r in data)}")
            print(f"Verified: {sum(r['verified_docs'] for r in data)}")

            # Compliance alerts
            license_warnings = sum(1 for r in data if 'WARNING' in r['license_compliance_status'])
            license_critical = sum(1 for r in data if 'CRITICAL' in r['license_compliance_status'])
            cme_warnings = sum(1 for r in data if r['cme_compliance_status'] != 'OK')
            doc_warnings = sum(1 for r in data if 'PENDING' in r['document_compliance_status'])

            print("\n" + "="*60)
            print("COMPLIANCE ALERTS")
            print("="*60)
            print(f"License Warnings: {license_warnings}")
            print(f"License Critical: {license_critical}")
            print(f"CME Warnings: {cme_warnings}")
            print(f"Document Warnings: {doc_warnings}")

            # State distribution
            all_states = []
            for row in data:
                if row['license_states']:
                    all_states.extend(str(row['license_states']).split(', '))

            if all_states:
                from collections import Counter
                state_counts = Counter(all_states)
                print("\n" + "="*60)
                print("TOP STATES BY LICENSE COUNT")
                print("="*60)
                for state, count in state_counts.most_common(10):
                    print(f"{state}: {count}")

            print("\n" + "="*60)
            print(f"✅ Full report saved to: {output_file}")
            print("="*60)

        else:
            print("❌ No data found")

        session.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
