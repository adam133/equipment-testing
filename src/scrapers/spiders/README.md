# Quality Farm Supply Tractor Scraper

This directory contains a web scraper for collecting tractor specifications from Quality Farm Supply's tractor specs page.

## Overview

The scraper is built using Scrapy with Playwright integration and targets `https://www.qualityfarmsupply.com/pages/tractor-specs` to extract tractor specifications including:

- Make (manufacturer)
- Model
- Series
- Engine HP
- PTO HP
- Transmission type
- Weight
- Additional specifications

**Important:** This scraper uses Playwright to handle JavaScript-based form navigation. The tractor specs page requires interacting with make/model filter dropdowns to load the data dynamically.

## Files

- `quality_farm_supply.py` - The Scrapy spider implementation with Playwright support

## Features

- **Playwright integration**: Handles JavaScript-rendered content and form navigation
- **Dynamic form filtering**: Automatically iterates through manufacturer filters to extract data
- **Multiple parsing strategies**: Handles different page layouts (tables, cards, detail pages)
- **Data validation**: Uses Pydantic models for type checking and validation
- **Flexible filtering**: Can filter by specific manufacturers
- **Multiple output formats**: Supports JSON, CSV, and other Scrapy feed formats
- **Robust selectors**: Multiple fallback CSS selectors for resilient scraping

## Dependencies

Before running the scraper, ensure you have the required dependencies installed:

```bash
# Install Playwright dependencies
pip install scrapy-playwright playwright

# Install Playwright browsers
python -m playwright install chromium
```

Or install from the optional dependency group:

```bash
pip install -e ".[scraping]"
python -m playwright install chromium
```

## Usage

### Run the Spider Directly

```bash
# Output to JSON
scrapy crawl quality_farm_supply -o tractors.json

# Output to CSV
scrapy crawl quality_farm_supply -o tractors.csv

# With custom settings
scrapy crawl quality_farm_supply -o output.json -s CONCURRENT_REQUESTS=1
```

### Use in Python Code

```python
from scrapy.crawler import CrawlerProcess
from scrapers.spiders.quality_farm_supply import QualityFarmSupplySpider

process = CrawlerProcess(settings={
    'FEEDS': {
        'tractors.json': {'format': 'json'},
    },
})
process.crawl(QualityFarmSupplySpider)
process.start()
```

## Configuration

### Filter by Manufacturer

Edit the `target_makes` list in `quality_farm_supply.py`:

```python
# Only scrape these manufacturers
target_makes = ["John Deere", "Case IH", "New Holland"]
```

The spider will automatically iterate through each make, applying the filter and scraping results.

### Playwright Settings

The spider includes custom settings for Playwright. These can be overridden in your Scrapy settings:

```python
# In settings.py or spider custom_settings
PLAYWRIGHT_BROWSER_TYPE = "chromium"  # or "firefox", "webkit"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,  # Run without visible browser
    "timeout": 30000,  # 30 second timeout
}
```

### Customize Output

Use Scrapy's feed settings to control output:

```python
FEEDS = {
    'tractors.json': {
        'format': 'json',
        'encoding': 'utf8',
        'indent': 2,
    },
    'tractors.csv': {
        'format': 'csv',
        'fields': ['make', 'model', 'engine_hp', 'pto_hp'],
    },
}
```

## Data Structure

The scraper returns tractor data in the following structure:

```json
{
  "make": "John Deere",
  "model": "5075E",
  "series": "5E Series",
  "category": "tractor",
  "engine_hp": 75.0,
  "pto_hp": 65.0,
  "transmission_type": "powershift",
  "weight_lbs": 7700.0,
  "source_url": "https://www.qualityfarmsupply.com/pages/tractor-specs"
}
```

All fields are validated using the `Tractor` Pydantic model from `core.models`.

## Parsing Strategies

The spider implements multiple parsing strategies to handle different page layouts:

1. **Form Navigation** (Primary): Uses Playwright to interact with make/model filter dropdowns
2. **Table-based parsing** (`_parse_table`): For pages with specification tables
3. **Card-based parsing** (`_parse_cards`): For pages with card/grid layouts
4. **Detail page parsing** (`parse_tractor_detail`): For individual tractor pages

### How Form Navigation Works

1. Spider loads the initial page with Playwright
2. If no make filter is active, it generates requests for each target make
3. For each make, Playwright:
   - Waits for the page to load completely (`networkidle`)
   - Locates filter select elements
   - Selects the desired make from the dropdown
   - Triggers the change event to load filtered results
   - Waits for results to render
4. Spider then parses the filtered HTML content using the appropriate strategy

## Best Practices

1. **Respect robots.txt**: The spider respects the site's robots.txt by default
2. **Rate limiting**: Use `CONCURRENT_REQUESTS` setting to control request rate (especially important with Playwright)
3. **User agent**: Set a descriptive user agent in Scrapy settings
4. **Error handling**: The spider logs warnings for parsing issues and closes Playwright pages properly
5. **Data validation**: All data is validated through Pydantic models before output
6. **Browser resources**: Playwright contexts are limited to avoid resource exhaustion

## Troubleshooting

### No data extracted

1. Verify Playwright is working:
```bash
scrapy crawl quality_farm_supply -L DEBUG
```

2. Check for JavaScript errors in logs

3. Test with Playwright shell:
```bash
scrapy shell "https://www.qualityfarmsupply.com/pages/tractor-specs" -s DOWNLOAD_HANDLERS='{"https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"}'
```

Then test selectors:
```python
# For table layout
response.css('table tr')

# For card layout
response.css('.tractor-card')

# Check if Playwright rendered the page
await response.meta['playwright_page'].content()
```

### Playwright issues

If you get "No module named 'playwright'":
```bash
pip install scrapy-playwright playwright
python -m playwright install chromium
```

If browser doesn't launch:
```bash
# Check playwright installation
playwright install --help

# Try with visible browser (for debugging)
scrapy crawl quality_farm_supply -s PLAYWRIGHT_LAUNCH_OPTIONS='{"headless": False}'
```

### Validation errors

Check the logs for Pydantic validation errors:
```bash
scrapy crawl quality_farm_supply -L DEBUG
```

### Network issues

Add retry middleware and increase timeout:
```python
RETRY_TIMES = 3
DOWNLOAD_TIMEOUT = 30
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 60000  # 60 seconds for slow connections
```

## Technical Implementation Details

### Playwright Page Actions

The spider uses Playwright page actions to manipulate the page:

1. `page.wait_for_load_state('networkidle')` - Waits for network to be idle
2. `page.wait_for_selector()` - Waits for filter elements to appear
3. `page.evaluate()` - Executes JavaScript to select filter options
4. `page.wait_for_timeout()` - Waits for filtered results to render

### Request Flow

```
Initial Request (no filter)
    ↓
Generate Requests for Each Make
    ↓
Playwright Request (make=John Deere)
    ↓
Page loads → Execute JS to filter → Wait for results
    ↓
Parse HTML → Extract Items
```

## Future Enhancements

- [ ] Add support for additional equipment types (combines, implements)
- [ ] Implement pagination for multiple pages of specs
- [ ] Add support for model-level filtering in addition to make filtering
- [ ] Implement caching to avoid re-filtering unchanged data
- [ ] Integrate with Unity Catalog for storage
- [ ] Add data quality checks and anomaly detection

## Dependencies

- `scrapy>=2.11.0` - Web scraping framework
- `scrapy-playwright>=0.0.34` - Playwright integration for Scrapy
- `playwright>=1.40.0` - Browser automation
- `pydantic>=2.0.0` - Data validation
- `httpx>=0.25.0` - HTTP client (used by Scrapy)

## License

MIT License - See LICENSE file in repository root.
