# **CredentialMate API Contract Document**

## **Version 2.0 — Full Rewrite With Complete Endpoint Coverage, Error Rules, Versioning, and Admin Controls**

### **Sources Incorporated:**

- Section 18: API Governance
- Error Pattern Rules (404/403/500 taxonomy)
- Data Bible v2.0
- PRD v2.0
- System Architecture Document v1.0
- AI Governance Rules
- Notification Architecture
- Compliance Engine Specs

---

# **1. PURPOSE OF THIS DOCUMENT**

This API Contract Document defines the **complete, authoritative, version-locked interface** for all CredentialMate components.

This document exists to:

- Enforce deterministic, stable, non-hallucinated endpoints
- Maintain strict versioning for frontend, backend, workers, and external integrations
- Prevent API drift across multi-repo architecture
- Ensure HIPAA & SOC2 compliant data contracts
- Define full request/response schemas and error structures
- Establish filtering, pagination, and permission rules

**No endpoint may exist outside this document.** **No agent or developer may invent or assume endpoints.**

---

# **2. GLOBAL API RULES**

## **2.1 Versioning**

- Base version prefix: `/api/v1/`
- Breaking changes → `/api/v2/`
- Deprecation window: 6 months minimum
- Clients must specify the version explicitly

## **2.2 Deterministic Schema Rule**

All endpoints must:

- Return strongly typed JSON
- Never include dynamic/unstructured LLM output
- Use consistent casing (snake\_case)
- Include timestamps in ISO8601

## **2.3 Error Response Contract (Mandatory)**

```
{
  "error": {
    "code": "<UPPER_SNAKE_CASE>",
    "message": "<human-readable>",
    "details": { ... },
    "trace_id": "uuid4"
  }
}
```

Supported codes:

- NOT\_FOUND
- UNAUTHORIZED
- FORBIDDEN
- VALIDATION\_ERROR
- INTERNAL\_ERROR
- CONFLICT
- RATE\_LIMIT
- PARSING\_FAILED

## **2.4 Pagination & Filtering Contract**

Every list endpoint MUST support:

```
?page=1&page_size=50&sort=created_at&order=desc
```

Optional filters:

- date\_from/date\_to
- entity-specific filters (state, status, severity)

## **2.5 PHI Safety Rules**

- Return minimum necessary PHI only
- Sensitive fields (DOB, phone, email) masked where possible
- Full PHI available only to authorized backend flows via RLS

## **2.6 No Hallucinated Endpoints**

- Only endpoints listed here may exist
- AI agents must stop if asked to generate unspecified endpoints

---

# **3. AUTHENTICATION & AUTHORIZATION CONTRACTS**

## **3.1 POST /api/v1/auth/login**

Authenticate with email + password.

## **3.2 POST /api/v1/auth/refresh**

Obtain a new access token using refresh token.

## **3.3 GET /api/v1/auth/me**

Returns authenticated user identity + roles.

## **3.4 ROLE RULES**

- Provider → own data only
- Admin → organization data
- SuperAdmin → global data (write restricted)

---

# **4. PROVIDER API CONTRACTS**

## **4.1 GET /api/v1/providers/me**

Return profile.

## **4.2 PUT /api/v1/providers/me**

Update provider metadata (email, preferences, settings).

## **4.3 GET /api/v1/providers/me/states**

Return `provider_states` entries.

## **4.4 POST /api/v1/providers/me/states**

Add states (optional; may be admin-driven only).

## **4.5 ADMIN ENDPOINTS**

### **GET /api/v1/admin/providers**

List providers in organization. Supports pagination & filtering.

### **GET /api/v1/admin/providers/{id}**

Return provider + linked credentials.

---

# **5. LICENSE API CONTRACTS**

## **5.1 GET /api/v1/licenses**

Return licenses for authenticated provider.

## **5.2 GET /api/v1/licenses/{id}**

Return full license record.

## **5.3 POST /api/v1/licenses**

System-only (parsing pipeline).

## **5.4 PUT /api/v1/licenses/{id}**

Manual corrections (admin only; versioning enforced).

## **5.5 ADMIN ENDPOINTS**

### **GET /api/v1/admin/licenses**

List licenses across org.

---

# **6. DEA / CSR / BOARD CERTIFICATION CONTRACTS**

## **6.1 GET /api/v1/dea**

## **6.2 GET /api/v1/csr**

## **6.3 GET /api/v1/board-certifications**

Return these credentials.

Admin versions available:

- `/api/v1/admin/dea`
- `/api/v1/admin/csr`
- `/api/v1/admin/board-certifications`

---

# **7. CME CONTRACTS**

## **7.1 GET /api/v1/cme**

List CME events.

## **7.2 GET /api/v1/cme/{id}**

Return a specific CME event.

## **7.3 POST /api/v1/cme**

Created via parsed documents.

## **7.4 GET /api/v1/cme/categories**

Return `cme_categories_required`.

Admin endpoints:

- `/api/v1/admin/cme`

---

# **8. DOCUMENT & PARSING CONTRACTS**

## **8.1 POST /api/v1/documents/upload**

Accepts PDF, PNG, JPG, DOCX, PPTX. Returns `document_id`.

## **8.2 GET /api/v1/documents/{id}**

Returns metadata + storage info.

## **8.3 GET /api/v1/documents/{id}/metadata**

Extracted metadata + confidence scores.

## **8.4 GET /api/v1/documents/{id}/lineage**

Record-by-record linkage to structured database.

## **8.5 GET /api/v1/parsing/jobs**

List parsing jobs.

## **8.6 GET /api/v1/parsing/jobs/{id}**

Detailed parsing job status.

---

# **9. COMPLIANCE ENGINE CONTRACTS**

## **9.1 GET /api/v1/compliance/windows**

Return active windows.

## **9.2 GET /api/v1/compliance/gaps**

Return structured summary.

## **9.3 POST /api/v1/compliance/recalculate**

Trigger a deterministic rule evaluation.

Admin endpoints:

- `/api/v1/admin/compliance/providers`
- `/api/v1/admin/compliance/summary`

---

# **10. RULE PACK & VERSIONING CONTRACTS**

## **10.1 GET /api/v1/system/rules**

Return latest rule pack.

## **10.2 GET /api/v1/system/rules/versions**

Return list of rule versions.

## **10.3 GET /api/v1/system/rules/{version\_id}**

Return specific version.

## **10.4 POST /api/v1/system/rules/validate**

Dev-only validation before publishing rule pack.

---

# **11. NOTIFICATION CONTRACTS**

## **11.1 GET /api/v1/notifications**

Return notification history.

## **11.2 GET /api/v1/notifications/preferences**

Return provider prefs.

## **11.3 PUT /api/v1/notifications/preferences**

Update preferences.

## **11.4 GET /api/v1/notifications/email-events/{notification\_id}**

SES lifecycle events.

Admin endpoints:

- `/api/v1/admin/notifications/overview`
- `/api/v1/admin/bulk-message`

---

# **12. AUDIT & CHANGE EVENT CONTRACTS**

## **12.1 GET /api/v1/admin/audit/logs**

Filterable by:

- actor\_id
- resource
- date range

## **12.2 GET /api/v1/admin/change-events**

Return historical row-level changes.

---

# **13. SYSTEM METADATA CONTRACTS**

## **13.1 GET /api/v1/system/status**

Health check used by ALB.

## **13.2 GET /api/v1/system/readiness**

Used by ECS task health.

## **13.3 GET /api/v1/system/version**

Returns application + rule pack version.

---

# **14. FORBIDDEN API ACTIONS**

Agents and developers may NEVER:

- Invent endpoints
- Invent query parameters
- Modify API behavior without updating this document
- Add AI/LLM-driven endpoints to production
- Return non-deterministic outputs
- Expose PHI in debug responses
- Bypass compliance or lineage checks

---

# **15. FUTURE ENDPOINT PLACEHOLDERS**

Reserved for future development:

- State board license verification
- CME vendor integrations
- Webhook delivery endpoints

---

# **END OF API CONTRACT DOCUMENT — VERSION 2.0**

