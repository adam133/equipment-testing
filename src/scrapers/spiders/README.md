# Quality Farm Supply Tractor Scraper

This directory contains a web scraper for collecting tractor specifications from Quality Farm Supply's tractor specs page.

## Overview

The scraper is built using Scrapy and targets `https://www.qualityfarmsupply.com/pages/tractor-specs` to extract tractor specifications including:

- Make (manufacturer)
- Model
- Series
- Engine HP
- PTO HP
- Transmission type
- Weight
- Additional specifications

## Files

- `quality_farm_supply.py` - The Scrapy spider implementation
- `../../../example_scraper.py` - Example script demonstrating usage and output formats

## Features

- **Multiple parsing strategies**: Handles different page layouts (tables, cards, detail pages)
- **Data validation**: Uses Pydantic models for type checking and validation
- **Flexible filtering**: Can filter by specific manufacturers
- **Multiple output formats**: Supports JSON, CSV, and other Scrapy feed formats
- **Robust selectors**: Multiple fallback CSS selectors for resilient scraping

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

### Run the Example Script

```bash
# From repository root
python3 example_scraper.py
```

The example script demonstrates:
- Data validation with Pydantic models
- Exporting to JSON and CSV formats
- Summary statistics
- Proper data structure

## Configuration

### Filter by Manufacturer

Edit the `target_makes` list in `quality_farm_supply.py`:

```python
# Only scrape these manufacturers
target_makes = ["John Deere", "Case IH", "New Holland"]
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

The spider implements three parsing strategies to handle different page layouts:

1. **Table-based parsing** (`_parse_table`): For pages with specification tables
2. **Card-based parsing** (`_parse_cards`): For pages with card/grid layouts
3. **Detail page parsing** (`parse_tractor_detail`): For individual tractor pages

The spider automatically detects which strategy to use based on the page structure.

## Best Practices

1. **Respect robots.txt**: The spider respects the site's robots.txt by default
2. **Rate limiting**: Use `CONCURRENT_REQUESTS` setting to control request rate
3. **User agent**: Set a descriptive user agent in Scrapy settings
4. **Error handling**: The spider logs warnings for parsing issues
5. **Data validation**: All data is validated through Pydantic models before output

## Troubleshooting

### No data extracted

Check the page structure:
```bash
scrapy shell "https://www.qualityfarmsupply.com/pages/tractor-specs"
```

Then test selectors:
```python
response.css('table tr')  # For table layout
response.css('.tractor-card')  # For card layout
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
```

## Future Enhancements

- [ ] Add support for additional equipment types (combines, implements)
- [ ] Implement pagination for multiple pages of specs
- [ ] Add caching to avoid re-scraping unchanged data
- [ ] Integrate with Unity Catalog for storage
- [ ] Add data quality checks and anomaly detection

## Dependencies

- `scrapy>=2.11.0` - Web scraping framework
- `pydantic>=2.0.0` - Data validation
- `httpx>=0.25.0` - HTTP client (used by Scrapy)

## License

MIT License - See LICENSE file in repository root.
