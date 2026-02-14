"""Scrapy pipelines for processing scraped equipment data.

Pipelines:
1. ValidationPipeline - Validates items against Pydantic models
2. UnityCatalogWriterPipeline - Writes validated data to Unity Catalog Delta tables
"""

from typing import Any

from pydantic import ValidationError
from scrapy import Spider
from scrapy.crawler import Crawler
from scrapy.exceptions import DropItem

from core.databricks_utils import TableManager
from core.models import create_equipment


class ValidationPipeline:
    """Validate scraped items using Pydantic models."""

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

    def process_item(self, item: dict) -> dict:
        """Process and validate an item.

        Args:
            item: Scraped item dictionary

        Returns:
            Validated item

        Raises:
            DropItem: If validation fails
        """
        try:
            # Create appropriate equipment model based on category
            equipment = create_equipment(item)

            # Convert back to dict for further processing
            validated_item: dict[Any, Any] = equipment.model_dump()

            self.crawler.spider.logger.info(
                f"Validated {item.get('make')} {item.get('model')} "
                f"({item.get('category')})"
            )

            return validated_item

        except ValidationError as e:
            self.crawler.spider.logger.error(f"Validation error for item {item}: {e}")
            raise DropItem(f"Validation failed: {e}") from e
        except Exception as e:
            self.crawler.spider.logger.error(
                f"Unexpected error validating item {item}: {e}"
            )
            raise DropItem(f"Validation failed: {e}") from e


class UnityCatalogWriterPipeline:
    """Write validated items to Unity Catalog Delta tables.

    This pipeline stages validated equipment data for writing to Unity Catalog
    using DuckDB.
    """

    def __init__(self) -> None:
        """Initialize the pipeline."""
        self.items_buffer: list[dict] = []
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

    def open_spider(self) -> None:
        """Called when spider is opened."""
        self.crawler.spider.logger.info("Unity Catalog writer pipeline opened")
        self.items_buffer = []

        # Initialize Unity Catalog connection
        try:
            from core.databricks_utils import get_table_manager

            self.table_manager = get_table_manager()
            self.crawler.spider.logger.info("Connected to Unity Catalog")
        except Exception as e:
            self.crawler.spider.logger.warning(
                f"Could not connect to Unity Catalog: {e}. "
                "Items will be buffered but not written."
            )

    def close_spider(self) -> None:
        """Called when spider is closed. Flush remaining items."""
        if self.items_buffer:
            self._write_batch()

        # Close Unity Catalog connection
        if self.table_manager:
            try:
                self.table_manager.close()
                self.crawler.spider.logger.info("Closed Unity Catalog connection")
            except Exception as e:
                self.crawler.spider.logger.warning(
                    f"Error closing Unity Catalog connection: {e}"
                )

        self.crawler.spider.logger.info("Unity Catalog writer pipeline closed")

    def process_item(self, item: dict) -> dict:
        """Process an item by adding it to the buffer.

        Args:
            item: Validated item dictionary

        Returns:
            The item (unchanged)
        """
        self.items_buffer.append(item)

        if len(self.items_buffer) >= self.buffer_size:
            self._write_batch()

        return item

    def _write_batch(self) -> None:
        """Write buffered items to Unity Catalog Delta table."""
        self.crawler.spider.logger.info(
            f"Writing batch of {len(self.items_buffer)} items to Unity Catalog"
        )

        if not self.table_manager:
            self.crawler.spider.logger.warning(
                "Table manager not initialized. Skipping batch write."
            )
            self.items_buffer = []
            return

        try:
            # Group by category
            tractors = [i for i in self.items_buffer if i.get("category") == "tractor"]
            combines = [i for i in self.items_buffer if i.get("category") == "combine"]
            implements = [
                i for i in self.items_buffer if i.get("category") == "implement"
            ]

            # Write to appropriate tables
            if tractors:
                self.table_manager.insert_records("tractors", tractors)
                self.crawler.spider.logger.info(f"Wrote {len(tractors)} tractors")

            if combines:
                self.table_manager.insert_records("combines", combines)
                self.crawler.spider.logger.info(f"Wrote {len(combines)} combines")

            if implements:
                self.table_manager.insert_records("implements", implements)
                self.crawler.spider.logger.info(f"Wrote {len(implements)} implements")

        except Exception as e:
            self.crawler.spider.logger.error(
                f"Error writing batch to Unity Catalog: {e}"
            )

        self.items_buffer = []
