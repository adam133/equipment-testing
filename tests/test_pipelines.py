"""Tests for Scrapy pipelines and pipeline configuration."""

import importlib

import pytest
from scrapy import Spider
from scrapy.exceptions import DropItem

from core.models import EquipmentCategory
from scrapers.pipelines import UnityCatalogWriterPipeline, ValidationPipeline


@pytest.fixture
def mock_spider():
    """Create a mock spider for testing."""

    class MockSpider(Spider):
        name = "test_spider"

        def __init__(self):
            super().__init__()

    return MockSpider()


@pytest.fixture
def valid_tractor_item():
    """Create a valid tractor item for testing."""
    return {
        "make": "John Deere",
        "model": "5075E",
        "category": "tractor",
        "series": "5E Series",
        "engine_hp": 75,
        "pto_hp": 65,
        "source_url": "https://example.com/tractor",
    }


@pytest.fixture
def invalid_item():
    """Create an invalid item for testing."""
    return {
        "make": "John Deere",
        # Missing required 'model' field
        "category": "tractor",
    }


class TestValidationPipeline:
    """Tests for the ValidationPipeline."""

    @pytest.fixture
    def pipeline(self):
        """Create a ValidationPipeline instance."""
        return ValidationPipeline()

    def test_process_valid_item(self, pipeline, mock_spider, valid_tractor_item):
        """Test processing a valid item."""
        # Set up the crawler attribute
        from unittest.mock import Mock

        pipeline.crawler = Mock()
        pipeline.crawler.spider = mock_spider

        result = pipeline.process_item(valid_tractor_item)

        # Should return validated item
        assert result is not None
        assert result["make"] == "John Deere"
        assert result["model"] == "5075E"
        assert result["category"] == EquipmentCategory.TRACTOR.value

    def test_process_invalid_item(self, pipeline, mock_spider, invalid_item):
        """Test processing an invalid item raises DropItem."""
        # Set up the crawler attribute
        from unittest.mock import Mock

        pipeline.crawler = Mock()
        pipeline.crawler.spider = mock_spider

        with pytest.raises(DropItem):
            pipeline.process_item(invalid_item)

    def test_process_item_with_extra_fields(self, pipeline, mock_spider):
        """Test that extra fields are handled correctly."""
        # Set up the crawler attribute
        from unittest.mock import Mock

        pipeline.crawler = Mock()
        pipeline.crawler.spider = mock_spider

        item = {
            "make": "John Deere",
            "model": "5075E",
            "category": "tractor",
            "extra_field": "should be ignored",
        }

        result = pipeline.process_item(item)

        # Should validate and strip extra fields per Pydantic model config
        assert result is not None
        assert result["make"] == "John Deere"
        assert result["model"] == "5075E"

    def test_process_combine_item(self, pipeline, mock_spider):
        """Test processing a combine harvester item."""
        # Set up the crawler attribute
        from unittest.mock import Mock

        pipeline.crawler = Mock()
        pipeline.crawler.spider = mock_spider

        item = {
            "make": "Case IH",
            "model": "8250",
            "category": "combine",
            "separator_width_inches": 35,
            "grain_tank_capacity_bu": 300,
            "source_url": "https://example.com/combine",
        }

        result = pipeline.process_item(item)

        assert result is not None
        assert result["make"] == "Case IH"
        assert result["category"] == EquipmentCategory.COMBINE.value
        assert result["separator_width_inches"] == 35

    def test_process_implement_item(self, pipeline, mock_spider):
        """Test processing an implement item."""
        # Set up the crawler attribute
        from unittest.mock import Mock

        pipeline.crawler = Mock()
        pipeline.crawler.spider = mock_spider

        item = {
            "make": "John Deere",
            "model": "1890",
            "category": "implement",
            "working_width_ft": 60,
            "number_of_rows": 24,
            "source_url": "https://example.com/implement",
        }

        result = pipeline.process_item(item)

        assert result is not None
        assert result["make"] == "John Deere"
        assert result["category"] == EquipmentCategory.IMPLEMENT.value
        assert result["working_width_ft"] == 60


class TestUnityCatalogWriterPipeline:
    """Tests for the UnityCatalogWriterPipeline."""

    @pytest.fixture
    def pipeline(self):
        """Create a UnityCatalogWriterPipeline instance."""
        return UnityCatalogWriterPipeline()

    def test_pipeline_initialization(self, pipeline):
        """Test that pipeline initializes correctly."""
        assert pipeline.items_buffer == []
        assert pipeline.buffer_size == 100
        assert pipeline.table_manager is None

    def test_open_spider(self, pipeline, mock_spider):
        """Test open_spider initialization."""
        # Set up the crawler attribute
        from unittest.mock import Mock

        pipeline.crawler = Mock()
        pipeline.crawler.spider = mock_spider

        pipeline.open_spider()

        # Buffer should be reset
        assert pipeline.items_buffer == []

    def test_close_spider(self, pipeline, mock_spider):
        """Test close_spider cleanup."""
        # Set up the crawler attribute
        from unittest.mock import Mock

        pipeline.crawler = Mock()
        pipeline.crawler.spider = mock_spider

        pipeline.open_spider()

        # Add some items to buffer
        pipeline.items_buffer = [{"test": "item"}]

        pipeline.close_spider()

        # Buffer should be cleared after close
        assert len(pipeline.items_buffer) == 0

    def test_process_item_adds_to_buffer(
        self, pipeline, mock_spider, valid_tractor_item
    ):
        """Test that process_item adds items to buffer."""
        # Set up the crawler attribute
        from unittest.mock import Mock

        pipeline.crawler = Mock()
        pipeline.crawler.spider = mock_spider

        pipeline.open_spider()

        result = pipeline.process_item(valid_tractor_item)

        # Should return the item unchanged
        assert result == valid_tractor_item

        # Should add to buffer
        assert len(pipeline.items_buffer) == 1
        assert pipeline.items_buffer[0] == valid_tractor_item

    def test_process_multiple_items(self, pipeline, mock_spider):
        """Test processing multiple items."""
        # Set up the crawler attribute
        from unittest.mock import Mock

        pipeline.crawler = Mock()
        pipeline.crawler.spider = mock_spider

        pipeline.open_spider()

        items = [
            {
                "make": "John Deere",
                "model": f"Model{i}",
                "category": "tractor",
                "source_url": f"https://example.com/{i}",
            }
            for i in range(5)
        ]

        for item in items:
            pipeline.process_item(item)

        # All items should be in buffer
        assert len(pipeline.items_buffer) == 5

    def test_buffer_flush_on_close(self, pipeline, mock_spider, valid_tractor_item):
        """Test that buffer is flushed when spider closes."""
        # Set up the crawler attribute
        from unittest.mock import Mock

        pipeline.crawler = Mock()
        pipeline.crawler.spider = mock_spider

        pipeline.open_spider()
        pipeline.process_item(valid_tractor_item)

        # Buffer should have item
        assert len(pipeline.items_buffer) == 1

        # Close spider (should attempt to flush)
        pipeline.close_spider()

        # After close, buffer should be empty (even if write failed due to no
        # connection). The _write_batch method clears the buffer regardless of
        # write success
        assert len(pipeline.items_buffer) == 0


class TestPipelineConfiguration:
    """Tests for pipeline configuration from settings."""

    def test_pipeline_classes_are_importable(self):
        """Test that all configured pipeline classes can be imported."""
        # Import settings module
        from scrapers import settings

        # Get configured pipelines
        pipelines = settings.ITEM_PIPELINES

        # Verify each pipeline class can be imported
        for pipeline_path in pipelines.keys():
            module_path, class_name = pipeline_path.rsplit(".", 1)

            # Import the module
            module = importlib.import_module(module_path)

            # Verify the class exists
            assert hasattr(module, class_name), (
                f"Module '{module_path}' does not have class '{class_name}'"
            )

            # Get the class
            pipeline_class = getattr(module, class_name)

            # Verify it's a class
            assert isinstance(pipeline_class, type), f"'{pipeline_path}' is not a class"

    def test_validation_pipeline_is_configured(self):
        """Test that ValidationPipeline is in settings."""
        from scrapers import settings

        pipelines = settings.ITEM_PIPELINES

        # Should have ValidationPipeline configured
        assert any("ValidationPipeline" in path for path in pipelines.keys()), (
            "ValidationPipeline not found in ITEM_PIPELINES"
        )

    def test_writer_pipeline_is_configured(self):
        """Test that a writer pipeline is configured."""
        from scrapers import settings

        pipelines = settings.ITEM_PIPELINES

        # Should have a writer pipeline (UnityCatalogWriterPipeline)
        assert any("WriterPipeline" in path for path in pipelines.keys()), (
            "No WriterPipeline found in ITEM_PIPELINES"
        )

    def test_pipeline_priorities_are_correct(self):
        """Test that pipeline priorities are set correctly."""
        from scrapers import settings

        pipelines = settings.ITEM_PIPELINES

        # ValidationPipeline should run first (lower priority number)
        validation_priority = None
        writer_priority = None

        for path, priority in pipelines.items():
            if "ValidationPipeline" in path:
                validation_priority = priority
            elif "WriterPipeline" in path:
                writer_priority = priority

        # Both should be configured
        assert validation_priority is not None, "ValidationPipeline not configured"
        assert writer_priority is not None, "Writer pipeline not configured"

        # Validation should run before writer
        assert validation_priority < writer_priority, (
            "ValidationPipeline should have lower priority (run first) "
            "than WriterPipeline"
        )

    def test_can_instantiate_all_pipelines(self):
        """Test that all configured pipelines can be instantiated."""
        from scrapers import settings

        pipelines = settings.ITEM_PIPELINES

        for pipeline_path in pipelines.keys():
            module_path, class_name = pipeline_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            pipeline_class = getattr(module, class_name)

            # Try to instantiate
            try:
                instance = pipeline_class()
                assert instance is not None
            except Exception as e:
                pytest.fail(f"Failed to instantiate {pipeline_path}: {e}")
