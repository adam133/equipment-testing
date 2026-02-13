"""Tests for equipment hierarchy and sprayer models."""

import pytest
from core.models import (
    CommonEquipment,
    EquipmentCategory,
    Sprayer,
    SprayerBoomType,
    Tractor,
    TransmissionType,
    create_equipment,
)
from pydantic import ValidationError


def test_brand_hierarchy_field():
    """Test that brand field can be set on equipment."""
    tractor = Tractor(
        brand="Deere & Company",
        make="John Deere",
        model="5075E",
        series="5E Series",
    )

    assert tractor.brand == "Deere & Company"
    assert tractor.make == "John Deere"
    assert tractor.series == "5E Series"


def test_submodel_field():
    """Test that submodel field works for variants."""
    tractor = Tractor(
        make="John Deere",
        model="5075E",
        series="5E Series",
        submodel="Premium",
        rear_remote_valves=4,
    )

    assert tractor.submodel == "Premium"
    assert tractor.rear_remote_valves == 4


def test_complete_hierarchy():
    """Test all hierarchy levels together."""
    equipment = Tractor(
        brand="CNH Industrial",
        make="Case IH",
        series="Magnum Series",
        model="Magnum 340",
        submodel="CVX",
        engine_hp=340,
    )

    assert equipment.brand == "CNH Industrial"
    assert equipment.make == "Case IH"
    assert equipment.series == "Magnum Series"
    assert equipment.model == "Magnum 340"
    assert equipment.submodel == "CVX"


def test_hierarchy_all_optional():
    """Test that hierarchy fields are all optional."""
    # Should work with just required fields
    equipment = CommonEquipment(
        make="Test",
        model="Model",
        category=EquipmentCategory.OTHER,
    )

    assert equipment.brand is None
    assert equipment.series is None
    assert equipment.submodel is None


def test_sprayer_creation():
    """Test creating a sprayer instance."""
    sprayer = Sprayer(
        make="John Deere",
        model="R4045",
        series="R4 Series",
        engine_hp=405,
        tank_capacity_gal=1200,
        boom_width_ft=120,
        boom_type=SprayerBoomType.FOLDING,
    )

    assert sprayer.make == "John Deere"
    assert sprayer.model == "R4045"
    assert sprayer.category == EquipmentCategory.SPRAYER
    assert sprayer.engine_hp == 405
    assert sprayer.tank_capacity_gal == 1200
    assert sprayer.boom_width_ft == 120


def test_sprayer_complete_attributes():
    """Test sprayer with comprehensive attributes."""
    sprayer = Sprayer(
        make="John Deere",
        series="R4 Series",
        model="R4045",
        year_start=2020,
        # Power
        engine_hp=405,
        rated_rpm=2100,
        # Tank
        tank_capacity_gal=1200,
        tank_material="Polyethylene",
        # Boom
        boom_width_ft=120,
        boom_height_ft=60,
        boom_type=SprayerBoomType.FOLDING,
        nozzle_spacing_inches=20,
        number_of_nozzles=72,
        # Application
        application_rate_gal_per_acre=15.0,
        ground_speed_mph_min=5.0,
        ground_speed_mph_max=25.0,
        pump_capacity_gal_min=80.0,
        # Physical
        weight_lbs=36000,
        wheelbase_inches=156,
        row_crop_capable=True,
    )

    assert sprayer.engine_hp == 405
    assert sprayer.boom_type == SprayerBoomType.FOLDING
    assert sprayer.number_of_nozzles == 72
    assert sprayer.row_crop_capable is True


def test_sprayer_negative_values():
    """Test that sprayer validates negative values."""
    with pytest.raises(ValidationError):
        Sprayer(
            make="Test",
            model="Model",
            tank_capacity_gal=-100,
        )


def test_sprayer_invalid_speed_range():
    """Test that max speed cannot be less than min speed."""
    with pytest.raises(ValidationError):
        Sprayer(
            make="Test",
            model="Model",
            ground_speed_mph_min=20.0,
            ground_speed_mph_max=10.0,
        )


def test_sprayer_boom_width_limit():
    """Test that boom width has reasonable upper limit."""
    with pytest.raises(ValidationError):
        Sprayer(
            make="Test",
            model="Model",
            boom_width_ft=250,  # Over 200 ft limit
        )


def test_sprayer_boom_types():
    """Test different boom type enums."""
    for boom_type in [
        SprayerBoomType.RIGID,
        SprayerBoomType.FOLDING,
        SprayerBoomType.TRUSS,
        SprayerBoomType.HYBRID,
    ]:
        sprayer = Sprayer(
            make="Test",
            model="Model",
            boom_type=boom_type,
        )
        assert sprayer.boom_type == boom_type


def test_create_equipment_sprayer():
    """Test create_equipment factory function for sprayer."""
    data = {
        "make": "Case IH",
        "model": "Patriot 4440",
        "category": "sprayer",
        "tank_capacity_gal": 1200,
        "boom_width_ft": 120,
    }

    equipment = create_equipment(data)

    assert isinstance(equipment, Sprayer)
    assert equipment.make == "Case IH"
    assert equipment.tank_capacity_gal == 1200


def test_sprayer_serialization():
    """Test that sprayer can be serialized to dict."""
    sprayer = Sprayer(
        make="New Holland",
        model="Guardian SP.345F",
        engine_hp=345,
        boom_width_ft=120,
    )

    data = sprayer.model_dump()

    assert isinstance(data, dict)
    assert data["make"] == "New Holland"
    assert data["model"] == "Guardian SP.345F"
    assert data["category"] == "sprayer"
    assert data["engine_hp"] == 345


def test_hierarchy_with_sprayer():
    """Test hierarchy fields work with sprayer."""
    sprayer = Sprayer(
        brand="CNH Industrial",
        make="Case IH",
        series="Patriot Series",
        model="Patriot 4440",
        submodel="AirRide",
        tank_capacity_gal=1200,
    )

    assert sprayer.brand == "CNH Industrial"
    assert sprayer.make == "Case IH"
    assert sprayer.series == "Patriot Series"
    assert sprayer.submodel == "AirRide"


def test_tractor_with_hierarchy():
    """Test tractor with full hierarchy and realistic attributes."""
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
        rear_remote_valves=4,  # Premium package upgrade
        hydraulic_flow=16.0,
    )

    assert tractor.brand == "Deere & Company"
    assert tractor.submodel == "Premium"
    assert tractor.rear_remote_valves == 4


def test_equipment_without_hierarchy():
    """Test that equipment works without hierarchy fields."""
    # Mimics older data without hierarchy
    sprayer = Sprayer(
        make="Generic",
        model="Sprayer 1000",
        tank_capacity_gal=800,
    )

    assert sprayer.brand is None
    assert sprayer.series is None
    assert sprayer.submodel is None
    assert sprayer.make == "Generic"


def test_hierarchy_inheritance_concept():
    """Test concept of attribute inheritance (documentation example)."""
    # In practice, series-level attributes would be stored separately
    # and merged at query time, but models support the fields

    # Series-level tractor (conceptual)
    series_tractor = Tractor(
        make="John Deere",
        series="5E Series",
        model="5E Series",  # Generic series entry
        transmission_type=TransmissionType.POWERSHIFT,
        hydraulic_pressure=3000,
    )

    # Specific model inherits/overrides
    model_tractor = Tractor(
        make="John Deere",
        series="5E Series",
        model="5075E",
        pto_hp=65,  # Model-specific
        engine_hp=75,
        transmission_type=TransmissionType.POWERSHIFT,  # Inherited from series
        hydraulic_pressure=3000,  # Inherited from series
    )

    assert series_tractor.transmission_type == model_tractor.transmission_type
    assert model_tractor.pto_hp == 65  # Model-specific attribute
