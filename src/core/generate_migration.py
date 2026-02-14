"""Generate SQL migration scripts for Databricks Unity Catalog setup.

This script generates SQL migration files that can be manually executed
in Databricks to create all required tables. This approach avoids CI/CD
issues with external table creation restrictions.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from core.models import Combine, Implement, Sprayer, Tractor

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def pydantic_to_sql_type(field_info: FieldInfo, python_type: Any) -> str:
    """Convert Pydantic field type to SQL type.

    Args:
        field_info: Pydantic field information
        python_type: Python type annotation

    Returns:
        SQL type string
    """
    # Handle Optional types (Union with None)
    origin = getattr(python_type, "__origin__", None)
    if origin is type(None):  # noqa: E721
        return "STRING"

    # Handle Literal types
    if origin is not None:
        origin_name = getattr(origin, "__name__", str(origin))
        if origin_name == "Literal":
            return "STRING"

    # Get actual type if it's a Union (e.g., str | None)
    args = getattr(python_type, "__args__", ())
    if args:
        non_none_types = [arg for arg in args if arg is not type(None)]  # noqa: E721
        if non_none_types:
            python_type = non_none_types[0]

    # Map Python types to Databricks SQL types
    # Use STRING instead of VARCHAR (Databricks native type, no length required)
    type_mapping: dict[type, str] = {
        str: "STRING",
        int: "INT",
        float: "DOUBLE",
        bool: "BOOLEAN",
    }

    # Check if it's a string-based Enum
    if hasattr(python_type, "__mro__"):
        for base in python_type.__mro__:
            if base.__name__ == "StrEnum" or (
                hasattr(base, "__bases__")
                and any(b.__name__ == "str" for b in base.__bases__)
            ):
                return "STRING"

    # Handle datetime
    if hasattr(python_type, "__name__") and python_type.__name__ == "datetime":
        return "TIMESTAMP"

    return type_mapping.get(python_type, "STRING")


def get_schema_from_model(model_class: type[BaseModel]) -> dict[str, str]:
    """Extract SQL schema from a Pydantic model.

    Args:
        model_class: Pydantic model class

    Returns:
        Dictionary mapping column names to SQL types
    """
    schema: dict[str, str] = {}

    for field_name, field_info in model_class.model_fields.items():
        annotation = field_info.annotation
        if annotation is None:
            sql_type = "VARCHAR"
        else:
            sql_type = pydantic_to_sql_type(field_info, annotation)

        schema[field_name] = sql_type

    return schema


def generate_migration_sql() -> str:
    """Generate SQL migration script for all equipment tables.

    Returns:
        SQL script as string
    """
    sql_lines: list[str] = []

    # Header comment
    timestamp = datetime.now().isoformat()
    sql_lines.append(f"-- Generated migration script: {timestamp}")
    sql_lines.append("-- Run this script in Databricks to create all required tables")
    sql_lines.append("-- for equipment data in Unity Catalog")
    sql_lines.append("")

    # Create catalog and schema (if needed)
    sql_lines.append("-- Create catalog (if not exists)")
    sql_lines.append("-- CREATE CATALOG IF NOT EXISTS equip;")
    sql_lines.append("")
    sql_lines.append("-- Create schema")
    sql_lines.append("CREATE SCHEMA IF NOT EXISTS equip.ag_equipment;")
    sql_lines.append("")

    # Define tables and their models
    tables: list[tuple[str, type[BaseModel]]] = [
        ("tractors", Tractor),
        ("combines", Combine),
        ("sprayers", Sprayer),
        ("implements", Implement),
    ]

    # Main equipment tables
    sql_lines.append("-- Main equipment tables")
    sql_lines.append("")

    for table_name, model_class in tables:
        schema_dict = get_schema_from_model(model_class)
        columns = ",\n    ".join(
            [f"{col} {dtype}" for col, dtype in schema_dict.items()]
        )

        sql_lines.append(
            f"CREATE TABLE IF NOT EXISTS equip.ag_equipment.{table_name} ("
        )
        sql_lines.append(f"    {columns}")
        sql_lines.append(")")
        sql_lines.append("USING DELTA;")
        sql_lines.append("")

    # Error tables
    sql_lines.append("-- Error tables (for validation failures)")
    sql_lines.append("")

    error_tables: list[tuple[str, type[BaseModel]]] = [
        ("tractors_error", Tractor),
        ("combines_error", Combine),
        ("sprayers_error", Sprayer),
        ("implements_error", Implement),
    ]

    for error_table_name, model_class in error_tables:
        schema_dict = get_schema_from_model(model_class)
        # Add error tracking fields
        schema_dict["_validation_error"] = "STRING"
        schema_dict["_error_type"] = "STRING"

        columns = ",\n    ".join(
            [f"{col} {dtype}" for col, dtype in schema_dict.items()]
        )

        sql_lines.append(
            f"CREATE TABLE IF NOT EXISTS equip.ag_equipment.{error_table_name} ("
        )
        sql_lines.append(f"    {columns}")
        sql_lines.append(")")
        sql_lines.append("USING DELTA;")
        sql_lines.append("")

    # Verification queries
    sql_lines.append("-- Verification: List all tables")
    sql_lines.append("SELECT table_name FROM equip.ag_equipment")
    sql_lines.append("WHERE table_catalog = 'equip' AND table_schema = 'ag_equipment'")
    sql_lines.append("ORDER BY table_name;")
    sql_lines.append("")

    return "\n".join(sql_lines)


def write_migration_file(
    output_path: str | Path = "migrations/001_create_tables.sql",
) -> Path:
    """Write migration SQL to a file.

    Args:
        output_path: Path where to write the migration file

    Returns:
        Path to the written file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sql_content = generate_migration_sql()

    with open(output_path, "w") as f:
        f.write(sql_content)

    logger.info(f"✓ Migration script generated: {output_path}")
    logger.info(f"  Size: {len(sql_content)} bytes")
    logger.info("")
    logger.info("To apply this migration:")
    logger.info("1. Open Databricks workspace")
    logger.info("2. Create a new SQL Notebook")
    logger.info(f"3. Copy and paste contents of {output_path}")
    logger.info("4. Execute all cells")
    logger.info("")

    return output_path


def main() -> int:
    """Generate migration script and write to file.

    Returns:
        Exit code
    """
    try:
        output_file = write_migration_file()
        logger.info(f"✓ Migration script ready at: {output_file.resolve()}")
        return 0
    except Exception as e:
        logger.error(f"Error generating migration script: {e}")
        import traceback

        logger.debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
