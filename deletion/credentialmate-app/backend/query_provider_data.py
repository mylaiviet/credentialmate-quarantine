#!/usr/bin/env python3
"""
Provider Data Query Script

Queries all user/provider data with associated licenses, credentials, and documents.
Each license/credential is a separate row (not rolled up).

Usage:
    python query_provider_data.py
    python query_provider_data.py --format csv
    python query_provider_data.py --format json
    python query_provider_data.py --output providers.csv
"""

import os
import sys
import json
import csv
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

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
        db_url = f"postgresql://credentialmate:{db_password}@localhost:5432/credentialmate"
    return db_url


def query_user_licenses(session) -> List[Dict[str, Any]]:
    """
    Query all users with their licenses (one row per license).

    Returns:
        List of dictionaries with user and license data
    """
    query = text("""
        SELECT
            -- User/Provider Info
            u.id as user_id,
            u.email,
            u.first_name,
            u.last_name,
            u.npi_encrypted as npi,
            u.role,
            u.is_active,
            u.is_verified,
            u.created_at as user_created_at,
            u.last_login,

            -- License Info
            l.id as license_id,
            l.state,
            l.license_number,
            l.license_type,
            l.issue_date,
            l.expiration_date,
            l.status as license_status,
            l.renewal_cycle_months,
            l.created_at as license_created_at,
            l.updated_at as license_updated_at,
            l.license_metadata

        FROM users u
        LEFT JOIN licenses l ON l.user_id = u.id

        ORDER BY u.last_name, u.first_name, l.state, l.license_number
    """)

    result = session.execute(query)
    rows = result.fetchall()

    # Convert to list of dicts
    columns = result.keys()
    return [dict(zip(columns, row)) for row in rows]


def query_user_cme(session) -> List[Dict[str, Any]]:
    """
    Query all users with their CME activities (one row per CME).

    Returns:
        List of dictionaries with user and CME data
    """
    query = text("""
        SELECT
            -- User/Provider Info
            u.id as user_id,
            u.email,
            u.first_name,
            u.last_name,
            u.npi_encrypted as npi,
            u.role,

            -- CME Info
            c.id as cme_id,
            c.title,
            c.credits,
            c.completion_date,
            c.activity_type,
            c.category,
            c.provider as cme_provider,
            c.state as cme_state,
            c.certificate_number,
            c.certificate_url,
            c.notes,
            c.compliance_status,
            c.created_at as cme_created_at,
            c.cme_metadata

        FROM users u
        LEFT JOIN cme_activities c ON c.user_id = u.id

        ORDER BY u.last_name, u.first_name, c.completion_date DESC
    """)

    result = session.execute(query)
    rows = result.fetchall()

    columns = result.keys()
    return [dict(zip(columns, row)) for row in rows]


def query_user_documents(session) -> List[Dict[str, Any]]:
    """
    Query all users with their uploaded documents (one row per document).

    Returns:
        List of dictionaries with user and document data
    """
    query = text("""
        SELECT
            -- User/Provider Info
            u.id as user_id,
            u.email,
            u.first_name,
            u.last_name,
            u.npi_encrypted as npi,

            -- Document Info
            d.id as document_id,
            d.document_type,
            d.document_status,
            d.original_filename,
            d.stored_filename,
            d.file_path,
            d.mime_type,
            d.file_size_bytes,
            d.uploaded_at,
            d.parsed_at,
            d.reviewed_at,
            d.confidence_score,
            d.parsing_method,
            d.validation_status,
            d.edit_count,
            d.extracted_data,
            d.ai_extracted_data,
            d.user_edited_data,
            d.created_at as document_created_at,
            d.document_metadata

        FROM users u
        LEFT JOIN documents d ON d.user_id = u.id

        ORDER BY u.last_name, u.first_name, d.uploaded_at DESC
    """)

    result = session.execute(query)
    rows = result.fetchall()

    columns = result.keys()
    return [dict(zip(columns, row)) for row in rows]


def query_user_summary(session) -> List[Dict[str, Any]]:
    """
    Query user summary with counts (one row per user).

    Returns:
        List of dictionaries with user summary data
    """
    query = text("""
        SELECT
            -- User/Provider Info
            u.id as user_id,
            u.email,
            u.first_name,
            u.last_name,
            u.npi_encrypted as npi,
            u.role,
            u.is_active,
            u.is_verified,
            u.created_at as user_created_at,
            u.last_login,

            -- Counts
            COUNT(DISTINCT l.id) as license_count,
            COUNT(DISTINCT c.id) as cme_count,
            COUNT(DISTINCT d.id) as document_count,

            -- License States (aggregated)
            STRING_AGG(DISTINCT l.state, ', ' ORDER BY l.state) as license_states,

            -- Total CME Credits
            COALESCE(SUM(c.credits), 0) as total_cme_credits

        FROM users u
        LEFT JOIN licenses l ON l.user_id = u.id
        LEFT JOIN cme_activities c ON c.user_id = u.id
        LEFT JOIN documents d ON d.user_id = u.id

        GROUP BY u.id, u.email, u.first_name, u.last_name, u.npi_encrypted,
                 u.role, u.is_active, u.is_verified, u.created_at, u.last_login

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


def export_to_csv(data: List[Dict[str, Any]], output_file: str):
    """Export data to CSV file"""
    if not data:
        print("No data to export")
        return

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()

        for row in data:
            # Serialize complex types
            serialized_row = {k: serialize_value(v) for k, v in row.items()}
            writer.writerow(serialized_row)

    print(f"✅ Exported {len(data)} rows to {output_file}")


def export_to_json(data: List[Dict[str, Any]], output_file: str):
    """Export data to JSON file"""
    # Serialize datetime objects
    serialized_data = []
    for row in data:
        serialized_row = {k: serialize_value(v) if isinstance(v, datetime) else v
                         for k, v in row.items()}
        serialized_data.append(serialized_row)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(serialized_data, f, indent=2, default=str)

    print(f"✅ Exported {len(data)} rows to {output_file}")


def print_table(data: List[Dict[str, Any]], max_rows: int = 50):
    """Print data as formatted table"""
    if not data:
        print("No data found")
        return

    # Print summary
    print(f"\n📊 Found {len(data)} rows\n")

    # Print first few rows
    display_data = data[:max_rows]

    for i, row in enumerate(display_data, 1):
        print(f"─── Row {i} ───")
        for key, value in row.items():
            if value is not None and value != "":
                # Truncate long JSON values
                if isinstance(value, (dict, str)) and len(str(value)) > 100:
                    print(f"  {key}: {str(value)[:100]}...")
                else:
                    print(f"  {key}: {value}")
        print()

    if len(data) > max_rows:
        print(f"... and {len(data) - max_rows} more rows")
        print(f"\nTip: Use --output to export all data to a file")


def main():
    parser = argparse.ArgumentParser(description='Query provider/user data from CredentialMate database')
    parser.add_argument(
        '--query',
        choices=['licenses', 'cme', 'documents', 'summary'],
        default='licenses',
        help='Type of query to run (default: licenses)'
    )
    parser.add_argument(
        '--format',
        choices=['table', 'csv', 'json'],
        default='table',
        help='Output format (default: table)'
    )
    parser.add_argument(
        '--output',
        help='Output file path (required for csv/json formats)'
    )
    parser.add_argument(
        '--max-rows',
        type=int,
        default=50,
        help='Maximum rows to display in table format (default: 50)'
    )

    args = parser.parse_args()

    # Validate output file for csv/json
    if args.format in ['csv', 'json'] and not args.output:
        parser.error(f"--output is required for {args.format} format")

    # Create database session
    try:
        db_url = get_database_url()
        engine = create_engine(db_url, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()

        print(f"🔍 Running query: {args.query}")
        print(f"📁 Database: {db_url.split('@')[1] if '@' in db_url else 'local'}")
        print()

        # Execute query based on type
        if args.query == 'licenses':
            data = query_user_licenses(session)
            print("📋 User Licenses (one row per license)")
        elif args.query == 'cme':
            data = query_user_cme(session)
            print("🎓 User CME Activities (one row per CME)")
        elif args.query == 'documents':
            data = query_user_documents(session)
            print("📄 User Documents (one row per document)")
        elif args.query == 'summary':
            data = query_user_summary(session)
            print("📊 User Summary (one row per user)")

        # Output data
        if args.format == 'csv':
            export_to_csv(data, args.output)
        elif args.format == 'json':
            export_to_json(data, args.output)
        else:
            print_table(data, max_rows=args.max_rows)

        session.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
