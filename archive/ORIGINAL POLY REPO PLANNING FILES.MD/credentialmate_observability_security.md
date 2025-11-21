# **CredentialMate Observability & Security Document**
## **Version 1.0 — SEV Management, Logging, Monitoring, WAF, IAM Drift, SOC2/HIPAA Controls**
### **Sources Incorporated:**
- Section 19 (Observability)
- Section 20 (Security)
- Data Bible v2.0 (audit + change events)
- SAD v1.0 (architecture linkage)
- API Contract v2.0 (error taxonomy)
- AI Governance (immutable logs, drift detection)
- Terraform structure (IAM + VPC)

---
# **1. PURPOSE OF THIS DOCUMENT**
This Observability & Security Document defines the full monitoring, logging, incident response, intrusion detection, and compliance structure for CredentialMate.

It is the **authoritative reference** for:
- SEV0–SEV4 escalation
- Logging & retention rules
- Metrics
- Tracing
- IAM drift detection
- WAF & network security
- Threat detection
- SOC2 & HIPAA audit alignment
- Immutable event capture
- Error classification & remediation

This document is mandatory for engineering, compliance, auditors, and AI agents.

---
# **2. OBSERVABILITY MODEL OVERVIEW**
CredentialMate uses a **three-layer observability model**:
1. **Metrics** (Prometheus, CloudWatch)
2. **Logs** (structured JSON logs)
3. **Traces** (request-scoped identifiers)

These layers feed into dashboards, alerting rules, and automated SEV triggers.

---
# **3. LOGGING ARCHITECTURE**
## **3.1 Logging Principles**
- Structured JSON only
- Timestamped in ISO8601
- `trace_id` attached to every request
- No PHI in logs
- Logs are immutable and append-only

## **3.2 Log Sources**
- Backend (FastAPI logger)
- ECS tasks (stdout/stderr)
- RDS performance logs
- ALB access logs
- Notification events (SES, SNS)
- Parsing job logs
- Compliance engine logs
- Application audit logs

## **3.3 Log Retention Rules**
- Application logs: 30–90 days
- Audit logs: 7 years (HIPAA)
- Change events: 7 years
- Notification logs: 7 years

## **3.4 Log Storage**
- CloudWatch Logs
- Audit logs stored in PostgreSQL (immutable tables)

---
# **4. METRICS SYSTEM (PROMETHEUS + CLOUDWATCH)**
## **4.1 API Metrics**
- Request latency (p50, p95, p99)
- 4xx / 5xx error rate
- Rate of endpoint hits

## **4.2 Compliance Engine Metrics**
- Rule execution duration
- Execution failures
- Window generation counts

## **4.3 Parsing Pipeline Metrics**
- OCR time
- Extraction confidence
- Parsing errors per document

## **4.4 Notification Metrics**
- Email sent/failed
- SMS success rate
- Bounce rate
- Click/open rate

## **4.5 Database Metrics**
- Connections
- CPU / Memory
- Lock wait times
- Slow queries (>200ms)

---
# **5. TRACING ARCHITECTURE**
- Each inbound request gets a `trace_id`
- Propagated through:
  - backend
  - notification engine
  - parsing engine
  - compliance engine
- Included in:
  - logs
  - API responses (error blocks)
  - audit trails

---
# **6. INCIDENT MANAGEMENT (SEV0–SEV4)**
## **6.1 Severity Levels**
### **SEV0 — Critical Outage**
- RDS down
- ECS cluster down
- ALB unreachable

### **SEV1 — Major Degradation**
- 50%+ error rate
- Notification engine failure
- Compliance engine failure

### **SEV2 — Moderate Impact**
- Parsing failures
- RDS slow queries

### **SEV3 — Minor Impact**
- Single endpoint outage
- SES soft bounces

### **SEV4 — Cosmetic Issues**
- UI layout issues
- Minor API latency

## **6.2 Escalation Rules**
- SEV0 → alert engineering + compliance immediately
- SEV1 → engineering within 15 minutes
- SEV2/3 → engineering within 1 hour
- SEV4 → backlog ticket

## **6.3 Incident Logging**
Every incident writes:
- `incident_logs` entry
- trace_id
- environment
- root cause
- resolution
- timestamp

---
# **7. SECURITY MODEL OVERVIEW**
CredentialMate uses a **zero-trust**, **least-privilege**, **defense-in-depth** security model.

---
# **8. IDENTITY & ACCESS MANAGEMENT (IAM)**
## **8.1 IAM Principles**
- No wildcard permissions
- No long-lived keys
- MFA required for all administrators
- ECS tasks use IAM Roles (no credentials)
- Developer access separated from prod access

## **8.2 IAM Drift Detection**
Drift includes:
- Role permissions expanded
- Policies modified without change request
- Unauthorized new IAM users
- Disabled MFA

Detection via:
- AWS Config
- IAM Access Analyzer
- Daily drift scanning workflow

---
# **9. NETWORK SECURITY**
## **9.1 VPC Design**
- Public subnets only host ALB
- Private subnets for ECS + RDS
- No public RDS access

## **9.2 Security Groups**
- Backend accepts ALB-only
- RDS accepts backend-only
- No ingress from the public internet

## **9.3 WAF (Web Application Firewall)**
Rules include:
- SQL injection
- XSS detection
- Rate limiting
- Bad bot blocking
- Geo-blocking (optional)

## **9.4 Shield Standard (Optional)**
DDoS mitigation on ALB.

---
# **10. THREAT DETECTION & INTRUSION MONITORING**
## **10.1 GuardDuty**
Detects threats:
- Suspicious IAM actions
- Possible credentials leaks
- Tor exit nodes
- Malware-like DNS patterns

## **10.2 CloudTrail**
Logs every AWS API call.

## **10.3 RDS Security Monitoring**
- Failed logins
- Role changes
- Privilege escalations

## **10.4 Suspicious Pattern Detection**
Backend identifies:
- Login anomalies
- Excessive failed uploads
- Multi-state parsing failures
- Unusual notification patterns

---
# **11. APPLICATION SECURITY**
## **11.1 API Security**
- JWT auth
- Rate limiting
- RLS + row-level isolation
- Validation on every request
- Deterministic responses

## **11.2 Secrets Management**
- AWS Secrets Manager only
- No secrets in environment variables in CI
- Rotation optional but recommended

---
# **12. SOC2 ALIGNMENT**
## **12.1 Relevant SOC2 Controls**
- CC1: Control environment
- CC6: Logical access
- CC7: Monitoring & anomaly detection
- CC8: Change management
- A1: Availability
- PI1: Processing integrity

## **12.2 Evidence Automatically Collected**
- audit_logs
- change_events
- incident_logs
- CloudTrail events
- RDS logs
- ECS logs

---
# **13. HIPAA ALIGNMENT (164.312 TECHNICAL SAFEGUARDS)**
## **13.1 Access Control**
- RBAC roles
- RLS enforcement
- Session tokens

## **13.2 Audit Controls**
- Immutable audit_logs
- change_events history
- Notification logs

## **13.3 Integrity Controls**
- Versioning for credentials & documents
- Rule pack version locking

## **13.4 Transmission Security**
- TLS 1.2+ enforced
- No plaintext PHI allowed

---
# **14. ERROR CLASSIFICATION & AUTO-MITIGATION**
## **14.1 Error Types**
- 404 NOT_FOUND
- 403 FORBIDDEN
- 500 INTERNAL_ERROR
- 422 VALIDATION_ERROR
- 503 SERVICE_UNAVAILABLE

## **14.2 Automated Agent Guidance**
If error detected:
- Identify classification
- Reference remediation matrix
- Perform only approved actions
- Never attempt schema changes

---
# **15. FORBIDDEN SECURITY ACTIONS**
CredentialMate must NEVER:
- Allow public RDS access
- Log PHI
- Disable audit logs
- Disable MFA
- Allow AI agents access to prod
- Create IAM policies with `*:*`
- Disable RLS

---
# **16. FUTURE EXTENSIONS**
- SIEM integration (Splunk, Datadog)
- Anomaly detection via ML (internal only)
- Multi-region WAF
- Private CA for internal cert rotation
- Tamper-proof audit log sink

---
# **SUMMARY OF WHAT WAS ADDED FOR COMPLETENESS**
Below is the full list of features added beyond your original outline:

### ⭐ **1. Full Logging Architecture (structured JSON, 7-year retention)**
### ⭐ **2. Comprehensive Metrics Catalog (API, OCR, compliance, notifications, DB)**
### ⭐ **3. Request Tracing Model (trace_id propagation)**
### ⭐ **4. Complete SEV0–SEV4 Incident Framework + escalation**
### ⭐ **5. IAM Drift Detection (AWS Config, IAM Access Analyzer)**
### ⭐ **6. WAF + Shield rules**
### ⭐ **7. Threat detection (GuardDuty + CloudTrail)**
### ⭐ **8. RDS security monitoring**
### ⭐ **9. Application-layer security (RLS, API limits)**
### ⭐ **10. SOC2 control mappings (CC6, CC7, PI1, etc.)**
### ⭐ **11. HIPAA 164.312 mapping (access, audit, integrity, transmission)**
### ⭐ **12. Error classification + remediation matrix**
### ⭐ **13. Forbidden security actions section**
### ⭐ **14. Future extension roadmap**

---
# **END OF OBSERVABILITY & SECURITY DOCUMENT — VERSION 1.0**

