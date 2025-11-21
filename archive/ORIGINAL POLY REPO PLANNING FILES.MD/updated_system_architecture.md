# CredentialMate System Architecture Document (SAD)
# Version 1.1 — Fully Integrated With Governance, Roles, and Multi-Repo Model

This updated SAD integrates:
- Product / Project / Program governance roles
- ChatGPT PM orchestration model
- Claire Delegation Framework
- Local CSV-based PM workflow (SOC2)
- Multi-repo architecture alignment
- Timestamp + ORIGIN/UPDATED_FOR tagging
- AI governance and lane boundaries

This is now the authoritative architectural view for the entire CredentialMate platform.

---
# 1. PURPOSE OF THIS DOCUMENT
The System Architecture Document (SAD) defines the **technical, operational, orchestration, governance, and compliance architecture** for CredentialMate.

It describes:
- System components
- Data flows
- Agent orchestration flows
- Repo interactions
- AWS infrastructure
- Networking & security
- Observability
- Execution boundaries
- Multi-repo lifecycle
- SOC2/HIPAA constraints

This document guides engineers, auditors, operations, and AI agents.

---
# 2. HIGH-LEVEL SYSTEM OVERVIEW
CredentialMate is a **document-driven compliance platform** deployed on an ECS + RDS HIPAA-grade stack.

### Core traits:
- Deterministic backend logic (NO AI in prod)
- Stateless compute layer (Fargate)
- Versioned S3 document storage
- Full audit logging
- Zero-trust VPC
- Multi-repo isolation
- Versioned rule packs
- Versioned templates
- Versioned schemas

---
# 3. ORCHESTRATION LAYER (NEW — REQUIRED)
The CredentialMate system includes three governance + orchestration layers sitting **above all engineering components**.

## 3.1 Product Management (Human — WHAT & WHY)
- Owns vision & feature scope.
- Defines acceptance criteria.
- Approves any scope or repo-boundary change.

## 3.2 Project Management (ChatGPT PM — HOW & WHEN)
- Converts product goals → tasks.
- Generates Claire prompts.
- Reviews Claire summaries.
- Produces **CSV logs** (planned + completed tasks).
- Ensures SOC2 timestamping + ORIGIN/UPDATED_FOR tagging.

## 3.3 Program Management (ChatGPT + Human — ALIGNMENT)
- Ensures all 7 repos remain synchronized.
- Maintains architectural coherence.
- Oversees phase transitions.
- Ensures drift-free system evolution.

## 3.4 Claire (Master Executor)
- Enforces lane boundaries.
- Delegates to backend/frontend/infra/rules/etc.
- Executes only deterministic tasks.
- Returns a single optimized summary.

---
# 4. MULTI-REPO ARCHITECTURE (REINFORCED)
CredentialMate uses **7 hard-bounded repos**:
1. credentialmate-app
2. credentialmate-infra
3. credentialmate-rules
4. credentialmate-notification
5. credentialmate-ai
6. credentialmate-schemas
7. credentialmate-docs

Repos communicate only through:
- API (OpenAPI)
- versioned rule packs
- versioned schema snapshots
- versioned templates
- GitHub artifacts

No shared code.
No cross-repo mutations.
Human approval required for any boundary modification.

---
# 5. SYSTEM COMPONENTS (UNCHANGED WITH GOVERNANCE OVERLAY)
## 5.1 Frontend
- Next.js 14 + Tailwind + Radix
- Containerized on ECS
- API-only communication
- Zero PHI logs

## 5.2 Backend (FastAPI)
- Stateless
- SQLAlchemy 2
- Rule-engine integration
- Notification orchestrator
- Audit middleware

## 5.3 Database (RDS Postgres 15)
- Encrypted
- RLS
- Change events table
- Lineage enforced

## 5.4 S3 Storage
- Versioned
- Encrypted
- Lineage preserved

## 5.5 Notification Engine
- Template versioning
- SES/SNS
- Delivery tracking

## 5.6 Parsing Engine
- OCR + extraction
- Confidence scores
- No AI inference in prod

---
# 6. AWS INFRASTRUCTURE
(VPC, private subnets, VPC endpoints, ECS tasks, RDS, CloudWatch, Secrets Manager — same as prior SAD, preserved.)

---
# 7. SECURITY ARCHITECTURE
- Least privilege IAM
- Zero-trust networking
- RBAC + RLS
- No PHI to AI systems
- All agent actions logged

---
# 8. OBSERVABILITY
- Prometheus metrics
- Grafana dashboards
- CloudWatch logs
- Alerting for failures & performance degradation

---
# 9. NOTIFICATION ARCHITECTURE
(preserved — template versioning, quiet hours, fallback, retries.)

---
# 10. DOCUMENT & PARSING ARCHITECTURE
- OCR pipeline
- Metadata extraction
- Lineage enforcement

---
# 11. COMPLIANCE ENGINE
- Deterministic JSON rule packs
- Versioned
- Outputs windows, gaps, urgency

---
# 12. CI/CD ARCHITECTURE
(preserved — GitHub Actions → ECR → ECS deploy.)

---
# 13. INTEGRATION ARCHITECTURE
(preserved — NPI, SES, SNS, S3, Secrets Manager.)

---
# 14. GOVERNANCE INTEGRATION (NEW)
This SAD is now formally bound to:
- Context Summary Capsule
- AI Governance Document
- Phase 1 Master Prompt for Claire
- Agent Matrix
- Multi-Repo Blueprint

Agents MUST enforce:
- lane boundaries
- SOC2 timestamping
- ORIGIN/UPDATED_FOR tagging
- local CSV PM logging
- human approval gate

---
# 15. TIMESTAMPING + ORIGIN/UPDATED_FOR (SOC2)
All generated files must begin with:
```
# TIMESTAMP: <UTC ISO8601>
# ORIGIN: <repo>
# UPDATED_FOR: <repo-if-modified>
```
Binary assets use `.meta` files.

---
# 16. LOCAL CSV PM WORKFLOW (REQUIRED)
ChatGPT PM will:
- generate CSV entries after each Claire task
- specify which repo + agent lane
- maintain task_id continuity
- ensure SOC2 alignment

Human will paste rows into local Excel tracker.
Agents MUST NOT modify local PM files.

---
# 17. ARCHITECTURE DIAGRAM (UPDATED — SUMMARY)
```
Product (Human)
        ↓
Project Manager (ChatGPT PM)
        ↓
Program Manager (ChatGPT + Human)
        ↓
Claire — Master Executor
        ↓
Agent Lanes (Backend, Frontend, Infra, Rules, DB, Notification, QA)
        ↓
7 Repos (app/infra/rules/notification/ai/schemas/docs)
        ↓
AWS Stack (ECS/RDS/S3/SES/SNS/CloudWatch)
```

---
# END OF UPDATED SYSTEM ARCHITECTURE DOCUMENT