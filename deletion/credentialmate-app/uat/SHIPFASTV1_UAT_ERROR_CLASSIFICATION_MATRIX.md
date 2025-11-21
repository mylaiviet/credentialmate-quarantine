# SHIPFASTV1 UAT ERROR CLASSIFICATION MATRIX

**TIMESTAMP:** 2025-11-16T06:25:00Z
**ORIGIN:** credentialmate-app/uat
**UPDATED_FOR:** phase5-step4-uat-support-pack

---

## Purpose
Maps common errors encountered during UAT to:
- Issue type classification
- Severity level
- Responsible lane
- Required agent
- Drift type
- Resolution path
- Priority in Phase 6

This matrix ensures consistent triage and enables quick escalation.

---

## CLASSIFICATION MATRIX

| Error/Symptom | Issue Type | Severity | Lane | Agent | Drift Type | Resolution | Phase 6 Priority |
|---|---|---|---|---|---|---|---|
| **UI ERRORS** |
| Component not rendering / blank page | UI Issue | High | Frontend | Frontend Dev | UI Drift | Rebuild component, check imports, test render | P1 |
| CSS styling broken / misaligned layout | UI Issue | Medium | Frontend | Frontend Dev | UI Drift | Fix styles, test responsive, verify alignment | P2 |
| Modal/dialog won't close | UI Issue | High | Frontend | Frontend Dev | UI Drift | Check close handler, verify event listeners | P1 |
| Form validation not showing errors | UI Issue | Medium | Frontend | Frontend Dev | UI Drift | Check error state, verify UI display | P2 |
| Button/link doesn't respond to clicks | UI Issue | High | Frontend | Frontend Dev | UI Drift | Check onClick handler, verify event bubbling | P1 |
| Image/icon not displaying | UI Issue | Low | Frontend | Frontend Dev | UI Drift | Check image path, verify asset bundled | P3 |
| Text overflow / truncation broken | UI Issue | Low | Frontend | Frontend Dev | UI Drift | Adjust CSS, test with long content | P3 |
| Responsive design broken on mobile | UI Issue | Medium | Frontend | Frontend Dev | UI Drift | Test with mobile breakpoints, fix media queries | P2 |
| **API ERRORS** |
| 500 Internal Server Error | API Issue | Critical | Backend | Backend Dev | API Contract Drift | Check server logs, identify exception, fix root cause | P0 |
| 400 Bad Request with unclear message | API Issue | High | Backend | Backend Dev | API Contract Drift | Improve error message, validate input, update schema | P1 |
| 401 Unauthorized / 403 Forbidden | API Issue | Critical | Backend | Security/Backend | API Contract Drift | Verify auth flow, check token, test permissions | P0 |
| 404 Not Found (endpoint exists) | API Issue | High | Backend | Backend Dev | API Contract Drift | Debug routing, verify endpoint registration | P1 |
| Timeout / 504 Gateway Timeout | API Issue | High | Backend | Backend Dev | API Contract Drift | Optimize query, add caching, increase timeout | P1 |
| Response schema mismatch (missing field) | API Issue | High | Backend | Backend Dev | API Contract Drift | Update response model, verify serialization | P1 |
| CORS error preventing request | API Issue | High | Backend | Backend Dev | API Contract Drift | Fix CORS headers, whitelist origin | P1 |
| Wrong Content-Type in response | API Issue | Medium | Backend | Backend Dev | API Contract Drift | Set correct header, verify serialization | P2 |
| **PARSING ERRORS** |
| PDF file rejected / unsupported | Parsing Issue | High | Backend (Parsing) | Parsing Specialist | Parsing Logic Drift | Add format support, test parser, update filters | P1 |
| Extracted text is garbage/corrupted | Parsing Issue | High | Backend (Parsing) | Parsing Specialist | Parsing Logic Drift | Debug OCR, check encoding, validate output | P1 |
| Parsing job hangs indefinitely | Parsing Issue | Critical | Backend (Parsing) | Parsing Specialist | Parsing Logic Drift | Add timeout, debug worker, check resources | P0 |
| Metadata extraction returns NULL | Parsing Issue | High | Backend (Parsing) | Parsing Specialist | Parsing Logic Drift | Check extractor logic, add fallback, test | P1 |
| File encoding issues (unicode) | Parsing Issue | Medium | Backend (Parsing) | Parsing Specialist | Parsing Logic Drift | Fix encoding detection, add validation | P2 |
| Scanned PDF produces no text | Parsing Issue | High | Backend (Parsing) | Parsing Specialist | Parsing Logic Drift | Enable OCR, test image quality, verify config | P1 |
| **COMPLIANCE ERRORS** |
| License shows valid when expired | Compliance Issue | Critical | Backend | Compliance Lead | Business Logic Drift | Fix expiration check, add validation, test dates | P0 |
| CME credits miscounted | Compliance Issue | Critical | Backend | Compliance Lead | Business Logic Drift | Review calculation logic, fix aggregation, verify totals | P0 |
| Risk assessment score incorrect | Compliance Issue | High | Backend | Compliance Lead | Business Logic Drift | Review scoring rules, fix weights, test scenarios | P1 |
| Retention policy not enforced (data not deleted) | Compliance Issue | Critical | Backend | Compliance Lead | Business Logic Drift | Implement delete job, fix schedule, verify cleanup | P0 |
| Audit trail entry missing | Compliance Issue | High | Backend | Compliance Lead | Business Logic Drift | Add audit logging, verify capture, test events | P1 |
| Document not flagged for review | Compliance Issue | High | Backend | Compliance Lead | Business Logic Drift | Add flag logic, test conditions, notify users | P1 |
| **NOTIFICATION ERRORS** |
| Email not sent (alert missing) | Notification Issue | High | Backend (Notifications) | Backend Dev | Notification Logic Drift | Check email service, verify queue, test SMTP | P1 |
| Webhook not called after event | Notification Issue | High | Backend (Notifications) | Backend Dev | Notification Logic Drift | Debug webhook trigger, verify URL, check auth | P1 |
| Notification sent to wrong user | Notification Issue | Critical | Backend (Notifications) | Backend Dev | Notification Logic Drift | Fix recipient lookup, verify filtering, test RLS | P0 |
| Email contains HTML tags instead of rendering | Notification Issue | Medium | Backend (Notifications) | Backend Dev | Notification Logic Drift | Use HTML email template, test rendering | P2 |
| Notification appears after event is stale | Notification Issue | Medium | Backend (Notifications) | Backend Dev | Notification Logic Drift | Speed up notification processing, reduce delay | P2 |
| Alert threshold not triggered | Notification Issue | Medium | Backend (Notifications) | Backend Dev | Notification Logic Drift | Review threshold logic, fix comparisons, test edge cases | P2 |
| **SCHEMA DRIFT ERRORS** |
| INSERT/UPDATE fails with constraint error | Schema Drift Issue | Critical | Backend | Database Admin | Schema Drift | Run migration, verify constraints, check data | P0 |
| Column does not exist error | Schema Drift Issue | Critical | Backend | Database Admin | Schema Drift | Run all migrations, check schema sync | P0 |
| Foreign key constraint violated | Schema Drift Issue | Critical | Backend | Database Admin | Schema Drift | Fix referential integrity, run cleanup, test | P0 |
| Field has unexpected type (int vs string) | Schema Drift Issue | High | Backend | Database Admin | Schema Drift | Migrate type, verify casting, test serialization | P1 |
| Enum value not recognized | Schema Drift Issue | High | Backend | Database Admin | Schema Drift | Add enum value, update constraints, test | P1 |
| Index missing causing slow query | Schema Drift Issue | Medium | Backend | Database Admin | Schema Drift | Create index, verify statistics, test performance | P2 |
| JSON schema validation fails | Schema Drift Issue | High | Backend | Backend Dev | Schema Drift | Update schema definition, validate payload, test | P1 |
| **DATA DRIFT ERRORS** |
| Duplicate records appear in list | Data Drift Issue | High | Backend (Data) | Database Admin | Data Drift | Identify duplicates, add unique constraint, clean data | P1 |
| Orphaned records (FK parent deleted) | Data Drift Issue | High | Backend (Data) | Database Admin | Data Drift | Add ON DELETE CASCADE, clean orphans, verify integrity | P1 |
| Data corruption (unicode, encoding) | Data Drift Issue | Medium | Backend (Data) | Database Admin | Data Drift | Validate data, fix encoding, migrate records | P2 |
| Cache returns stale/deleted data | Data Drift Issue | High | Backend (Data) | Backend Dev | Data Drift | Clear cache, add invalidation, verify sync | P1 |
| Concurrent uploads create conflicting state | Data Drift Issue | Critical | Backend (Data) | Database Admin | Data Drift | Add database lock, verify atomicity, test race | P0 |
| Upload date shows incorrect value (2099) | Data Drift Issue | Medium | Backend (Data) | Backend Dev | Data Drift | Verify timezone handling, fix timestamp, test | P2 |
| **RLS VIOLATION ERRORS** |
| User sees other user's data (provider A sees provider B docs) | RLS Violation Issue | Critical | Backend | Security/Backend | RLS Violation | Review RLS policy, add row filter, test access | P0 |
| Non-admin user can perform admin action | RLS Violation Issue | Critical | Backend | Security/Backend | RLS Violation | Add role check, verify permission, test authorization | P0 |
| Public data exposed as private (or vice versa) | RLS Violation Issue | Critical | Backend | Security/Backend | RLS Violation | Review visibility rules, fix policy, test access | P0 |
| RLS policy missing in database | RLS Violation Issue | Critical | Backend | Security/Backend | RLS Violation | Create policy, enable RLS, test enforcement | P0 |
| Auth token not validated in middleware | RLS Violation Issue | Critical | Backend | Security/Backend | RLS Violation | Add token validation, verify middleware, test | P0 |
| Endpoint should require auth but doesn't | RLS Violation Issue | Critical | Backend | Security/Backend | RLS Violation | Add @auth_required, verify decorator, test | P0 |

---

## PRIORITY LEVELS EXPLAINED

| Priority | Definition | Example | SLA |
|---|---|---|---|
| **P0** | Critical - Blocks all testing, security/compliance risk, data loss | RLS violation, 500 errors, expired licenses not caught | Fix within 4 hours |
| **P1** | High - Blocks workflow, impacts core feature | File upload fails, document doesn't appear | Fix within 1 day |
| **P2** | Medium - Inconvenient, workaround exists | CSS misalignment, slow query, minor validation issue | Fix within 2 days |
| **P3** | Low - Polish, cosmetic, no functional impact | Icon not showing, text alignment | Fix after P0/P1/P2 |

---

## SEVERITY vs PRIORITY

**Severity** (impact to user):
- Critical: User cannot complete task
- High: User can complete task but with friction
- Medium: Annoying but user can work around
- Low: Cosmetic/polish

**Priority** (Phase 6 fix sequence):
- P0: Fix first (blocking issues)
- P1: Fix second (core functionality)
- P2: Fix third (enhancements)
- P3: Fix fourth (polish)

---

## TRIAGE WORKFLOW

1. **QA Reports Error** → Files BUG_REPORT
2. **PM Triages** → Classifies using this matrix
3. **PM Assigns** → Route + Agent + Priority
4. **Agent Fixes** → Phase 6 implementation
5. **QA Verifies** → Updates bug report with verification
6. **PM Signs Off** → Closes ticket

---

## USING THIS MATRIX DURING UAT

When you encounter an error:

1. **Identify the symptom** (what failed)
2. **Find it in the matrix** (left column)
3. **Note the issue type** (second column)
4. **Report with that classification** (in bug report)
5. **PM uses remainder of row** (lane, agent, path)

**Example Workflow:**
```
UAT Test: Upload document
Error: Backend returns 500, file not created
Find in matrix: "500 Internal Server Error"
Issue Type: API Issue
Severity: Critical
Lane: Backend
Agent: Backend Dev
Drift: API Contract Drift
Phase 6 Path: Check logs, identify exception, fix root cause
Priority: P0
```

---

## NOTES

- **This matrix is living** - update as new error patterns emerge
- **Lane assignments are recommendations** - PM may adjust based on availability
- **Severity can be adjusted** - consider context (development vs production)
- **Phase 6 resolution paths are guidelines** - agent may follow different approach
- **Escalate if uncertain** - ask PM before assigning to wrong lane

---

**Last Updated:** 2025-11-16
**Matrix Version:** 1.0
**Approved by:** PM/QA Lead
