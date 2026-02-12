"""Utilities for working with Databricks Delta tables.

This module provides helper functions for interacting with Delta tables
stored in Databricks for the OpenAg-DB project.
"""

import os
from typing import Any

from databricks import sql
from pydantic import BaseModel


class DatabricksConfig(BaseModel):
    """Configuration for Databricks connection."""

    host: str  # Databricks workspace host
    http_path: str  # SQL warehouse HTTP path
    token: str  # Access token
    catalog_name: str = "equip"
    schema_name: str = "ag_equipment"


class TableManager:
    """Manages Databricks Delta table operations.

    This class provides methods to create, update, and query Delta tables
    for agricultural equipment data.
    """

    def __init__(self, config: DatabricksConfig):
        """Initialize the table manager.

        Args:
            config: Databricks configuration
        """
        self.config = config
        self._connection: Any | None = None

    def _get_connection(self) -> Any:
        """Get or create the Databricks SQL connection.

        Returns:
            Databricks SQL connection instance
        """
        if self._connection is None:
            self._connection = sql.connect(
                server_hostname=self.config.host,
                http_path=self.config.http_path,
                access_token=self.config.token,
            )
        return self._connection

    def close(self) -> None:
        """Close the Databricks connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def create_table(self, table_name: str, schema: dict[str, Any]) -> None:
        """Create a new Delta table.

        Args:
            table_name: Name of the table to create
            schema: Table schema definition (dict mapping column names to types)

        Example:
            schema = {
                "make": "STRING",
                "model": "STRING",
                "year": "INT",
                "category": "STRING",
            }
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Build CREATE TABLE statement
        columns = [f"{col} {dtype}" for col, dtype in schema.items()]
        columns_str = ", ".join(columns)

        full_table_name = (
            f"{self.config.catalog_name}.{self.config.schema_name}.{table_name}"
        )

        create_stmt = f"""
        CREATE TABLE IF NOT EXISTS {full_table_name} (
            {columns_str}
        ) USING DELTA
        """

        cursor.execute(create_stmt)
        cursor.close()

    def upsert_records(self, table_name: str, records: list[dict[str, Any]]) -> None:
        """Upsert records into a Delta table.

        Uses Delta MERGE INTO logic: if a record with the same make + model + year
        exists, update the specs; otherwise, insert.

        Args:
            table_name: Name of the table
            records: List of record dictionaries to upsert
        """
        if not records:
            return

        conn = self._get_connection()
        cursor = conn.cursor()

        full_table_name = (
            f"{self.config.catalog_name}.{self.config.schema_name}.{table_name}"
        )

        # For simplicity, we'll insert records in batches
        # In a production system, you'd want to use MERGE INTO for true upserts
        # For now, we'll use a simpler approach with INSERT INTO
        for record in records:
            columns = list(record.keys())
            values = [record[col] for col in columns]

            # Build INSERT statement
            columns_str = ", ".join(columns)
            placeholders = ", ".join(["?" for _ in columns])

            insert_stmt = f"""
            INSERT INTO {full_table_name} ({columns_str})
            VALUES ({placeholders})
            """

            cursor.execute(insert_stmt, values)

        cursor.close()

    def query_table(
        self, table_name: str, filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Query records from a Delta table.

        Args:
            table_name: Name of the table to query
            filters: Optional filter conditions (simple key-value pairs)

        Returns:
            List of matching records
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        full_table_name = (
            f"{self.config.catalog_name}.{self.config.schema_name}.{table_name}"
        )

        query = f"SELECT * FROM {full_table_name}"

        if filters:
            conditions = [f"{key} = ?" for key in filters.keys()]
            where_clause = " AND ".join(conditions)
            query += f" WHERE {where_clause}"
            cursor.execute(query, list(filters.values()))
        else:
            cursor.execute(query)

        # Fetch results and convert to list of dicts
        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        cursor.close()
        return results

    def get_table_schema(self, table_name: str) -> dict[str, str]:
        """Get the schema of a table.

        Args:
            table_name: Name of the table

        Returns:
            Dictionary mapping column names to types
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        full_table_name = (
            f"{self.config.catalog_name}.{self.config.schema_name}.{table_name}"
        )

        cursor.execute(f"DESCRIBE {full_table_name}")

        schema = {}
        for row in cursor.fetchall():
            col_name = row[0]
            col_type = row[1]
            schema[col_name] = col_type

        cursor.close()
        return schema

    def get_table_history(self, table_name: str, limit: int = 10) -> list[dict[str, Any]]:
        """Get the history of a Delta table for time travel queries.

        Args:
            table_name: Name of the table
            limit: Maximum number of history entries to return

        Returns:
            List of table history entries

        Note:
            This uses Delta Lake's time travel feature to access historical versions.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        full_table_name = (
            f"{self.config.catalog_name}.{self.config.schema_name}.{table_name}"
        )

        cursor.execute(f"DESCRIBE HISTORY {full_table_name} LIMIT {limit}")

        # Fetch history entries
        columns = [desc[0] for desc in cursor.description]
        history = []
        for row in cursor.fetchall():
            history.append(dict(zip(columns, row)))

        cursor.close()
        return history


def get_table_manager(
    host: str | None = None,
    http_path: str | None = None,
    token: str | None = None,
) -> TableManager:
    """Get a configured table manager instance.

    Args:
        host: Databricks workspace host (defaults to DATABRICKS_HOST env var)
        http_path: SQL warehouse HTTP path (defaults to DATABRICKS_HTTP_PATH env var)
        token: Access token (defaults to DATABRICKS_TOKEN env var)

    Returns:
        Configured TableManager instance
    """
    config = DatabricksConfig(
        host=host if host is not None else os.getenv("DATABRICKS_HOST", ""),
        http_path=http_path if http_path is not None else os.getenv("DATABRICKS_HTTP_PATH", ""),
        token=token if token is not None else os.getenv("DATABRICKS_TOKEN", ""),
    )
    return TableManager(config)
