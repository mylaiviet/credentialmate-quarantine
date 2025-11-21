# TIMESTAMP: 2025-11-15T00:00:00Z
# ORIGIN: credentialmate-schemas
# PURPOSE: Event schema contracts directory - Phase 1 scaffolding only

# Event Schema Contracts

**Phase 1:** Placeholder directory for event schema contracts.
**Phase 2+:** Event-driven architecture schemas for asynchronous messaging.

---

## Purpose

This directory stores event schema definitions for:
- SNS/SQS message schemas
- CloudWatch event patterns
- Webhook payload schemas
- Event versioning contracts

---

## Directory Structure (Phase 2+)

```
event_schemas/
├── sns_topics/
│   ├── license_expiration.json
│   ├── cme_deadline.json
│   ├── document_processed.json
│   └── compliance_alert.json
├── sqs_queues/
│   ├── notification_queue.json
│   ├── document_processing_queue.json
│   └── email_delivery_queue.json
├── webhooks/
│   ├── license_updated.json
│   └── document_validated.json
└── README.md                      # This file
```

---

## Event Schema Format (Phase 2+)

Event schemas follow this structure:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "License Expiration Event",
  "description": "Published when a license expiration notification is triggered",
  "version": "1.0.0",
  "type": "object",
  "required": ["event_type", "event_id", "timestamp", "payload"],
  "properties": {
    "event_type": {
      "type": "string",
      "const": "license.expiration.warning"
    },
    "event_id": {
      "type": "string",
      "format": "uuid"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "payload": {
      "type": "object",
      "required": ["user_id", "license_id", "days_until_expiration"],
      "properties": {
        "user_id": { "type": "string", "format": "uuid" },
        "license_id": { "type": "string", "format": "uuid" },
        "license_type": { "type": "string" },
        "state": { "type": "string" },
        "expiration_date": { "type": "string", "format": "date" },
        "days_until_expiration": { "type": "integer" }
      }
    }
  }
}
```

---

## Event Types (Phase 2+)

### License Events
- `license.created`
- `license.updated`
- `license.expiration.warning.90d`
- `license.expiration.warning.60d`
- `license.expiration.warning.30d`
- `license.expired`

### CME Events
- `cme.activity.created`
- `cme.activity.validated`
- `cme.deadline.warning`
- `cme.compliance.at_risk`

### Document Events
- `document.uploaded`
- `document.classified`
- `document.parsed`
- `document.validation.required`
- `document.processing.failed`

### Notification Events
- `notification.queued`
- `notification.sent`
- `notification.failed`
- `notification.bounced`

---

## Event Versioning (Phase 2+)

Event schema versioning strategy:
- Include `version` field in all events
- Maintain backward compatibility for 12 months
- Use semantic versioning for event schemas
- Publish schema changes to consumers before deployment

---

## Event Publishing (Phase 2+)

Events are published to AWS SNS topics:
```python
sns_client.publish(
    TopicArn='arn:aws:sns:us-east-1:xxx:license-events',
    Message=json.dumps(event),
    MessageAttributes={
        'event_type': {'DataType': 'String', 'StringValue': 'license.expiration.warning'},
        'version': {'DataType': 'String', 'StringValue': '1.0.0'}
    }
)
```

---

## Event Consumption (Phase 2+)

Events are consumed via SQS queues:
- Notification service subscribes to license/CME events
- Email delivery service subscribes to notification events
- Audit service subscribes to all events for logging

---

## Phase 2+ Requirements

- [ ] Define JSON schemas for all event types
- [ ] Create event versioning policy
- [ ] Add event schema validation to publishers
- [ ] Create event catalog documentation
- [ ] Add schema registry (e.g., AWS EventBridge Schema Registry)
- [ ] Implement event replay capabilities

---

## Related

- See `credentialmate-notification/engine/` for event consumers
- See `credentialmate-app/backend/app/services/` for event publishers
- See `credentialmate-docs/architecture/event_driven.md` for event architecture
