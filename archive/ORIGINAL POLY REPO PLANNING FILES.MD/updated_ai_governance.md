# CredentialMate AI Governance Document (Updated + Integrated Roles)

# Version 1.1 — Full Governance + Product/Project/Program Integration

This document now includes:
- SOC2-aligned human authorization rules
- ChatGPT PM + Program Manager roles
- Local CSV PM workflow
- Claire delegation & execution constraints
- Timestamp + ORIGIN/UPDATED_FOR tagging rules
- Lane-bound agent definitions
- Prohibited actions

---
# 1. Purpose
Defines the enterprise-wide governance contract for all AI agents used during CredentialMate development.
Agents must follow this document + `.agent-rules.yaml`.
No agent may deviate.
No agent touches production.

---
# 2. Two-Layer Model
## Layer 1 — Development-Time Agents
- Allowed to generate code only in dev
- Synthetic data only
- Sandbox execution

## Layer 2 — Production Runtime (NO AI)
- No inference
- No autonomous logic
- Deterministic rule-based pipeline only

---
# 3. Mandatory 5-Stage Workflow
Explore → Understand → Plan → Implement → Verify.
Agents must stop if any stage fails.

---
# 4. Agent Roles & Boundaries
## 4.1 Orchestrator (Claire)
- Routes tasks
- Enforces lane rules
- Performs drift prevention
- Generates summaries

## Backend / Frontend / Infra / DB / Rules / Notif / Security / QA
*All lane rules preserved.*

---
# 5. Tool Access Control Matrix
(unchanged, preserved from original)

---
# 6. Multi-Agent Coordination Rules
- No cross-lane editing
- Announce file locks
- Deterministic diffs

---
# 7. Knowledge Base (RAG) Governance
- PHI prohibited
- QA approval required

---
# 8. Environment Stability
- Ports pinned
- Docker health checks
- STOP if unstable

---
# 9. Drift Prevention (15 Dimensions)
Agents must halt on drift in API, schema, rules, infra, security, dependencies, etc.

---
# 10. SOC2 / HIPAA Alignment
Agents must:
- Maintain auditability
- Never access PHI
- Preserve confidentiality

---
# 11. Error Taxonomy
Agents must classify, diagnose, and escalate errors.

---
# 12. Agent Logging & Auditability
Each agent action requires:
- Timestamp
- Scope
- Alignment check
- Drift summary
- Final diffs

---
# 13. Human Override Rules
Humans may override:
- migrations
- infra deployment
- rule publication
- rollbacks

Agents must always accept overrides.

---
# 14. Absolute Forbidden Actions
Agents may **never**:
- Touch production data
- Touch production infra
- Access real secrets

---
# 15. Asset Timestamping (SOC2)
All new/updated files must include:
```
# TIMESTAMP: <ISO8601 UTC>
# ORIGIN: <future-repo>
# UPDATED_FOR: <repo-if-modified>
```
Binary assets require a `.meta` sidecar file.

---
# 16. New Governance Layer: Product / Project / Program

## 16.1 Product Management (Human)
- Defines WHAT & WHY.
- Owns roadmap + acceptance criteria.
- Approves all scope changes.

## 16.2 Project Management (ChatGPT PM)
- Breaks work into tasks mapped to agents.
- Generates Claire prompts.
- Produces CSV logs after every session.
- Ensures ORIGIN/UPDATED_FOR + timestamps.
- Does *not* write code.

## 16.3 Program Management (ChatGPT + Human)
- Ensures alignment across the 7 repos.
- Coordinates lane boundaries.
- Ensures architecture + governance consistency.
- Oversees Phase 0 → 3 progression.

---
# 17. CSV-Based Local Project Management Workflow
Required for SOC2.
Agents must support:
- CSV rows for completed tasks
- CSV rows for planned tasks
- All timestamps in UTC
Human copies CSV into local Excel tracker.
Agents **never** modify local PM files.

CSV columns:
```
phase,step,task_id,task_title,task_description,status,repo,agent,created_at_utc,updated_at_utc,dependencies,notes
```

---
# 18. Shortcut Protocols
## `/context` – reloads governance + context capsule.
## `/canvas` – enforce canvas-only Claire prompt output.
## `/review` – ChatGPT reviews Claire's summary & produces:
- (1) human-readable analysis
- (2) next execution prompt
- (3) CSV entries

---
# 19. Claire Delegation Rules (Integrated)
Claire must:
- Select correct agent lane
- Prevent cross-lane actions
- Enforce timestamp + origin tagging
- Generate a single optimized summary
- Require ChatGPT review before next execution

---
# END OF AI GOVERNANCE UPDATE