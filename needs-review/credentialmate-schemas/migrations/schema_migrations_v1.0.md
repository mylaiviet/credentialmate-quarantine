# TIMESTAMP: 2025-11-15T00:00:00Z
# ORIGIN: credentialmate-schemas
# PURPOSE: Migrations directory overview - Phase 1 scaffolding only

# Database Migrations

**Phase 1:** Placeholder migration directory structure.
**Phase 2+:** Complete Alembic migration system for database schema evolution.

---

## Purpose

This directory manages database schema migrations:
- Version-controlled schema changes
- Rollback capabilities
- Environment-specific migrations
- Data migration support

---

## Directory Structure

```
migrations/
├── alembic/                # Alembic migration framework
│   ├── versions/           # Migration version files
│   ├── env.py              # Environment configuration
│   └── alembic.ini         # Alembic settings
└── README.md               # This file
```

---

## Migration Workflow (Phase 2+)

### 1. Model Changes
Make changes to SQLAlchemy models in credentialmate-app.

### 2. Generate Migration
```bash
cd credentialmate-schemas/migrations
alembic revision --autogenerate -m "Add user specialty field"
```

### 3. Review Migration
Review generated migration file in `alembic/versions/`.

### 4. Test Migration
```bash
# Apply to test database
alembic upgrade head

# Verify schema
# Run tests

# Test rollback
alembic downgrade -1
```

### 5. Deploy Migration
Apply to staging and production environments.

---

## Best Practices (Phase 2+)

### Migration Safety
- Always review auto-generated migrations
- Test both upgrade and downgrade
- Never modify existing migration files after deployment
- Include data migrations when schema changes affect existing data

### Naming Conventions
- Use descriptive migration names
- Include table name in description
- Example: `add_license_status_column`

### Data Migrations
- Separate data migrations from schema migrations when possible
- Use `op.execute()` for complex data transformations
- Include rollback logic for data changes

---

## Phase 2+ Requirements

- [ ] Set up migration testing in CI/CD
- [ ] Add migration approval workflow
- [ ] Create migration rollback runbooks
- [ ] Add migration monitoring and alerting
- [ ] Implement zero-downtime migration strategies

---

## Related

- See `/snapshots/` for schema version snapshots
- See `credentialmate-app/backend/app/models/` for SQLAlchemy models
- See `credentialmate-docs/runbooks/` for migration runbooks
