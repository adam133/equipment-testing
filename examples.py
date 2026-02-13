"""Example usage of OpenAg-DB models and API.

This script demonstrates how to create equipment models, validate data,
and work with the OpenAg-DB API.
"""

from core.models import (
    Combine,
    Implement,
    SeparatorType,
    Sprayer,
    SprayerBoomType,
    Tractor,
    TransmissionType,
)


def example_tractor() -> Tractor:
    """Create and display a tractor example."""
    print("=" * 60)
    print("Example: Creating a Tractor with Hierarchy")
    print("=" * 60)

    tractor = Tractor(
        brand="Deere & Company",
        make="John Deere",
        series="5E Series",
        model="5075E",
        submodel="Premium",
        year_start=2014,
        year_end=2022,
        pto_hp=65,
        engine_hp=75,
        transmission_type=TransmissionType.POWERSHIFT,
        forward_gears=12,
        reverse_gears=12,
        hydraulic_flow=16.0,
        hydraulic_pressure=3000,
        rear_remote_valves=4,  # Premium package
        weight_lbs=7700,
    )

    print(f"\nBrand: {tractor.brand}")
    print(f"Make: {tractor.make}")
    print(f"Series: {tractor.series}")
    print(f"Model: {tractor.model}")
    print(f"Submodel: {tractor.submodel}")
    print(f"Years: {tractor.year_start}-{tractor.year_end}")
    print(f"PTO HP: {tractor.pto_hp}")
    print(f"Engine HP: {tractor.engine_hp}")
    print(f"Transmission: {tractor.transmission_type}")
    print(f"Hydraulic Flow: {tractor.hydraulic_flow} GPM")
    print(f"Remote Valves: {tractor.rear_remote_valves}")
    print(f"Weight: {tractor.weight_lbs} lbs")

    return tractor


def example_combine() -> Combine:
    """Create and display a combine example."""
    print("\n" + "=" * 60)
    print("Example: Creating a Combine")
    print("=" * 60)

    combine = Combine(
        make="Case IH",
        model="8250",
        series="Axial-Flow",
        year_start=2018,
        engine_hp=450,
        separator_type=SeparatorType.ROTARY,
        separator_width_inches=44,
        grain_tank_capacity_bu=350,
        unloading_rate_bu_min=4.5,
        unloading_auger_length_ft=28,
        weight_lbs=42000,
    )

    print(f"\nMake: {combine.make}")
    print(f"Model: {combine.model}")
    print(f"Series: {combine.series}")
    print(f"Engine HP: {combine.engine_hp}")
    print(f"Separator Type: {combine.separator_type}")
    print(f"Grain Tank: {combine.grain_tank_capacity_bu} bu")
    print(f"Unloading Rate: {combine.unloading_rate_bu_min} bu/min")

    return combine


def example_implement() -> Implement:
    """Create and display an implement example."""
    print("\n" + "=" * 60)
    print("Example: Creating an Implement (Planter)")
    print("=" * 60)

    planter = Implement(
        make="Kinze",
        model="3600",
        year_start=2015,
        working_width_ft=40,
        number_of_rows=16,
        row_spacing_inches=30,
        required_hp_min=250,
        required_hp_max=350,
        weight_lbs=18500,
    )

    print(f"\nMake: {planter.make}")
    print(f"Model: {planter.model}")
    print(f"Working Width: {planter.working_width_ft} ft")
    print(f"Rows: {planter.number_of_rows}")
    print(f"Row Spacing: {planter.row_spacing_inches} in")
    print(f"Required HP: {planter.required_hp_min}-{planter.required_hp_max}")
    print(f"Weight: {planter.weight_lbs} lbs")

    return planter


def example_sprayer() -> Sprayer:
    """Create and display a self-propelled sprayer example."""
    print("\n" + "=" * 60)
    print("Example: Creating a Self-Propelled Sprayer")
    print("=" * 60)

    sprayer = Sprayer(
        brand="CNH Industrial",
        make="Case IH",
        series="Patriot Series",
        model="Patriot 4440",
        submodel="AirRide",
        year_start=2020,
        engine_hp=405,
        tank_capacity_gal=1200,
        tank_material="Polyethylene",
        boom_width_ft=120,
        boom_height_ft=60,
        boom_type=SprayerBoomType.FOLDING,
        nozzle_spacing_inches=20,
        number_of_nozzles=72,
        application_rate_gal_per_acre=15.0,
        pump_capacity_gal_min=80.0,
        ground_speed_mph_max=25.0,
        row_crop_capable=True,
        weight_lbs=36000,
        wheelbase_inches=156,
    )

    print(f"\nBrand: {sprayer.brand}")
    print(f"Make: {sprayer.make}")
    print(f"Series: {sprayer.series}")
    print(f"Model: {sprayer.model}")
    print(f"Submodel: {sprayer.submodel}")
    print(f"Engine HP: {sprayer.engine_hp}")
    print(f"Tank Capacity: {sprayer.tank_capacity_gal} gal")
    print(f"Boom Width: {sprayer.boom_width_ft} ft")
    print(f"Boom Type: {sprayer.boom_type}")
    print(f"Number of Nozzles: {sprayer.number_of_nozzles}")
    print(f"Max Speed: {sprayer.ground_speed_mph_max} MPH")
    print(f"Row Crop Capable: {sprayer.row_crop_capable}")

    return sprayer


def example_json_export(equipment: Tractor | Combine | Implement | Sprayer) -> None:
    """Demonstrate JSON export."""
    print("\n" + "=" * 60)
    print("Example: Exporting to JSON")
    print("=" * 60)

    import json

    data = equipment.model_dump()
    print("\nJSON Output:")
    print(json.dumps(data, indent=2, default=str))


def main() -> None:
    """Run all examples."""
    print("\n🌾 OpenAg-DB - Agricultural Equipment Database Examples 🌾\n")

    # Create examples
    tractor = example_tractor()
    combine = example_combine()
    sprayer = example_sprayer()
    planter = example_implement()

    # Show JSON export for all examples
    example_json_export(tractor)
    example_json_export(combine)
    example_json_export(sprayer)
    example_json_export(planter)

    print("\n" + "=" * 60)
    print("Examples Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start the API server: uv run openagdb-api")
    print("2. Visit API docs: http://localhost:8000/docs")
    print("3. Query equipment: http://localhost:8000/equipment")
    print()


if __name__ == "__main__":
    main()
