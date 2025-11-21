# TIMESTAMP: 2025-11-15T00:00:00Z
# ORIGIN: credentialmate-schemas
# PURPOSE: API schema contracts directory - Phase 1 scaffolding only

# API Schema Contracts

**Phase 1:** Placeholder directory for API schema contracts.
**Phase 2+:** OpenAPI specifications and JSON schema contracts for all API endpoints.

---

## Purpose

This directory stores API contract definitions:
- OpenAPI 3.0+ specifications
- Request/response JSON schemas
- API versioning contracts
- Breaking change documentation

---

## Directory Structure (Phase 2+)

```
api_schemas/
├── openapi/
│   ├── v1/
│   │   ├── auth.yaml              # Authentication endpoints
│   │   ├── licenses.yaml          # License management endpoints
│   │   ├── cme_activities.yaml    # CME endpoints
│   │   └── documents.yaml         # Document upload/download endpoints
│   └── v2/                        # Future API version
├── json_schemas/
│   ├── requests/
│   │   ├── license_create.json
│   │   ├── cme_create.json
│   │   └── document_upload.json
│   └── responses/
│       ├── license_response.json
│       ├── cme_response.json
│       └── error_response.json
└── README.md                      # This file
```

---

## OpenAPI Specifications (Phase 2+)

API contracts will be defined using OpenAPI 3.0+ format:

```yaml
openapi: 3.0.0
info:
  title: CredentialMate API
  version: 1.0.0
  description: License and CME credential management

paths:
  /api/v1/licenses:
    get:
      summary: List user licenses
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LicenseList'
```

---

## JSON Schema Validation (Phase 2+)

Request and response validation schemas:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "License Creation Request",
  "type": "object",
  "required": ["license_type", "license_number", "state", "expiration_date"],
  "properties": {
    "license_type": {
      "type": "string",
      "enum": ["MEDICAL_LICENSE", "DEA", "CSR", "BOARD_CERTIFICATION"]
    }
  }
}
```

---

## Contract Testing (Phase 2+)

API contracts should be tested using:
- Pact for consumer-driven contract testing
- OpenAPI validators in integration tests
- JSON schema validators for request/response validation

---

## Versioning Strategy (Phase 2+)

API versioning approach:
- **Major version:** Breaking changes (v1 → v2)
- **Minor version:** Backward-compatible additions (v1.0 → v1.1)
- **Patch version:** Bug fixes (v1.0.0 → v1.0.1)

Maintain previous major versions for 12 months after deprecation notice.

---

## Phase 2+ Requirements

- [ ] Generate OpenAPI specs from FastAPI endpoints
- [ ] Create JSON schemas for all request/response types
- [ ] Add contract testing to CI/CD pipeline
- [ ] Create API documentation portal from OpenAPI specs
- [ ] Add breaking change detection
- [ ] Create API versioning runbook

---

## Related

- See `credentialmate-app/backend/app/routers/` for FastAPI endpoint implementations
- See `credentialmate-docs/api/` for API documentation
- See `/snapshots/` for database schema contracts
