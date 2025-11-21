# TIMESTAMP: {{UTC_ISO8601}}
# ORIGIN: credentialmate-quarantine
# UPDATED_FOR: credentialmate-quarantine
# PURPOSE: Quarantine workspace specification and governance
# VERSION: v1.0

## Overview
The quarantine repository stores non-runtime files removed from CredentialMate application repos during cleanup waves. It preserves provenance, supports SOC2 change control, and allows manual review before deletion or archival.

## Directory Structure
- deletion/: files approved for future deletion
- archive/: deprecated files retained for long-term reference
- needs-review/: files requiring human review before disposition
- manifests/provenance/: provenance logs and chain-of-custody records
- metadata/: governance documentation and operational logs

## Retention and Compliance
- Supports SOC2 CC8.1 (change control), CC6.6 (audit logging)
- Supports HIPAA 164.308(a)(1) (security management)
- No secrets or runtime code stored
- All file movements logged in operations_log.csv and provenance logs

## Workflow
1. Claire generates a cleanup plan in credentialmate-ai.
2. Execution moves files from source repos to this quarantine repo.
3. Each move is logged with:
   - timestamp
   - operator
   - source repo and path
   - destination folder
   - justification
4. Provenance logs capture file hash, source commit, and review status.

## Required Metadata Files
- metadata/operations_log.csv  
  Columns: timestamp,operation,source_repo,file_path,destination_folder,operator,justification,soc2_control

- manifests/provenance/file_provenance_log.csv  
  Columns: timestamp,file_hash,original_path,source_repo,source_commit,quarantine_folder,review_status,reviewer
