# Databricks Setup Guide for OpenAg-DB

This guide explains how to configure OpenAg-DB to use Databricks Delta tables for data storage.

## Overview

OpenAg-DB now uses **Databricks Delta tables** instead of AWS S3 for data storage. This provides:
- Unified data lakehouse architecture
- ACID transactions for data reliability
- Time travel capabilities for historical queries
- SQL-based queries through Databricks SQL warehouses
- Simplified data management

## Prerequisites

1. **Databricks Workspace**: Active Databricks workspace (AWS, Azure, or GCP)
2. **SQL Warehouse**: A running SQL warehouse for query execution
3. **Catalog**: The catalog "equip" should be created in your workspace

## Required Credentials

### GitHub Secrets

Configure the following secrets in your GitHub repository (`Settings` → `Secrets and variables` → `Actions`):

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DATABRICKS_HOST` | Your Databricks workspace hostname | `adb-1234567890123456.7.azuredatabricks.net` |
| `DATABRICKS_TOKEN` | Personal Access Token for authentication | `dapi1234567890abcdef...` |
| `DATABRICKS_HTTP_PATH` | SQL warehouse HTTP path | `/sql/1.0/warehouses/abc123def456` |

### How to Get These Values

#### 1. DATABRICKS_HOST

This is your workspace URL without the protocol:
- Example: If your workspace URL is `https://adb-1234567890123456.7.azuredatabricks.net/`, 
  then `DATABRICKS_HOST` is `adb-1234567890123456.7.azuredatabricks.net`

#### 2. DATABRICKS_TOKEN

Create a Personal Access Token (PAT):

1. Log into your Databricks workspace
2. Click your username in the top right corner
3. Select **User Settings**
4. Go to **Developer** → **Access tokens**
5. Click **Generate new token**
6. Set an appropriate lifetime (e.g., 90 days)
7. Copy the token immediately (you won't be able to see it again)

#### 3. DATABRICKS_HTTP_PATH

Get the SQL warehouse HTTP path:

1. In Databricks, go to **SQL Warehouses**
2. Click on your warehouse
3. Go to the **Connection details** tab
4. Copy the **HTTP Path** value (starts with `/sql/1.0/warehouses/`)

## Catalog Configuration

The application uses the catalog name **"equip"** as specified. Ensure this catalog exists:

```sql
-- Create the catalog if it doesn't exist
CREATE CATALOG IF NOT EXISTS equip;

-- Create the schema for equipment data
CREATE SCHEMA IF NOT EXISTS equip.ag_equipment;

-- Grant appropriate permissions
GRANT USE CATALOG ON CATALOG equip TO your_user_or_group;
GRANT USE SCHEMA ON SCHEMA equip.ag_equipment TO your_user_or_group;
GRANT SELECT, INSERT ON SCHEMA equip.ag_equipment TO your_user_or_group;
```

## Table Structure

The application will create these Delta tables:

1. **equip.ag_equipment.tractors** - Tractor equipment data
2. **equip.ag_equipment.combines** - Combine harvester data
3. **equip.ag_equipment.implements** - Implement equipment data

Tables are created automatically when the scraper runs for the first time.

## Local Development

For local development, set environment variables:

```bash
export DATABRICKS_HOST="your-workspace.databricks.com"
export DATABRICKS_TOKEN="dapi..."
export DATABRICKS_HTTP_PATH="/sql/1.0/warehouses/..."
```

Or create a `.env` file (remember to add it to `.gitignore`):

```env
DATABRICKS_HOST=your-workspace.databricks.com
DATABRICKS_TOKEN=dapi...
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/...
```

## Testing the Connection

You can test the Databricks connection using Python:

```python
from core.databricks_utils import get_table_manager

# Create a table manager instance
manager = get_table_manager()

# Test connection by querying table schema
try:
    schema = manager.get_table_schema("tractors")
    print("Connected successfully!")
    print(f"Schema: {schema}")
except Exception as e:
    print(f"Connection failed: {e}")
finally:
    manager.close()
```

## Architecture Changes

### What Changed

1. **Storage Backend**: AWS S3 Iceberg tables → Databricks Delta tables
2. **Connection Method**: AWS SDK → Databricks SQL Connector
3. **Authentication**: AWS OIDC → Databricks Personal Access Token
4. **Catalog Structure**: AWS S3 paths → Databricks Unity Catalog

### What Stayed the Same

1. **Data Models**: Pydantic models unchanged
2. **API Endpoints**: All FastAPI endpoints remain the same
3. **Scraper Logic**: Validation pipeline unchanged
4. **Tests**: All existing tests still pass

## Code Changes Summary

### New Files

- `src/core/databricks_utils.py` - Databricks Delta table utilities

### Modified Files

- `src/scrapers/pipelines.py` - Updated to use `DatabricksWriterPipeline`
- `src/api/main.py` - Updated comments to reference Databricks
- `.github/workflows/scraper.yml` - Updated to use Databricks credentials
- `pyproject.toml` - Added `databricks-sql-connector` dependency
- `README.md` - Updated documentation

### Archived Files

The following AWS-specific files have been moved to the `archive/` directory:
- `AWS_CONFIGURATION.md`
- `AWS_QUICKSTART.md`
- `terraform/` - Terraform infrastructure code
- `.github/workflows/deploy-api.yml.example`

## Security Considerations

### Token Security

- **Never commit tokens** to source control
- Store tokens as **GitHub Secrets** only
- Set appropriate token expiration (e.g., 90 days)
- Rotate tokens regularly
- Use service principals for production (instead of PATs)

### Access Control

- Grant minimum required permissions to the catalog
- Use separate catalogs/schemas for dev, staging, and prod
- Enable audit logging in Databricks
- Use IP access lists if required

### Network Security

- Use private link connections when possible
- Enable SSL/TLS for all connections (enabled by default)
- Configure VPC/VNet peering for enhanced security

## Troubleshooting

### Connection Errors

**Error**: `Could not connect to Databricks: Invalid access token`
- **Solution**: Verify your `DATABRICKS_TOKEN` is correct and not expired

**Error**: `Catalog 'equip' does not exist`
- **Solution**: Create the catalog using the SQL commands above

**Error**: `SQL warehouse is not running`
- **Solution**: Start your SQL warehouse in the Databricks console

### Permission Errors

**Error**: `User does not have access to catalog`
- **Solution**: Grant appropriate permissions using the GRANT statements above

**Error**: `Cannot create table in schema`
- **Solution**: Ensure you have `CREATE TABLE` permission on the schema

### General Issues

1. **Verify credentials**: Double-check all three secrets are set correctly
2. **Check warehouse status**: Ensure SQL warehouse is running
3. **Review logs**: Check GitHub Actions logs for detailed error messages
4. **Test locally**: Use the connection test script above

## Monitoring

### SQL Warehouse Monitoring

Monitor warehouse usage in Databricks:
1. Go to **SQL Warehouses**
2. Click your warehouse
3. View the **Monitoring** tab for:
   - Query history
   - Performance metrics
   - Costs

### Query History

View all queries executed:
1. Go to **SQL** → **Query History**
2. Filter by user, warehouse, or time range
3. Analyze query performance

## Cost Optimization

1. **Use serverless SQL warehouses** for automatic scaling
2. **Set auto-stop** for warehouses when not in use (default: 10 minutes)
3. **Right-size warehouses** based on workload
4. **Monitor query costs** regularly

## Migration Notes

### What Was Removed

- AWS S3 bucket configuration
- AWS IAM roles and policies
- AWS OIDC authentication
- Apache Iceberg table management
- DuckDB query engine

### Benefits of Databricks

1. **Unified Platform**: No need to manage separate storage, compute, and catalog services
2. **Better Performance**: Optimized Delta Lake format with caching
3. **ACID Transactions**: Data consistency guaranteed
4. **Time Travel**: Query historical versions of data
5. **SQL Analytics**: Built-in query optimization and BI tools

## Support

For issues or questions:
1. Check this documentation
2. Review Databricks documentation: https://docs.databricks.com/
3. Open an issue on the GitHub repository
4. Contact your Databricks administrator

## Additional Resources

- [Databricks SQL Connector Documentation](https://docs.databricks.com/dev-tools/python-sql-connector.html)
- [Delta Lake Documentation](https://docs.delta.io/)
- [Unity Catalog Guide](https://docs.databricks.com/data-governance/unity-catalog/)
- [SQL Warehouses Guide](https://docs.databricks.com/sql/admin/sql-endpoints.html)
