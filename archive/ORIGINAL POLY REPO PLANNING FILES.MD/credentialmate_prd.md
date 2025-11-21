# **CredentialMate Product Requirements Document (PRD)**
## **Version 2.0 — Rebuilt Based on Uploaded Files**
## **Source Files Included:**
- credentialmate_master_summary_updated (2).md
- section_15_data_architecture.md
- section_21_notification_ux.md
- TECH-STACK-SUMMARY.md
- agentic_ai_chat_summary.md

---
# **1. PRODUCT VISION**
CredentialMate is a **healthcare‑grade, deterministic compliance platform** that ensures:
- Zero missed license renewals
- Zero CME gaps
- Zero expired DEA/CSR credentials
- Zero drift in compliance logic
- Zero PHI exposure to LLMs

CredentialMate becomes the **single source of truth** for:
- State licensing data
- CME history & category‑specific requirements
- DEA/CSR renewals
- Board certification tracking
- Multi‑state compliance merging

**Guiding Principles:**
- Deterministic logic in production
- AI‑assisted development only (never production)
- Immutable audit logging
- Zero‑trust architecture
- Fully versioned rules engine

---
# **2. USER ROLES & PERSONAS**
## **2.1 Providers**
Need: quick uploads, clear compliance status, proactive reminders.

## **2.2 Admins**
Need: org‑wide compliance monitoring, bulk messaging, risk dashboards.

## **2.3 SuperAdmins**
Need: audit oversight, troubleshooting, administrative corrections.

## **2.4 System Agents (Dev‑time only)**
- Backend agent
- Frontend agent
- DB agent
- Infra agent
- QA agent
- Governance agent

These follow the **5‑stage agent workflow** from agentic_ai_chat_summary.md.

---
# **3. PROBLEM STATEMENT**
Providers fall out of compliance because:
- Every state has unique renewal timelines
- CME categories differ by state
- DEA/CSR follow separate cycles
- Document storage is fragmented
- Organizations cannot track multiple states

CredentialMate centralizes and automates the entire workflow using deterministic compliance logic.

---
# **4. SCOPE (MVP)**
### **In Scope:**
- License upload & parsing
- CME upload & parsing
- DEA/CSR tracking
- Compliance engine
- Notification UX (Section 21)
- Messaging engine (Section 23)
- Provider dashboard
- Admin dashboard
- Audit logs (HIPAA 45 CFR 164.312)
- RLS enforcement (Section 15)

### **Out of Scope:**
- Mobile apps
- CME marketplace
- Automated state license applications
- Real‑time voice automation

---
# **5. CORE FEATURES**
## **5.1 Document Upload & Parsing**
Source: TECH‑STACK-SUMMARY.md + Section 15

Supports PDF, DOCX, PPTX, images. Pipeline:
1. Upload → S3
2. MIME detection
3. OCR (PyMuPDF, pytesseract)
4. Rigid schema extraction
5. Confidence scoring
6. Conversational fallback (Bedrock, dev‑time only)
7. Validation & normalization
8. Storage into RDS

## **5.2 Classification Engine**
Types:
- Medical license
- CME certificate
- DEA registration
- CSR credential
- Board certification
- Misc

## **5.3 Compliance Engine**
Uses deterministic rule packs from Section 17 & Section 15:
- Renewals (T‑90/60/30/7)
- CME categories (ethics, implicit bias, opioid, etc.)
- DEA/CSR cycle logic
- Multi‑state merges
- Org‑level scoring

## **5.4 Notification UX (Section 21)**
User‑facing reminders:
- License renewals
- CME gaps
- Document requests
- Multi‑state overlaps

Follows provider preferences (email, SMS, in‑app). Quiet hours enforced.

## **5.5 Messaging Engine (Section 23)**
Backend routing logic:
- SES emails
- Optional SNS/Twilio SMS
- In‑app notifications via WebSockets
- Template versioning
- Fallback logic (SMS → email → in‑app)
- Delivery tracking

## **5.6 Dashboards**
### Provider Dashboard:
- Renewal timeline
- CME checklist
- Notification feed
- Upload actions

### Admin Dashboard:
- Org compliance score
- Provider risk list
- Expiring licenses table
- Bulk messaging

## **5.7 Audit Logging**
From TECH‑STACK-SUMMARY.md (AuditLoggingMiddleware):
- Logs all PHI access
- Immutable
- Actor, IP, timestamp, resource
- Data lineage logging for all parsed content

## **5.8 Access Control (RLS)**
From Section 15:
- Provider → own data
- Admin → org data
- SuperAdmin → restricted full access
- Agents → dev‑time only, synthetic data

---
# **6. DETAILED USER WORKFLOWS**
## **6.1 Provider Onboarding**
1. Enter NPI → lookup
2. Confirm identity
3. Upload required documents
4. Set preferences
5. View compliance dashboard

## **6.2 Document Upload**
- Drag & drop
- Parser runs
- Confirm extracted metadata
- Stored with lineage

## **6.3 Notification Cycle**
Triggered by compliance engine:
- T‑90 → prepare
- T‑60 → action needed
- T‑30 → urgent
- T‑7 → final warning
- Day‑0 → expired

## **6.4 Admin Workflow**
- Review org score
- Filter risky providers
- Send reminders
- View multi‑state merges

---
# **7. NON‑FUNCTIONAL REQUIREMENTS**
## **Security**
- HIPAA / SOC2 alignment
- Zero‑trust VPC
- Encryption in transit + at rest
- PHI never leaves backend

## **Performance**
- API P95 < 200ms
- Parsing < 10s
- Notification pipeline < 1s dispatch

## **Scalability**
- ECS + RDS foundation
- Support 20 → 100+ daily users over 6 months

## **Determinism**
- Strict API contracts
- No AI in production
- Version‑locked rules

---
# **8. DATA REQUIREMENTS (Section 15)**
## **8.1 Schema Components**
- providers
- licenses
- cme_events
- dea_registrations
- csr_certificates
- credential_versions
- document_metadata
- compliance_windows
- notifications
- audit_logs
- change_events
- data_lineage

## **8.2 Data Flow**
Raw Document → OCR → Classification → Normalization → DB → Compliance Engine → Notification Engine → Dashboards

## **8.3 Data Governance**
- Immutable versioning
- No silent mutations
- All changes logged
- RLS enforced

---
# **9. TECHNICAL ARCHITECTURE SUMMARY**
Source: TECH‑STACK-SUMMARY.md

## **9.1 Frontend:**
- Next.js 14
- Tailwind + Radix
- React Query
- Dockerized

## **9.2 Backend:**
- FastAPI
- SQLAlchemy 2.0
- Pydantic v2
- AuditMiddleware
- Bedrock parsing (dev‑time)
- S3 storage
- SES notifications

## **9.3 Deployment Target:**
**ECS + RDS + VPC** (based on your scaling + HIPAA needs)
- ALB → ECS services
- Private subnets → backend + RDS
- Secrets Manager
- CloudWatch logs

## **9.4 Local Dev:**
- Docker Compose (frontend/backend/db)
- Prometheus/Grafana for metrics

---
# **10. INTEGRATIONS**
- AWS S3
- AWS SES
- AWS SNS/Twilio (optional)
- AWS Bedrock (dev‑time)
- NPI Registry

---
# **11. RISKS & MITIGATIONS**
## **11.1 Compliance Drift**
Mitigation: versioned rule packs.

## **11.2 Parsing Failures**
Mitigation: hybrid parser + confidence scoring.

## **11.3 Notification Delivery Failures**
Mitigation: routing fallback + retry logic.

## **11.4 Infrastructure Risk**
Mitigation: ECS + RDS baseline.

---
# **12. ANALYTICS & REPORTING**
- Compliance score
- CME status
- Multi‑state overlaps
- Delivery metrics
- Parsing confidence trends

---
# **13. TESTING REQUIREMENTS**
- Unit tests (backend/frontend)
- Parsing tests
- API contract tests
- RLS tests
- Drift detection tests
- Notification delivery tests

---
# **14. SUCCESS CRITERIA**
- Zero missed renewals
- >90% onboarding completion
- >95% notification delivery
- API P95 <200ms

---
# **15. ROADMAP**
## Phase 1:
- Uploads
- Parsing
- Compliance engine
- Provider dashboard

## Phase 2:
- Admin dashboard
- Notifications
- Multi‑state logic

## Phase 3:
- Org analytics
- Bulk messaging
- Advanced reports

---
# **END OF CREDENTIALMATE PRD v2.0**

