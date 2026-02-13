"""Utilities for working with Unity Catalog via DuckDB.

This module provides helper functions for interacting with Unity Catalog
Delta tables using DuckDB for the OpenAg-DB project. Unity Catalog can be
hosted on Databricks, or run as an open-source server.
"""

import os
import re
from typing import Any
from urllib.parse import urlparse, urlunparse

import duckdb
from pydantic import BaseModel


def _validate_identifier(identifier: str, name: str = "identifier") -> None:
    """Validate that an identifier is safe to use in SQL.
    
    Args:
        identifier: The identifier to validate (table name, column name, etc.)
        name: Description of the identifier for error messages
        
    Raises:
        ValueError: If identifier contains invalid characters
    """
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        raise ValueError(
            f"Invalid {name}: '{identifier}'. Must contain only alphanumeric "
            "characters and underscores, and start with a letter or underscore."
        )


def _validate_sql_type(sql_type: str) -> None:
    """Validate that a SQL type is safe to use.
    
    Args:
        sql_type: The SQL type to validate
        
    Raises:
        ValueError: If SQL type contains invalid characters
    """
    # Allow common SQL types with optional parameters
    if not re.match(r'^[A-Z_][A-Z0-9_]*(\([0-9,\s]+\))?$', sql_type, re.IGNORECASE):
        raise ValueError(
            f"Invalid SQL type: '{sql_type}'. Must be a valid SQL type name."
        )


class UnityCatalogConfig(BaseModel):
    """Configuration for Unity Catalog connection via DuckDB."""

    token: str  # Unity Catalog API token
    endpoint: str  # Unity Catalog endpoint URL
    aws_region: str = "us-east-1"  # Cloud region (AWS/Azure/GCP)
    catalog_name: str = "equip"
    schema_name: str = "ag_equipment"


class TableManager:
    """Manages Unity Catalog Delta table operations via DuckDB.

    This class provides methods to create, update, and query Delta tables
    for agricultural equipment data using DuckDB's Unity Catalog extension.
    """

    def __init__(self, config: UnityCatalogConfig):
        """Initialize the table manager.

        Args:
            config: Unity Catalog configuration
        """
        self.config = config
        self._connection: duckdb.DuckDBPyConnection | None = None
        self._initialized = False

    def _get_connection(self) -> duckdb.DuckDBPyConnection:
        """Get or create the DuckDB connection with Unity Catalog.

        Returns:
            DuckDB connection instance
        """
        if self._connection is None:
            self._connection = duckdb.connect()
            self._initialize_unity_catalog()
        return self._connection

    def _initialize_unity_catalog(self) -> None:
        """Initialize Unity Catalog extensions and connection."""
        if self._initialized or self._connection is None:
            return

        # Install and load required extensions
        self._connection.execute("INSTALL delta;")
        self._connection.execute("INSTALL unity_catalog;")
        self._connection.execute("LOAD delta;")
        self._connection.execute("LOAD unity_catalog;")

        # Create Unity Catalog secret for authentication
        # Use parameterized query to prevent SQL injection
        self._connection.execute(
            """
            CREATE SECRET uc (
                TYPE unity_catalog,
                TOKEN ?,
                ENDPOINT ?,
                AWS_REGION ?
            );
            """,
            [self.config.token, self.config.endpoint, self.config.aws_region],
        )

        # Validate catalog name before using it in SQL
        _validate_identifier(self.config.catalog_name, "catalog_name")
        _validate_identifier(self.config.schema_name, "schema_name")

        # Attach the catalog
        self._connection.execute(
            f"""
            ATTACH '{self.config.catalog_name}' AS {self.config.catalog_name} (
                TYPE unity_catalog,
                DEFAULT_SCHEMA '{self.config.schema_name}'
            );
            """
        )

        self._initialized = True

    def close(self) -> None:
        """Close the DuckDB connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            self._initialized = False

    def create_table(self, table_name: str, schema: dict[str, Any]) -> None:
        """Create a new Delta table in Unity Catalog.

        Args:
            table_name: Name of the table to create
            schema: Table schema definition (dict mapping column names to SQL types)

        Raises:
            ValueError: If table_name or schema contains invalid identifiers

        Example:
            schema = {
                "make": "VARCHAR",
                "model": "VARCHAR",
                "year": "INTEGER",
                "category": "VARCHAR",
            }
        """
        # Validate table name
        _validate_identifier(table_name, "table_name")
        
        conn = self._get_connection()

        # Validate column names and types, then build CREATE TABLE statement
        validated_columns = []
        for col, dtype in schema.items():
            _validate_identifier(col, f"column name '{col}'")
            _validate_sql_type(dtype)
            validated_columns.append(f"{col} {dtype}")
        
        columns_str = ", ".join(validated_columns)

        full_table_name = (
            f"{self.config.catalog_name}.{self.config.schema_name}.{table_name}"
        )

        create_stmt = f"""
        CREATE TABLE IF NOT EXISTS {full_table_name} (
            {columns_str}
        );
        """

        conn.execute(create_stmt)

    def insert_records(self, table_name: str, records: list[dict[str, Any]]) -> None:
        """Insert records into a Delta table.

        Args:
            table_name: Name of the table
            records: List of record dictionaries to insert

        Raises:
            ValueError: If table_name or column names contain invalid characters,
                       or if records have inconsistent schemas
        
        Note:
            All records must have the same set of keys. For upsert behavior
            (update if exists, insert if not), use MERGE logic separately.
        """
        if not records:
            return

        # Validate table name
        _validate_identifier(table_name, "table_name")
        
        conn = self._get_connection()

        full_table_name = (
            f"{self.config.catalog_name}.{self.config.schema_name}.{table_name}"
        )

        # Get column names from first record and validate all records have same keys
        columns = list(records[0].keys())
        for col in columns:
            _validate_identifier(col, f"column name '{col}'")
        
        # Validate that all records have the same keys
        first_keys = set(records[0].keys())
        for i, record in enumerate(records[1:], start=1):
            record_keys = set(record.keys())
            if record_keys != first_keys:
                missing = first_keys - record_keys
                extra = record_keys - first_keys
                error_msg = f"Record at index {i} has inconsistent schema. "
                if missing:
                    error_msg += f"Missing keys: {missing}. "
                if extra:
                    error_msg += f"Extra keys: {extra}."
                raise ValueError(error_msg)
        
        columns_str = ", ".join(columns)
        placeholders = ", ".join(["?" for _ in columns])

        insert_stmt = f"""
        INSERT INTO {full_table_name} ({columns_str})
        VALUES ({placeholders});
        """

        # Prepare data as list of tuples
        data = [tuple(record[col] for col in columns) for record in records]

        # Execute batch insert
        conn.executemany(insert_stmt, data)

    def query_table(
        self, table_name: str, filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Query records from a Delta table.

        Args:
            table_name: Name of the table to query
            filters: Optional filter conditions (simple key-value pairs)

        Returns:
            List of matching records as dictionaries
            
        Raises:
            ValueError: If table_name or filter keys contain invalid characters
        """
        # Validate table name
        _validate_identifier(table_name, "table_name")
        
        conn = self._get_connection()

        full_table_name = (
            f"{self.config.catalog_name}.{self.config.schema_name}.{table_name}"
        )

        query = f"SELECT * FROM {full_table_name}"
        params: list[Any] = []

        if filters:
            # Validate filter keys against the actual table schema to prevent
            # SQL injection via column names
            try:
                schema = self.get_table_schema(table_name)
                valid_columns = set(schema.keys())
            except Exception as e:
                raise ValueError(
                    f"Unable to validate filter columns for table '{table_name}': {e}"
                ) from e

            invalid_keys = [key for key in filters.keys() if key not in valid_columns]
            if invalid_keys:
                raise ValueError(
                    f"Invalid filter column(s) for table '{table_name}': "
                    f"{', '.join(invalid_keys)}"
                )

            conditions: list[str] = []
            for key, value in filters.items():
                conditions.append(f"{key} = ?")
                params.append(value)

            where_clause = " AND ".join(conditions)
            query += f" WHERE {where_clause}"

        cursor = conn.execute(query, params) if params else conn.execute(query)
        result = cursor.fetchall()

        # Get column names
        description = cursor.description
        if description:
            columns = [desc[0] for desc in description]
            # Convert to list of dicts
            return [dict(zip(columns, row)) for row in result]

        return []

    def get_table_schema(self, table_name: str) -> dict[str, str]:
        """Get the schema of a table.

        Args:
            table_name: Name of the table

        Returns:
            Dictionary mapping column names to types
            
        Raises:
            ValueError: If table_name contains invalid characters
        """
        # Validate table name
        _validate_identifier(table_name, "table_name")
        
        conn = self._get_connection()

        full_table_name = (
            f"{self.config.catalog_name}.{self.config.schema_name}.{table_name}"
        )

        result = conn.execute(f"DESCRIBE {full_table_name}").fetchall()

        schema = {}
        for row in result:
            col_name = row[0]
            col_type = row[1]
            schema[col_name] = col_type

        return schema

    def get_table_history(
        self, table_name: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get the history of a Delta table for time travel queries.

        Args:
            table_name: Name of the table
            limit: Maximum number of history entries to return (must be positive integer)

        Returns:
            List of table history entries
            
        Raises:
            ValueError: If table_name contains invalid characters or limit is invalid

        Note:
            This uses Delta Lake's time travel feature to access historical versions.
            History information may be limited depending on table configuration.
        """
        # Validate table name and limit
        _validate_identifier(table_name, "table_name")
        if not isinstance(limit, int) or limit < 1:
            raise ValueError(f"limit must be a positive integer, got: {limit}")
        
        conn = self._get_connection()

        full_table_name = (
            f"{self.config.catalog_name}.{self.config.schema_name}.{table_name}"
        )

        # Query delta log for version history
        # Note: Exact syntax may vary based on DuckDB delta extension version
        try:
            # Use parameterized query for limit
            result = conn.execute(
                f"SELECT * FROM delta_log('{full_table_name}') LIMIT ?",
                [limit]
            ).fetchall()

            if conn.description:
                columns = [desc[0] for desc in conn.description]
                return [dict(zip(columns, row)) for row in result]
        except duckdb.CatalogException as e:
            # delta_log function not available or table doesn't support it
            # Log the specific error but return empty list gracefully
            import logging
            logging.debug(f"delta_log not available for {full_table_name}: {e}")
            return []
        except Exception as e:
            # Unexpected error - log and re-raise
            import logging
            logging.error(f"Error retrieving table history for {full_table_name}: {e}")
            raise

        return []


def get_table_manager(
    token: str | None = None,
    endpoint: str | None = None,
    aws_region: str | None = None,
) -> TableManager:
    """Get a configured table manager instance.

    Args:
        token: Unity Catalog API token (defaults to DATABRICKS_TOKEN env var)
        endpoint: Unity Catalog endpoint URL (defaults to DATABRICKS_HOST env var)
        aws_region: Cloud region (defaults to us-east-1)

    Returns:
        Configured TableManager instance

    Raises:
        ValueError: If required credentials are missing
    """
    final_token = token if token is not None else os.getenv("DATABRICKS_TOKEN", "")
    final_endpoint = (
        endpoint if endpoint is not None else os.getenv("DATABRICKS_HOST", "")
    )
    final_aws_region = aws_region if aws_region is not None else "us-east-1"

    # Validate required credentials
    if not final_token:
        raise ValueError("Missing required environment variable: DATABRICKS_TOKEN")
    if not final_endpoint:
        raise ValueError("Missing required environment variable: DATABRICKS_HOST")

    # Format endpoint as Unity Catalog API URL if needed
    if not final_endpoint.startswith("http"):
        # No protocol provided, add https and API path
        final_endpoint = f"https://{final_endpoint}/api/2.1/unity-catalog"
    else:
        # Protocol provided, check if API path is present
        parsed = urlparse(final_endpoint)
        if not parsed.path or parsed.path == "/":
            # No path, add the API path
            final_endpoint = f"{final_endpoint.rstrip('/')}/api/2.1/unity-catalog"
        elif not parsed.path.endswith("/api/2.1/unity-catalog"):
            # Has a path but not the correct one
            # Check if it's already a proper Unity Catalog endpoint
            if "/api/2.1/unity-catalog" in parsed.path:
                # Path contains the endpoint somewhere, use as-is
                pass
            else:
                # Append the API path
                final_endpoint = f"{final_endpoint.rstrip('/')}/api/2.1/unity-catalog"

    config = UnityCatalogConfig(
        token=final_token,
        endpoint=final_endpoint,
        aws_region=final_aws_region,
    )
    return TableManager(config)
