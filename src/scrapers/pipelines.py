"""Scrapy pipelines for processing scraped equipment data.

Pipelines:
1. ValidationPipeline - Validates items against Pydantic models
2. UnityCatalogWriterPipeline - Writes validated data to Unity Catalog Delta tables
"""

from typing import Any

from pydantic import ValidationError
from scrapy import Spider
from scrapy.exceptions import DropItem

from core.databricks_utils import TableManager
from core.models import create_equipment


class ValidationPipeline:
    """Validate scraped items using Pydantic models."""

    def process_item(self, item: dict, spider: Spider) -> dict:
        """Process and validate an item.

        Args:
            item: Scraped item dictionary
            spider: Spider that scraped the item

        Returns:
            Validated item

        Raises:
            DropItem: If validation fails
        """
        try:
            # Create appropriate equipment model based on category
            equipment = create_equipment(item)

            # Convert back to dict for further processing
            validated_item = equipment.model_dump()

            spider.logger.info(
                f"Validated {item.get('make')} {item.get('model')} "
                f"({item.get('category')})"
            )

            return validated_item

        except ValidationError as e:
            spider.logger.error(f"Validation error for item {item}: {e}")
            raise DropItem(f"Validation failed: {e}") from e
        except Exception as e:
            spider.logger.error(f"Unexpected error validating item {item}: {e}")
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

    def open_spider(self, spider: Spider) -> None:
        """Called when spider is opened.

        Args:
            spider: The spider being opened
        """
        spider.logger.info("Unity Catalog writer pipeline opened")
        self.items_buffer = []

        # Initialize Unity Catalog connection
        try:
            from core.databricks_utils import get_table_manager

            self.table_manager = get_table_manager()
            spider.logger.info("Connected to Unity Catalog")
        except Exception as e:
            spider.logger.warning(
                f"Could not connect to Unity Catalog: {e}. "
                "Items will be buffered but not written."
            )

    def close_spider(self, spider: Spider) -> None:
        """Called when spider is closed. Flush remaining items.

        Args:
            spider: The spider being closed
        """
        if self.items_buffer:
            self._write_batch(spider)

        # Close Unity Catalog connection
        if self.table_manager:
            try:
                self.table_manager.close()
                spider.logger.info("Closed Unity Catalog connection")
            except Exception as e:
                spider.logger.warning(f"Error closing Unity Catalog connection: {e}")

        spider.logger.info("Unity Catalog writer pipeline closed")

    def process_item(self, item: dict, spider: Spider) -> dict:
        """Process an item by adding it to the buffer.

        Args:
            item: Validated item dictionary
            spider: Spider that scraped the item

        Returns:
            The item (unchanged)
        """
        self.items_buffer.append(item)

        if len(self.items_buffer) >= self.buffer_size:
            self._write_batch(spider)

        return item

    def _write_batch(self, spider: Spider) -> None:
        """Write buffered items to Unity Catalog Delta table.

        Args:
            spider: Spider instance for logging
        """
        spider.logger.info(
            f"Writing batch of {len(self.items_buffer)} items to Unity Catalog"
        )

        if not self.table_manager:
            spider.logger.warning(
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
                self.table_manager.upsert_records("tractors", tractors)
                spider.logger.info(f"Wrote {len(tractors)} tractors")

            if combines:
                self.table_manager.upsert_records("combines", combines)
                spider.logger.info(f"Wrote {len(combines)} combines")

            if implements:
                self.table_manager.upsert_records("implements", implements)
                spider.logger.info(f"Wrote {len(implements)} implements")

        except Exception as e:
            spider.logger.error(f"Error writing batch to Unity Catalog: {e}")

        self.items_buffer = []
