"""Base spider class for agricultural equipment scraping.

This module provides a base spider class that implements common functionality
for scraping agricultural equipment specifications from manufacturer websites
and equipment databases.
"""

from collections.abc import Iterator
from typing import Any

import scrapy
from core.models import EquipmentCategory
from scrapy.http import Response


class BaseEquipmentSpider(scrapy.Spider):
    """Base spider for scraping agricultural equipment data.

    All equipment spiders should inherit from this class to ensure
    consistent data structure and validation.
    """

    name = "base_equipment"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    # Default category for this spider
    default_category: EquipmentCategory = EquipmentCategory.OTHER

    def parse(self, response: Response) -> Iterator[dict[str, Any]]:
        """Parse the response and extract equipment data.

        Args:
            response: HTTP response from the scraped page

        Yields:
            Equipment data dictionaries

        Note:
            Subclasses should override this method to implement
            site-specific parsing logic.
        """
        raise NotImplementedError("Subclasses must implement parse method")

    def create_equipment_item(
        self, make: str, model: str, category: EquipmentCategory, **kwargs: Any
    ) -> dict[str, Any]:
        """Create a standardized equipment item.

        Args:
            make: Manufacturer name
            model: Model designation
            category: Equipment category
            **kwargs: Additional equipment-specific fields

        Returns:
            Equipment item dictionary ready for validation
        """
        item = {
            "make": make.strip(),
            "model": model.strip(),
            "category": category.value,
            **kwargs,
        }

        # Remove None values
        return {k: v for k, v in item.items() if v is not None}


class TractorDataSpider(BaseEquipmentSpider):
    """Example spider for scraping tractor data.

    This is a template/example spider showing how to implement
    a specific equipment spider.
    """

    name = "tractordata"
    allowed_domains = ["tractordata.com"]
    # start_urls would be populated with actual URLs in production
    start_urls: list[str] = []

    default_category = EquipmentCategory.TRACTOR

    def parse(self, response: Response) -> Iterator[dict[str, Any]]:
        """Parse tractor data from the page.

        Args:
            response: HTTP response

        Yields:
            Tractor data items

        Note:
            This is a placeholder implementation. Actual implementation
            would parse real HTML/JSON from the website.
        """
        # Example placeholder - would be replaced with actual parsing logic
        self.logger.info(f"Parsing {response.url}")

        # Example: In a real implementation, you would:
        # 1. Extract data from HTML using CSS selectors or XPath
        # 2. Clean and normalize the data
        # 3. Create items using create_equipment_item

        # Placeholder example item
        # item = self.create_equipment_item(
        #     make="John Deere",
        #     model="5075E",
        #     category=EquipmentCategory.TRACTOR,
        #     series="5E Series",
        #     year_start=2014,
        #     engine_hp=75,
        #     pto_hp=65,
        #     transmission_type="powershift",
        #     source_url=response.url,
        # )
        # yield item

        # Follow pagination links
        # next_page = response.css('a.next-page::attr(href)').get()
        # if next_page:
        #     yield response.follow(next_page, self.parse)

        yield from []  # Placeholder - no items in example
