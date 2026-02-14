# Database Setup - Migration Script Approach

## Quick Start

```bash
# Generate SQL migration
uv run python -m core.generate_migration

# Execute in Databricks
# 1. Open Databricks workspace
# 2. Create SQL notebook
# 3. Paste migrations/001_create_tables.sql
# 4. Run All
```

## What Changed

Previously: CI/CD attempted to create tables automatically (blocked by workspace config)
Now: Generate SQL migration scripts for manual execution in Databricks

## Files

- **`src/core/generate_migration.py`** - Migration generator script
- **`migrations/001_create_tables.sql`** - Generated SQL (run this in Databricks)
- **`migrations/README.md`** - Detailed documentation
- **`.github/workflows/deploy-production.yml`** - Updated to generate (not execute) migrations

## Workflow

1. **Developer**: Updates Pydantic models → generates migration → commits
2. **CI/CD**: Validates migration can be generated → uploads as artifact
3. **Admin**: Executes migration in Databricks (one-time or on schema changes)
4. **Scrapers**: Run and populate existing tables

## Benefits

✅ No workspace configuration conflicts
✅ Full control over when schema changes apply
✅ SQL scripts can be reviewed before execution
✅ Clear audit trail of schema changes
✅ Works with any Databricks workspace config

## Tables Created

8 tables in `equip.ag_equipment`:
- tractors, combines, sprayers, implements (main data)
- tractors_error, combines_error, sprayers_error, implements_error (validation errors)

See `migrations/README.md` for detailed usage instructions.
