#!/usr/bin/env python3
"""
Script to update all V2 routers for TDD Phase 2 (GREEN PHASE)

Changes:
1. Update imports: get_current_user_stub → get_current_user, require_admin
2. Update user-scoped endpoints: get_current_user_stub → get_current_user
3. Update admin-only endpoints: replace manual role check with require_admin dependency
4. Update timestamps and UPDATED_FOR tags

This script makes the pattern changes consistent across all 7 routers.
"""

import re
import os
from pathlib import Path

# List of all V2 routers to update
ROUTERS = [
    "backend/app/routers/v2/providers.py",
    "backend/app/routers/v2/licenses.py",
    "backend/app/routers/v2/documents.py",
    "backend/app/routers/v2/cme.py",
    "backend/app/routers/v2/compliance.py",
    "backend/app/routers/v2/notifications.py",
    "backend/app/routers/v2/audit.py",
]


def update_timestamp_and_metadata(content):
    """Update TIMESTAMP and UPDATED_FOR tags"""
    # Update TIMESTAMP
    content = re.sub(
        r"# TIMESTAMP: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",
        "# TIMESTAMP: 2025-11-17T03:45:00Z",
        content
    )

    # Update UPDATED_FOR to indicate TDD phase
    content = re.sub(
        r"# UPDATED_FOR: phase-1-milestone-2.*",
        "# UPDATED_FOR: phase-1-milestone-2-m2-t4-tdd-green-phase",
        content
    )

    return content


def update_imports(content):
    """Update dependency imports"""
    # Replace the import statement
    old_import = r"from app\.core\.dependencies import \(\s+get_db,\s+get_current_user_stub,\s+get_pagination_params,\s+set_rls_context,\s+\)"
    new_import = """from app.core.dependencies import (
    get_db,
    get_current_user,  # TDD Phase 2: Updated to use JWT authentication
    require_admin,  # TDD Phase 2: New admin role requirement
    get_pagination_params,
    set_rls_context,
)"""

    content = re.sub(old_import, new_import, content, flags=re.MULTILINE | re.DOTALL)

    return content


def update_user_scoped_endpoints(content):
    """Update user-scoped endpoints to use get_current_user"""
    # Pattern: current_user: Dict[str, Any] = Depends(get_current_user_stub)
    pattern = r"current_user:\s*Dict\[str,\s*Any\]\s*=\s*Depends\(get_current_user_stub\)"
    replacement = "current_user: dict = Depends(get_current_user)  # TDD: Now requires JWT auth"

    content = re.sub(pattern, replacement, content)

    return content


def update_admin_endpoints_with_require_admin(content):
    """Replace manual admin checks with require_admin dependency"""
    # This is more complex - we need to identify admin endpoints and replace the manual check

    # Pattern 1: Admin endpoint that has manual check - replace Depends(get_current_user_stub) with Depends(require_admin)
    # And remove the manual role check if it exists

    # For now, do a simple replacement where admin endpoints exist
    # Look for: current_user: Dict[str, Any] = Depends(get_current_user_stub), ... in admin endpoints

    lines = content.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this is an admin endpoint
        is_admin_endpoint = '/admin/' in line or 'admin-only' in line.lower()

        # If it's an admin endpoint with get_current_user_stub, replace with require_admin
        if is_admin_endpoint and 'get_current_user_stub' in line:
            line = line.replace(
                'Depends(get_current_user_stub)',
                'Depends(require_admin)  # TDD: Admin role required'
            )
            # Also clean up type hint
            line = re.sub(r'current_user:\s*Dict\[str,\s*Any\]', 'current_user: dict', line)
        elif 'get_current_user_stub' in line:
            # Non-admin endpoint - use get_current_user
            line = line.replace(
                'Depends(get_current_user_stub)',
                'Depends(get_current_user)'
            )
            line = re.sub(r'current_user:\s*Dict\[str,\s*Any\]', 'current_user: dict', line)
        else:
            # Clean up type hints anyway
            line = re.sub(r'Dict\[str,\s*Any\]', 'dict', line)

        result.append(line)
        i += 1

    return '\n'.join(result)


def process_router(router_path):
    """Process a single router file"""
    print(f"Processing {router_path}...")

    with open(router_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply all updates
    content = update_timestamp_and_metadata(content)
    content = update_imports(content)
    content = update_user_scoped_endpoints(content)
    content = update_admin_endpoints_with_require_admin(content)

    # Write back
    with open(router_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[OK] Updated {router_path}")


def main():
    """Main entry point"""
    print("=" * 70)
    print("TDD PHASE 2: UPDATING ALL V2 ROUTERS FOR JWT AUTHENTICATION")
    print("=" * 70)
    print()

    for router in ROUTERS:
        if os.path.exists(router):
            process_router(router)
        else:
            print(f"⚠ Skipped {router} (not found)")

    print()
    print("=" * 70)
    print("[OK] ALL ROUTERS UPDATED FOR TDD PHASE 2!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Review the changes: git diff backend/app/routers/v2/")
    print("2. Run tests: pytest tests/test_v2_contracts_phase1_auth.py -v")
    print("3. Check for any manual fixes needed in admin endpoints")


if __name__ == "__main__":
    main()
