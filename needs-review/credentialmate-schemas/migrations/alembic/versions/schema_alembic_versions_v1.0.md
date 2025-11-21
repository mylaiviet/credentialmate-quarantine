# TIMESTAMP: 2025-11-15T00:00:00Z
# ORIGIN: credentialmate-schemas
# PURPOSE: Alembic versions directory - Phase 1 scaffolding only

# Alembic Migration Versions

**Phase 1:** Placeholder directory for migration version files.
**Phase 2+:** Repository of all database migration scripts.

---

## Purpose

This directory contains Alembic migration version files:
- Each migration represents a database schema change
- Migrations are ordered by revision ID
- Migrations can be applied forward or rolled back

---

## Migration File Naming (Phase 2+)

Migration files follow this format:
```
{revision_id}_{description}.py
```

Example:
```
20251115_120000_create_users_table.py
20251115_130000_add_license_status_column.py
```

---

## Migration Structure (Phase 2+)

Each migration file contains:
```python
"""
Migration description

Revision ID: {revision_id}
Revises: {previous_revision}
Create Date: {timestamp}
"""

def upgrade() -> None:
    # Schema changes to apply
    pass

def downgrade() -> None:
    # Schema changes to rollback
    pass
```

---

## Creating Migrations (Phase 2+)

### Auto-generate from model changes:
```bash
alembic revision --autogenerate -m "description"
```

### Create empty migration:
```bash
alembic revision -m "description"
```

### Apply migrations:
```bash
alembic upgrade head
```

### Rollback migrations:
```bash
alembic downgrade -1  # Rollback one version
alembic downgrade {revision}  # Rollback to specific version
```

---

## Phase 2+ Requirements

- [ ] Implement migration testing before deployment
- [ ] Add data migration utilities
- [ ] Add rollback verification
- [ ] Add migration documentation templates
- [ ] Add migration approval workflow

---

## Related

- See `/snapshots/` for schema version snapshots
- See `../alembic.ini` for Alembic configuration
- See `../env.py` for migration environment setup
