# Unity Catalog Table Setup

This directory contains the deployment automation for setting up Unity Catalog tables.

## Overview

The table setup process ensures that all required Delta tables exist in Unity Catalog before scrapers or other components attempt to write data. This prevents runtime errors and ensures proper schema consistency.

## Components

### Script: `src/core/setup_tables.py`

Automated script that:
- Extracts SQL schemas from Pydantic models
- Creates or updates tables in Unity Catalog
- Handles all equipment types (tractors, combines, sprayers, implements)
- Uses idempotent `CREATE TABLE IF NOT EXISTS` statements
- Returns proper exit codes for CI/CD integration

**Usage:**
```bash
# With environment variables set
export DATABRICKS_HOST="your-unity-catalog-host"
export DATABRICKS_TOKEN="your-api-token"
uv run python -m core.setup_tables

# Script will create/verify these tables:
# - equip.ag_equipment.tractors
# - equip.ag_equipment.combines
# - equip.ag_equipment.sprayers
# - equip.ag_equipment.implements
# - equip.ag_equipment.tractors_error
# - equip.ag_equipment.combines_error
# - equip.ag_equipment.sprayers_error
# - equip.ag_equipment.implements_error
```

**Exit Codes:**
- `0`: Success - all tables created/verified
- `1`: Failure - missing credentials or setup error

### Workflow: `deploy-production.yml`

GitHub Actions workflow that runs table setup on deployment:

**Triggers:**
- Push to `main` branch (when core/api/scrapers change)
- Manual workflow dispatch

**Environment:**
- Uses `production` environment
- Requires GitHub secrets:
  - `DATABRICKS_HOST`: Unity Catalog endpoint
  - `DATABRICKS_TOKEN`: Unity Catalog API token

**Steps:**
1. Checkout code
2. Install uv and Python 3.12
3. Install dependencies
4. Run table setup script
5. Verify success

## Schema Mapping

The script automatically maps Pydantic field types to SQL types:

| Pydantic Type | SQL Type |
|---------------|----------|
| `str` | `VARCHAR` |
| `int` | `INTEGER` |
| `float` | `DOUBLE` |
| `bool` | `BOOLEAN` |
| `datetime` | `TIMESTAMP` |
| Enums (StrEnum) | `VARCHAR` |
| Optional types | Same as base type |

## Error Tables

For each equipment type, the script also creates error tables to store validation failures:

**Error Tables:**
- `tractors_error`
- `combines_error`
- `sprayers_error`
- `implements_error`

**Error Table Schema:**
Error tables include all fields from the base equipment model, plus:
- `_validation_error` (VARCHAR): Error message
- `_error_type` (VARCHAR): Error type (e.g., "ValidationError")

These tables allow the scraper to capture and store items that fail validation, enabling debugging and data quality monitoring without losing the original data.

## Adding New Equipment Types

To add a new equipment type:

1. Create Pydantic model in `src/core/models.py`
2. Add table entries in `setup_tables.py`:
   ```python
   tables: list[tuple[str, type[BaseModel]]] = [
       ("tractors", Tractor),
       ("combines", Combine),
       ("sprayers", Sprayer),
       ("implements", Implement),
       ("new_equipment", NewEquipment),  # Add here
   ]
   
   # Also add to error_tables list
   error_tables: list[tuple[str, type[BaseModel]]] = [
       ("tractors_error", Tractor),
       ("combines_error", Combine),
       ("sprayers_error", Sprayer),
       ("implements_error", Implement),
       ("new_equipment_error", NewEquipment),  # Add here
   ]
   ```
3. Run tests: `uv run pytest tests/test_setup_tables.py`
   ```
3. Run tests: `uv run pytest tests/test_setup_tables.py`

## Development

### Running Tests

```bash
# Test table setup logic
uv run pytest tests/test_setup_tables.py -v

# All tests
uv run pytest tests/ -v
```

### Code Quality

```bash
# Linting
uv run ruff check src/core/setup_tables.py

# Type checking
uv run mypy src/core/setup_tables.py

# Format
uv run ruff format src/core/setup_tables.py
```

## Security

- **Never** commit Unity Catalog credentials to source control
- Store credentials as GitHub Secrets
- Use environment-specific secrets (dev, staging, production)
- Rotate tokens regularly
- Monitor Unity Catalog audit logs

## Troubleshooting

### Missing Credentials Error

```
ERROR - Configuration error: Missing required environment variable: DATABRICKS_TOKEN
```

**Solution:** Ensure both `DATABRICKS_HOST` and `DATABRICKS_TOKEN` are set.

### Catalog Not Found Error

```
ERROR - Failed to setup table tractors: Catalog 'equip' does not exist
```

**Solution:** Create the catalog and schema in Unity Catalog:
```sql
CREATE CATALOG IF NOT EXISTS equip;
CREATE SCHEMA IF NOT EXISTS equip.ag_equipment;
```

### Connection Error

```
ERROR - Could not connect to Unity Catalog: Invalid access token
```

**Solution:** Verify token is correct and not expired. Generate a new token if needed.

## Monitoring

After deployment, verify table creation:

1. Check workflow logs in GitHub Actions
2. Query Unity Catalog to verify tables exist:
   ```sql
   SHOW TABLES IN equip.ag_equipment;
   ```
3. Review Unity Catalog audit logs for API access

## References

- [Unity Catalog Documentation](https://docs.unitycatalog.io/)
- [DuckDB Unity Catalog Extension](https://duckdb.org/docs/stable/core_extensions/unity_catalog)
- [DATABRICKS_SETUP.md](../../DATABRICKS_SETUP.md) - Unity Catalog configuration guide
