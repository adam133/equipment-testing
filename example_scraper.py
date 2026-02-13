"""Example script demonstrating the Quality Farm Supply tractor scraper.

This script shows how to use the Quality Farm Supply spider to scrape
tractor specifications and return the data in useful formats (JSON, CSV, etc.).

Since the scraper requires network access to the actual website, this example
also includes mock data to demonstrate the output format.
"""

import json

from core.models import EquipmentCategory, Tractor, TransmissionType


def example_scraped_data() -> list[dict]:
    """Generate example data that would be returned by the scraper.

    Returns:
        List of tractor specification dictionaries
    """
    # Example data structure that the Quality Farm Supply scraper would return
    example_tractors = [
        {
            "make": "John Deere",
            "model": "5075E",
            "series": "5E Series",
            "category": EquipmentCategory.TRACTOR.value,
            "engine_hp": 75,
            "pto_hp": 65,
            "transmission_type": TransmissionType.POWERSHIFT.value,
            "weight_lbs": 7700,
            "source_url": "https://www.qualityfarmsupply.com/pages/tractor-specs",
        },
        {
            "make": "John Deere",
            "model": "6120M",
            "series": "6M Series",
            "category": EquipmentCategory.TRACTOR.value,
            "engine_hp": 120,
            "pto_hp": 105,
            "transmission_type": TransmissionType.POWERSHIFT.value,
            "weight_lbs": 12500,
            "source_url": "https://www.qualityfarmsupply.com/pages/tractor-specs",
        },
        {
            "make": "Case IH",
            "model": "Farmall 75C",
            "series": "Farmall C",
            "category": EquipmentCategory.TRACTOR.value,
            "engine_hp": 75,
            "pto_hp": 64,
            "transmission_type": TransmissionType.MANUAL.value,
            "weight_lbs": 7900,
            "source_url": "https://www.qualityfarmsupply.com/pages/tractor-specs",
        },
        {
            "make": "New Holland",
            "model": "T4.75",
            "series": "T4 Series",
            "category": EquipmentCategory.TRACTOR.value,
            "engine_hp": 75,
            "pto_hp": 59,
            "transmission_type": TransmissionType.POWERSHIFT.value,
            "weight_lbs": 8200,
            "source_url": "https://www.qualityfarmsupply.com/pages/tractor-specs",
        },
        {
            "make": "Kubota",
            "model": "M7-172",
            "series": "M7 Series",
            "category": EquipmentCategory.TRACTOR.value,
            "engine_hp": 170,
            "pto_hp": 145,
            "transmission_type": TransmissionType.CVT.value,
            "weight_lbs": 16500,
            "source_url": "https://www.qualityfarmsupply.com/pages/tractor-specs",
        },
    ]

    return example_tractors


def validate_and_convert_to_models(data: list[dict]) -> list[Tractor]:
    """Validate scraped data using Pydantic models.

    Args:
        data: List of tractor dictionaries

    Returns:
        List of validated Tractor model instances
    """
    tractors = []
    for item in data:
        try:
            tractor = Tractor(**item)
            tractors.append(tractor)
        except Exception as e:
            print(f"Validation error for {item.get('make')} {item.get('model')}: {e}")
    return tractors


def export_to_json(tractors: list[Tractor], filename: str = "tractors.json") -> None:
    """Export tractor data to JSON file.

    Args:
        tractors: List of Tractor model instances
        filename: Output filename
    """
    data = [tractor.model_dump(mode="json") for tractor in tractors]
    with open(filename, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"✓ Exported {len(tractors)} tractors to {filename}")


def export_to_csv(tractors: list[Tractor], filename: str = "tractors.csv") -> None:
    """Export tractor data to CSV file.

    Args:
        tractors: List of Tractor model instances
        filename: Output filename
    """
    import csv

    if not tractors:
        print("No tractors to export")
        return

    # Get all fields from the first tractor
    fieldnames = list(tractors[0].model_dump().keys())

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for tractor in tractors:
            writer.writerow(tractor.model_dump())

    print(f"✓ Exported {len(tractors)} tractors to {filename}")


def print_summary(tractors: list[Tractor]) -> None:
    """Print a summary of the scraped tractors.

    Args:
        tractors: List of Tractor model instances
    """
    print("\n" + "=" * 70)
    print("TRACTOR SPECIFICATIONS SUMMARY")
    print("=" * 70)
    print(f"\nTotal tractors scraped: {len(tractors)}")

    # Group by make
    makes = {}
    for tractor in tractors:
        makes[tractor.make] = makes.get(tractor.make, 0) + 1

    print("\nTractors by manufacturer:")
    for make, count in sorted(makes.items()):
        print(f"  - {make}: {count}")

    # Calculate average HP
    avg_engine_hp = sum(t.engine_hp for t in tractors if t.engine_hp) / len(
        [t for t in tractors if t.engine_hp]
    )
    avg_pto_hp = sum(t.pto_hp for t in tractors if t.pto_hp) / len(
        [t for t in tractors if t.pto_hp]
    )

    print(f"\nAverage Engine HP: {avg_engine_hp:.1f}")
    print(f"Average PTO HP: {avg_pto_hp:.1f}")

    print("\n" + "=" * 70)
    print("DETAILED SPECIFICATIONS")
    print("=" * 70)

    for i, tractor in enumerate(tractors, 1):
        print(f"\n{i}. {tractor.make} {tractor.model}")
        if tractor.series:
            print(f"   Series: {tractor.series}")
        if tractor.engine_hp:
            print(f"   Engine HP: {tractor.engine_hp}")
        if tractor.pto_hp:
            print(f"   PTO HP: {tractor.pto_hp}")
        if tractor.transmission_type:
            print(f"   Transmission: {tractor.transmission_type}")
        if tractor.weight_lbs:
            print(f"   Weight: {tractor.weight_lbs:,} lbs")


def run_scraper_example() -> None:
    """Demonstrate how to run the scraper and process results."""
    print("\n🚜 Quality Farm Supply Tractor Scraper Example 🚜\n")
    print("=" * 70)

    # In production, you would run the actual spider like this:
    # from scrapy.crawler import CrawlerProcess
    # from scrapers.spiders.quality_farm_supply import QualityFarmSupplySpider
    #
    # process = CrawlerProcess(settings={
    #     'FEEDS': {
    #         'tractors.json': {'format': 'json'},
    #     },
    # })
    # process.crawl(QualityFarmSupplySpider)
    # process.start()

    print("NOTE: This example uses mock data to demonstrate the output format.")
    print("To scrape real data, run: scrapy crawl quality_farm_supply")
    print("=" * 70)

    # Get example data
    print("\nLoading example tractor data...")
    raw_data = example_scraped_data()

    # Validate with Pydantic models
    print("Validating data with Pydantic models...")
    tractors = validate_and_convert_to_models(raw_data)

    # Print summary
    print_summary(tractors)

    # Export to different formats
    print("\n" + "=" * 70)
    print("EXPORTING DATA")
    print("=" * 70 + "\n")

    export_to_json(tractors, "/tmp/quality_farm_tractors.json")
    export_to_csv(tractors, "/tmp/quality_farm_tractors.csv")

    # Show JSON example
    print("\nExample JSON output (first tractor):")
    print("-" * 70)
    print(json.dumps(tractors[0].model_dump(mode="json"), indent=2, default=str))

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("""
To use this scraper in production:

1. Run the spider directly:
   scrapy crawl quality_farm_supply -o output.json

2. Run with custom settings:
   scrapy crawl quality_farm_supply -o output.csv -s CONCURRENT_REQUESTS=1

3. Use in Python code:
   from scrapy.crawler import CrawlerProcess
   from scrapers.spiders.quality_farm_supply import QualityFarmSupplySpider

   process = CrawlerProcess()
   process.crawl(QualityFarmSupplySpider)
   process.start()

4. Filter by specific makes:
   Modify the `target_makes` list in the spider to focus on specific manufacturers.
""")


def main() -> None:
    """Main entry point."""
    run_scraper_example()


if __name__ == "__main__":
    main()
