"""Tests for the Quality Farm Supply spider."""

import pytest
from scrapy.http import HtmlResponse

from core.models import EquipmentCategory
from scrapers.spiders.quality_farm_supply import QualityFarmSupplySpider


@pytest.fixture
def spider():
    """Create a QualityFarmSupplySpider instance for testing."""
    return QualityFarmSupplySpider()


@pytest.fixture
def mock_response_table():
    """Create a mock HTML response with table layout."""
    from scrapy.http import Request
    
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
    from scrapy.http import Request
    
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
    """Test that parse generates requests for each target make when no filter is set."""
    from scrapy.http import Request
    
    html = "<html><body></body></html>"
    url = "https://www.qualityfarmsupply.com/pages/tractor-specs"
    # Create response without make_filter in meta
    request = Request(url=url, meta={})
    response = HtmlResponse(url=url, body=html, encoding="utf-8", request=request)
    
    results = list(spider.parse(response))
    
    # Should generate requests for each target make instead of parsing items
    assert len(results) == len(spider.target_makes)
    
    # Check that each result is a Request (not an item dict)
    for result in results:
        assert isinstance(result, Request)


def test_target_makes_filter(spider):
    """Test that target_makes filtering works."""
    from scrapy.http import Request
    
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
    from scrapy.http import Request
    
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
