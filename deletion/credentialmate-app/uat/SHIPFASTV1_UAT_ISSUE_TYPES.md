# SHIPFASTV1 UAT ISSUE TYPES TAXONOMY

**TIMESTAMP:** 2025-11-16T06:15:00Z
**ORIGIN:** credentialmate-app/uat
**UPDATED_FOR:** phase5-step4-uat-support-pack

---

## Purpose
Define all issue categories that testers will encounter during UAT execution. Each issue type maps to a resolution lane and required agent for Phase 6 (Fix & Verify).

---

## Issue Type Definitions

### 1. UI Issue
**Category:** Frontend rendering / UX behavior

**Scope:**
- Component rendering failure
- CSS/styling defects
- Layout breaks
- Navigation issues
- Responsive design failures
- Accessibility problems (WCAG)

**Examples:**
- Document list doesn't render
- Upload button disappears on mobile
- Modal backdrop is misaligned
- Icons not displaying
- Form validation messages missing

**Lane:** Frontend
**Required Agent:** Frontend Developer
**Drift Type:** UI Drift
**Resolution Path:** Fix component/style in Next.js, test in browser, verify with QA

---

### 2. API Issue
**Category:** Backend endpoint failure / contract mismatch

**Scope:**
- 5xx server errors
- Endpoint returns wrong status code
- Response schema mismatch
- Missing headers/CORS issues
- Timeout errors
- Authentication/authorization failures

**Examples:**
- GET /documents returns 500
- POST /upload returns 400 with wrong message
- Response missing required fields
- CORS headers missing
- Token validation fails

**Lane:** Backend
**Required Agent:** Backend Developer
**Drift Type:** API Contract Drift
**Resolution Path:** Debug endpoint in FastAPI, check logs, verify schema, deploy fix, retest

---

### 3. Parsing Issue
**Category:** Document ingestion / OCR / text extraction

**Scope:**
- PDF parsing fails
- OCR produces garbage text
- File format unsupported
- Metadata extraction missing
- Parsing job hangs/timeout
- Page detection fails

**Examples:**
- Scanned PDF returns no text
- Docx file rejected
- Extracted text is corrupted
- Parsing job stuck in "processing"
- Metadata fields empty

**Lane:** Backend (Parsing Service)
**Required Agent:** Parsing Specialist
**Drift Type:** Parsing Logic Drift
**Resolution Path:** Check parser logs, test file directly, update parser config, validate output

---

### 4. Compliance Issue
**Category:** Business rule / policy violation

**Scope:**
- License expiration not flagged
- CME credits miscounted
- Risk assessment wrong
- Retention policy violated
- Audit trail incomplete
- RLS (Row-Level Security) bypass

**Examples:**
- Expired license shows as valid
- CME total doesn't match DB
- Provider marked low-risk when should be high
- Document not deleted after retention period
- User sees data they shouldn't

**Lane:** Backend
**Required Agent:** Compliance Lead / Backend Developer
**Drift Type:** Business Logic Drift
**Resolution Path:** Review business rules, check database constraints, update logic, run compliance checks

---

### 5. Notification Issue
**Category:** Alert/messaging system failure

**Scope:**
- Email not sent
- Push notification missing
- Webhook delivery fails
- Alert threshold not triggered
- Message formatting wrong
- Notification preferences not honored

**Examples:**
- User doesn't receive expiration warning
- Webhook never called after upload
- Notification timestamp wrong
- Message contains HTML tags instead of rendering
- Notification sent to wrong recipient

**Lane:** Backend (Notification Service)
**Required Agent:** Backend Developer
**Drift Type:** Notification Logic Drift
**Resolution Path:** Check notification queue, verify email service, test webhook, update rules

---

### 6. Schema Drift Issue
**Category:** Database or API schema mismatch

**Scope:**
- New column added without migration
- Foreign key constraint violated
- Enum value changed
- Type mismatch (int vs string)
- Index missing causing performance
- JSON schema validation fails

**Examples:**
- Database rejects INSERT due to missing column
- API returns field with old type
- Document.status has unexpected value
- Query returns NULL for expected field
- Foreign key reference broken

**Lane:** Backend
**Required Agent:** Database Admin / Backend Developer
**Drift Type:** Schema Drift (CRITICAL)
**Resolution Path:** Review schema changes, run migrations, verify data integrity, test queries

---

### 7. Data Drift Issue
**Category:** Inconsistent or corrupt data state

**Scope:**
- Duplicate records created
- Orphaned records (FK references deleted parent)
- Data type corruption (unicode, encoding)
- Missing cascade delete
- Stale cache serving old data
- Race condition creating bad state

**Examples:**
- Document record has no associated provider
- Provider appears twice in list
- Upload date shows year 2099
- Cache returns deleted document
- Concurrent uploads create duplicate entries

**Lane:** Backend (Data Team)
**Required Agent:** Database Admin / QA Engineer
**Drift Type:** Data Drift (MEDIUM)
**Resolution Path:** Validate data integrity, run cleanup scripts, fix constraints, clear cache, retest

---

### 8. RLS Violation Issue
**Category:** Row-Level Security / Data Access control failure

**Scope:**
- User sees another user's documents
- Admin controls not enforced
- Provider can modify other provider's data
- Public data exposed as private
- Policy rule not applied

**Examples:**
- Provider A sees Provider B's documents
- Non-admin user can delete any document
- Public API endpoint should require auth
- RLS policy missing in database
- Token not validated in middleware

**Lane:** Backend / Security
**Required Agent:** Security Engineer / Backend Developer
**Drift Type:** RLS Violation (CRITICAL)
**Resolution Path:** Review RLS policies, audit middleware, test auth flows, fix policy, retest with multiple users

---

## Issue Type Decision Tree

```
START: UAT Test Fails
├─ Does it involve rendering/UI?
│  └─ YES → UI Issue
├─ Does it involve HTTP request/response?
│  └─ YES → API Issue
├─ Does it involve document parsing/OCR?
│  └─ YES → Parsing Issue
├─ Does it involve business rules (licenses, CME, compliance)?
│  └─ YES → Compliance Issue
├─ Does it involve alerts/emails/webhooks?
│  └─ YES → Notification Issue
├─ Does it involve database structure/types?
│  └─ YES → Schema Drift Issue
├─ Does it involve bad/inconsistent data?
│  └─ YES → Data Drift Issue
├─ Does it involve security/access control?
│  └─ YES → RLS Violation Issue
└─ UNKNOWN → Escalate to Triage Team
```

---

## Triage Checklist

For each issue reported:

- [ ] Issue type identified
- [ ] Lane assigned
- [ ] Required agent assigned
- [ ] Severity assessed (Critical/High/Medium/Low)
- [ ] Reproducibility confirmed (always/sometimes/once)
- [ ] Dependencies identified (blocks other tests?)
- [ ] Escalation path clear

---

## Notes for QA Testers

1. **Be specific:** Use exact error messages, screenshots, and reproduction steps
2. **Check issue type carefully:** Wrong classification delays Phase 6 fix
3. **Provide context:** What was being tested when issue occurred?
4. **Prioritize critical issues:** RLS, Schema, Compliance first
5. **Flag data drift early:** Hard to fix after test data contaminated

---

**Last Reviewed:** 2025-11-16
**Next Review:** After Phase 5 Step 4 Completion
