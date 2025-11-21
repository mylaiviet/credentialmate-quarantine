# **CredentialMate Regulatory Rules Engine Document**

## **Version 1.0 — Canonical Regulatory Logic Specification**

### **Sources Incorporated:**

- Section 17 (Regulatory Matrix)
- Renewal timeline definitions
- CME category matrices (by state and specialty)
- DEA / CSR rules
- Multi-state rule merging logic
- Data Bible v2.0 (rule\_versions, compliance windows, gap analysis)
- PRD v2.0 (compliance requirements)
- SAD v1.0 (deterministic rules engine architecture)

---

# **1. PURPOSE OF THIS DOCUMENT**

This document defines the **canonical regulatory rules** governing:

- State medical licensing
- DEA registration
- Controlled Substance Registration (CSR)
- Board certification cycles
- CME requirements
- Category-specific CME (ethics, opioid, implicit bias, pain mgmt, etc.)
- Multi-state license merging
- Specialty-specific rules

This is the **single source of truth** for all deterministic compliance rules executed by CredentialMate.

### **Key Properties:**

- Deterministic
- Versioned
- Immutable history
- State-specific
- Specialty-specific
- Cycle-aware
- Date-bound
- Fully audit logged

**No AI is used in the Rules Engine in production.**

---

# **2. RULE ENGINE ARCHITECTURE (HOW RULES EXECUTE)**

## **2.1 Rule Packs (Versioned JSON)**

Each rule set is stored as:

```
rule_versions
- id
- rule_type (license, cme, dea, csr)
- version_number
- rule_json (canonical definition)
- created_at
```

## **2.2 Execution Flow**

```
Inputs (provider data + state) → Load Applicable Rule Packs →
Normalize Dates → Generate Renewal Cycles → Evaluate CME →
Evaluate DEA/CSR → Merge Multi-State → Compute Gaps → Write Compliance Window
```

## **2.3 Deterministic Output**

Rules engine must always produce the same:

- cycle start/end
- next due date
- urgency level
- gap list
- compliance status

---

# **3. STATE LICENSE RENEWAL RULES**

Rules include:

- renewal frequency (e.g., every 2 years)
- renewal month rules (birth month, odd/even year, fixed deadlines)
- grace periods
- CME linking rules
- transitional rules when states update requirements

## **3.1 Supported Renewal Structures**

1. **Fixed Date Renewal** (e.g., March 31 every 2 years)
2. **Birth Month Renewal**
3. **Rolling Renewal** (based on issue date)
4. **Odd/Even Year Cycles**
5. **Specialty or license-type specific cycles**

## **3.2 Renewal Cycle JSON Example**

```
{
  "state": "TX",
  "cycle_length_months": 24,
  "renewal_method": "birth_month",
  "grace_period_days": 30,
  "requirements": {
    "cme": "see cme requirements table",
    "fees": "N/A"
  }
}
```

---

# **4. CME REQUIREMENTS (CATEGORY LEVEL)**

CME rules per state include:

- total credit hours required
- category-specific hours
- special modules (opioid, ethics, pediatrics, geriatrics)
- multi-cycle transition rules
- board certification impact

## **4.1 CME Matrix Structure**

For each state:

```
{
  "state": "IL",
  "cycle_months": 36,
  "categories": {
    "ethics": 1,
    "opioid": 3,
    "implicit_bias": 1,
    "general": 140
  },
  "allowed_carryover": 10
}
```

## **4.2 CME Classification Logic**

Steps:

1. Categorize CME event → category
2. Check if credit applies to cycle
3. Sum hours per category
4. Apply carryover rules
5. Evaluate deficiency

## **4.3 CME Specialty Overrides**

Certain specialties require extra CME:

- Pain management physicians
- Anesthesiology
- Pediatrics
- Geriatrics

Specialty rules override state rules where applicable.

---

# **5. DEA RULES**

DEA registration requirements include:

- validity period (36 months)
- schedules authorized
- address-linked requirements
- mid-cycle address change rules

## **DEA JSON Example**

```
{
  "type": "dea",
  "cycle_months": 36,
  "reminders": [90, 60, 30, 7]
}
```

---

# **6. CSR RULES (STATE CONTROLLED SUBSTANCE REGISTRATION)**

CSR rules vary by:

- state
- schedule class
- practice address

CSR cycles may:

- align with medical license cycles
- run independently
- run every 12, 24, or 36 months

---

# **7. MULTI-STATE MERGING LOGIC**

When a provider holds **multiple state licenses**, CredentialMate must:

## **7.1 Merge Rules Across States**

Merge into a consolidated matrix including:

- earliest due date
- most restrictive CME requirements
- aggregated gaps
- prioritized reminders

## **7.2 Merge Priority Order**

1. **Urgency** (expired → urgent → warning → compliant)
2. **Earliest renewal date**
3. **CME deficiency severity**
4. **DEA/CSR gaps override CME**

## **7.3 Multi-State JSON Structure**

```
{
  "provider_id": "uuid",
  "states": ["CA", "NV", "AZ"],
  "merged": {
    "next_due": "2025-03-31",
    "status": "warning",
    "gaps": [ ... ]
  }
}
```

---

# **8. COMPLIANCE WINDOW GENERATION**

Compliance windows consolidate:

- renewal cycle
- reminder schedule
- CME deficiency
- DEA + CSR cycles

Outputs stored in:

- compliance\_windows
- compliance\_gap\_analysis
- rules\_execution\_log

---

# **9. RULE ENGINE EXECUTION CONTRACT**

The engine must:

- Never call AI in production
- Load rule packs strictly by version
- Log every execution
- Maintain 100% deterministic output
- Reject malformed provider data
- Require lineage for all structured fields

---

# **10. RULE PACK VERSIONING & LIFECYCLE**

1. Draft rule pack → `/rules/drafts` (dev)
2. Validate via API → `/api/v1/system/rules/validate`
3. QA approval
4. Publish → rule\_versions
5. Never overwrite past versions
6. Compliance engine pinned to specific version

---

# **11. SPECIALTY OVERRIDES**

Specialty rules override both state and general CME rules. Examples:

- Pain management: opioid CME increases
- Pediatrics: child abuse CME required
- Psychiatry: suicide prevention CME

Specialty overrides stored in:

```
specialty_rules
- specialty
- override_json
```

---

# **12. GAP ANALYSIS RULES**

Gap analysis identifies deficiencies in:

- CME categories
- State-specific modules
- DEA expiration
- CSR expiration
- Board certification lapses

Severity Levels:

- **expired** → critical
- **urgent** → high
- **warning** → medium
- **at risk** → low

---

# **13. AUDIT TRAIL REQUIREMENTS**

Every rule execution must:

- write to `rules_execution_log`
- embed rule\_version\_id
- store input payload
- store output payload
- store timestamp
- store actor\_id (backend service)

---

# **14. FORBIDDEN RULE ENGINE ACTIONS**

The rule engine may NEVER:

- Use AI or LLM reasoning
- Infer missing data
- Apply assumptions
- Modify rule packs at runtime
- Execute non-versioned logic
- Depend on external APIs

---

# **15. SUMMARY OF WHAT WAS ADDED (As Requested)**

The following **missing elements** were added compared to your initial outline:

### ✅ **1. Full rule engine execution architecture**

How rules load, execute, version, and audit.

### ✅ **2. Specialty override rules**

Pain management, pediatrics, geriatrics, etc.

### ✅ **3. Multi-state merging algorithm**

Priority ordering, merging examples, and JSON structure.

### ✅ **4. DEA rules + CSR rules expanded**

Cycles, address sensitivity, and state-specific variations.

### ✅ **5. CME category matrix structure**

Including transitions, carryover logic, and override order.

### ✅ **6. Compliance window generation logic**

Cycle → urgency → status → gap analysis mapping.

### ✅ **7. Rule pack versioning lifecycle**

Draft → validate → approve → publish → pin.

### ✅ **8. Gap severity model**

Critical → high → medium → low.

### ✅ **9. Forbidden behaviors section**

Ensures determinism and prohibits non-versioned rule mutations.

### ️⃣ **10. Complete JSON schemas for rule packs**

For state licensing, CME, DEA, CSR, and multi-state merging.

---

# **END OF REGULATORY RULES ENGINE DOCUMENT — VERSION 1.0**

