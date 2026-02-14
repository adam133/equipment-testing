"""Tests for the Quality Farm Supply spider."""

from typing import Any

import pytest
from scrapy.http import HtmlResponse, Request

from core.models import EquipmentCategory
from scrapers.spiders.quality_farm_supply import QualityFarmSupplySpider


@pytest.fixture
def spider():
    """Create a QualityFarmSupplySpider instance for testing."""
    return QualityFarmSupplySpider()


@pytest.fixture
def mock_response_table():
    """Create a mock HTML response with table layout."""
    html = """
    <html>
        <body>
            <table class="specs-table">
                <tr>
                    <th>Make</th>
                    <th>Model</th>
                    <th>Series</th>
                    <th>Engine HP</th>
                    <th>PTO HP</th>
                </tr>
                <tr>
                    <td>John Deere</td>
                    <td>5075E</td>
                    <td>5E Series</td>
                    <td>75</td>
                    <td>65</td>
                </tr>
                <tr>
                    <td>Case IH</td>
                    <td>Farmall 75C</td>
                    <td>Farmall C</td>
                    <td>75</td>
                    <td>64</td>
                </tr>
            </table>
        </body>
    </html>
    """
    url = "https://www.qualityfarmsupply.com/pages/tractor-specs"
    request = Request(url=url, meta={"make_filter": "John Deere"})
    return HtmlResponse(url=url, body=html, encoding="utf-8", request=request)


@pytest.fixture
def mock_response_cards():
    """Create a mock HTML response with card layout."""
    html = """
    <html>
        <body>
            <div class="tractor-card">
                <h2 class="title">John Deere 5075E</h2>
                <p class="series">5E Series</p>
                <p class="horsepower">75 HP</p>
                <p class="description">Versatile utility tractor</p>
                <img src="/images/5075e.jpg" alt="5075E">
            </div>
            <div class="tractor-card">
                <h2 class="title">Kubota M7-172</h2>
                <p class="series">M7 Series</p>
                <p class="horsepower">170 HP</p>
                <img src="/images/m7-172.jpg" alt="M7-172">
            </div>
        </body>
    </html>
    """
    url = "https://www.qualityfarmsupply.com/pages/tractor-specs"
    request = Request(url=url, meta={"make_filter": "John Deere"})
    return HtmlResponse(url=url, body=html, encoding="utf-8", request=request)


def test_spider_name(spider):
    """Test that spider has correct name."""
    assert spider.name == "quality_farm_supply"


def test_spider_allowed_domains(spider):
    """Test that spider has correct allowed domains."""
    assert "qualityfarmsupply.com" in spider.allowed_domains


def test_spider_start_urls(spider):
    """Test that spider has correct start URLs."""
    assert len(spider.start_urls) > 0
    assert any("tractor-specs" in url for url in spider.start_urls)


def test_spider_default_category(spider):
    """Test that spider has correct default category."""
    assert spider.default_category == EquipmentCategory.TRACTOR


def test_create_equipment_item(spider):
    """Test the create_equipment_item method."""
    item = spider.create_equipment_item(
        make="John Deere",
        model="5075E",
        category=EquipmentCategory.TRACTOR,
        series="5E Series",
        engine_hp=75,
        pto_hp=65,
    )

    assert item["make"] == "John Deere"
    assert item["model"] == "5075E"
    assert item["category"] == "tractor"
    assert item["series"] == "5E Series"
    assert item["engine_hp"] == 75
    assert item["pto_hp"] == 65


def test_create_equipment_item_strips_whitespace(spider):
    """Test that create_equipment_item strips whitespace."""
    item = spider.create_equipment_item(
        make="  John Deere  ",
        model=" 5075E ",
        category=EquipmentCategory.TRACTOR,
    )

    assert item["make"] == "John Deere"
    assert item["model"] == "5075E"


def test_create_equipment_item_removes_none_values(spider):
    """Test that create_equipment_item removes None values."""
    item = spider.create_equipment_item(
        make="John Deere",
        model="5075E",
        category=EquipmentCategory.TRACTOR,
        series=None,
        engine_hp=None,
    )

    assert "series" not in item
    assert "engine_hp" not in item
    assert item["make"] == "John Deere"


def test_parse_table(spider, mock_response_table):
    """Test parsing table-based layout with make filter."""
    results = list(spider.parse(mock_response_table))

    assert len(results) == 2

    # Check first tractor
    assert results[0]["make"] == "John Deere"
    assert results[0]["model"] == "5075E"
    assert results[0]["series"] == "5E Series"
    assert results[0]["category"] == "tractor"
    assert results[0]["source_url"] == mock_response_table.url

    # Check second tractor
    assert results[1]["make"] == "Case IH"
    assert results[1]["model"] == "Farmall 75C"


def test_parse_cards(spider, mock_response_cards):
    """Test parsing card-based layout with make filter."""
    results = list(spider.parse(mock_response_cards))

    assert len(results) == 2

    # Check first tractor
    assert results[0]["make"] == "John Deere"
    assert results[0]["model"] == "5075E"
    assert results[0]["category"] == "tractor"
    assert results[0]["source_url"] == mock_response_cards.url

    # Check second tractor
    assert results[1]["make"] == "Kubota"
    assert results[1]["model"] == "M7-172"


def test_parse_without_filter_generates_requests(spider):
    """Test that parse generates requests for each target make and model."""
    html = "<html><body></body></html>"
    url = "https://www.qualityfarmsupply.com/pages/tractor-specs"
    # Create response without make_filter in meta
    request = Request(url=url, meta={})
    response = HtmlResponse(url=url, body=html, encoding="utf-8", request=request)

    results = list(spider.parse(response))

    # Should generate requests for each target make * 5 models (first 5 models per make)
    expected_count = len(spider.target_makes) * 5
    assert len(results) == expected_count

    # Check that each result is a Request (not an item dict)
    for result in results:
        assert isinstance(result, Request)


def test_target_makes_filter(spider):
    """Test that target_makes filtering works."""
    # Set target makes to only include John Deere
    spider.target_makes = ["John Deere"]

    html = """
    <html>
        <body>
            <table class="specs-table">
                <tr><th>Make</th><th>Model</th></tr>
                <tr><td>John Deere</td><td>5075E</td></tr>
                <tr><td>Case IH</td><td>Farmall 75C</td></tr>
            </table>
        </body>
    </html>
    """
    url = "https://www.qualityfarmsupply.com/pages/tractor-specs"
    request = Request(url=url, meta={"make_filter": "John Deere"})
    response = HtmlResponse(url=url, body=html, encoding="utf-8", request=request)

    results = list(spider.parse(response))

    # Should only get John Deere tractors, not Case IH
    assert len(results) == 1
    assert results[0]["make"] == "John Deere"


def test_empty_target_makes(spider):
    """Test with empty target_makes (should parse immediately)."""
    spider.target_makes = []

    html = """
    <html>
        <body>
            <table class="specs-table">
                <tr><th>Make</th><th>Model</th></tr>
                <tr><td>John Deere</td><td>5075E</td></tr>
                <tr><td>Case IH</td><td>Farmall 75C</td></tr>
            </table>
        </body>
    </html>
    """
    url = "https://www.qualityfarmsupply.com/pages/tractor-specs"
    # No make_filter in meta
    request = Request(url=url, meta={})
    response = HtmlResponse(url=url, body=html, encoding="utf-8", request=request)

    # With empty target_makes, should parse immediately (no filter iteration)
    results = list(spider.parse(response))

    # Should get all tractors when target_makes is empty
    assert len(results) == 2


def test_parse_tractor_detail(spider):
    """Test parsing individual tractor detail page."""
    html = """
    <html>
        <body>
            <h1 class="product-title">John Deere 5075E</h1>
            <img class="product-image" src="/images/5075e.jpg" alt="5075E">
            <div class="specs">
                <dl>
                    <dt>Engine HP</dt>
                    <dd>75 HP</dd>
                    <dt>PTO HP</dt>
                    <dd>65 HP</dd>
                    <dt>Weight</dt>
                    <dd>7,700 lbs</dd>
                    <dt>Transmission</dt>
                    <dd>PowerShift</dd>
                </dl>
            </div>
        </body>
    </html>
    """
    url = "https://www.qualityfarmsupply.com/pages/tractor-specs/john-deere-5075e"
    response = HtmlResponse(url=url, body=html, encoding="utf-8")

    results = list(spider.parse_tractor_detail(response))

    assert len(results) == 1
    assert results[0]["make"] == "John Deere"
    assert results[0]["model"] == "5075E"
    assert results[0]["source_url"] == url


def test_parse_invalid_title(spider):
    """Test parsing with invalid/missing title."""
    html = """
    <html>
        <body>
            <h1 class="product-title">InvalidTitle</h1>
        </body>
    </html>
    """
    url = "https://www.qualityfarmsupply.com/pages/tractor-specs/invalid"
    response = HtmlResponse(url=url, body=html, encoding="utf-8")

    results = list(spider.parse_tractor_detail(response))

    # Should return nothing if title can't be parsed
    assert len(results) == 0


def test_parse_make_model_known_makes(spider):
    """Test _parse_make_model with known manufacturer names."""
    # Test multi-word makes
    assert spider._parse_make_model("John Deere 5075E") == ("John Deere", "5075E")
    assert spider._parse_make_model("Case IH Farmall 75C") == (
        "Case IH",
        "Farmall 75C",
    )
    assert spider._parse_make_model("New Holland T4.75") == ("New Holland", "T4.75")
    assert spider._parse_make_model("Massey Ferguson 1840M") == (
        "Massey Ferguson",
        "1840M",
    )

    # Test single-word makes
    assert spider._parse_make_model("Kubota M7-172") == ("Kubota", "M7-172")

    # Test with extra whitespace
    assert spider._parse_make_model("  John Deere 5075E  ") == ("John Deere", "5075E")


def test_parse_make_model_unknown_makes(spider):
    """Test _parse_make_model with unknown manufacturers (fallback behavior)."""
    # Should fall back to splitting on first space
    result = spider._parse_make_model("UnknownBrand Model123")
    assert result == ("UnknownBrand", "Model123")


def test_parse_make_model_invalid(spider):
    """Test _parse_make_model with invalid input."""
    # Single word with no space
    assert spider._parse_make_model("SingleWord") is None

    # Empty string
    assert spider._parse_make_model("") is None

    # Only whitespace
    assert spider._parse_make_model("   ") is None


def test_start_requests_uses_playwright(spider):
    """Test that start_requests generates Playwright-enabled requests."""
    requests = list(spider.start_requests())

    assert len(requests) > 0

    # Check first request has Playwright enabled
    first_request = requests[0]
    assert "playwright" in first_request.meta
    assert first_request.meta["playwright"] is True
    assert "playwright_include_page" in first_request.meta
    assert "playwright_page_actions" in first_request.meta


def test_custom_settings_has_playwright(spider):
    """Test that spider has custom settings for Playwright."""
    assert hasattr(spider, "custom_settings")
    assert "DOWNLOAD_HANDLERS" in spider.custom_settings
    assert "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler" in str(
        spider.custom_settings["DOWNLOAD_HANDLERS"]
    )


def test_make_playwright_request_without_filter(spider):
    """Test _make_playwright_request without make filter."""
    url = "https://www.qualityfarmsupply.com/pages/tractor-specs"
    request = spider._make_playwright_request(url, callback=spider.parse)

    assert request.url == url
    assert request.meta["playwright"] is True
    assert request.meta.get("make_filter") is None
    assert len(request.meta["playwright_page_actions"]) > 0
    # Requests without make filters should use default duplicate filtering
    assert request.dont_filter is False


def test_make_playwright_request_with_filter(spider):
    """Test _make_playwright_request with make filter."""
    url = "https://www.qualityfarmsupply.com/pages/tractor-specs"
    make = "John Deere"
    request = spider._make_playwright_request(url, callback=spider.parse, make=make)

    assert request.url == url
    assert request.meta["playwright"] is True
    assert request.meta.get("make_filter") == make
    # Should have more actions when filtering by make
    assert len(request.meta["playwright_page_actions"]) > 2
    # Check that make name is in the actions (for filtering)
    actions_str = str(request.meta["playwright_page_actions"])
    assert make in actions_str
    # Requests with make filters should not be filtered as duplicates
    assert request.dont_filter is True


def test_multiple_make_requests_not_filtered_as_duplicates(spider):
    """Test that requests for different makes to the same URL are not filtered."""
    html = "<html><body></body></html>"
    url = "https://www.qualityfarmsupply.com/pages/tractor-specs"
    # Create response without make_filter in meta
    request = Request(url=url, meta={})
    response = HtmlResponse(url=url, body=html, encoding="utf-8", request=request)

    results = list(spider.parse(response))

    # Should generate requests for each target make * 5 models
    expected_count = len(spider.target_makes) * 5
    assert len(results) == expected_count

    # All requests should have dont_filter=True to avoid being filtered
    for result in results:
        assert isinstance(result, Request)
        assert result.dont_filter is True
        # Each request should have a make_filter and model_index
        assert result.meta.get("make_filter") in spider.target_makes
        assert result.meta.get("model_index") is not None
        assert 0 <= result.meta.get("model_index") < 5


def test_make_playwright_request_with_model_index(spider):
    """Test _make_playwright_request with make and model index."""
    url = "https://www.qualityfarmsupply.com/pages/tractor-specs"
    make = "John Deere"
    model_index = 2
    request = spider._make_playwright_request(
        url, callback=spider.parse_model_data, make=make, model_index=model_index
    )

    assert request.url == url
    assert request.meta["playwright"] is True
    assert request.meta.get("make_filter") == make
    assert request.meta.get("model_index") == model_index
    # Should have actions for both make and model selection
    assert len(request.meta["playwright_page_actions"]) > 4
    # Check that make name and model index are in the actions
    actions_str = str(request.meta["playwright_page_actions"])
    assert make in actions_str
    assert str(model_index) in actions_str
    # Requests with model index should not be filtered as duplicates
    assert request.dont_filter is True


def test_parse_model_data_with_attributes(spider):
    """Test parsing model-specific data with attributes container."""
    html = """
    <html>
        <body>
            <div class="specs">
                <h2>John Deere 5075E</h2>
                <dl>
                    <dt>Series</dt>
                    <dd>5E Series</dd>
                    <dt>Engine HP</dt>
                    <dd>75 HP</dd>
                    <dt>PTO HP</dt>
                    <dd>65 HP</dd>
                    <dt>Weight</dt>
                    <dd>7,700 lbs</dd>
                    <dt>Transmission</dt>
                    <dd>PowerShift</dd>
                </dl>
            </div>
        </body>
    </html>
    """
    url = "https://www.qualityfarmsupply.com/pages/tractor-specs"

    # Test using the spider's method to create request
    request = spider._make_playwright_request(
        url, callback=spider.parse_model_data, make="John Deere", model_index=0
    )

    # Verify meta values are set correctly
    assert request.meta["make_filter"] == "John Deere"
    assert request.meta["model_index"] == 0

    # Create response from that request
    response = HtmlResponse(url=url, body=html, encoding="utf-8", request=request)

    results = list(spider.parse_model_data(response))

    assert len(results) == 1
    assert results[0]["make"] == "John Deere"
    assert results[0]["model"] == "5075E"
    assert results[0]["series"] == "5E Series"
    assert results[0]["engine_hp"] == 75.0
    assert results[0]["pto_hp"] == 65.0
    assert results[0]["weight_lbs"] == 7700.0
    assert results[0]["transmission_type"] == "powershift"


def test_parse_model_data_missing_attributes_container(spider):
    """Test parsing model data when attributes container is missing."""
    html = """
    <html>
        <body>
            <div>
                <p>Some other content</p>
            </div>
        </body>
    </html>
    """
    url = "https://www.qualityfarmsupply.com/pages/tractor-specs"
    request = Request(url=url, meta={"make_filter": "Kubota", "model_index": 1})
    response = HtmlResponse(url=url, body=html, encoding="utf-8", request=request)

    results = list(spider.parse_model_data(response))

    # Should log warning and return no results when no attributes found
    assert len(results) == 0


def test_extract_spec_value_various_formats(spider):
    """Test _extract_spec_value handles various value formats."""
    item_data: dict[str, Any] = {}

    # Test HP values with different formats
    spider._extract_spec_value("engine hp", "75 HP", item_data)
    assert item_data["engine_hp"] == 75.0

    spider._extract_spec_value("pto hp", "65hp", item_data)
    assert item_data["pto_hp"] == 65.0

    # Test weight with commas
    spider._extract_spec_value("weight", "7,700 lbs", item_data)
    assert item_data["weight_lbs"] == 7700.0

    # Test transmission type
    spider._extract_spec_value("transmission", "PowerShift", item_data)
    assert item_data["transmission_type"] == "powershift"

    # Test series
    spider._extract_spec_value("series", "5E Series", item_data)
    assert item_data["series"] == "5E Series"


def test_extract_specs_from_container_definition_list(spider):
    """Test _extract_specs_from_container with definition list."""
    html = """
    <div class="specs">
        <dl>
            <dt>Engine HP</dt>
            <dd>75 HP</dd>
            <dt>PTO HP</dt>
            <dd>65 HP</dd>
        </dl>
    </div>
    """
    response = HtmlResponse(url="http://test.com", body=html, encoding="utf-8")
    container = response.css(".specs")

    item_data: dict[str, Any] = {}
    spider._extract_specs_from_container(container[0], item_data)

    assert item_data["engine_hp"] == 75.0
    assert item_data["pto_hp"] == 65.0


def test_extract_specs_from_container_table(spider):
    """Test _extract_specs_from_container with table format."""
    html = """
    <div class="specifications">
        <table>
            <tr>
                <td>Engine HP</td>
                <td>75</td>
            </tr>
            <tr>
                <td>Weight</td>
                <td>7,700 lbs</td>
            </tr>
        </table>
    </div>
    """
    response = HtmlResponse(url="http://test.com", body=html, encoding="utf-8")
    container = response.css(".specifications")

    item_data: dict[str, Any] = {}
    spider._extract_specs_from_container(container[0], item_data)

    assert item_data["engine_hp"] == 75.0
    assert item_data["weight_lbs"] == 7700.0
