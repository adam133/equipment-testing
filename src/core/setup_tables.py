"""Script to create or update Unity Catalog tables for equipment data.

This script ensures all required tables exist in Unity Catalog with the
correct schema before deploying or running scrapers. It uses Pydantic
models to derive the table schemas.
"""

import logging
import sys
from typing import Any

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from core.databricks_utils import TableManager, get_table_manager
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
        return "VARCHAR"

    # Handle Literal types (e.g., Literal[EquipmentCategory.TRACTOR])
    # These are used for discriminated unions and should be VARCHAR
    if origin is not None:
        origin_name = getattr(origin, "__name__", str(origin))
        if origin_name == "Literal":
            return "VARCHAR"

    # Get actual type if it's a Union (e.g., str | None)
    args = getattr(python_type, "__args__", ())
    if args:
        # Filter out None type and get the actual type
        non_none_types = [arg for arg in args if arg is not type(None)]  # noqa: E721
        if non_none_types:
            python_type = non_none_types[0]

    # Map Python types to SQL types
    type_mapping: dict[type, str] = {
        str: "VARCHAR",
        int: "INTEGER",
        float: "DOUBLE",
        bool: "BOOLEAN",
    }

    # Check if it's a string-based Enum (e.g., StrEnum instances)
    if hasattr(python_type, "__mro__"):
        for base in python_type.__mro__:
            if base.__name__ == "StrEnum" or (
                hasattr(base, "__bases__")
                and any(b.__name__ == "str" for b in base.__bases__)
            ):
                return "VARCHAR"

    # Handle datetime
    if hasattr(python_type, "__name__") and python_type.__name__ == "datetime":
        return "TIMESTAMP"

    # Return mapped type or default to VARCHAR
    return type_mapping.get(python_type, "VARCHAR")


def get_schema_from_model(model_class: type[BaseModel]) -> dict[str, str]:
    """Extract SQL schema from a Pydantic model.

    Args:
        model_class: Pydantic model class

    Returns:
        Dictionary mapping column names to SQL types
    """
    schema: dict[str, str] = {}

    for field_name, field_info in model_class.model_fields.items():
        # Get the field's annotation (type)
        annotation = field_info.annotation
        if annotation is None:
            # Default to VARCHAR if no annotation
            sql_type = "VARCHAR"
        else:
            sql_type = pydantic_to_sql_type(field_info, annotation)

        schema[field_name] = sql_type

    return schema


def setup_table(
    table_manager: TableManager, table_name: str, model_class: type[BaseModel]
) -> bool:
    """Create or verify a table exists with the correct schema.

    Args:
        table_manager: TableManager instance
        table_name: Name of the table to create
        model_class: Pydantic model class defining the schema

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Setting up table: {table_name}")

        # Get schema from Pydantic model
        schema = get_schema_from_model(model_class)

        # Log schema for debugging
        logger.debug(f"Schema for {table_name}: {schema}")

        # Create table (IF NOT EXISTS, so safe to run multiple times)
        table_manager.create_table(table_name, schema)

        logger.info(f"✓ Table {table_name} is ready")
        return True

    except Exception as e:
        logger.error(f"✗ Failed to setup table {table_name}: {e}")
        return False


def setup_all_tables() -> int:
    """Create or verify all required tables exist.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger.info("Starting Unity Catalog table setup")

    try:
        # Get table manager
        table_manager = get_table_manager()
        logger.info("Connected to Unity Catalog")

        # Define tables and their models
        tables: list[tuple[str, type[BaseModel]]] = [
            ("tractors", Tractor),
            ("combines", Combine),
            ("sprayers", Sprayer),
            ("implements", Implement),
        ]

        # Track success
        all_success = True

        # Create each table
        for table_name, model_class in tables:
            success = setup_table(table_manager, table_name, model_class)
            if not success:
                all_success = False

        # Close connection
        table_manager.close()
        logger.info("Closed Unity Catalog connection")

        if all_success:
            logger.info("✓ All tables setup successfully")
            return 0
        else:
            logger.error("✗ Some tables failed to setup")
            return 1

    except ValueError as e:
        # Missing credentials
        logger.error(f"Configuration error: {e}")
        logger.error(
            "Please ensure DATABRICKS_HOST and DATABRICKS_TOKEN are set correctly"
        )
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


def main() -> int:
    """Main entry point for the script.

    Returns:
        Exit code
    """
    return setup_all_tables()


if __name__ == "__main__":
    sys.exit(main())
