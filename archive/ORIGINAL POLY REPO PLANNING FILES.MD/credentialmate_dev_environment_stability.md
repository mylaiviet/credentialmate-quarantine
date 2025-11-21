# **CredentialMate Developer Environment & Cross-Session Stability Specification**
## **Version 1.0 — Deterministic Local Environment, Zero Drift, Port Locking, Repair-First Protocols**
### **Sources Incorporated:**
- Section 11 (Environment Stability)
- AI Governance Document v1.0
- Master Summary (agent safety + drift rules)
- System Architecture Document (SAD)
- API Contract v2.0 (error taxonomy)
- Data Bible v2.0 (schema alignment)

---
# **1. PURPOSE OF THIS DOCUMENT**
This specification defines exactly **how developers and AI agents must configure, maintain, and validate** the CredentialMate development environment so that:
- builds are reproducible
- Docker runs deterministically
- ports NEVER drift
- backend/frontend/db ALWAYS align
- AI agents NEVER misinterpret the current state
- sessions remain stable across days/weeks

This is a **required standalone document** because environment drift is one of the top causes of:
- broken builds
- inconsistent behavior between agents
- misaligned migrations
- API errors caused by local environment
- failed uploads
- 404/403/500 confusion
- Docker rebuild loops

This document defines the **canonical and stable** environment developers must use.

---
# **2. CANONICAL LOCAL DEVELOPMENT STACK**
CredentialMate is developed locally using:
- **Docker Compose**
- FastAPI backend
- Next.js frontend
- Postgres + pgvector
- MinIO (optional) as S3 emulator for dev

Local dev **MUST** mirror production architecture:
```
Frontend → Backend → Postgres + S3
```

No direct DB access.
No bypass of backend API.

---
# **3. DETERMINISTIC DOCKER RULES**
## **3.1 All dependencies MUST be included in Docker images**
No local environment pip/node installs.
No dependency drift.

## **3.2 Docker Rebuild Rules**
Rebuild ONLY when:
- requirements.txt changes
- package.json changes
- Dockerfile changes

Rebuild NEVER for:
- backend code edits (hot reload)
- frontend code edits (hot reload)

## **3.3 Docker Caching**
Agents must use layer caching correctly.
No forced cache busting.

---
# **4. PORT LOCKING RULES**
These port assignments **MUST NEVER CHANGE**:
- Backend (FastAPI): **8000**
- Frontend (Next.js): **3000**
- Postgres: **5432**
- MinIO (S3 emulator): **9000**

AI agents must NOT:
- auto-select new ports
- create random ports
- modify docker-compose port mappings

If a port is in use:
- STOP ALL CONTAINERS
- Identify the process
- Kill the process

**Never shift ports to random values.**

---
# **5. CROSS-SESSION CONSISTENCY RULES**
## **5.1 Mandatory Context Reload**
Every new day/session → developer must run:
```
docker compose down
rm -rf __pycache__ .next
```
Then restart:
```
docker compose up --build --quiet-pull
```

## **5.2 Mandatory Branch Sync**
Before coding:
```
git pull origin main
poetry lock (if used)
```

## **5.3 Mandatory Schema Sync**
Before backend start:
```
alembic upgrade head
```

## **5.4 No Orphan Containers**
Orphan containers cause drift.
Agents must check:
```
docker ps -a
```
Delete orphans:
```
docker system prune -af
```

---
# **6. CONNECTIVITY VALIDATION (REQUIRED)**
Before ANY coding begins, run:

### **6.1 Backend Health Check**
```
curl http://localhost:8000/api/v1/system/health
```
Must return:
```
{"status": "ok"}
```

### **6.2 Database Connectivity Check**
```
docker exec -it credentialmate-db psql -U postgres -c "SELECT 1"
```

### **6.3 Frontend-to-Backend Check**
Open browser:
```
http://localhost:3000/api/ping
```
Should return:
```
pong
```

### **6.4 Migration Consistency Check**
Backend endpoint:
```
GET /api/v1/system/version
```
Must match local `alembic_head`.

---
# **7. ENVIRONMENT DRIFT DETECTION**
Common drift symptoms:
- 404 on valid routes
- 403 unauthorized errors after login
- 500 upload failures
- migrations missing
- schema mismatches
- docker-compose misalignment

## **7.1 Drift Detection Script** (Required)
Agents must run:
```
./scripts/check-drift.sh
```
This validates:
- open ports
- service health
- version alignment
- DB schema hash
- stale containers

---
# **8. REPAIR-FIRST PROTOCOL**
If an error appears, **agents must repair environment BEFORE writing code**.

## **8.1 General Repair Steps**
```
docker compose down -v
docker system prune -af
rm -rf .next
rm -rf __pycache__
docker compose up --build --force-recreate
```

## **8.2 Database Repair**
If schema mismatch:
```
alembic downgrade -1
alembic upgrade head
```

## **8.3 S3 Emulator Repair**
If MinIO fails:
```
docker compose restart minio
```

---
# **9. ERROR PATTERN REFERENCE (MANDATORY)**
This is a required reference table for AI agents.

### **404 NOT FOUND**
Cause:
- frontend hitting wrong port
- wrong URL
- backend container not running
Solution:
- verify port locking
- confirm backend health

### **403 FORBIDDEN**
Cause:
- missing cookies
- bad JWT
Solution:
- clear browser storage
- re-login

### **500 INTERNAL ERROR**
Cause:
- doc parsing failure
- schema mismatch
Solution:
- run drift detection
- review backend logs

### **422 VALIDATION ERROR**
Cause:
- mismatched payload
Solution:
- check API contract v2.0

### **503 SERVICE UNAVAILABLE**
Cause:
- container restart loop
Solution:
- apply repair-first steps

---
# **10. AGENT ALIGNMENT RULES**
## **10.1 Agents MUST Reload Context**
Agents must always ask:
> *“Has your local environment changed since last session?”*

## **10.2 Agents MUST Validate Environment Before Generating Code**
Checklist:
- backend healthy?
- DB schema aligned?
- ports locked?
- drift script passed?

## **10.3 Agents MUST Reject Tasks if Environment is Broken**
If backend is down:
- NO code generation allowed
- MUST issue repair-first commands

---
# **11. FORBIDDEN ACTIONS**
Agents and developers may NOT:
- change ports
- run backend without migrations
- bypass backend API for DB writes
- create new docker-compose files
- allow docker-compose.override to drift
- install local pip/node dependencies
- push code without drift resolution

---
# **12. FUTURE EXTENSIONS**
- Environment bootstrap script
- One-click repair script
- Docker-init consistency checker
- Automatic drift alerts via pre-commit hook
- Local S3 → AWS S3 sync tool

---
# **SUMMARY OF WHAT WAS ADDED (FOR COMPLETENESS)**
Below is exactly what was added beyond your initial outline:

### ⭐ **1. Full deterministic Docker rules** (no local deps, rebuild rules, layer caching)
### ⭐ **2. Port-locking section with rules for conflicts**
### ⭐ **3. Cross-session mandatory context reload** (down, prune, rebuild)
### ⭐ **4. Connectivity validation suite** (health, DB, API, migration consistency)
### ⭐ **5. Environment drift detection script + checklist**
### ⭐ **6. Repair-first protocol** (required before writing code)
### ⭐ **7. Error pattern reference tied to environment drift**
### ⭐ **8. Agent alignment rules** ensuring consistent context before coding
### ⭐ **9. Forbidden environment actions** to prevent misalignment
### ⭐ **10. Future enhancements for dev stability**

---
# **END OF DEVELOPER ENVIRONMENT & CROSS-SESSION STABILITY SPEC — VERSION 1.0**

