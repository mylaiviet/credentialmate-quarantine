# TIMESTAMP: 2025-11-20T20:39:15Z
# CLASSIFICATION: SOC2 Type II - User Documentation
# COMPLIANCE: HIPAA, SOC2
# ORIGIN: credentialmate-app
# PURPOSE: Repository documentation and quick start guide

# Database Export Scripts

This directory contains categorized export scripts for different parts of the CredentialMate database.

## Location

```
c:\CREDENTIALMATE-REBUILD\credentialmate\credentialmate-app\scripts\database_exports\
```

## Available Scripts

### 1. User Management Data
**Script:** `export_user_management.py`

**Tables:**
- users
- user_sessions
- user_actions
- delegations
- notification_settings
- password_reset_tokens
- token_blacklist
- login_lockout

**Use Case:** User account analysis, session tracking, delegation management

**Run:**
```bash
python scripts/database_exports/export_user_management.py
```

---

### 2. Credentials & Licensing
**Script:** `export_credentials.py`

**Tables:**
- providers
- licenses
- cme_activities
- state_cme_base_requirements
- content_specific_cme
- exemption_equivalents
- special_population_requirements
- state_board_contacts
- board_certifications
- dea_registrations
- csr_certificates
- documents

**Use Case:** License tracking, CME compliance, provider credentials

**Run:**
```bash
python scripts/database_exports/export_credentials.py
```

---

### 3. Compliance & Audit
**Script:** `export_compliance_audit.py`

**Tables:**
- audit_logs
- change_events
- keystroke_logs
- notification_queue

**Use Case:** HIPAA compliance, audit trails, notification tracking

**Run:**
```bash
python scripts/database_exports/export_compliance_audit.py
```

---

### 4. Tracking & Events
**Script:** `export_tracking_events.py`

**Tables:**
- events (Phase 1)
- user_actions (Phase 2)
- user_sessions (Phase 2)
- ai_actions (Phase 3)
- developer_events (Phase 3)

**Use Case:** User behavior analysis, AI tracking, developer activity monitoring

**Run:**
```bash
python scripts/database_exports/export_tracking_events.py
```

---

### 5. RIS & System
**Script:** `export_ris_system.py`

**Tables:**
- file_registry
- file_metadata
- file_dependencies
- file_history_events
- file_history_events_y2025m11
- alembic_version

**Use Case:** Repository intelligence, file dependency analysis, system metadata

**Run:**
```bash
python scripts/database_exports/export_ris_system.py
```

---

## All Tables at Once

**Script:** `../export_all_tables.py` (in project root)

Exports all 41 tables in one go.

**Run:**
```bash
python export_all_tables.py
```

---

## Output Structure

Each script creates timestamped directories:

```
database_export/
├── user_management/
│   └── 20251118_123456/
│       ├── users.csv
│       ├── user_sessions.csv
│       └── ...
├── credentials/
│   └── 20251118_123456/
│       ├── providers.csv
│       ├── licenses.csv
│       └── ...
├── compliance_audit/
├── tracking_events/
└── ris_system/
```

---

## Common Use Cases

### Monthly Compliance Report
```bash
python scripts/database_exports/export_compliance_audit.py
python scripts/database_exports/export_credentials.py
```

### User Activity Analysis
```bash
python scripts/database_exports/export_user_management.py
python scripts/database_exports/export_tracking_events.py
```

### Full Database Backup
```bash
python export_all_tables.py
```

---

## Requirements

- Python 3.7+
- `requests` library (`pip install requests`)
- Running CredentialMate backend (http://localhost:8000)
- Admin credentials

---

## Troubleshooting

**Connection Error:**
```bash
# Check if backend is running
docker ps | grep credentialmate-backend
```

**Login Failed:**
- Verify credentials in script (EMAIL, PASSWORD)
- Ensure admin account exists

**Permission Denied:**
- Check file/directory permissions
- Ensure output directory is writable

---

## Customization

To export specific tables, edit the `TABLES` list in any script:

```python
TABLES = [
    "users",
    "licenses",
    # Add or remove tables as needed
]
```

---

## Security Note

⚠️ **Important:**
- CSV files may contain PHI/PII data
- Handle exports according to HIPAA guidelines
- Do not commit CSV files to version control
- Store exports securely and delete when no longer needed

---

## Support

For issues or questions, see the main [DATABASE_API_USAGE_GUIDE.md](../../DATABASE_API_USAGE_GUIDE.md)
