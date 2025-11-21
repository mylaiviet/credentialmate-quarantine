#!/usr/bin/env python3
"""
Export User Management Tables

Exports all user-related tables including:
- users
- user_sessions
- user_actions
- delegations
- notification_settings
- password_reset_tokens
- token_blacklist
- login_lockout

Location: scripts/database_exports/export_user_management.py
"""

import requests
import os
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000/api"
EMAIL = "admin@blueshift.com"
PASSWORD = "BlueShift2024!"
EXPORT_DIR = "database_export/user_management"

# Tables to export
TABLES = [
    "users",
    "user_sessions",
    "user_actions",
    "delegations",
    "notification_settings",
    "password_reset_tokens",
    "token_blacklist",
    "login_lockout",
]

def export_tables():
    print("=" * 80)
    print("User Management Data Export")
    print("=" * 80)
    print()

    # Create export directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = os.path.join(EXPORT_DIR, timestamp)
    os.makedirs(export_path, exist_ok=True)

    # Login
    print("🔐 Logging in...")
    login_response = requests.post(
        f"{API_BASE}/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in")
    print()

    # Export each table
    for i, table_name in enumerate(TABLES, 1):
        print(f"[{i}/{len(TABLES)}] Exporting {table_name}...", end=" ")

        try:
            response = requests.get(
                f"{API_BASE}/admin/database/tables/{table_name}/export/csv",
                headers=headers
            )
            response.raise_for_status()

            filepath = os.path.join(export_path, f"{table_name}.csv")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(response.text)

            print(f"✅ ({len(response.text.splitlines())-1} rows)")
        except Exception as e:
            print(f"❌ {e}")

    print()
    print(f"📁 Files saved to: {os.path.abspath(export_path)}")

if __name__ == "__main__":
    export_tables()
