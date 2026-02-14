"""Spider for scraping tractor specifications from Quality Farm Supply.

This spider scrapes tractor data from qualityfarmsupply.com/pages/tractor-specs.
It loops through multiple makes and models and returns data in a structured format.
This spider prefers JSON API endpoints and falls back to Playwright for HTML.

API Response Mapping:
---------------------
The spider includes comprehensive mapping from the Quality Farm Supply API
response format to our Tractor data model. The API returns specifications in
a JSON-stringified format with the following mappings:

API Field                    -> Tractor Model Field
"Years manufactured"         -> year_start, year_end (parsed range)
"Hp pto"                     -> pto_hp (float)
"Hp engine"                  -> engine_hp (float)
"Transmission std"           -> transmission_type (enum: manual, hydrostatic, etc.)
"Fwd rev standard"           -> forward_gears, reverse_gears (parsed from various formats)
"Wheelbase inches"           -> wheelbase_inches (float)
"Hitch lift"                 -> hitch_lift_capacity (float, lbs)
"Hydraulics flow"            -> hydraulic_flow (float, GPM)
"Weight"                     -> weight_lbs (float)
"Engine make", "Fuel type"   -> description (combined into text field)

The mapping function handles:
- JSON string parsing (spec field is JSON-encoded)
- Null/missing value handling
- Unit extraction (removes "HP", "lbs", "in", etc.)
- Range parsing (e.g., "17-20" takes first value: 17)
- Transmission code mapping (e.g., "CM" -> "manual")
- Various gear format patterns ("8F/4R", "12/6", "42", etc.)
"""

from collections.abc import Iterator
import json
from typing import Any
from urllib.parse import urlencode

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

    The site exposes JSON endpoints for make/model/spec data, which we prefer.
    Playwright is still available for HTML-based fallbacks.
    """

    name = "quality_farm_supply"
    allowed_domains = ["qualityfarmsupply.com", "app.smalink.net"]
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

    # Prefer API endpoints instead of page parsing
    use_api_endpoints = True

    api_base_url = "https://app.smalink.net/pim/tractor-specs.php"
    api_origin = "https://www.qualityfarmsupply.com"

    api_headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Origin": api_origin,
        "Referer": f"{api_origin}/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
    }

    # Known manufacturer names for parsing
    # (ordered by length descending to match longest first)
       # Known manufacturer names for parsing
    # (ordered by length descending to match longest first)
    known_makes = [
        "Massey Ferguson",
        "Massey-Ferguson",
        "Massey-Harris",
        "Rumely Oil Pull",
        "Allis Chalmers",
        "Fiat Hesston",
        "Silver King",
        "Deutz-Allis",
        "Minneapolis-Moline",
        "Mpls-Moline",
        "Agco White",
        "David Brown",
        "Deutz-Fahr",
        "John Deere",
        "New Holland",
        "Agco Allis",
        "Caterpillar",
        "Cockshutt",
        "Cub Cadet",
        "Hart-Parr",
        "Case IH",
        "Case-IH",
        "Cla-Power",
        "Field King",
        "JI Case",
        "Twin City",
        "Agcostar",
        "Ferguson",
        "Universal",
        "Versatile",
        "Big Bud",
        "McCormick",
        "Mitsubishi",
        "International",
        "Kubota",
        "Landini",
        "Leyland",
        "Nuffield",
        "Steiger",
        "Ferrari",
        "Goldoni",
        "Belarus",
        "Co-Op",
        "Deutz",
        "Eagle",
        "Avery",
        "Bison",
        "Claas",
        "Fendt",
        "Kioti",
        "Long",
        "Oliver",
        "Same",
        "Satoh",
        "White",
        "Valtra",
        "Yanmar",
        "Zetor",
        "AGCO",
        "Ford",
        "CBT",
        "IMT",
        "Memo",
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

    async def start(self) -> Iterator[Any]:
        """Generate initial requests.

        This method prefers JSON API endpoints for makes/models/specs. If API
        scraping is disabled, it falls back to Playwright-based HTML parsing.

        Yields:
            Scrapy requests for API or Playwright workflows
        """
        if self.use_api_endpoints:
            params = {"tractor_make": "tractor-specs-make"}
            yield self._make_api_request(params, callback=self.parse_makes)
            return

        for url in self.start_urls:
            yield self._make_playwright_request(url, callback=self.parse)

    def _make_api_request(
        self,
        params: dict[str, str],
        callback: Any,
        meta: dict[str, Any] | None = None,
    ) -> Request:
        """Create a Scrapy request for the JSON API endpoints."""
        url = f"{self.api_base_url}?{urlencode(params)}"
        request_meta = meta.copy() if meta else {}
        request_meta["api_params"] = params
        return Request(
            url=url,
            callback=callback,
            dont_filter=True,
            headers=self.api_headers,
            meta=request_meta,
        )

    def _load_json(self, response: Response) -> dict[str, Any]:
        """Safely load JSON payloads from API responses."""
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.warning(
                "Failed to decode JSON from %s (first 200 chars: %s)",
                response.url,
                response.text[:200],
            )
            return {}

    def _normalize_make_value(self, value: str) -> str:
        """Normalize make values for comparison."""
        return value.strip().lower().replace(" ", "-")

    def _is_target_make(self, make_name: str, make_slug: str | None) -> bool:
        """Determine whether a make is in the configured target list."""
        if not self.target_makes:
            return True

        normalized_name = self._normalize_make_value(make_name)
        normalized_slug = self._normalize_make_value(make_slug or "")

        for target in self.target_makes:
            normalized_target = self._normalize_make_value(target)
            if normalized_target in {normalized_name, normalized_slug}:
                return True

        return False

    def parse_makes(self, response: Response) -> Iterator[Any]:
        """Parse the list of makes from the API endpoint."""
        payload = self._load_json(response)
        makes = payload.get("data") or payload.get("makes") or []

        if not makes:
            self.logger.warning(
                "No makes returned from API (%s)", response.meta.get("api_params")
            )
            return

        for make_entry in makes:
            make_name = (
                make_entry.get("make")
                or make_entry.get("name")
                or make_entry.get("title")
            )
            make_slug = make_entry.get("make_slug") or make_entry.get("slug")

            if not make_name:
                continue

            if not make_slug:
                make_slug = self._normalize_make_value(make_name)

            if not self._is_target_make(make_name, make_slug):
                continue

            params = {
                "tractor_model": "tractor-specs-model",
                "tractor_make": make_slug,
            }
            meta = {"make_name": make_name, "make_slug": make_slug}
            yield self._make_api_request(params, callback=self.parse_models, meta=meta)

    def parse_models(self, response: Response) -> Iterator[Any]:
        """Parse model list for a make and enqueue spec requests."""
        payload = self._load_json(response)
        models = payload.get("data") or payload.get("models") or []

        make_name = response.meta.get("make_name")
        make_slug = response.meta.get("make_slug")

        if not models:
            self.logger.warning(
                "No models returned for %s (%s)",
                make_name,
                response.meta.get("api_params"),
            )
            return

        for model_entry in models:
            model_name = (
                model_entry.get("model")
                or model_entry.get("name")
                or model_entry.get("title")
            )
            model_slug = model_entry.get("model_slug") or model_entry.get("slug")

            if not model_name and not model_slug:
                continue

            if not model_slug:
                model_slug = model_name
            if not model_name:
                model_name = model_slug

            params = {
                "serial": "tractor-specs-serial",
                "tractor_make": make_slug,
                "tractor_model": model_slug,
            }
            meta = {
                "make_name": make_name,
                "make_slug": make_slug,
                "model_name": model_name,
                "model_slug": model_slug,
            }
            yield self._make_api_request(params, callback=self.parse_specs, meta=meta)

    def _map_api_response_to_tractor(
        self, api_data: dict[str, Any], make_name: str, model_name: str, source_url: str
    ) -> dict[str, Any]:
        """Map API response attributes to Tractor model fields.

        Args:
            api_data: The API response data (typically contains 'spec' and 'serial')
            make_name: Manufacturer name
            model_name: Model designation
            source_url: Source URL for reference

        Returns:
            Dictionary with mapped attributes compatible with Tractor model
        """
        # Initialize mapped data with required fields
        mapped_data: dict[str, Any] = {
            "make": make_name,
            "model": model_name,
            "category": EquipmentCategory.TRACTOR,
            "source_url": source_url,
        }

        # Parse the spec field if it's a JSON string
        spec_data = api_data.get("spec", {})
        if isinstance(spec_data, str):
            try:
                spec_data = json.loads(spec_data)
            except json.JSONDecodeError:
                self.logger.warning(
                    f"Failed to parse spec JSON for {make_name} {model_name}"
                )
                spec_data = {}

        if not isinstance(spec_data, dict):
            self.logger.warning(
                f"Unexpected spec data type for {make_name} {model_name}: "
                f"{type(spec_data)}"
            )
            return mapped_data

        # Helper function to safely extract numeric values
        def extract_numeric(value: str | None) -> float | None:
            if not value or value == "null" or not str(value).strip():
                return None
            try:
                # Remove common units and thousands separators
                cleaned = (
                    str(value)
                    .replace(",", "")
                    .replace("lbs", "")
                    .replace("HP", "")
                    .replace("hp", "")
                    .replace("in", "")
                    .replace("gal", "")
                    .replace("gpm", "")
                    .replace("psi", "")
                    .strip()
                )
                # Handle ranges by taking the first value
                if "-" in cleaned and not cleaned.startswith("-"):
                    cleaned = cleaned.split("-")[0].strip()
                if "/" in cleaned:
                    # For formats like "3/77.2" (cylinders/cid), take second value
                    parts = cleaned.split("/")
                    if len(parts) == 2:
                        return float(parts[1])
                return float(cleaned) if cleaned else None
            except (ValueError, AttributeError):
                return None

        # Map year range
        years_manufactured = spec_data.get("Years manufactured")
        if years_manufactured and isinstance(years_manufactured, str):
            years = years_manufactured.split("-")
            if len(years) >= 1:
                try:
                    mapped_data["year_start"] = int(years[0].strip())
                except (ValueError, AttributeError):
                    pass
            if len(years) >= 2:
                try:
                    mapped_data["year_end"] = int(years[1].strip())
                except (ValueError, AttributeError):
                    pass

        # Map power specifications
        if hp_pto := extract_numeric(spec_data.get("Hp pto")):
            mapped_data["pto_hp"] = hp_pto

        if hp_engine := extract_numeric(spec_data.get("Hp engine")):
            mapped_data["engine_hp"] = hp_engine

        # Map transmission type
        transmission_std = spec_data.get("Transmission std")
        if transmission_std and transmission_std != "null":
            # Map common abbreviations to our enum values
            trans_map = {
                "CM": "manual",
                "CMT": "manual",
                "MANUAL": "manual",
                "HYDRO": "hydrostatic",
                "HYDROSTAT": "hydrostatic",
                "HYDROSTATIC": "hydrostatic",
                "PS": "powershift",
                "POWERSHIFT": "powershift",
                "CVT": "cvt",
                "IVT": "ivt",
            }
            trans_value = str(transmission_std).strip().upper()
            mapped_data["transmission_type"] = trans_map.get(
                trans_value, trans_value.lower()
            )

        # Map forward/reverse gears
        fwd_rev_std = spec_data.get("Fwd rev standard")
        if fwd_rev_std and fwd_rev_std != "null":
            # Format varies: could be "4/2/6/16", "8F/8R", "42616", etc.
            fwd_rev_str = str(fwd_rev_std)
            
            # Pattern 1: "8F/8R" format
            if "F" in fwd_rev_str.upper() and "R" in fwd_rev_str.upper():
                parts = fwd_rev_str.upper().split("/")
                for part in parts:
                    if "F" in part:
                        try:
                            mapped_data["forward_gears"] = int(part.replace("F", ""))
                        except ValueError:
                            pass
                    elif "R" in part:
                        try:
                            mapped_data["reverse_gears"] = int(part.replace("R", ""))
                        except ValueError:
                            pass
            # Pattern 2: "4/2/6/16" or similar slash-separated (take first two)
            elif "/" in fwd_rev_str:
                parts = fwd_rev_str.split("/")
                if len(parts) >= 2:
                    try:
                        mapped_data["forward_gears"] = int(parts[0])
                        mapped_data["reverse_gears"] = int(parts[1])
                    except ValueError:
                        pass
            # Pattern 3: "42616" - likely concatenated, take first 1-2 digits as forward
            elif fwd_rev_str.isdigit() and len(fwd_rev_str) >= 2:
                # Common patterns: single digit forward + single digit reverse (e.g., "42")
                # Or double digit forward + single digit reverse (e.g., "121" = 12F/1R)
                try:
                    # Try single digit forward first
                    if len(fwd_rev_str) <= 3:
                        mapped_data["forward_gears"] = int(fwd_rev_str[0])
                        mapped_data["reverse_gears"] = int(fwd_rev_str[1])
                    # For longer strings, don't parse as it's ambiguous
                except ValueError:
                    pass

        # Map hydraulics
        if hydraulic_flow := extract_numeric(spec_data.get("Hydraulics flow")):
            mapped_data["hydraulic_flow"] = hydraulic_flow

        if hydraulic_capacity := extract_numeric(spec_data.get("Hydraulics capacity")):
            # Assuming capacity is in GPM (flow) or could be pressure
            # The API spec is ambiguous, but we'll map to flow if not already set
            if "hydraulic_flow" not in mapped_data:
                mapped_data["hydraulic_flow"] = hydraulic_capacity

        # Map physical specifications
        if weight := extract_numeric(spec_data.get("Weight")):
            mapped_data["weight_lbs"] = weight

        if wheelbase := extract_numeric(spec_data.get("Wheelbase inches")):
            mapped_data["wheelbase_inches"] = wheelbase

        # Map hitch lift capacity
        if hitch_lift := extract_numeric(spec_data.get("Hitch lift")):
            mapped_data["hitch_lift_capacity"] = hitch_lift

        # Map PTO speed (stored as note since we don't have a specific field)
        pto_speed = spec_data.get("Pto speed")
        if pto_speed and pto_speed != "null":
            if "description" not in mapped_data:
                mapped_data["description"] = ""
            mapped_data["description"] += f"PTO Speed: {pto_speed} RPM. "

        # Add engine details to description
        engine_make = spec_data.get("Engine make")
        if engine_make and engine_make != "null":
            if "description" not in mapped_data:
                mapped_data["description"] = ""
            mapped_data["description"] += f"Engine: {engine_make}. "

        engine_type = spec_data.get("Engine fueld type")
        if engine_type and engine_type != "null":
            if "description" not in mapped_data:
                mapped_data["description"] = ""
            mapped_data["description"] += f"Fuel: {engine_type}. "

        engine_cylinders = spec_data.get("Engine cylinders cid")
        if engine_cylinders and engine_cylinders != "null":
            if "description" not in mapped_data:
                mapped_data["description"] = ""
            mapped_data["description"] += f"Cylinders/CID: {engine_cylinders}. "

        # Clean up description
        if "description" in mapped_data:
            mapped_data["description"] = mapped_data["description"].strip()

        return mapped_data

    def parse_specs(self, response: Response) -> Iterator[dict[str, Any]]:
        """Parse the model specs from the API endpoint."""
        payload = self._load_json(response)
        data = payload.get("data") or payload.get("specs") or payload

        make_name = response.meta.get("make_name") or ""
        model_name = response.meta.get("model_name") or response.meta.get(
            "model_slug", ""
        )

        if not make_name or not model_name:
            self.logger.warning(
                "Missing make/model context for %s", response.meta.get("api_params")
            )
            return

        # Try to use the structured mapping function if data has 'spec' field
        if isinstance(data, dict) and "spec" in data:
            self.logger.info(
                f"Using structured API mapping for {make_name} {model_name}"
            )
            item_data = self._map_api_response_to_tractor(
                data, make_name, model_name, response.url
            )
            yield self.create_equipment_item(**item_data)
            return

        # Fall back to generic extraction
        item_data: dict[str, Any] = {
            "make": make_name,
            "model": model_name,
            "category": EquipmentCategory.TRACTOR,
            "source_url": response.url,
        }

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (str, int, float)):
                    self._extract_spec_value(str(key).lower(), str(value), item_data)
        elif isinstance(data, list):
            for entry in data:
                if not isinstance(entry, dict):
                    continue
                key = (
                    entry.get("attribute")
                    or entry.get("label")
                    or entry.get("name")
                    or entry.get("key")
                    or entry.get("title")
                )
                value = entry.get("value") or entry.get("val") or entry.get("data")
                if key and value:
                    self._extract_spec_value(str(key).lower(), str(value), item_data)

        if len(item_data) <= 4:
            self.logger.info(
                "Spec payload had limited fields for %s %s (%s)",
                make_name,
                model_name,
                response.meta.get("api_params"),
            )

        yield self.create_equipment_item(**item_data)

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
                (  # noqa: E501
                    "page.wait_for_function("
                    "'() => typeof $ === \"function\"', "
                    "timeout=20000)"
                ),
                # Wait additional time for document ready and initial AJAX to complete
                "page.wait_for_timeout(5000)",
                # Check if make dropdown is populated, if not trigger AJAX manually
                "page.evaluate('() => { "
                "  const makeSelect = document.querySelector('#tractor-make'); "
                "  if (!makeSelect) return { error: 'Make select not found' }; "
                "  "
                "  // If dropdown only has placeholder, trigger AJAX manually "
                "  if (makeSelect.options.length <= 1) { "
                "    // Manually call the AJAX endpoint "
                "    return new Promise((resolve) => { "
                "      $.getJSON("  # noqa: E501
                "'https://app.smalink.net/pim/tractor-specs.php?"
                "tractor_make=tractor-specs-make', function(result) { "
                "        if (result && result.data) { "
                "          result.data.forEach(function(data) { "
                "            $('#tractor-make').append("  # noqa: E501
                "'<option value=\"' + data.make_slug + '\">' + "
                "data.make + '</option>'); "
                "          }); "
                "        } "
                "        resolve("  # noqa: E501
                "{ manually_loaded: true, count: result.data.length }); "
                "      }); "
                "    }); "
                "  } "
                "  return "  # noqa: E501
                "{ already_loaded: true, count: makeSelect.options.length }; "
                "}')",
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
                f"    makeSelect.dispatchEvent("  # noqa: E501
                f"new Event('change', {{ bubbles: true }})); "
                f"    return {{ "  # noqa: E501
                f"success: true, selected: option.text, value: option.value }}; "
                f"  }} "
                f"  return {{ "  # noqa: E501
                f"error: 'Make option not found', "
                f"available: options.map(o => o.text) }}; "
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
                f"    modelSelect.dispatchEvent("  # noqa: E501
                f"new Event('change', {{ bubbles: true }})); "
                f"    return {{ "  # noqa: E501
                f"success: true, selected: options[targetIndex].text, "
                f"value: options[targetIndex].value }}; "
                f"  }} "
                f"  return {{ "  # noqa: E501
                f"error: 'Model index out of range', "
                f"available: options.length, requested: targetIndex }}; "
                f"}}')",
                # Wait for tractor details data to load via AJAX
                "page.wait_for_timeout(5000)",
                # Wait for the details table to appear
                (  # noqa: E501
                    "page.wait_for_selector("
                    "'#tractor-details, .tractor-details-data', "
                    "timeout=10000)"
                ),
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
                "Expected table with id 'tractor-details' or "
                "class 'tractor-details-data'."
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
            fallback_index = model_index if model_index is not None else 0
            item_data["model"] = f"Model_{fallback_index + 1}"

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
