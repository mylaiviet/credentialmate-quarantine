# **CredentialMate Notification Architecture Document (Backend Messaging Engine)**
## **Version 1.0 — Complete Notification Pipeline + Backend Messaging System**
### **Sources Incorporated:**
- Section 21 (Provider & Admin Notification UX)
- Section 23 (Backend Messaging Infrastructure)
- LLM-safe content handling rules
- Quiet hours & throttling logic
- TCPA / CAN-SPAM compliance rules
- HIPAA-safe messaging constraints
- Template versioning system
- Data Bible v2.0 (notifications_sent, email_events, bulk_message_jobs)
- SAD v1.0 (Notification Engine architecture)

---
# **1. PURPOSE OF THIS DOCUMENT**
This document defines the **backend notification architecture**, separate from the UX layer. It specifies:
- Message orchestration
- Delivery pipeline
- Template versioning
- Compliance rules (TCPA, CAN-SPAM, HIPAA)
- Quiet hours
- Fallback logic
- Provider preferences
- Event tracking
- Bulk job execution
- LLM-safe message merging (dev-time only)

This ensures all outbound communication is **deterministic**, **compliant**, and **auditable**.

---
# **2. HIGH-LEVEL ARCHITECTURE**
```
Compliance Engine
     ↓
Notification Orchestrator
     ↓
Channel Router (email/sms/in-app)
     ↓
Template Engine (versioned)
     ↓
Delivery Providers (SES/SNS)
     ↓
Tracking + Logging → notifications_sent, email_events
```

---
# **3. NOTIFICATION ORCHESTRATOR**
The orchestrator is a backend subsystem responsible for:
- Determining which message to send
- Selecting channel priority
- Respecting quiet hours
- Applying throttling
- Ensuring message uniqueness (no spam)
- Routing through the correct provider
- Logging all activity

## **3.1 Inputs**
- Compliance engine outputs
- Admin bulk messaging actions
- System alerts (parsing failures, job issues)
- Provider preference settings

## **3.2 Outputs**
- Delivery request to template engine
- Message dispatch request
- Tracking logs

---
# **4. CHANNEL ROUTER**
Defines **channel priority** and fallback rules.

## **4.1 Channel Priority Order**
1. Email (SES)
2. SMS (SNS/Twilio)
3. In-app notification

## **4.2 Fallback Rules**
- If email bounces → SMS
- If SMS undelivered → in-app
- If all channels fail → mark as `failed` and retry after 6 hours

## **4.3 HIPAA Restriction**
- No PHI in SMS
- Limited PHI in email ("minimum necessary")

---
# **5. TEMPLATE ENGINE (VERSIONED)**
## **5.1 Template Structure**
Each template:
```
template_id
version_number
subject
body_text
body_html
placeholders_json
created_at
```

## **5.2 Template Versioning Rules**
- Templates are immutable once published
- Requires version bump for any content change
- QA approval required for new versions
- No AI-generated templates in production

## **5.3 LLM-Safe Merging (Dev-Time Only)**
- Agents assist with template drafting
- All PHI removed before LLM input
- Only humans approve final versions

---
# **6. QUIET HOURS & THROTTLING**
## **6.1 Quiet Hours Model**
Provider-defined settings:
- Block notifications during configured local time (e.g., 10pm–7am)
- Override for urgent expiration-only

## **6.2 Throttling Rules**
- Max 1 message every 6 hours per category
- Max 1 SMS per 24 hours
- Max 1 urgent escalation per cycle

## **6.3 TCPA / CAN-SPAM Enforcement**
- SMS opt-in required
- Opt-out (“STOP”) instantly disables SMS
- Unsubscribe link required for email
- Marketing messages disabled in healthcare context

---
# **7. PROVIDER NOTIFICATION PREFERENCES**
Stored in `notification_preferences`:
- channel_email_enabled
- channel_sms_enabled
- channel_voice_enabled (future)
- quiet_hours_json
- timezone

Preferences enforced at **all pipeline stages**.

---
# **8. DELIVERY PIPELINE (SES/SNS)**
## **8.1 SES Email Delivery**
- DKIM + SPF alignment required
- Feedback loops enabled
- Reputation monitored

Email events tracked in `email_events`:
- delivered
- bounced
- complaint
- opened
- clicked

## **8.2 SMS Delivery (SNS/Twilio)**
- HIPAA minimum-necessary messaging
- STOP/START logic
- Country-specific restrictions

## **8.3 In-App Delivery**
- Stored in DB
- Rendered in frontend notification center

---
# **9. BULK MESSAGE JOBS**
Used for admin communication.

## **9.1 Endpoint:**
- POST /api/v1/admin/bulk-message

## **9.2 Workflow:**
```
Admin → bulk_message_jobs → orchestrator → batched deliveries → logs
```

## **9.3 Safety Controls:**
- Hard cap: 2,000 recipients per batch
- Rate limit: 50 email/minute
- Dedicated SES configuration set
- No PHI allowed in bulk sends

---
# **10. NOTIFICATION LOGGING & TRACKING**
## **10.1 notifications_sent**
Logs each sent message.

Fields:
- provider_id
- channel
- type
- template_version
- sent_at
- delivered
- opened
- clicked
- retry_count
- failure_reason

## **10.2 email_events**
SES event webhook receiver.

## **10.3 audit_logs**
All admin-triggered messages logged here for HIPAA.

---
# **11. ERROR HANDLING PIPELINE**
Standardized error model from API Contract v2.0.

## **11.1 Notification-Specific Errors:**
- EMAIL_BOUNCED
- SMS_BLOCKED
- PROVIDER_OPTOUT
- TEMPLATE_NOT_FOUND
- CHANNEL_RATE_LIMIT
- QUIET_HOURS_BLOCK

## **11.2 Retry Engine**
Retries at: 10m → 1hr → 6hr → 24hr (max)

---
# **12. SECURITY MODEL**
## **12.1 HIPAA Safety**
- Minimum necessary messaging
- PHI never transmitted via SMS
- HTML email sanitized
- Audit logging for every send

## **12.2 SOC2 Controls**
- Immutable logs
- Access controls for admin bulk sends
- Monitoring for failed deliveries

---
# **13. FORBIDDEN BEHAVIORS**
The messaging engine must NEVER:
- Send PHI over non-compliant channels
- Deliver messages outside quiet hours (except urgent)
- Use AI-generated content in production
- Send duplicate notifications
- Skip template versioning
- Modify template history
- Send messages without logging

---
# **14. FUTURE EXTENSIONS**
- Voice reminders (HIPAA-safe IVR)
- WhatsApp messaging
- Provider-specific granular preferences
- Per-state regulatory delivery rules
- Multi-channel analytics dashboard

---
# **15. SUMMARY OF WHAT WAS ADDED (As Requested)**
The following **critical missing areas** were added compared to your original outline:

### ✅ **1. Full channel router + fallback pipeline**
Email → SMS → In-app with failure detection.

### ✅ **2. Template versioning system (immutable)**
Version bumping, approvals, dev-time LLM-only drafting.

### ✅ **3. Throttling + TCPA/CAN-SPAM enforcement**
SMS opt-ins, STOP compliance, unsubscribe rules.

### ✅ **4. Quiet hours model + urgent overrides**
Provider-specific rules with timezone handling.

### ✅ **5. Bulk messaging safety controls**
Rate limits, PHI restrictions, batching logic.

### ✅ **6. Email event tracking and SES feedback loop integration**
Delivered/bounced/complaint hooks.

### ✅ **7. Full logging stack**
notifications_sent, email_events, audit_logs.

### ✅ **8. Message retry engine**
Exponential retry with safety limits.

### ️⃣ **9. Forbidden actions section**
Ensures deterministic, safe, compliant behavior.

### ️⃣ **10. Future extensions planned**
IVR, WhatsApp, state-specific delivery rules.

---
# **END OF NOTIFICATION ARCHITECTURE DOCUMENT — VERSION 1.0**

