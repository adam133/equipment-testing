"""Scrapy pipelines for processing scraped equipment data.

Pipelines:
1. ValidationPipeline - Validates items against Pydantic models
2. IcebergWriterPipeline - Writes validated data to Iceberg tables
"""

from pydantic import ValidationError
from scrapy import Spider
from scrapy.exceptions import DropItem

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


class IcebergWriterPipeline:
    """Write validated items to Iceberg tables.

    This pipeline stages validated equipment data for writing to S3 Tables.
    """

    def __init__(self):
        """Initialize the pipeline."""
        self.items_buffer: list[dict] = []
        self.buffer_size = 100  # Write in batches

    def open_spider(self, spider: Spider) -> None:
        """Called when spider is opened.

        Args:
            spider: The spider being opened
        """
        spider.logger.info("Iceberg writer pipeline opened")
        self.items_buffer = []

    def close_spider(self, spider: Spider) -> None:
        """Called when spider is closed. Flush remaining items.

        Args:
            spider: The spider being closed
        """
        if self.items_buffer:
            self._write_batch(spider)
        spider.logger.info("Iceberg writer pipeline closed")

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
        """Write buffered items to Iceberg table.

        Args:
            spider: Spider instance for logging

        Note:
            This is a placeholder. Actual implementation would:
            1. Connect to Iceberg catalog
            2. Determine target table based on category
            3. Upsert records using MERGE INTO logic
        """
        spider.logger.info(
            f"Writing batch of {len(self.items_buffer)} items to Iceberg"
        )

        # Placeholder for actual Iceberg write logic
        # from core.iceberg_utils import get_table_manager
        # table_manager = get_table_manager(warehouse_path="s3://...")
        #
        # Group by category
        # tractors = [i for i in self.items_buffer if i['category'] == 'tractor']
        # combines = [i for i in self.items_buffer if i['category'] == 'combine']
        # implements = [i for i in self.items_buffer if i['category'] == 'implement']
        #
        # if tractors:
        #     table_manager.upsert_records('tractors', tractors)
        # if combines:
        #     table_manager.upsert_records('combines', combines)
        # if implements:
        #     table_manager.upsert_records('implements', implements)

        self.items_buffer = []
