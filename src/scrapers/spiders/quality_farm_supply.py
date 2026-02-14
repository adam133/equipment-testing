"""Spider for scraping tractor specifications from Quality Farm Supply.

This spider scrapes tractor data from qualityfarmsupply.com/pages/tractor-specs.
It loops through multiple makes and models and returns data in a structured format.
This spider uses Playwright to handle dynamic JavaScript-based form navigation.
"""

from collections.abc import Iterator
from typing import Any

from scrapy import Request
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

    The page uses JavaScript for form-based filtering, so Playwright is required
    to interact with the make/model filters and load dynamic content.
    """

    name = "quality_farm_supply"
    allowed_domains = ["qualityfarmsupply.com"]
    start_urls = ["https://www.qualityfarmsupply.com/pages/tractor-specs"]

    default_category = EquipmentCategory.TRACTOR

    # Custom settings to ensure Playwright is enabled for this spider
    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": True,
        },
    }

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

    def start_requests(self) -> Iterator[Any]:
        """Generate initial requests with Playwright enabled.

        This method creates requests that use Playwright to render JavaScript
        and interact with the page's form elements.

        Yields:
            Scrapy requests with Playwright meta options
        """
        for url in self.start_urls:
            yield self._make_playwright_request(url, callback=self.parse)

    def _make_playwright_request(
        self,
        url: str,
        callback: Any,
        make: str | None = None,
        model_index: int | None = None,
    ) -> Any:
        """Create a Scrapy request with Playwright options.

        Args:
            url: URL to request
            callback: Callback function for the response
            make: Optional manufacturer name to filter by
            model_index: Optional model dropdown index to select (0-based)

        Returns:
            Scrapy Request with Playwright meta options
        """
        # Playwright page actions to execute
        playwright_page_actions = []

        if make and model_index is not None:
            # Actions to select both make and model from tractor-specific filters
            playwright_page_actions = [
                # Wait for the page to load completely
                "page.wait_for_load_state('load')",
                # Wait for tractor-make dropdown to be available
                "page.wait_for_selector('#tractor-make', timeout=10000)",
                # Wait for jQuery to load (required for AJAX calls)
                "page.wait_for_function('() => typeof $ === \"function\"', timeout=20000)",
                # Wait additional time for document ready and initial AJAX to complete
                "page.wait_for_timeout(5000)",
                # Check if make dropdown is populated, if not trigger AJAX manually
                f"page.evaluate('() => {{ "
                f"  const makeSelect = document.querySelector('#tractor-make'); "
                f"  if (!makeSelect) return {{ error: 'Make select not found' }}; "
                f"  "
                f"  // If dropdown only has placeholder, trigger AJAX manually "
                f"  if (makeSelect.options.length <= 1) {{ "
                f"    // Manually call the AJAX endpoint "
                f"    return new Promise((resolve) => {{ "
                f"      $.getJSON('https://app.smalink.net/pim/tractor-specs.php?tractor_make=tractor-specs-make', function(result) {{ "
                f"        if (result && result.data) {{ "
                f"          result.data.forEach(function(data) {{ "
                f"            $('#tractor-make').append('<option value=\"' + data.make_slug + '\">' + data.make + '</option>'); "
                f"          }}); "
                f"        }} "
                f"        resolve({{ manually_loaded: true, count: result.data.length }}); "
                f"      }}); "
                f"    }}); "
                f"  }} "
                f"  return {{ already_loaded: true, count: makeSelect.options.length }}; "
                f"}}')",
                # Wait for make dropdown population
                "page.wait_for_timeout(2000)",
                # Select the make from #tractor-make dropdown
                f"page.evaluate('() => {{ "
                f"  const makeSelect = document.querySelector('#tractor-make'); "
                f"  if (!makeSelect) return {{ error: 'Make select not found' }}; "
                f"  const options = Array.from(makeSelect.options); "
                f'  const option = options.find(opt => opt.text.includes("{make}")); '
                f"  if (option) {{ "
                f"    makeSelect.value = option.value; "
                f"    makeSelect.dispatchEvent(new Event('change', {{ bubbles: true }})); "
                f"    return {{ success: true, selected: option.text, value: option.value }}; "
                f"  }} "
                f"  return {{ error: 'Make option not found', available: options.map(o => o.text) }}; "
                f"}}')",
                # Wait for model dropdown to populate via AJAX
                "page.wait_for_timeout(5000)",
                # Select the model by index from #tractor-model dropdown
                f"page.evaluate('() => {{ "
                f"  const modelSelect = document.querySelector('#tractor-model'); "
                f"  if (!modelSelect) return {{ error: 'Model select not found' }}; "
                f"  const options = Array.from(modelSelect.options); "
                f"  // Skip first option (placeholder 'Select One') "
                f"  const targetIndex = {model_index + 1}; "
                f"  if (targetIndex < options.length) {{ "
                f"    modelSelect.value = options[targetIndex].value; "
                f"    modelSelect.dispatchEvent(new Event('change', {{ bubbles: true }})); "
                f"    return {{ success: true, selected: options[targetIndex].text, value: options[targetIndex].value }}; "
                f"  }} "
                f"  return {{ error: 'Model index out of range', available: options.length, requested: targetIndex }}; "
                f"}}')",
                # Wait for tractor details data to load via AJAX
                "page.wait_for_timeout(5000)",
                # Wait for the details table to appear
                "page.wait_for_selector('#tractor-details, .tractor-details-data', timeout=10000)",
            ]
        elif make:
            # Actions to select only make from the filter
            playwright_page_actions = [
                # Wait for the page to load
                "page.wait_for_load_state('networkidle')",
                # Wait for filter elements to be available
                (
                    "page.wait_for_selector("
                    "'select, .filter-select, [data-filter-make]', "
                    "timeout=10000)"
                ),
                # Try to find and click the make filter dropdown
                f"page.evaluate('() => {{ "
                f"  const selects = document.querySelectorAll('select'); "
                f"  for (const select of selects) {{ "
                f"    const options = Array.from(select.options); "
                f'    const option = options.find(opt => opt.text.includes("{make}")); '
                f"    if (option) {{ "
                f"      select.value = option.value; "
                f"      select.dispatchEvent("
                f"        new Event('change', {{ bubbles: true }})"
                f"      ); "
                f"      return true; "
                f"    }} "
                f"  }} "
                f"  return false; "
                f"}}')",
                # Wait for results to load after filtering
                "page.wait_for_timeout(2000)",
            ]
        else:
            # Just wait for the page to fully load
            playwright_page_actions = [
                "page.wait_for_load_state('networkidle')",
                # Wait a bit for any dynamic content to render
                "page.wait_for_timeout(2000)",
            ]

        return Request(
            url=url,
            callback=callback,
            # Don't filter duplicate requests when we have a make/model filter
            # since each request is actually unique (different filter + actions)
            dont_filter=(make is not None or model_index is not None),
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_actions": playwright_page_actions,
                "errback": self.errback_close_page,
                "make_filter": make,
                "model_index": model_index,
            },
        )

    async def errback_close_page(self, failure: Any) -> None:
        """Error callback to close Playwright page on failure.

        Args:
            failure: Scrapy failure object
        """
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()
        self.logger.error(f"Error processing {failure.request.url}: {failure}")

    def parse_model_data(self, response: Response) -> Iterator[dict[str, Any]]:
        """Parse model-specific data after make and model selection.

        This method is called after both make and model have been selected
        from their respective dropdowns. It verifies the DOM structure for
        model attributes and extracts the data.

        Args:
            response: HTTP response from the tractor specs page with model selected

        Yields:
            Tractor specification item for the selected model
        """
        make_filter = response.meta.get("make_filter")
        model_index = response.meta.get("model_index")

        self.logger.info(
            f"Parsing model data for {make_filter}, model index {model_index}"
        )

        # Look for the tractor-details table (populated by AJAX)
        details_table = response.css("#tractor-details, .tractor-details-data")

        if not details_table:
            self.logger.warning(
                f"No tractor details table found for {make_filter} "
                f"model {model_index}. "
                f"Expected table with id 'tractor-details' or class 'tractor-details-data'."
            )
            return

        self.logger.info("Found tractor details table")

        # Extract data from the table
        # The table has rows with two cells: key and value
        rows = details_table.css("tr")

        if not rows or len(rows) == 0:
            self.logger.warning(
                f"Tractor details table is empty for {make_filter} model {model_index}"
            )
            return

        self.logger.info(f"Found {len(rows)} rows in tractor details table")

        # Initialize item data
        item_data: dict[str, Any] = {
            "make": make_filter,
            "category": EquipmentCategory.TRACTOR,
            "source_url": response.url,
        }

        # Extract model name from the first row or from selected option
        # Try to get the selected model name from the dropdown
        model_name = response.css("#tractor-model option[selected]::text").get()
        if model_name:
            item_data["model"] = model_name.strip()
        else:
            # Fallback to using model index
            item_data["model"] = f"Model_{model_index + 1}"

        # Parse each row for specifications
        for row in rows:
            cells = row.css("td")
            if len(cells) >= 2:
                key = cells[0].css("::text").get(default="").strip().lower()
                value = cells[1].css("::text").get(default="").strip()

                if key and value:
                    self._extract_spec_value(key, value, item_data)

        # Log what we extracted
        self.logger.info(
            f"Successfully extracted model data for {item_data.get('make')} "
            f"{item_data.get('model')} with {len(item_data)} fields"
        )

        yield self.create_equipment_item(**item_data)

    def _extract_specs_from_container(
        self, container: Any, item_data: dict[str, Any]
    ) -> None:
        """Extract specifications from a container element.

        Args:
            container: Scrapy selector for the container element
            item_data: Dictionary to populate with extracted specs
        """
        # Try different spec extraction patterns
        # Pattern 1: Definition list (dt/dd pairs)
        spec_terms = container.css("dt")
        if spec_terms:
            for dt in spec_terms:
                key = dt.css("::text").get(default="").strip().lower()
                value = dt.xpath("following-sibling::dd[1]//text()").get(default="")

                self._extract_spec_value(key, value, item_data)

        # Pattern 2: Divs with class patterns
        spec_items = container.css(".spec-item, .attribute-item")
        for spec_item in spec_items:
            key = (
                spec_item.css(".label::text, .key::text")
                .get(default="")
                .strip()
                .lower()
            )
            value = spec_item.css(".value::text, .val::text").get(default="")

            self._extract_spec_value(key, value, item_data)

        # Pattern 3: Table rows
        rows = container.css("tr")
        for row in rows:
            cells = row.css("td::text").getall()
            if len(cells) >= 2:
                key = cells[0].strip().lower()
                value = cells[1].strip()

                self._extract_spec_value(key, value, item_data)

    def _extract_spec_value(
        self, key: str, value: str, item_data: dict[str, Any]
    ) -> None:
        """Extract and normalize a specific spec value.

        Args:
            key: Specification key (normalized to lowercase)
            value: Raw specification value
            item_data: Dictionary to populate with extracted value
        """
        if not key or not value:
            return

        value = value.strip()

        # Map common spec keys to our data model
        if "series" in key:
            item_data["series"] = value
        elif "engine" in key and "hp" in key:
            try:
                item_data["engine_hp"] = float(
                    value.replace("HP", "").replace("hp", "").strip()
                )
            except ValueError:
                pass
        elif "pto" in key and "hp" in key:
            try:
                item_data["pto_hp"] = float(
                    value.replace("HP", "").replace("hp", "").strip()
                )
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
        elif "model" in key and "model" not in item_data:
            # Update model if found in attributes
            item_data["model"] = value

    def parse(self, response: Response) -> Iterator[dict[str, Any] | Any]:
        """Parse the main tractor specs page.

        This method handles both initial page load and filtered results.
        If no make filter is active, it will iterate through target makes
        and make separate requests for each one. For each make, it will
        iterate through the first 5 models in the dropdown.

        Args:
            response: HTTP response from the tractor specs page

        Yields:
            Tractor specification items or new requests for filtered results
        """
        make_filter = response.meta.get("make_filter")
        model_index = response.meta.get("model_index")

        log_msg = f"Parsing tractor specs from {response.url}"
        if make_filter:
            log_msg += f" (filtered by {make_filter}"
            if model_index is not None:
                log_msg += f", model index {model_index}"
            log_msg += ")"
        self.logger.info(log_msg)

        # Note: Playwright page cleanup is handled automatically by scrapy-playwright
        # No manual page.close() needed here

        # If we haven't applied a make filter yet, iterate through target makes
        if not make_filter and self.target_makes:
            self.logger.info(
                f"No make filter active. Will iterate through "
                f"{len(self.target_makes)} target makes."
            )
            for make in self.target_makes:
                # For each make, iterate through first 5 models
                for model_idx in range(5):
                    yield self._make_playwright_request(
                        response.url,
                        callback=self.parse_model_data,
                        make=make,
                        model_index=model_idx,
                    )
            return

        # Parse the filtered results
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
                # Strategy 3: Try to find any divs or sections with tractordata
                # Look for common patterns in product listings
                product_items = response.css(
                    "div[class*='product'], div[class*='item'], "
                    "div[class*='tractor'], li[class*='product']"
                )
                if product_items:
                    self.logger.info(
                        f"Found {len(product_items)} potential product items"
                    )
                    yield from self._parse_cards(response, product_items)
                else:
                    # Strategy 4: Try to find links to individual tractor pages
                    tractor_links = response.css(
                        'a[href*="tractor"]::attr(href)'
                    ).getall()
                    if tractor_links:
                        self.logger.info(f"Found {len(tractor_links)} tractor links")
                        for link in tractor_links[:10]:  # Limit to first 10 for example
                            yield response.follow(
                                link, callback=self.parse_tractor_detail
                            )
                    else:
                        self.logger.warning(
                            f"No tractors found on page. "
                            f"Page might have different structure. "
                            f"First 500 chars of body: {response.text[:500]}"
                        )

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
                item_data: dict[str, Any] = {
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

                item_data: dict[str, Any] = {
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

        item_data: dict[str, Any] = {
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
