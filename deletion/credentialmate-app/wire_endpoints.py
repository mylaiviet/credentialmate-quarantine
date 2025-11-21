#!/usr/bin/env python3
"""
Script to wire all remaining 501 endpoints to their service calls.
M2-T3 Backend Implementation - Final Wiring Phase
"""

import re
import os

# Define the routers and their service mappings
ROUTER_MAPPINGS = {
    "providers.py": {
        "service_class": "ProviderService",
        "service_import": "from app.services.provider_service import ProviderService",
    },
    "licenses.py": {
        "service_class": "LicenseService",
        "service_import": "from app.services.license_service import LicenseService",
    },
    "cme.py": {
        "service_class": "CMEService",
        "service_import": "from app.services.cme_service import CMEService",
    },
    "documents.py": {
        "service_class": "DocumentService",
        "service_import": "from app.services.document_service import DocumentService",
    },
}

def uncomment_service_import(content, service_import):
    """Uncomment the service import if it's commented out."""
    commented_import = f"    # {service_import}"
    if commented_import in content:
        content = content.replace(commented_import, service_import)
    elif service_import not in content:
        # Add the import after the schema imports
        # Find the last 'from app.schemas' import
        lines = content.split('\n')
        last_schema_import_idx = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('from app.schemas'):
                last_schema_import_idx = i

        if last_schema_import_idx >= 0:
            lines.insert(last_schema_import_idx + 1, service_import)
            content = '\n'.join(lines)

    return content

def wire_router(router_path, service_class, service_import):
    """Wire all 501 endpoints in a router to service calls."""
    print(f"\nProcessing {router_path}...")

    with open(router_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Uncomment or add service import
    content = uncomment_service_import(content, service_import)

    # Replace all 501 HTTP_NOT_IMPLEMENTED errors with service instantiation
    # Pattern: raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, ...)
    # Replace with: service = ServiceClass(db) followed by appropriate service call

    # For now, let's just replace the 501 errors with a placeholder that indicates
    # the service should be called. The actual implementation depends on the endpoint.
    pattern = r'raise HTTPException\(\s*status_code=status\.HTTP_501_NOT_IMPLEMENTED,\s*detail="([^"]+)"\s*\)'

    def replacer(match):
        detail = match.group(1)
        return f'# TODO: Wire service call - {detail}\n    service = {service_class}(db)\n    raise HTTPException(\n        status_code=status.HTTP_501_NOT_IMPLEMENTED,\n        detail="{detail} (SERVICE READY - NEEDS WIRING)"\n    )'

    content = re.sub(pattern, replacer, content)

    # Write back
    with open(router_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Updated {router_path}")

    # Count remaining 501s
    remaining_501s = len(re.findall(r'HTTP_501_NOT_IMPLEMENTED', content))
    print(f"  Remaining 501 endpoints: {remaining_501s}")

def main():
    """Main function to wire all routers."""
    base_path = r"c:\CREDENTIALMATE-REBUILD\credentialmate\credentialmate-app\backend\app\routers\v2"

    print("=" * 60)
    print("M2-T3 Endpoint Wiring Tool")
    print("=" * 60)

    for router_file, config in ROUTER_MAPPINGS.items():
        router_path = os.path.join(base_path, router_file)
        if os.path.exists(router_path):
            wire_router(
                router_path,
                config["service_class"],
                config["service_import"]
            )
        else:
            print(f"✗ Router not found: {router_path}")

    print("\n" + "=" * 60)
    print("Phase 1 Complete: Service imports added and 501s marked")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Manually wire each endpoint to its service method")
    print("2. Test each endpoint")
    print("3. Remove all HTTP_501_NOT_IMPLEMENTED errors")

if __name__ == "__main__":
    main()
