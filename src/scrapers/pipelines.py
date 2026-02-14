"""Scrapy pipelines for processing scraped equipment data.

Pipelines:
1. ValidationPipeline - Validates items against Pydantic models
2. UnityCatalogWriterPipeline - Writes validated data to Unity Catalog Delta tables
"""

from typing import Any

from pydantic import ValidationError
from scrapy import Spider
from scrapy.crawler import Crawler

from core.databricks_utils import TableManager
from core.models import create_equipment


class ValidationPipeline:
    """Validate scraped items using Pydantic models."""

    crawler: Crawler

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "ValidationPipeline":
        """Create pipeline instance from crawler.

        Args:
            crawler: The crawler instance

        Returns:
            ValidationPipeline instance
        """
        pipeline = cls()
        pipeline.crawler = crawler
        return pipeline

    @property
    def spider(self) -> Spider:
        """Get the spider instance from the crawler.

        Returns:
            The spider instance

        Raises:
            RuntimeError: If spider is not set
        """
        if self.crawler.spider is None:
            raise RuntimeError("Spider not initialized")
        return self.crawler.spider

    def process_item(self, item: dict) -> dict:
        """Process and validate an item.

        Args:
            item: Scraped item dictionary

        Returns:
            Validated item or error item for downstream processing

        Note:
            Failed items are marked with '_validation_error' and passed to
            the next pipeline for writing to error tables instead of being dropped.
        """
        try:
            # Create appropriate equipment model based on category
            equipment = create_equipment(item)

            # Convert back to dict for further processing
            validated_item: dict[Any, Any] = equipment.model_dump()

            self.spider.logger.info(
                f"Validated {item.get('make')} {item.get('model')} "
                f"({item.get('category')})"
            )

            return validated_item

        except ValidationError as e:
            self.spider.logger.error(f"Validation error for item {item}: {e}")
            # Mark item as error and pass to writer pipeline instead of dropping
            error_item = {
                **item,  # Keep original data
                "_validation_error": str(e),
                "_error_type": "ValidationError",
            }
            return error_item
        except Exception as e:
            self.spider.logger.error(f"Unexpected error validating item {item}: {e}")
            # Mark item as error and pass to writer pipeline instead of dropping
            error_item = {
                **item,  # Keep original data
                "_validation_error": str(e),
                "_error_type": type(e).__name__,
            }
            return error_item


class UnityCatalogWriterPipeline:
    """Write validated items to Unity Catalog Delta tables.

    This pipeline stages validated equipment data for writing to Unity Catalog
    using DuckDB.
    """

    crawler: Crawler

    def __init__(self) -> None:
        """Initialize the pipeline."""
        self.items_buffer: list[dict] = []
        self.error_items_buffer: list[dict] = []
        self.buffer_size = 100  # Write in batches
        self.table_manager: TableManager | None = None

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "UnityCatalogWriterPipeline":
        """Create pipeline instance from crawler.

        Args:
            crawler: The crawler instance

        Returns:
            UnityCatalogWriterPipeline instance
        """
        pipeline = cls()
        pipeline.crawler = crawler
        return pipeline

    @property
    def spider(self) -> Spider:
        """Get the spider instance from the crawler.

        Returns:
            The spider instance

        Raises:
            RuntimeError: If spider is not set
        """
        if self.crawler.spider is None:
            raise RuntimeError("Spider not initialized")
        return self.crawler.spider

    def open_spider(self) -> None:
        """Called when spider is opened."""
        self.spider.logger.info("Unity Catalog writer pipeline opened")
        self.items_buffer = []
        self.error_items_buffer = []

        # Initialize Unity Catalog connection
        try:
            from core.databricks_utils import get_table_manager

            self.table_manager = get_table_manager()
            self.spider.logger.info("Connected to Unity Catalog")
        except Exception as e:
            self.spider.logger.warning(
                f"Could not connect to Unity Catalog: {e}. "
                "Items will be buffered but not written."
            )

    def close_spider(self) -> None:
        """Called when spider is closed. Flush remaining items."""
        if self.items_buffer:
            self._write_batch()

        if self.error_items_buffer:
            self._write_error_batch()

        # Close Unity Catalog connection
        if self.table_manager:
            try:
                self.table_manager.close()
                self.spider.logger.info("Closed Unity Catalog connection")
            except Exception as e:
                self.spider.logger.warning(
                    f"Error closing Unity Catalog connection: {e}"
                )

        self.spider.logger.info("Unity Catalog writer pipeline closed")

    def process_item(self, item: dict) -> dict:
        """Process an item by adding it to the appropriate buffer.

        Args:
            item: Validated item or error item dictionary

        Returns:
            The item (unchanged)
        """
        # Check if this is an error item
        if "_validation_error" in item:
            self.error_items_buffer.append(item)
            if len(self.error_items_buffer) >= self.buffer_size:
                self._write_error_batch()
        else:
            self.items_buffer.append(item)
            if len(self.items_buffer) >= self.buffer_size:
                self._write_batch()

        return item

    def _write_batch(self) -> None:
        """Write buffered items to Unity Catalog Delta table."""
        self.spider.logger.info(
            f"Writing batch of {len(self.items_buffer)} items to Unity Catalog"
        )

        if not self.table_manager:
            self.spider.logger.warning(
                "Table manager not initialized. Skipping batch write."
            )
            self.items_buffer = []
            return

        try:
            # Group by category in a single pass for efficiency
            items_by_category: dict[str, list[dict]] = {
                "tractor": [],
                "combine": [],
                "implement": [],
            }

            for item in self.items_buffer:
                category = item.get("category")
                if category in items_by_category:
                    items_by_category[category].append(item)

            # Write to appropriate tables
            if items_by_category["tractor"]:
                self.table_manager.insert_records(
                    "tractors", items_by_category["tractor"]
                )
                self.spider.logger.info(
                    f"Wrote {len(items_by_category['tractor'])} tractors"
                )

            if items_by_category["combine"]:
                self.table_manager.insert_records(
                    "combines", items_by_category["combine"]
                )
                self.spider.logger.info(
                    f"Wrote {len(items_by_category['combine'])} combines"
                )

            if items_by_category["implement"]:
                self.table_manager.insert_records(
                    "implements", items_by_category["implement"]
                )
                self.spider.logger.info(
                    f"Wrote {len(items_by_category['implement'])} implements"
                )

        except Exception as e:
            self.spider.logger.error(f"Error writing batch to Unity Catalog: {e}")

        self.items_buffer = []

    def _write_error_batch(self) -> None:
        """Write buffered error items to Unity Catalog error tables."""
        self.spider.logger.info(
            f"Writing batch of {len(self.error_items_buffer)} error items to "
            "Unity Catalog error tables"
        )

        if not self.table_manager:
            self.spider.logger.warning(
                "Table manager not initialized. Skipping error batch write."
            )
            self.error_items_buffer = []
            return

        try:
            # Group by category in a single pass for efficiency
            error_items_by_category: dict[str, list[dict]] = {
                "tractor": [],
                "combine": [],
                "implement": [],
            }

            for error_item in self.error_items_buffer:
                category = error_item.get("category")
                if category in error_items_by_category:
                    error_items_by_category[category].append(error_item)

            # Write to appropriate error tables
            if error_items_by_category["tractor"]:
                self.table_manager.insert_records(
                    "tractors_error", error_items_by_category["tractor"]
                )
                self.spider.logger.info(
                    f"Wrote {len(error_items_by_category['tractor'])} "
                    "failed tractors to error table"
                )

            if error_items_by_category["combine"]:
                self.table_manager.insert_records(
                    "combines_error", error_items_by_category["combine"]
                )
                self.spider.logger.info(
                    f"Wrote {len(error_items_by_category['combine'])} "
                    "failed combines to error table"
                )

            if error_items_by_category["implement"]:
                self.table_manager.insert_records(
                    "implements_error", error_items_by_category["implement"]
                )
                self.spider.logger.info(
                    f"Wrote {len(error_items_by_category['implement'])} "
                    "failed implements to error table"
                )

        except Exception as e:
            self.spider.logger.error(f"Error writing error batch to Unity Catalog: {e}")

        self.error_items_buffer = []
