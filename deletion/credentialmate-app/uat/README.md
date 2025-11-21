# SHIPFASTV1 UAT — User Acceptance Testing Guide

**TIMESTAMP:** 2025-11-16T15:00:00Z
**ORIGIN:** credentialmate-app/uat
**UPDATED_FOR:** shipfastv1-frontend-isolation-fix

---

## Overview

This UAT environment provides an isolated, containerized testing setup for ShipFastV1 frontend validation. All services run inside Docker with seed data pre-loaded.

**Key Features:**
- ✅ Frontend only (V2 documents pages protected)
- ✅ Mock backend APIs (no real ingestion/parsing)
- ✅ Seed data for providers and documents
- ✅ Health checks and validation scripts
- ✅ No secrets exposed (env.local.example provided)
- ✅ SOC2 compliant configuration

---

## Quick Start

### Prerequisites
- Docker & Docker Compose 2.0+
- 4GB RAM available
- Ports 3000, 5678, 5432, 6379 available

### Launch UAT

```bash
cd credentialmate-app

# Copy environment template
cp uat/env.local.example uat/.env.local

# Start all services
bash uat/scripts/start-uat.sh

# Wait for health checks (2-3 minutes)
```

### Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | ShipFastV1 app (document pages) |
| API Docs | http://localhost:5678/api/docs | Mock API endpoints |
| Database | localhost:5432 | PostgreSQL (seed data loaded) |
| Cache | localhost:6379 | Redis |

---

## UAT Scope — ShipFastV1 Features

### ✅ Protected/Tested
- **Document Upload & Management** (`/dashboard/v2/documents`)
- **Document Detail View** (`/dashboard/v2/documents/[id]`)
- **Document Parsing Status** (mock data)
- **Admin Ingestion Dashboard** (`/dashboard/v2/admin/ingestion`)
- **Authentication & Login**
- **V1 Provider Dashboard** (legacy)
- **V1 License/CME Pages** (legacy)

### ❌ Not in Scope (Dead Code Removed)
- V2 Compliance Dashboard (removed)
- V2 CME/License Management (removed)
- V2 Notifications (removed)
- V2 Provider Details (removed)
- All broken admin pages (removed)

---

## Test Workflows

### 1. Login & Navigation
```
1. Visit http://localhost:3000
2. Login with mock credentials (see seed data)
3. Navigate to /dashboard/v2/documents
4. Verify document list loads
```

### 2. Document Upload
```
1. Click "Upload Document"
2. Select a test file (PDF, docx)
3. Verify upload succeeds
4. Check document appears in list
```

### 3. Document Review
```
1. Click document in list
2. Verify detail page loads
3. Check parsing status (mock)
4. Review metadata panels
```

### 4. Admin Monitoring
```
1. Navigate to /dashboard/v2/admin/ingestion
2. Verify ingestion dashboard loads
3. Check all panels render (stubbed)
```

---

## Seed Data

### Providers
- **ID:** `provider-001` | **Name:** John Smith MD | **State:** CA
- **ID:** `provider-002` | **Name:** Jane Doe MD | **State:** TX
- **ID:** `provider-003` | **Name:** Bob Johnson MD | **State:** NY

### Documents
- 3 sample PDFs (mock references)
- Parsing status: 1 completed, 1 processing, 1 failed
- Metadata: License, DEA, CME references

See `uat/seed/` directory for JSON details.

---

## Health Checks

```bash
# Manual health check
bash uat/scripts/health-check.sh

# Check individual services
curl http://localhost:3000/health
curl http://localhost:5678/health
curl http://localhost:5432:0  # PostgreSQL
curl http://localhost:6379:0  # Redis
```

---

## Troubleshooting

### Frontend not loading
```bash
docker-compose -f uat/docker-compose.uat.yml logs frontend
```

### Database connection error
```bash
docker-compose -f uat/docker-compose.uat.yml logs postgres
```

### Port conflicts
```bash
# Free port 3000
lsof -ti:3000 | xargs kill -9
# Adjust docker-compose.uat.yml ports if needed
```

---

## Cleanup

```bash
# Stop and remove all containers
docker-compose -f uat/docker-compose.uat.yml down

# Remove volumes (data)
docker-compose -f uat/docker-compose.uat.yml down -v

# Prune unused images
docker image prune -f
```

---

## Governance & Compliance

- **Lane:** Frontend/UAT only (no backend/infra changes)
- **Build:** Next.js 14.2.33 (isolated build)
- **SOC2:** No secrets in UAT files (use .env.local for sensitive data)
- **Approval:** Ready for PM review and testing

---

## Support

For issues, check logs in `uat/logs/` or run:
```bash
docker-compose -f uat/docker-compose.uat.yml logs -f
```
