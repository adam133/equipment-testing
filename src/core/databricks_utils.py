"""Utilities for working with Databricks Unity Catalog via DuckDB.

This module provides helper functions for interacting with Unity Catalog
Delta tables using DuckDB for the OpenAg-DB project.
"""

import os
from typing import Any

import duckdb
from pydantic import BaseModel


class UnityCatalogConfig(BaseModel):
    """Configuration for Unity Catalog connection via DuckDB."""

    token: str  # Unity Catalog API token
    endpoint: str  # Unity Catalog endpoint URL
    aws_region: str = "us-east-1"  # AWS region if using AWS
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
        self._connection.execute(f"""
            CREATE SECRET uc (
                TYPE unity_catalog,
                TOKEN '{self.config.token}',
                ENDPOINT '{self.config.endpoint}',
                AWS_REGION '{self.config.aws_region}'
            );
        """)

        # Attach the catalog
        self._connection.execute(f"""
            ATTACH '{self.config.catalog_name}' AS {self.config.catalog_name} (
                TYPE unity_catalog,
                DEFAULT_SCHEMA '{self.config.schema_name}'
            );
        """)

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

        Example:
            schema = {
                "make": "VARCHAR",
                "model": "VARCHAR",
                "year": "INTEGER",
                "category": "VARCHAR",
            }
        """
        conn = self._get_connection()

        # Build CREATE TABLE statement
        columns = [f"{col} {dtype}" for col, dtype in schema.items()]
        columns_str = ", ".join(columns)

        full_table_name = (
            f"{self.config.catalog_name}.{self.config.schema_name}.{table_name}"
        )

        create_stmt = f"""
        CREATE TABLE IF NOT EXISTS {full_table_name} (
            {columns_str}
        );
        """

        conn.execute(create_stmt)

    def upsert_records(self, table_name: str, records: list[dict[str, Any]]) -> None:
        """Insert records into a Delta table.

        Note: True upsert (MERGE) logic would require identifying primary keys.
        This implementation performs INSERT operations.

        Args:
            table_name: Name of the table
            records: List of record dictionaries to insert
        """
        if not records:
            return

        conn = self._get_connection()

        full_table_name = (
            f"{self.config.catalog_name}.{self.config.schema_name}.{table_name}"
        )

        # Get column names from first record
        columns = list(records[0].keys())
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
        """
        conn = self._get_connection()

        full_table_name = (
            f"{self.config.catalog_name}.{self.config.schema_name}.{table_name}"
        )

        query = f"SELECT * FROM {full_table_name}"

        if filters:
            conditions = [f"{key} = ?" for key in filters.keys()]
            where_clause = " AND ".join(conditions)
            query += f" WHERE {where_clause}"
            result = conn.execute(query, list(filters.values())).fetchall()
        else:
            result = conn.execute(query).fetchall()

        # Get column names
        description = conn.description
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
        """
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
            limit: Maximum number of history entries to return

        Returns:
            List of table history entries

        Note:
            This uses Delta Lake's time travel feature to access historical versions.
            History information may be limited depending on table configuration.
        """
        conn = self._get_connection()

        full_table_name = (
            f"{self.config.catalog_name}.{self.config.schema_name}.{table_name}"
        )

        # Query delta log for version history
        # Note: Exact syntax may vary based on DuckDB delta extension version
        try:
            result = conn.execute(
                f"SELECT * FROM delta_log('{full_table_name}') LIMIT {limit}"
            ).fetchall()

            if conn.description:
                columns = [desc[0] for desc in conn.description]
                return [dict(zip(columns, row)) for row in result]
        except Exception:
            # If delta_log is not available, return empty list
            pass

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
        aws_region: AWS region (defaults to us-east-1)

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
        final_endpoint = f"https://{final_endpoint}/api/2.1/unity-catalog"
    elif "/api/2.1/unity-catalog" not in final_endpoint:
        final_endpoint = f"{final_endpoint}/api/2.1/unity-catalog"

    config = UnityCatalogConfig(
        token=final_token,
        endpoint=final_endpoint,
        aws_region=final_aws_region,
    )
    return TableManager(config)
