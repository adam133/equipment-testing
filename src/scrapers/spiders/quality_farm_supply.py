"""Spider for scraping tractor specifications from Quality Farm Supply.

This spider scrapes tractor data from qualityfarmsupply.com/pages/tractor-specs.
It loops through multiple makes and models and returns data in a structured format.
"""

from collections.abc import Iterator
from typing import Any

from scrapy.http import Response

from core.models import EquipmentCategory
from scrapers.spiders.base_spider import BaseEquipmentSpider


class QualityFarmSupplySpider(BaseEquipmentSpider):
    """Spider for Quality Farm Supply tractor specifications page.

    This spider navigates to the tractor specs page and extracts:
    - Make (manufacturer)
    - Model
    - Series
    - Engine HP
    - PTO HP
    - Transmission type
    - Weight
    - Other specifications

    The page typically has a table or structured layout with tractor specs.
    """

    name = "quality_farm_supply"
    allowed_domains = ["qualityfarmsupply.com"]
    start_urls = ["https://www.qualityfarmsupply.com/pages/tractor-specs"]

    default_category = EquipmentCategory.TRACTOR

    # Example makes to filter for (can be customized)
    target_makes = ["John Deere", "Case IH", "New Holland", "Kubota", "Massey Ferguson"]

    # Known manufacturer names for parsing
    # (ordered by length descending to match longest first)
    known_makes = [
        "Massey Ferguson",
        "John Deere",
        "Case IH",
        "New Holland",
        "Kubota",
        "Caterpillar",
        "AGCO",
        "Fendt",
        "Deutz-Fahr",
        "Claas",
        "Valtra",
        "McCormick",
        "Landini",
    ]

    def _parse_make_model(self, title: str) -> tuple[str, str] | None:
        """Parse make and model from a title string.

        Args:
            title: Title string like "John Deere 5075E"

        Returns:
            Tuple of (make, model) or None if parsing fails
        """
        title = title.strip()

        # Try to match known makes
        for make in self.known_makes:
            if title.startswith(make):
                # Everything after the make is the model
                model = title[len(make) :].strip()
                if model:
                    return make, model

        # Fallback: split on first space
        parts = title.split(maxsplit=1)
        if len(parts) >= 2:
            return parts[0], parts[1]

        return None

    def parse(self, response: Response) -> Iterator[dict[str, Any]]:
        """Parse the main tractor specs page.

        Args:
            response: HTTP response from the tractor specs page

        Yields:
            Tractor specification items
        """
        self.logger.info(f"Parsing tractor specs from {response.url}")

        # Strategy 1: If the page has a table of tractors
        # Look for common table structures
        tractor_rows = response.css("table.specs-table tr") or response.css("table tr")

        if tractor_rows:
            # Parse table-based layout
            yield from self._parse_table(response, tractor_rows)
        else:
            # Strategy 2: If the page has individual cards/sections
            tractor_cards = response.css(".tractor-card, .product-card, .spec-item")
            if tractor_cards:
                yield from self._parse_cards(response, tractor_cards)
            else:
                # Strategy 3: Try to find links to individual tractor pages
                tractor_links = response.css('a[href*="tractor"]::attr(href)').getall()
                for link in tractor_links[:10]:  # Limit to first 10 for example
                    yield response.follow(link, callback=self.parse_tractor_detail)

    def _parse_table(self, response: Response, rows: Any) -> Iterator[dict[str, Any]]:
        """Parse tractor data from a table structure.

        Args:
            response: HTTP response
            rows: Table row selectors

        Yields:
            Tractor items
        """
        # Skip header row(s)
        for row in rows[1:]:
            # Extract data from table cells
            cells = row.css("td::text, td a::text").getall()

            if len(cells) >= 2:  # At least make and model
                # Typical table format: Make | Model | Series | HP | etc.
                make = cells[0].strip() if len(cells) > 0 else ""
                model = cells[1].strip() if len(cells) > 1 else ""

                # Filter by target makes if specified
                if self.target_makes and make not in self.target_makes:
                    continue

                # Extract other fields based on table structure
                item_data = {
                    "make": make,
                    "model": model,
                    "category": EquipmentCategory.TRACTOR,
                    "source_url": response.url,
                }

                # Try to extract additional fields
                # (adjust indices based on actual table)
                if len(cells) > 2:
                    item_data["series"] = cells[2].strip()
                if len(cells) > 3:
                    try:
                        item_data["engine_hp"] = float(cells[3].strip())
                    except (ValueError, AttributeError):
                        pass
                if len(cells) > 4:
                    try:
                        item_data["pto_hp"] = float(cells[4].strip())
                    except (ValueError, AttributeError):
                        pass

                yield self.create_equipment_item(**item_data)

    def _parse_cards(self, response: Response, cards: Any) -> Iterator[dict[str, Any]]:
        """Parse tractor data from card/section layout.

        Args:
            response: HTTP response
            cards: Card/section selectors

        Yields:
            Tractor items
        """
        for card in cards:
            # Extract data from card structure
            make = card.css(".make::text, .manufacturer::text").get(default="").strip()
            model = card.css(".model::text, .model-name::text").get(default="").strip()

            if not make or not model:
                # Try alternative selectors
                title = card.css("h2::text, h3::text, .title::text").get(default="")
                if title:
                    # Try to parse "Make Model" format using helper
                    parsed = self._parse_make_model(title)
                    if parsed:
                        make, model = parsed

            if make and model:
                # Filter by target makes if specified
                if self.target_makes and make not in self.target_makes:
                    continue

                item_data = {
                    "make": make,
                    "model": model,
                    "category": EquipmentCategory.TRACTOR,
                    "source_url": response.url,
                }

                # Extract additional specifications
                series = card.css(".series::text").get()
                if series:
                    item_data["series"] = series.strip()

                # Try to extract HP values
                hp_text = card.css(".horsepower::text, .hp::text").get()
                if hp_text:
                    try:
                        item_data["engine_hp"] = float(
                            hp_text.replace("HP", "").strip()
                        )
                    except ValueError:
                        pass

                # Extract description
                description = card.css(".description::text, p::text").get()
                if description:
                    item_data["description"] = description.strip()

                # Extract image URL
                image_url = card.css("img::attr(src)").get()
                if image_url:
                    item_data["image_url"] = response.urljoin(image_url)

                yield self.create_equipment_item(**item_data)

    def parse_tractor_detail(self, response: Response) -> Iterator[dict[str, Any]]:
        """Parse individual tractor detail page.

        Args:
            response: HTTP response from tractor detail page

        Yields:
            Tractor item with detailed specifications
        """
        self.logger.info(f"Parsing tractor detail from {response.url}")

        # Extract make and model from page
        title = response.css("h1::text, .product-title::text").get(default="")

        parsed = self._parse_make_model(title)
        if not parsed:
            self.logger.warning(f"Could not parse make/model from: {title}")
            return

        make, model = parsed

        # Filter by target makes if specified
        if self.target_makes and make not in self.target_makes:
            return

        item_data = {
            "make": make,
            "model": model,
            "category": EquipmentCategory.TRACTOR,
            "source_url": response.url,
        }

        # Extract specifications from detail page
        # Common patterns: key-value pairs in a list or table
        specs = response.css(".specs dl, .specifications dl")
        if specs:
            for dt in specs.css("dt"):
                key = dt.css("::text").get(default="").strip().lower()
                value = dt.xpath("following-sibling::dd[1]//text()").get(default="")

                if "engine" in key and "hp" in key:
                    try:
                        item_data["engine_hp"] = float(value.replace("HP", "").strip())
                    except ValueError:
                        pass
                elif "pto" in key and "hp" in key:
                    try:
                        item_data["pto_hp"] = float(value.replace("HP", "").strip())
                    except ValueError:
                        pass
                elif "weight" in key:
                    try:
                        item_data["weight_lbs"] = float(
                            value.replace("lbs", "").replace(",", "").strip()
                        )
                    except ValueError:
                        pass
                elif "transmission" in key:
                    item_data["transmission_type"] = value.strip().lower()

        # Extract image
        image_url = response.css(".product-image img::attr(src)").get()
        if image_url:
            item_data["image_url"] = response.urljoin(image_url)

        yield self.create_equipment_item(**item_data)
