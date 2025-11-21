# CredentialMate Multi-Repo Integration Blueprint (Updated v1.2)

This updated blueprint integrates:
- Product / Project / Program governance roles
- ChatGPT PM orchestration
- Claire Delegation Framework
- Local CSV-based PM system
- SOC2 human-authorization boundary
- Timestamp + ORIGIN/UPDATED_FOR tagging
- Strict repo-lane mapping

---
# 1. Purpose
Defines the authoritative model for:
- Repo boundaries
- API-only communication
- Cross-repo versioning
- Drift detection
- Release lifecycle
- Promotion model
- Multi-repo alignment under governance

This file is a top-level **Program Management artifact**.

---
# 2. Canonical Repo Structure (7 Repos)
1. credentialmate-app
2. credentialmate-infra
3. credentialmate-rules
4. credentialmate-notification
5. credentialmate-ai
6. credentialmate-schemas
7. credentialmate-docs

Repo count is permanently fixed at **7**.
No extra repos may be created.

---
# 3. Repo Boundary Rules (Enforced)
- No shared code across repos
- No cross-repo file access
- Single-lane agent per repo
- All cross-repo interaction via:
  - REST API
  - versioned artifacts (rules, templates, schemas)

Human approval required for any boundary change.

---
# 4. Cross-Repo Contracts
Types of contracts:
- API Contract (credentialmate-app)
- Schema Contract (credentialmate-schemas)
- Rule Pack Contract (credentialmate-rules)
- Template Contract (credentialmate-notification)
- Infra Contract (credentialmate-infra)

All contracts use semantic versioning.
Breaking changes require human approval + major version bump.

---
# 5. Multi-Repo Drift Detection
Agents must halt execution if any drift is detected.
Drift dimensions:
- Schema
- API
- Rule packs
- Templates
- Infra
- Mode files

Cross-repo drift must be resolved BEFORE writing code.

---
# 6. Release Lifecycle (Multi-Repo)
Four-stage pipeline:
- dev
- sandbox
- staging
- production

Promotion requires:
- schema alignment
- rule pack version alignment
- template version alignment
- infra plan approval
- drift checks

---
# 7. Versioning Policy
Each repo maintains its own version file.
Platform releases bump ALL relevant versions:
- app
- rules
- templates
- schemas
- infra

---
# 8. API-Only Communication Rule
Repos MUST interact via API or artifacts.
No shared code.
No database access across repos.

---
# 9. Release Orchestration
A Release Coordinator workflow validates:
- version alignment
- schema consistency
- tests
- drift detection
- infra plan
- rule pack + template versions

Release tags follow:
```
release-YYYY-MM-DD-vX
```

---
# 10. Forbidden Multi-Repo Actions
Agents may NOT:
- modify multiple repos in one task
- bypass API for direct DB access
- write shared utility repos
- introduce silent breaking changes
- access undeclared infra resources

---
# 11. Governance Integration (Updated)

## 11.1 Product, Project, Program Management
This document aligns all repos under:
- **Product Management (Human)** → defines WHAT to build
- **Project Management (ChatGPT PM)** → defines HOW + WHEN
- **Program Management (ChatGPT + Human)** → ensures repo alignment

## 11.2 Claire Delegation
All multi-repo tasks must flow through Claire:
- Claire selects correct agent lane
- Enforces ORIGIN and UPDATED_FOR tagging
- Ensures timestamping
- Prevents cross-lane contamination

## 11.3 Local CSV PM System
Project Manager (ChatGPT) must produce CSV logs after each Claire summary:
- completed tasks
- upcoming tasks
- correct repo lane

Human must paste CSV rows into the local project tracker.
Agents may NOT modify external PM files.

---
# 12. Timestamping + ORIGIN/UPDATED_FOR (SOC2 Requirement)
EVERY new or updated file across repos must include:
```
# TIMESTAMP: <ISO8601>
# ORIGIN: <target repo>
# UPDATED_FOR: <repo>
```
Binary assets must include sidecar `.meta` files.

---
# 13. Future Extensions
- automated drift dashboard
- multi-repo dependency maps
- unified release notes generator

---
# END OF UPDATED MULTI-REPO BLUEPRINT

