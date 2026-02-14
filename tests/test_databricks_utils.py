"""Tests for Unity Catalog utilities using DuckDB."""

from unittest.mock import MagicMock, patch

import duckdb
import pytest

from core.databricks_utils import (
    TableManager,
    UnityCatalogConfig,
    _validate_identifier,
    _validate_sql_type,
    get_table_manager,
)


class TestIdentifierValidation:
    """Test identifier validation functions."""

    def test_validate_identifier_valid(self):
        """Test that valid identifiers pass validation."""
        _validate_identifier("valid_name", "test")
        _validate_identifier("ValidName123", "test")
        _validate_identifier("_private", "test")

    def test_validate_identifier_invalid_start(self):
        """Test that identifiers starting with numbers fail."""
        with pytest.raises(ValueError, match="Invalid test"):
            _validate_identifier("123invalid", "test")

    def test_validate_identifier_special_chars(self):
        """Test that identifiers with special characters fail."""
        with pytest.raises(ValueError, match="Invalid test"):
            _validate_identifier("table-name", "test")
        with pytest.raises(ValueError, match="Invalid test"):
            _validate_identifier("table name", "test")
        with pytest.raises(ValueError, match="Invalid test"):
            _validate_identifier("table;DROP TABLE", "test")

    def test_validate_sql_type_valid(self):
        """Test that valid SQL types pass validation."""
        _validate_sql_type("VARCHAR")
        _validate_sql_type("INTEGER")
        _validate_sql_type("DECIMAL(10,2)")
        _validate_sql_type("VARCHAR(255)")

    def test_validate_sql_type_invalid(self):
        """Test that invalid SQL types fail."""
        with pytest.raises(ValueError, match="Invalid SQL type"):
            _validate_sql_type("VARCHAR; DROP TABLE")
        with pytest.raises(ValueError, match="Invalid SQL type"):
            _validate_sql_type("VARCHAR' OR '1'='1")


class TestTableManager:
    """Test TableManager class."""

    @pytest.fixture
    def config(self):
        """Provide test configuration."""
        return UnityCatalogConfig(
            token="test_token",
            endpoint="https://test.example.com/api/2.1/unity-catalog",
            aws_region="us-east-2",
            catalog_name="test_catalog",
            schema_name="test_schema",
        )

    @pytest.fixture
    def mock_connection(self):
        """Create a mock DuckDB connection."""
        conn = MagicMock(spec=duckdb.DuckDBPyConnection)
        conn.description = [("col1",), ("col2",)]
        return conn

    def test_init(self, config):
        """Test TableManager initialization."""
        manager = TableManager(config)
        assert manager.config == config
        assert manager._connection is None
        assert manager._initialized is False

    @patch("core.databricks_utils.duckdb.connect")
    def test_get_connection_initializes_once(self, mock_connect, config):
        """Test that connection is initialized only once."""
        mock_conn = MagicMock(spec=duckdb.DuckDBPyConnection)
        mock_connect.return_value = mock_conn

        manager = TableManager(config)
        conn1 = manager._get_connection()
        conn2 = manager._get_connection()

        assert conn1 is conn2
        mock_connect.assert_called_once()

    @patch("core.databricks_utils.duckdb.connect")
    def test_create_table_validates_table_name(self, mock_connect, config):
        """Test that create_table validates table name."""
        mock_conn = MagicMock(spec=duckdb.DuckDBPyConnection)
        mock_connect.return_value = mock_conn

        manager = TableManager(config)

        with pytest.raises(ValueError, match="Invalid table_name"):
            manager.create_table("invalid-name", {"col1": "VARCHAR"})

    @patch("core.databricks_utils.duckdb.connect")
    def test_create_table_validates_column_names(self, mock_connect, config):
        """Test that create_table validates column names."""
        mock_conn = MagicMock(spec=duckdb.DuckDBPyConnection)
        mock_connect.return_value = mock_conn

        manager = TableManager(config)

        with pytest.raises(ValueError, match="Invalid column name"):
            manager.create_table("valid_table", {"col-1": "VARCHAR"})

    @patch("core.databricks_utils.duckdb.connect")
    def test_create_table_validates_sql_types(self, mock_connect, config):
        """Test that create_table validates SQL types."""
        mock_conn = MagicMock(spec=duckdb.DuckDBPyConnection)
        mock_connect.return_value = mock_conn

        manager = TableManager(config)

        with pytest.raises(ValueError, match="Invalid SQL type"):
            manager.create_table("valid_table", {"col1": "VARCHAR; DROP"})

    @patch("core.databricks_utils.duckdb.connect")
    def test_insert_records_validates_table_name(self, mock_connect, config):
        """Test that insert_records validates table name."""
        mock_conn = MagicMock(spec=duckdb.DuckDBPyConnection)
        mock_connect.return_value = mock_conn

        manager = TableManager(config)
        records = [{"col1": "value1"}]

        with pytest.raises(ValueError, match="Invalid table_name"):
            manager.insert_records("invalid-name", records)

    @patch("core.databricks_utils.duckdb.connect")
    def test_insert_records_validates_column_names(self, mock_connect, config):
        """Test that insert_records validates column names."""
        mock_conn = MagicMock(spec=duckdb.DuckDBPyConnection)
        mock_connect.return_value = mock_conn

        manager = TableManager(config)
        records = [{"col-1": "value1"}]

        with pytest.raises(ValueError, match="Invalid column name"):
            manager.insert_records("valid_table", records)

    @patch("core.databricks_utils.duckdb.connect")
    def test_insert_records_validates_consistent_schema(self, mock_connect, config):
        """Test that insert_records validates all records have same schema."""
        mock_conn = MagicMock(spec=duckdb.DuckDBPyConnection)
        mock_connect.return_value = mock_conn

        manager = TableManager(config)
        records = [
            {"col1": "value1", "col2": "value2"},
            {"col1": "value1"},  # Missing col2
        ]

        with pytest.raises(ValueError, match="inconsistent schema"):
            manager.insert_records("valid_table", records)

    @patch("core.databricks_utils.duckdb.connect")
    def test_insert_records_empty_list(self, mock_connect, config):
        """Test that insert_records handles empty list."""
        mock_conn = MagicMock(spec=duckdb.DuckDBPyConnection)
        mock_connect.return_value = mock_conn

        manager = TableManager(config)
        manager.insert_records("valid_table", [])

        # Should not raise and should not call executemany
        mock_conn.executemany.assert_not_called()

    @patch("core.databricks_utils.duckdb.connect")
    def test_query_table_validates_table_name(self, mock_connect, config):
        """Test that query_table validates table name."""
        mock_conn = MagicMock(spec=duckdb.DuckDBPyConnection)
        mock_connect.return_value = mock_conn

        manager = TableManager(config)

        with pytest.raises(ValueError, match="Invalid table_name"):
            manager.query_table("invalid-name")

    @patch("core.databricks_utils.duckdb.connect")
    def test_query_table_validates_filter_keys(self, mock_connect, config):
        """Test that query_table validates filter keys against schema."""
        mock_conn = MagicMock(spec=duckdb.DuckDBPyConnection)
        mock_connect.return_value = mock_conn

        # Mock get_table_schema to return specific columns
        with patch.object(TableManager, "get_table_schema") as mock_schema:
            mock_schema.return_value = {"col1": "VARCHAR", "col2": "INTEGER"}

            manager = TableManager(config)

            with pytest.raises(ValueError, match="Invalid filter column"):
                manager.query_table("valid_table", {"invalid_col": "value"})

    @patch("core.databricks_utils.duckdb.connect")
    def test_get_table_history_validates_limit(self, mock_connect, config):
        """Test that get_table_history validates limit parameter."""
        mock_conn = MagicMock(spec=duckdb.DuckDBPyConnection)
        mock_connect.return_value = mock_conn

        manager = TableManager(config)

        with pytest.raises(ValueError, match="limit must be a positive integer"):
            manager.get_table_history("valid_table", limit=-1)

        with pytest.raises(ValueError, match="limit must be a positive integer"):
            manager.get_table_history("valid_table", limit=0)

    def test_close(self, config):
        """Test that close method properly closes connection."""
        with patch("core.databricks_utils.duckdb.connect") as mock_connect:
            mock_conn = MagicMock(spec=duckdb.DuckDBPyConnection)
            mock_connect.return_value = mock_conn

            manager = TableManager(config)
            manager._get_connection()  # Initialize connection
            manager.close()

            mock_conn.close.assert_called_once()
            assert manager._connection is None
            assert manager._initialized is False


class TestGetTableManager:
    """Test get_table_manager function."""

    def test_missing_token(self):
        """Test that missing token raises ValueError."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="DATABRICKS_TOKEN"):
                get_table_manager()

    def test_missing_endpoint(self):
        """Test that missing endpoint raises ValueError."""
        with patch.dict("os.environ", {"DATABRICKS_TOKEN": "test"}, clear=True):
            with pytest.raises(ValueError, match="DATABRICKS_HOST"):
                get_table_manager()

    def test_endpoint_formatting_no_protocol(self):
        """Test that endpoint without protocol is formatted correctly."""
        with patch.dict(
            "os.environ",
            {
                "DATABRICKS_TOKEN": "test_token",
                "DATABRICKS_HOST": "example.com",
            },
        ):
            manager = get_table_manager()
            assert (
                manager.config.endpoint == "https://example.com/api/2.1/unity-catalog"
            )

    def test_endpoint_formatting_with_protocol(self):
        """Test that endpoint with protocol is formatted correctly."""
        with patch.dict(
            "os.environ",
            {
                "DATABRICKS_TOKEN": "test_token",
                "DATABRICKS_HOST": "https://example.com",
            },
        ):
            manager = get_table_manager()
            assert (
                manager.config.endpoint == "https://example.com/api/2.1/unity-catalog"
            )

    def test_endpoint_already_complete(self):
        """Test that complete endpoint is not modified."""
        with patch.dict(
            "os.environ",
            {
                "DATABRICKS_TOKEN": "test_token",
                "DATABRICKS_HOST": "https://example.com/api/2.1/unity-catalog",
            },
        ):
            manager = get_table_manager()
            assert (
                manager.config.endpoint == "https://example.com/api/2.1/unity-catalog"
            )

    def test_explicit_parameters(self):
        """Test that explicit parameters override environment variables."""
        with patch.dict("os.environ", {}, clear=True):
            manager = get_table_manager(
                token="explicit_token",
                endpoint="https://explicit.com",
                aws_region="eu-west-1",
            )
            assert manager.config.token == "explicit_token"
            assert "explicit.com" in manager.config.endpoint
            assert manager.config.aws_region == "eu-west-1"
