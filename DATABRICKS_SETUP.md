# Unity Catalog Setup Guide for OpenAg-DB

This guide explains how to configure OpenAg-DB to use Unity Catalog Delta tables via DuckDB.

## Overview

OpenAg-DB uses **Unity Catalog Delta tables** accessed through **DuckDB** instead of AWS S3 for data storage. This provides:
- Unified data lakehouse architecture
- ACID transactions for data reliability
- Time travel capabilities for historical queries
- Lightweight embedded database (no separate SQL warehouse needed)
- Direct Unity Catalog REST API integration
- Simplified data management

## Prerequisites

1. **Unity Catalog Server**: Active Unity Catalog server (can be hosted on Databricks, AWS, Azure, GCP, or open-source)
2. **Unity Catalog API Access**: Enabled Unity Catalog with REST API access
3. **Catalog**: The catalog "equip" should be created in your Unity Catalog instance

## Required Credentials

### GitHub Secrets

Configure the following secrets in your GitHub repository (`Settings` → `Secrets and variables` → `Actions`):

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DATABRICKS_HOST` | Unity Catalog endpoint URL | `adb-1234567890123456.7.azuredatabricks.net` or `your-uc-server.com` |
| `DATABRICKS_TOKEN` | Unity Catalog API token | `dapi1234567890abcdef...` |

**Note**: The `DATABRICKS_HOST` and `DATABRICKS_TOKEN` environment variables are used for backward compatibility, but they connect to Unity Catalog (which can be hosted on Databricks or elsewhere). No SQL warehouse is required!

### How to Get These Values

#### 1. DATABRICKS_HOST (Unity Catalog Endpoint)

This is your Unity Catalog endpoint URL without the protocol:
- **If using Databricks**: Your workspace URL (e.g., `adb-1234567890123456.7.azuredatabricks.net`)
- **If using open-source Unity Catalog**: Your server hostname (e.g., `unitycatalog.mycompany.com`)

#### 2. DATABRICKS_TOKEN (Unity Catalog API Token)

Create an API token for Unity Catalog access:

**For Databricks-hosted Unity Catalog:**
1. Log into your Databricks workspace
2. Click your username in the top right corner
3. Select **User Settings**
4. Go to **Developer** → **Access tokens**
5. Click **Generate new token**
6. Set an appropriate lifetime (e.g., 90 days)
7. Copy the token immediately (you won't be able to see it again)

**For open-source Unity Catalog:**
- Follow your Unity Catalog server's authentication setup

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
```

Or create a `.env` file (remember to add it to `.gitignore`):

```env
DATABRICKS_HOST=your-workspace.databricks.com
DATABRICKS_TOKEN=dapi...
```

## Testing the Connection

You can test the Unity Catalog connection using Python with DuckDB:

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

1. **Storage Backend**: AWS S3 Iceberg tables → Unity Catalog Delta tables
2. **Connection Method**: AWS SDK → DuckDB with Unity Catalog extension
3. **Authentication**: AWS OIDC → Unity Catalog API token
4. **Catalog Structure**: AWS S3 paths → Unity Catalog (catalog.schema.table)
5. **Query Engine**: SQL warehouse → DuckDB (embedded, lightweight)

### What Stayed the Same

1. **Data Models**: Pydantic models unchanged
2. **API Endpoints**: All FastAPI endpoints remain the same
3. **Scraper Logic**: Validation pipeline unchanged
4. **Tests**: All existing tests still pass

## Code Changes Summary

### New Files

- `src/core/databricks_utils.py` - Unity Catalog utilities using DuckDB

### Modified Files

- `src/scrapers/pipelines.py` - Updated to use `DatabricksWriterPipeline`
- `src/api/main.py` - Updated comments to reference Unity Catalog
- `.github/workflows/scraper.yml` - Updated to use Unity Catalog credentials (no HTTP_PATH needed)
- `pyproject.toml` - Added `duckdb>=1.0.0` dependency
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
- Enable audit logging in Unity Catalog
- Use IP access lists if required

### Network Security

- Use private link connections when possible
- Enable SSL/TLS for all connections (enabled by default)
- Configure VPC/VNet peering for enhanced security

## Troubleshooting

### Connection Errors

**Error**: `Could not connect to Unity Catalog: Invalid access token`
- **Solution**: Verify your `DATABRICKS_TOKEN` is correct and not expired

**Error**: `Catalog 'equip' does not exist`
- **Solution**: Create the catalog using the SQL commands above

**Error**: `DuckDB extension installation failed`
- **Solution**: Ensure you have internet access for DuckDB to download extensions

### Permission Errors

**Error**: `User does not have access to catalog`
- **Solution**: Grant appropriate permissions using the GRANT statements above

**Error**: `Cannot create table in schema`
- **Solution**: Ensure you have `CREATE TABLE` permission on the schema

### General Issues

1. **Verify credentials**: Double-check both secrets are set correctly
2. **Check catalog exists**: Ensure the "equip" catalog is created
3. **Review logs**: Check GitHub Actions logs for detailed error messages
4. **Test locally**: Use the connection test script above
5. **DuckDB extensions**: Ensure DuckDB can install delta and unity_catalog extensions

## Monitoring

### Unity Catalog Monitoring

Monitor usage in Unity Catalog:
1. Access your Unity Catalog admin interface
2. Navigate to **Data** → **Catalogs**
3. Click on the **equip** catalog
4. View usage statistics and audit logs

### Query History

View all queries executed via Unity Catalog:
1. Check Unity Catalog audit logs for API access patterns
2. Review query history in your Unity Catalog admin interface (if available)

## Cost Optimization

1. **No SQL warehouse costs** - DuckDB runs locally without compute charges
2. **API call limits** - Monitor Unity Catalog REST API usage
3. **Storage costs** - Delta tables stored in cloud storage (S3/Azure/GCS)
4. **Optimize queries** - DuckDB is very efficient for analytical queries

## Migration Notes

### What Was Removed

- AWS S3 bucket configuration
- AWS IAM roles and policies
- AWS OIDC authentication
- Apache Iceberg table management
- DuckDB query engine

### Benefits of DuckDB + Unity Catalog

1. **Lightweight**: No SQL warehouse needed - DuckDB runs embedded in your Python process
2. **Cost Effective**: No compute charges, only storage and API calls
3. **Fast**: DuckDB is highly optimized for analytical queries
4. **ACID Transactions**: Delta Lake format ensures data consistency
5. **Time Travel**: Query historical versions of data via Delta
6. **Unified Governance**: Unity Catalog provides centralized access control and audit logs
7. **No Infrastructure**: No servers to manage or maintain

## Support

For issues or questions:
1. Check this documentation
2. Review Unity Catalog documentation: https://docs.unitycatalog.io/
3. Review DuckDB documentation: https://duckdb.org/docs/
4. Open an issue on the GitHub repository
5. Contact your Unity Catalog administrator

## Additional Resources

- [DuckDB Unity Catalog Extension](https://duckdb.org/docs/stable/core_extensions/unity_catalog)
- [DuckDB Delta Extension](https://duckdb.org/docs/stable/core_extensions/delta)
- [Unity Catalog Documentation](https://docs.unitycatalog.io/)
- [Delta Lake Documentation](https://docs.delta.io/)
- [Unity Catalog DuckDB Integration](https://docs.unitycatalog.io/integrations/unity-catalog-duckdb/)
