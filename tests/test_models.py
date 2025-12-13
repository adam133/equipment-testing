"""Tests for core equipment models."""

import pytest
from pydantic import ValidationError

from core.models import (
    Combine,
    CommonEquipment,
    EquipmentCategory,
    Implement,
    SeparatorType,
    Tractor,
    TransmissionType,
    create_equipment,
)


def test_common_equipment_creation():
    """Test creating a basic CommonEquipment instance."""
    equipment = CommonEquipment(
        make="Generic",
        model="Test Model",
        category=EquipmentCategory.OTHER,
    )

    assert equipment.make == "Generic"
    assert equipment.model == "Test Model"
    assert equipment.category == EquipmentCategory.OTHER


def test_common_equipment_with_years():
    """Test CommonEquipment with year range."""
    equipment = CommonEquipment(
        make="Test",
        model="Model",
        category=EquipmentCategory.TRACTOR,
        year_start=2010,
        year_end=2020,
    )

    assert equipment.year_start == 2010
    assert equipment.year_end == 2020


def test_invalid_year_range():
    """Test that year_end cannot be before year_start."""
    with pytest.raises(ValidationError):
        CommonEquipment(
            make="Test",
            model="Model",
            category=EquipmentCategory.TRACTOR,
            year_start=2020,
            year_end=2010,
        )


def test_tractor_creation():
    """Test creating a Tractor instance."""
    tractor = Tractor(
        make="John Deere",
        model="5075E",
        series="5E Series",
        year_start=2014,
        pto_hp=65,
        engine_hp=75,
        transmission_type=TransmissionType.POWERSHIFT,
        hydraulic_flow=16.0,
    )

    assert tractor.make == "John Deere"
    assert tractor.model == "5075E"
    assert tractor.category == EquipmentCategory.TRACTOR
    assert tractor.pto_hp == 65
    assert tractor.engine_hp == 75
    assert tractor.transmission_type == TransmissionType.POWERSHIFT


def test_tractor_negative_hp():
    """Test that tractor HP cannot be negative."""
    with pytest.raises(ValidationError):
        Tractor(
            make="Test",
            model="Model",
            pto_hp=-10,
        )


def test_combine_creation():
    """Test creating a Combine instance."""
    combine = Combine(
        make="Case IH",
        model="8250",
        series="Axial-Flow",
        year_start=2018,
        engine_hp=450,
        separator_type=SeparatorType.ROTARY,
        grain_tank_capacity_bu=350,
        unloading_rate_bu_min=4.5,
    )

    assert combine.make == "Case IH"
    assert combine.model == "8250"
    assert combine.category == EquipmentCategory.COMBINE
    assert combine.separator_type == SeparatorType.ROTARY
    assert combine.grain_tank_capacity_bu == 350


def test_implement_creation():
    """Test creating an Implement instance."""
    implement = Implement(
        make="Kinze",
        model="3600",
        year_start=2015,
        working_width_ft=40,
        number_of_rows=16,
        row_spacing_inches=30,
        required_hp_min=250,
        required_hp_max=350,
    )

    assert implement.make == "Kinze"
    assert implement.model == "3600"
    assert implement.category == EquipmentCategory.IMPLEMENT
    assert implement.number_of_rows == 16
    assert implement.row_spacing_inches == 30


def test_create_equipment_tractor():
    """Test create_equipment factory function for tractor."""
    data = {
        "make": "New Holland",
        "model": "T7.270",
        "category": "tractor",
        "engine_hp": 270,
    }

    equipment = create_equipment(data)

    assert isinstance(equipment, Tractor)
    assert equipment.make == "New Holland"
    assert equipment.engine_hp == 270


def test_create_equipment_combine():
    """Test create_equipment factory function for combine."""
    data = {
        "make": "John Deere",
        "model": "S780",
        "category": "combine",
        "grain_tank_capacity_bu": 400,
    }

    equipment = create_equipment(data)

    assert isinstance(equipment, Combine)
    assert equipment.make == "John Deere"
    assert equipment.grain_tank_capacity_bu == 400


def test_create_equipment_implement():
    """Test create_equipment factory function for implement."""
    data = {
        "make": "Great Plains",
        "model": "3P1006NT",
        "category": "implement",
        "working_width_ft": 10,
    }

    equipment = create_equipment(data)

    assert isinstance(equipment, Implement)
    assert equipment.make == "Great Plains"
    assert equipment.working_width_ft == 10


def test_model_serialization():
    """Test that models can be serialized to dict."""
    tractor = Tractor(
        make="Kubota",
        model="M7-172",
        engine_hp=170,
        transmission_type=TransmissionType.CVT,
    )

    data = tractor.model_dump()

    assert isinstance(data, dict)
    assert data["make"] == "Kubota"
    assert data["model"] == "M7-172"
    assert data["category"] == "tractor"
    assert "created_at" in data
    assert "updated_at" in data
