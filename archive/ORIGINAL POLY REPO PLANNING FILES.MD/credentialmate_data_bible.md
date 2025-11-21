# **CredentialMate Data Layer Document (The Data Bible)**
## **Version 2.0 — Full Rebuild With Expanded Schema, Jobs, Lineage, Governance, and RLS**
## **Sources Incorporated:**
- section_15_data_architecture.md
- section_15.11 RLS model
- credentialmate_master_summary_updated
- TECH-STACK-SUMMARY.md
- section_21_notification_ux.md
- All lineage + audit logging rules (HIPAA 164.312)

---
# **1. PURPOSE OF THIS DOCUMENT**
The CredentialMate **Data Bible** defines *everything related to data* inside the platform. It is the authoritative reference for:
- Database schema and relationships
- Document → data lineage
- RLS (Row-Level Security) rules
- Compliance engine data inputs/outputs
- Audit logging
- Notification logging
- Versioning
- Integration logging
- Data governance policies
- Data retention strategy
- Data moat strategy (CredentialMate’s long-term defensibility)

This document is binding for all engineering, product, infra, and AI agents.

---
# **2. DATA ARCHITECTURE OVERVIEW**
CredentialMate uses a **document-centric, deterministic compliance architecture** based on:
- **PostgreSQL 15 (AWS RDS)**
- **Field-level encryption** (PII/PHI)
- **RLS enforcement** across all identity-bound tables
- **Immutable audit logs**
- **Versioned credentials + versioned rule packs**
- **Document-lineage-first design** (ALL facts must map back to uploaded artifacts)
- **S3 document storage** with versioning + server-side encryption

### **High-Level Data Flow**
```
Raw Document → OCR → Classification → Normalization → RDS → Compliance Engine → Notification Engine → Dashboards
```

### **Core Data Domains**
1. Provider Identity
2. Organization data
3. License & Credential data
4. DEA / CSR domain
5. CME domain
6. Regulatory rules domain
7. Compliance engine domain
8. Document & metadata domain
9. Notification domain
10. Audit & lineage domain
11. System metadata
12. Job processing domain

---
# **3. FULL DATABASE SCHEMA (v2.0)**
This includes all improvements approved earlier: identifiers, parsing jobs, integration logs, email events, bulk jobs, provider state mapping, extended lineage, and rule execution logging.

---
## **3.1 PROVIDER DOMAIN**
### **providers**
- id (uuid)
- npi (encrypted)
- first_name
- last_name
- email (encrypted)
- phone (encrypted)
- date_of_birth (encrypted)
- address_json (jsonb)
- created_at
- updated_at
- org_id (fk → organizations)

### **provider_identifiers (NEW)**
Unifies identifiers across systems.
- id
- provider_id
- id_type (npi, dea, csr, board_cert, state_system, other)
- id_value (encrypted)
- source (parsed, manual, external_api)
- created_at

### **provider_roles**
- provider_id
- role (provider, admin, superadmin)
- created_at

### **provider_settings (NEW)**
- provider_id
- timezone
- prefers_list_view
- prefers_compact_view
- created_at
- updated_at

### **provider_states (NEW)**
- id
- provider_id
- state
- created_at

---
## **3.2 ORGANIZATION DOMAIN**
### **organizations**
- id
- name
- timezone
- created_at

---
## **3.3 LICENSE DOMAIN**
### **licenses**
- id
- provider_id
- state
- license_number
- status
- issue_date
- expiration_date
- credential_version_id
- extracted_from_doc_id
- created_at
- updated_at

### **dea_registrations**
- id
- provider_id
- registration_number
- schedules (jsonb)
- expiration_date
- extracted_from_doc_id
- created_at
- updated_at

### **csr_certificates**
- id
- provider_id
- state
- csr_number
- expiration_date
- extracted_from_doc_id
- created_at
- updated_at

### **board_certifications**
- id
- provider_id
- specialty
- board_name
- expiration_date
- extracted_from_doc_id
- created_at

---
## **3.4 CME DOMAIN**
### **cme_events**
- id
- provider_id
- title
- category
- credits_earned
- completion_date
- expiration_date
- extracted_from_doc_id
- created_at

### **cme_categories_required**
- id
- state
- cycle_length_months
- category
- credits_required
- rule_version_id

---
## **3.5 COMPLIANCE DOMAIN**
### **compliance_windows**
- id
- provider_id
- license_id (nullable)
- cme_window_start
- cme_window_end
- next_renewal_date
- days_until_due
- compliance_status
- rule_version_id
- created_at
- updated_at

### **compliance_gap_analysis**
- id
- provider_id
- gap_type
- description
- severity
- rule_version_id
- created_at

### **rules_execution_log (NEW)**
Tracks rule evaluations.
- id
- provider_id
- rule_version_id
- rule_type
- inputs_json
- outputs_json
- executed_at

---
## **3.6 DOCUMENT & PARSING DOMAIN**
### **documents**
- id
- provider_id
- s3_uri
- file_type
- sha256_hash
- uploaded_at
- uploaded_by

### **document_metadata**
- id
- document_id
- key
- value
- confidence_score
- extraction_method
- created_at

### **document_lineage**
- id
- document_id
- table_name
- column_name
- row_id
- created_at

### **parsing_jobs (NEW)**
- id
- document_id
- provider_id
- status
- started_at
- completed_at
- duration_ms
- parser_type
- confidence_score
- error_message

### **credential_confidence_audit (NEW)**
- id
- provider_id
- document_id
- category
- confidence_score
- parser_used
- created_at

---
## **3.7 VERSIONING DOMAIN**
### **credential_versions**
- id
- provider_id
- entity_type
- entity_id
- version_number
- diff_json
- created_at

---
## **3.8 NOTIFICATION DOMAIN**
### **notification_preferences**
- id
- provider_id
- channel_email_enabled
- channel_sms_enabled
- channel_voice_enabled
- quiet_hours_json
- timezone
- created_at

### **notifications_sent**
- id
- provider_id
- channel
- type
- template_version
- sent_at
- delivered
- opened
- clicked
- retry_count
- failure_reason

### **email_events (NEW)**
- id
- notification_id
- provider_id
- event_type
- timestamp
- metadata_json

### **bulk_message_jobs (NEW)**
- id
- admin_id
- org_id
- criteria_json
- message_template_id
- recipients_count
- sent_count
- failed_count
- created_at

---
## **3.9 AUDIT & INTEGRATION DOMAIN**
### **audit_logs**
- id
- actor_id
- actor_role
- action
- resource
- resource_id
- ip
- user_agent
- timestamp
- status
- metadata_json

### **change_events**
- id
- table_name
- row_id
- change_type
- previous_value
- new_value
- actor_id
- created_at

### **integration_logs (NEW)**
- id
- provider_id
- integration_name
- request_json
- response_json
- status
- timestamp

---
## **3.10 SYSTEM DOMAIN**
### **rule_versions**
- id
- rule_type
- version_number
- rule_json
- created_at

### **system_settings**
- key
- value
- updated_at

---
# **4. DATA FLOW DIAGRAM**
```
Raw → OCR → Classification → Parsing Job → Normalization → RDS → Compliance → Notifications → Dashboards
```

---
# **5. DATA MOAT STRATEGY**
- High-fidelity S3 document archive
- Immutable lineage mapping
- Versioned rules + versioned credentials
- Longitudinal multi-year provider history
- Regulatory dataset library
- Analytics from rules engine + parsing engine
- Synthetic datasets for AI development

---
# **6. ROW LEVEL SECURITY (RLS)**
### Roles
- provider: only their data
- admin: org data
- superadmin: all data, restricted writes
- agent: synthetic data only

### Session Variables
- app.current_provider_id
- app.current_org_id
- app.current_role

### Policies
(Examples preserved from prior version.)

---
# **7. DATA GOVERNANCE**
- Immutable tables: audit_logs, document_lineage, credential_versions
- No silent mutations (all writes → change_events)
- API-only data writes
- Versioned rule packs
- Versioned templates
- Agents cannot touch production data

---
# **8. COMPLIANCE ALIGNMENT**
- HIPAA 164.312 logging + access control
- SOC2 security, availability, confidentiality principles

---
# **9. DATA RETENTION**
- Documents: indefinitely
- Credentials: indefinitely
- Notifications: 7 yrs
- Audit logs: 7 yrs
- Change events: 7 yrs

---

