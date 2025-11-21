# SHIPFASTV1 UAT BUG REPORT TEMPLATE

**TIMESTAMP:** 2025-11-16T06:20:00Z
**ORIGIN:** credentialmate-app/uat
**UPDATED_FOR:** phase5-step4-uat-support-pack

---

## Instructions for QA Testers

1. **Copy this template** for each bug found
2. **Fill ALL sections** - incomplete reports will be returned
3. **Include screenshots** - UI issues require visual proof
4. **Attach logs** - API/Backend issues require backend logs
5. **Be deterministic** - provide exact reproduction steps
6. **Save as:** `BUG_REPORT_[DATE]_[ISSUE_TYPE]_[BRIEF_TITLE].md`

---

## BUG REPORT FORM

### METADATA
```
Report ID:        [Auto-assigned by PM on review]
Date Reported:    [YYYY-MM-DD HH:MM:SS UTC]
Reported By:      [Tester Name]
Severity:         [ ] Critical  [ ] High  [ ] Medium  [ ] Low
Reproducibility:  [ ] Always    [ ] Often  [ ] Sometimes  [ ] Once
Status:           [ ] New  [ ] Triaged  [ ] Assigned  [ ] Fixed  [ ] Verified
```

---

### ISSUE SUMMARY

**Title:**
[One-line summary of issue. Be specific.]

**Issue Type:**
[ ] UI Issue
[ ] API Issue
[ ] Parsing Issue
[ ] Compliance Issue
[ ] Notification Issue
[ ] Schema Drift Issue
[ ] Data Drift Issue
[ ] RLS Violation Issue

**Description:**
[What is the problem? 2-3 sentences. Be objective.]

---

### REPRODUCTION STEPS

**Preconditions:**
- [ ] User logged in as: [Role/Provider ID]
- [ ] System state: [What should be true before starting? e.g., "Document exists in DB", "Cache cleared"]
- [ ] Environment: [UAT/Local/other]
- [ ] Browser: [Chrome/Firefox/Safari version]

**Steps to Reproduce:**
1. [Specific action]
2. [Specific action]
3. [Specific action]
4. [Expected result NOT achieved]

**Exact API Call (if applicable):**
```
Method: GET / POST / PUT / DELETE
URL: http://localhost:5678/api/...
Headers: { Content-Type: application/json, Authorization: Bearer ... }
Body:
{
  "field": "value"
}
```

**Expected Result:**
[What should happen]

**Actual Result:**
[What actually happened]

---

### EVIDENCE

**Screenshots:**
- [ ] Screenshot 1: [Description] - ATTACHED
- [ ] Screenshot 2: [Description] - ATTACHED
- [ ] Screenshot 3: [Description] - ATTACHED

**Browser Console Errors:**
```
[Copy exact error text from browser console]
```

**Application Logs:**
```
[Relevant log excerpts - get from: docker-compose logs backend]
```

**Database Query Results (if applicable):**
```sql
SELECT * FROM [table] WHERE [condition];
-- [Result set]
```

**API Response (if applicable):**
```json
{
  "status": "error",
  "message": "..."
}
```

---

### ROOT CAUSE ANALYSIS (Filled by PM/Engineer)

**Impact Assessment:**
- [ ] Blocks user workflow
- [ ] Blocks other tests
- [ ] Data integrity risk
- [ ] Security risk
- [ ] Performance issue

**Likely Root Cause:**
[To be filled during triage]

**Affected Component:**
- Route: [e.g., `/dashboard/v2/documents`]
- Component: [e.g., `DocumentList.tsx`]
- Service: [e.g., `document_service.py`]
- Database Table: [e.g., `documents`]

---

### CONTEXT

**What were you testing?**
[Which UAT test case? Reference SHIPFASTV1_UAT_TRACEABILITY_SHEET.csv]

**Test Case ID:**
[e.g., `TC-001-DOC-UPLOAD`]

**Frequency:**
- First occurrence: [Date/Time]
- Last verified: [Date/Time]
- Frequency: [Always happens / After N retries / Intermittent]

**Data Involved:**
- Provider ID: [if applicable]
- Document ID: [if applicable]
- User ID: [if applicable]
- Session ID: [if applicable]

---

### DEPENDENCIES

**Does this block other tests?**
[ ] Yes - Which ones? [List test IDs]
[ ] No

**Does this depend on another bug?**
[ ] Yes - Which one? [Reference other Bug Report ID]
[ ] No

---

### RESOLUTION TRACKING

**Assigned To:**
[Lane: Frontend / Backend / Parsing / Database / Security]
[Agent: Specific engineer name]

**Target Fix Date:**
[YYYY-MM-DD]

**Fix Status:**
- [ ] Not Started
- [ ] In Progress
- [ ] Ready for Review
- [ ] Fixed
- [ ] Tested & Verified

**Fix Summary:**
[What was changed to fix this issue?]

**Verification Method:**
[How will QA verify the fix?]

**Verified By:**
[QA Tester Name & Date]

---

### SIGN-OFF

**QA Tester Sign-Off:**
- Name: _________________________
- Date: _________________________
- Signature: _________________________

**PM/Lead Sign-Off:**
- Name: _________________________
- Date: _________________________
- Signature: _________________________

---

## EXAMPLE COMPLETED REPORT

### METADATA
```
Report ID:        BUG-2025-001
Date Reported:    2025-11-16 14:30:00 UTC
Reported By:      Alice Chen (QA Lead)
Severity:         High
Reproducibility:  Always
Status:           New
```

### ISSUE SUMMARY

**Title:**
Document upload fails with 500 error on PDF files over 10MB

**Issue Type:**
[x] API Issue

**Description:**
When uploading PDF files larger than 10MB, the backend returns HTTP 500 "Internal Server Error". The upload form shows no error message to user, causing confusion.

### REPRODUCTION STEPS

**Preconditions:**
- [x] User logged in as: provider-001
- [x] System state: Fresh UAT environment, upload service running
- [x] Environment: UAT
- [x] Browser: Chrome 131.0

**Steps to Reproduce:**
1. Navigate to http://localhost:3000/dashboard/v2/documents
2. Click "Upload Document" button
3. Select any PDF file larger than 10MB (e.g., 15MB_sample.pdf)
4. Click "Upload"
5. See spinner for 10 seconds, then page shows no error

**Exact API Call:**
```
Method: POST
URL: http://localhost:5678/api/v2/documents/upload
Headers: { Content-Type: multipart/form-data, Authorization: Bearer eyJhbG... }
Body:
{
  "file": [15MB PDF binary],
  "provider_id": "provider-001"
}
```

**Expected Result:**
File uploads successfully, document appears in list with "processing" status

**Actual Result:**
Backend returns 500 error, user sees loading spinner forever, must refresh page, file not created

### EVIDENCE

**Browser Console Errors:**
```
POST http://localhost:5678/api/v2/documents/upload 500 (Internal Server Error)
Uncaught (in promise) Error: Upload failed: 500 Internal Server Error
```

**Application Logs:**
```
2025-11-16 14:31:22.456 ERROR [upload] | Traceback (most recent call last):
  File "app/routers/upload.py", line 45, in upload_document
    await file.read()
MemoryError: Cannot allocate 15MB in memory
```

**Database Query Results:**
```sql
SELECT count(*) FROM documents WHERE provider_id = 'provider-001';
-- Returns: 2 (no new document created)
```

**API Response:**
```json
{
  "detail": "Internal server error"
}
```

### ROOT CAUSE ANALYSIS

**Impact Assessment:**
- [x] Blocks user workflow
- [ ] Blocks other tests
- [x] Data integrity risk
- [ ] Security risk
- [ ] Performance issue

**Likely Root Cause:**
[To be filled during triage]

**Affected Component:**
- Route: `/api/v2/documents/upload`
- Component: `DocumentUpload.tsx` (frontend) & `upload.py` (backend)
- Service: `document_service.py`
- Database Table: `documents`

---

**Last Updated:** 2025-11-16
**Template Version:** 1.0
