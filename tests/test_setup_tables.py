"""Tests for the Unity Catalog table setup script."""

from unittest.mock import MagicMock, patch

from pydantic import Field

from core.models import Combine, Implement, Sprayer, Tractor
from core.setup_tables import (
    get_schema_from_model,
    pydantic_to_sql_type,
    setup_all_tables,
    setup_error_table,
    setup_table,
)


class TestPydanticToSqlType:
    """Tests for pydantic_to_sql_type function."""

    def test_str_type(self):
        """Test string type conversion."""
        field_info = Field(default=None)
        assert pydantic_to_sql_type(field_info, str) == "VARCHAR"

    def test_int_type(self):
        """Test integer type conversion."""
        field_info = Field(default=None)
        assert pydantic_to_sql_type(field_info, int) == "INTEGER"

    def test_float_type(self):
        """Test float type conversion."""
        field_info = Field(default=None)
        assert pydantic_to_sql_type(field_info, float) == "DOUBLE"

    def test_bool_type(self):
        """Test boolean type conversion."""
        field_info = Field(default=None)
        assert pydantic_to_sql_type(field_info, bool) == "BOOLEAN"


class TestGetSchemaFromModel:
    """Tests for get_schema_from_model function."""

    def test_tractor_schema(self):
        """Test schema extraction from Tractor model."""
        schema = get_schema_from_model(Tractor)

        # Check required fields
        assert "make" in schema
        assert "model" in schema
        assert "category" in schema

        # Check tractor-specific fields
        assert "pto_hp" in schema
        assert "engine_hp" in schema
        assert "transmission_type" in schema

        # Verify types
        assert schema["make"] == "VARCHAR"
        assert schema["pto_hp"] == "DOUBLE"

    def test_combine_schema(self):
        """Test schema extraction from Combine model."""
        schema = get_schema_from_model(Combine)

        # Check required fields
        assert "make" in schema
        assert "model" in schema

        # Check combine-specific fields
        assert "grain_tank_capacity_bu" in schema
        assert "separator_type" in schema

    def test_sprayer_schema(self):
        """Test schema extraction from Sprayer model."""
        schema = get_schema_from_model(Sprayer)

        # Check required fields
        assert "make" in schema

        # Check sprayer-specific fields
        assert "tank_capacity_gal" in schema
        assert "boom_width_ft" in schema

    def test_implement_schema(self):
        """Test schema extraction from Implement model."""
        schema = get_schema_from_model(Implement)

        # Check implement-specific fields
        assert "working_width_ft" in schema
        assert "required_hp_min" in schema


class TestSetupTable:
    """Tests for setup_table function."""

    @patch("core.setup_tables.logger")
    def test_setup_table_success(self, mock_logger):
        """Test successful table setup."""
        mock_table_manager = MagicMock()
        mock_table_manager.create_table.return_value = None

        result = setup_table(mock_table_manager, "test_table", Tractor)

        assert result is True
        mock_table_manager.create_table.assert_called_once()
        call_args = mock_table_manager.create_table.call_args
        assert call_args[0][0] == "test_table"
        assert isinstance(call_args[0][1], dict)

    @patch("core.setup_tables.logger")
    def test_setup_table_failure(self, mock_logger):
        """Test table setup failure handling."""
        mock_table_manager = MagicMock()
        mock_table_manager.create_table.side_effect = Exception("Connection error")

        result = setup_table(mock_table_manager, "test_table", Tractor)

        assert result is False


class TestSetupErrorTable:
    """Tests for setup_error_table function."""

    @patch("core.setup_tables.logger")
    def test_setup_error_table_success(self, mock_logger):
        """Test successful error table setup."""
        mock_table_manager = MagicMock()
        mock_table_manager.create_table.return_value = None

        result = setup_error_table(mock_table_manager, "tractors_error", Tractor)

        assert result is True
        mock_table_manager.create_table.assert_called_once()
        call_args = mock_table_manager.create_table.call_args
        assert call_args[0][0] == "tractors_error"
        schema = call_args[0][1]
        assert isinstance(schema, dict)
        # Verify error fields are present
        assert "_validation_error" in schema
        assert "_error_type" in schema
        assert schema["_validation_error"] == "VARCHAR"
        assert schema["_error_type"] == "VARCHAR"

    @patch("core.setup_tables.logger")
    def test_setup_error_table_has_base_schema(self, mock_logger):
        """Test that error table includes base model schema."""
        mock_table_manager = MagicMock()
        mock_table_manager.create_table.return_value = None

        result = setup_error_table(mock_table_manager, "combines_error", Combine)

        assert result is True
        call_args = mock_table_manager.create_table.call_args
        schema = call_args[0][1]
        # Verify some base fields are present
        assert "make" in schema
        assert "model" in schema
        assert "category" in schema
        # Verify error fields are also present
        assert "_validation_error" in schema
        assert "_error_type" in schema

    @patch("core.setup_tables.logger")
    def test_setup_error_table_failure(self, mock_logger):
        """Test error table setup failure handling."""
        mock_table_manager = MagicMock()
        mock_table_manager.create_table.side_effect = Exception("Connection error")

        result = setup_error_table(mock_table_manager, "tractors_error", Tractor)

        assert result is False


class TestSetupAllTables:
    """Tests for setup_all_tables function."""

    @patch("core.setup_tables.get_table_manager")
    @patch("core.setup_tables.setup_table")
    @patch("core.setup_tables.setup_error_table")
    def test_setup_all_tables_success(
        self, mock_setup_error_table, mock_setup_table, mock_get_table_manager
    ):
        """Test successful setup of all tables."""
        mock_table_manager = MagicMock()
        mock_get_table_manager.return_value = mock_table_manager
        mock_setup_table.return_value = True
        mock_setup_error_table.return_value = True

        result = setup_all_tables()

        assert result == 0
        # Verify setup_table was called for each regular table (4)
        assert mock_setup_table.call_count == 4
        # Verify setup_error_table was called for each error table (4)
        assert mock_setup_error_table.call_count == 4
        mock_table_manager.close.assert_called_once()

    @patch("core.setup_tables.get_table_manager")
    @patch("core.setup_tables.setup_table")
    @patch("core.setup_tables.setup_error_table")
    def test_setup_all_tables_partial_failure(
        self, mock_setup_error_table, mock_setup_table, mock_get_table_manager
    ):
        """Test when some tables fail to setup."""
        mock_table_manager = MagicMock()
        mock_get_table_manager.return_value = mock_table_manager
        # First table succeeds, second fails, etc.
        mock_setup_table.side_effect = [True, False, True, True]
        mock_setup_error_table.return_value = True

        result = setup_all_tables()

        assert result == 1
        mock_table_manager.close.assert_called_once()

    @patch("core.setup_tables.get_table_manager")
    def test_setup_all_tables_connection_error(self, mock_get_table_manager):
        """Test connection error handling."""
        mock_get_table_manager.side_effect = ValueError("Missing DATABRICKS_TOKEN")

        result = setup_all_tables()

        assert result == 1
