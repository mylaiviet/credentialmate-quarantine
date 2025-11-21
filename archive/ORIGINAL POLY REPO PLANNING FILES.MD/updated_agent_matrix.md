# CredentialMate Named Agent Matrix (Updated + Integrated Governance Roles)

# Version 1.1 — Agent Lanes + Governance Layer Integration

This matrix now includes **all engineering agents**, **their detailed skill sets**, and the newly formalized **Human + Orchestration Meta-Roles** (Product, Project, Program Management). These meta-roles coordinate the engineering agents via ChatGPT ↔ Claire orchestration.

---

# 🔵 Primary Domain Agents (Engineering Lanes)

| Agent Name   | Domain Role                    | High-Level Function                          | Core Responsibilities                                                                                |
| ------------ | ------------------------------ | -------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **Claire**   | Master Orchestrator            | Global routing & task decomposition          | Intent parsing, delegation to agent lanes, drift prevention, governance enforcement, summary output |
| **Backend**  | Backend Engineering Agent      | API, backend logic, parsing orchestration    | FastAPI endpoints, SQLAlchemy models, migrations, parsing pipeline, rule-engine integration          |
| **Frontend** | Frontend Engineering Agent     | UI/UX, dashboards, user flows                | Next.js pages, Tailwind UI, component library, upload/UI forms, provider/admin dashboards            |
| **Infra**    | Infrastructure & DevOps Agent  | AWS, Terraform, ECS/RDS, CI/CD               | Infra automation, deployments, rollbacks, monitoring, ECS/RDS/S3 config                              |
| **Data**     | Data & Schema Agent            | Database schemas, RLS, DQ rules              | Schema governance, lineage, field-level encryption, RLS policies, change events                      |
| **Rules**    | Rules & Compliance Agent       | Renewal cycles, CME, DEA/CSR logic           | Deterministic rules, rule packs, multi-state merges, category mapping, versioning                    |
| **Notif**    | Notification & Messaging Agent | SES/SMS, template engine, delivery           | Template versioning, quiet hours, fallback routing, retry engine, event tracking                     |
| **Security** | Security & Observability Agent | IAM, audit logs, monitoring, drift detection | IAM model, PHI protection, security scans, drift alerts, monitoring dashboards                       |
| **Gov**      | AI Governance Agent            | Agent rules, safety, guardrails              | Prompt templates, safety enforcement, lane definitions, session logs, dev-time AI controls           |

---

# 🟦 Human + Orchestration Meta-Roles (NEW)
These roles sit **above the engineering agents** and govern scope, execution sequencing, and cross-repo alignment.

## **Product Management (Human Role — WHAT & WHY)**
- Owns CredentialMate vision and long-term roadmap.
- Defines requirements, acceptance criteria, and prioritization.
- Determines **WHAT** should be built.
- Final authority on scope changes across repos.

## **Project Management (ChatGPT PM — HOW & WHEN)**
- Converts Product-level goals into actionable tasks.
- Maps each task to the correct agent lane (Backend, Infra, Data, etc.).
- Produces **CSV entries** after every Claire execution:
  - completed tasks
  - new planned tasks
- Generates Claire-ready prompts.
- Maintains local project log (Excel/CSV) — **human-approved updates only**.
- Ensures SOC2 timestamp, ORIGIN/UPDATED_FOR tagging.

## **Program Management (ChatGPT + Human Co-Ownership — ALIGNMENT)**
- Ensures the 7 repos, agent lanes, and phases move in sync.
- Coordinates multi-repo evolution.
- Ensures governance, architecture, and mode files remain aligned.
- Oversees Phase 0 → 1 → 2 → 3 sequencing.

### Integration Responsibilities Across All Agents
- Product → Defines WHAT to build.
- Project → Defines HOW + WHEN to execute.
- Program → Ensures system-wide alignment.

---

# 🟩 Detailed Sub-Agent Skills (Engineering)

## **Backend Engineering Skills**

| Skill                     | Description                                   |
| ------------------------- | --------------------------------------------- |
| API Contract Validator    | Ensures endpoints match API Contract v2.0     |
| CRUD Workers              | Providers, licenses, CME, DEA, CSR CRUD flows |
| Parsing Orchestrator      | Manages parsing jobs + metadata normalization |
| Document Classifier       | Determines document type (license/CME/DEA)    |
| Provider Identity Mapper  | Maps NPI/DEA/CSR to internal provider IDs     |
| Migration Generator       | Creates versioned Alembic migrations          |
| Backend Error Normalizer  | Enforces deterministic error model            |
| Audit Middleware Enforcer | Ensures audit logs on all PHI access          |

---

## **Frontend Engineering Skills**

| Skill                        | Description                                     |
| ---------------------------- | ----------------------------------------------- |
| Component Builder            | Creates accessible, deterministic UI components |
| Tailwind Styler              | Ensures design system token compliance          |
| Form Schema Mapper           | Maps Pydantic schemas → forms                   |
| Dashboard Renderer           | Compliance windows, CME, expiring items         |
| Upload Flow Builder          | Drag-and-drop → parse → confirm                 |
| State Management Worker      | React Query integration                         |
| Notification Center Renderer | In-app notifications UI                         |

---

## **Infrastructure & DevOps Skills**

| Skill                      | Description                           |
| -------------------------- | ------------------------------------- |
| Terraform Module Validator | Validates modules across environments |
| ECS Service Builder        | Deploys backend/frontend containers   |
| Dockerfile Auditor         | Ensures secure, minimal images        |
| VPC/Subnet Designer        | Zero-trust, endpoint-first VPCs       |
| Secrets Manager Integrator | Injects secrets into ECS tasks        |
| CloudWatch Alert Engineer  | Builds alerts, metrics, dashboards    |
| CI/CD Workflow Enforcer    | GitHub Actions pipelines              |

---

## **Data & Schema Skills**

| Skill                     | Description                               |
| ------------------------- | ----------------------------------------- |
| Schema Diff Worker        | Validates schema evolution                |
| Column Encryption Manager | Applies KMS field-level encryption        |
| Data Lineage Recorder     | Maintains mapping doc → structured DB     |
| Data Quality Validator    | Completeness, accuracy, consistency rules |
| RLS Policy Generator      | Enforces provider/admin isolation         |
| Change Event Producer     | Creates immutable change history          |

---

## **Rules & Compliance Skills**

| Skill                    | Description                       |
| ------------------------ | --------------------------------- |
| Renewal Cycle Evaluator  | Fixed/birth month/odd-even cycles |
| CME Matrix Interpreter   | Category-level mapping            |
| DEA Rule Evaluator       | 36-month cycles evaluation        |
| CSR Rule Evaluator       | State-specific CSR logic          |
| Multi-State Merge Worker | Consolidates multiple states      |
| Rule Version Packager    | Publishes versioned rule packs    |
| Citation Link Verifier   | RSAM linkage validation           |

---

## **Notification & Messaging Skills**

| Skill                    | Description                         |
| ------------------------ | ----------------------------------- |
| Email Template Versioner | Version-based template engine       |
| Quiet Hours Enforcer     | Timezone-aware quiet hour logic     |
| Routing Worker           | Email → SMS → in-app                |
| Fallback Router          | On bounce: retry next channel       |
| Retry Engine             | Multi-step retry pipeline           |
| SES Event Listener       | Delivered/opened/bounced tracking   |
| Notification Logger      | Writes notifications_sent + events |

---

## **Security & Observability Skills**

| Skill                  | Description                             |
| ---------------------- | --------------------------------------- |
| Audit Log Writer       | Immutable logging for all actions       |
| IAM Policy Validator   | Least-privilege policy enforcement      |
| Drift Detector         | Detects schema/API/infrastructure drift |
| Security Scanner       | Trivy/Bandit/npm-audit integration      |
| Vulnerability Analyzer | Patterns + severity scoring             |
| Encryption Validator   | Verifies at-rest/in-transit encryption  |

---

## **AI Governance Skills**

| Skill                     | Description                      |
| ------------------------- | -------------------------------- |
| Prompt Template Generator | Deterministic prompt templates   |
| Guardrail Enforcer        | Safety, constraints, PHI rules   |
| Lane Auditor              | Ensures agents stay in-lane      |
| Session Log Manager       | Writes session summaries + scope |
| Policy Serializer         | Converts policies into YAML      |
| PHI Redaction Validator   | Ensures no PHI in AI tasks       |

---

# Summary
This matrix now includes:
- All engineering agents
- Their detailed skill sets
- **Integrated Product, Project, Program governance roles**
- How these roles guide agent lanes and Claire’s orchestration

Fully aligned with the CredentialMate Context Summary and SOC2 governance model.

