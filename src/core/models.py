"""Pydantic models for agricultural equipment data.

This module defines the base equipment model and polymorphic sub-models
for different types of agricultural equipment (tractors, combines, implements).
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class EquipmentCategory(StrEnum):
    """Category of agricultural equipment."""

    TRACTOR = "tractor"
    COMBINE = "combine"
    IMPLEMENT = "implement"
    HARVESTER = "harvester"
    PLANTER = "planter"
    SPRAYER = "sprayer"
    OTHER = "other"


class TransmissionType(StrEnum):
    """Type of transmission for tractors."""

    MANUAL = "manual"
    POWERSHIFT = "powershift"
    CVT = "cvt"
    HYDROSTATIC = "hydrostatic"
    IVT = "ivt"
    OTHER = "other"


class SeparatorType(StrEnum):
    """Type of separator for combines."""

    CONVENTIONAL = "conventional"
    ROTARY = "rotary"
    HYBRID = "hybrid"


class SprayerBoomType(StrEnum):
    """Type of boom configuration for sprayers."""

    RIGID = "rigid"
    FOLDING = "folding"
    TRUSS = "truss"
    HYBRID = "hybrid"
    OTHER = "other"


class CommonEquipment(BaseModel):
    """Base model for all agricultural equipment.

    This model contains common fields shared across all equipment types.
    Supports equipment hierarchy: Brand → Make → Series → Model → Submodel.
    """

    # Required fields
    make: str = Field(..., description="Manufacturer/brand name")
    model: str = Field(..., description="Model designation")
    category: EquipmentCategory = Field(..., description="Equipment category")

    # Hierarchy fields (optional, support attribute inheritance)
    brand: str | None = Field(
        None, description="Parent brand or ownership (e.g., CNH Industrial, AGCO)"
    )
    series: str | None = Field(
        None, description="Model series or family (e.g., 5E Series, Magnum Series)"
    )
    submodel: str | None = Field(
        None,
        description="Configuration variant or package (e.g., Premium, Deluxe)",
    )

    # Production years
    year_start: int | None = Field(
        None, description="First year of production", ge=1900, le=2100
    )
    year_end: int | None = Field(
        None, description="Last year of production", ge=1900, le=2100
    )

    # Optional descriptive fields
    description: str | None = Field(None, description="Equipment description")
    image_url: str | None = Field(None, description="URL to equipment image")

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source_url: str | None = Field(None, description="URL of data source")

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("year_end")
    @classmethod
    def validate_year_range(cls, v: int | None, info: ValidationInfo) -> int | None:
        """Validate that year_end is not before year_start."""
        if v is not None and info.data.get("year_start") is not None:
            if v < info.data["year_start"]:
                raise ValueError("year_end must be >= year_start")
        return v


class Tractor(CommonEquipment):
    """Model for tractor equipment.

    Extends CommonEquipment with tractor-specific attributes.
    """

    category: Literal[EquipmentCategory.TRACTOR] = EquipmentCategory.TRACTOR

    # Power specifications
    pto_hp: float | None = Field(None, description="Power Take-Off horsepower", ge=0)
    engine_hp: float | None = Field(None, description="Engine horsepower", ge=0)
    rated_rpm: int | None = Field(None, description="Rated engine RPM", ge=0, le=10000)

    # Transmission
    transmission_type: TransmissionType | None = Field(
        None, description="Type of transmission"
    )
    forward_gears: int | None = Field(None, description="Number of forward gears", ge=0)
    reverse_gears: int | None = Field(None, description="Number of reverse gears", ge=0)

    # Hydraulics
    hydraulic_flow: float | None = Field(
        None, description="Hydraulic flow rate in GPM", ge=0
    )
    hydraulic_pressure: float | None = Field(
        None, description="Hydraulic pressure in PSI", ge=0
    )
    rear_remote_valves: int | None = Field(
        None, description="Number of rear hydraulic remote valves", ge=0
    )

    # Physical specifications
    weight_lbs: float | None = Field(None, description="Operating weight in lbs", ge=0)
    wheelbase_inches: float | None = Field(
        None, description="Wheelbase length in inches", ge=0
    )

    # Three-point hitch
    hitch_lift_capacity: float | None = Field(
        None, description="Three-point hitch lift capacity in lbs", ge=0
    )


class Combine(CommonEquipment):
    """Model for combine harvester equipment.

    Extends CommonEquipment with combine-specific attributes.
    """

    category: Literal[EquipmentCategory.COMBINE] = EquipmentCategory.COMBINE

    # Power
    engine_hp: float | None = Field(None, description="Engine horsepower", ge=0)

    # Separator
    separator_type: SeparatorType | None = Field(
        None, description="Type of grain separator"
    )
    separator_width_inches: float | None = Field(
        None, description="Separator width in inches", ge=0
    )
    rotor_width_inches: float | None = Field(
        None, description="Rotor width in inches", ge=0
    )

    # Grain handling
    grain_tank_capacity_bu: float | None = Field(
        None, description="Grain tank capacity in bushels", ge=0
    )
    unloading_rate_bu_min: float | None = Field(
        None, description="Unloading rate in bushels per minute", ge=0
    )
    unloading_auger_length_ft: float | None = Field(
        None, description="Unloading auger length in feet", ge=0
    )

    # Physical specifications
    weight_lbs: float | None = Field(None, description="Operating weight in lbs", ge=0)


class Sprayer(CommonEquipment):
    """Model for self-propelled sprayer equipment.

    Extends CommonEquipment with sprayer-specific attributes for
    chemical application equipment.
    """

    category: Literal[EquipmentCategory.SPRAYER] = EquipmentCategory.SPRAYER

    # Power and engine
    engine_hp: float | None = Field(None, description="Engine horsepower", ge=0)
    rated_rpm: int | None = Field(None, description="Rated engine RPM", ge=0, le=10000)

    # Tank system
    tank_capacity_gal: float | None = Field(
        None, description="Solution tank capacity in gallons", ge=0
    )
    tank_material: str | None = Field(
        None, description="Tank construction material (e.g., polyethylene, stainless)"
    )

    # Boom system
    boom_width_ft: float | None = Field(
        None, description="Boom width in feet", ge=0, le=200
    )
    boom_height_ft: float | None = Field(
        None, description="Maximum boom height in feet", ge=0
    )
    boom_type: SprayerBoomType | None = Field(
        None, description="Boom configuration type"
    )
    nozzle_spacing_inches: float | None = Field(
        None, description="Nozzle spacing in inches", ge=0
    )
    number_of_nozzles: int | None = Field(
        None, description="Total number of nozzles", ge=0
    )

    # Application specifications
    application_rate_gal_per_acre: float | None = Field(
        None, description="Typical application rate in gallons per acre", ge=0
    )
    swath_width_ft: float | None = Field(
        None, description="Effective spray swath width in feet", ge=0
    )
    ground_speed_mph_min: float | None = Field(
        None, description="Minimum operating speed in MPH", ge=0
    )
    ground_speed_mph_max: float | None = Field(
        None, description="Maximum operating speed in MPH", ge=0
    )
    pump_type: str | None = Field(
        None, description="Pump type (e.g., centrifugal, piston, diaphragm)"
    )
    pump_capacity_gal_min: float | None = Field(
        None, description="Pump flow rate in gallons per minute", ge=0
    )

    # Tire configuration
    tire_type: str | None = Field(
        None, description="Tire type (e.g., agricultural, turf, track)"
    )
    number_of_wheels: int | None = Field(
        None, description="Number of wheels or tracks", ge=0
    )
    row_crop_capable: bool | None = Field(
        None, description="Can navigate between crop rows"
    )

    # Physical specifications
    weight_lbs: float | None = Field(None, description="Operating weight in lbs", ge=0)
    wheelbase_inches: float | None = Field(
        None, description="Wheelbase length in inches", ge=0
    )
    transport_width_ft: float | None = Field(
        None, description="Width when folded for transport in feet", ge=0
    )

    @field_validator("ground_speed_mph_max")
    @classmethod
    def validate_speed_range(
        cls, v: float | None, info: ValidationInfo
    ) -> float | None:
        """Validate that ground_speed_mph_max is not less than ground_speed_mph_min."""
        if v is not None and info.data.get("ground_speed_mph_min") is not None:
            if v < info.data["ground_speed_mph_min"]:
                raise ValueError("ground_speed_mph_max must be >= ground_speed_mph_min")
        return v


class Implement(CommonEquipment):
    """Model for implement equipment.

    Extends CommonEquipment with implement-specific attributes.
    """

    category: Literal[EquipmentCategory.IMPLEMENT] = EquipmentCategory.IMPLEMENT

    # Physical specifications
    working_width_ft: float | None = Field(
        None, description="Working width in feet", ge=0
    )
    working_width_inches: float | None = Field(
        None, description="Working width in inches", ge=0
    )
    transport_width_ft: float | None = Field(
        None, description="Transport width in feet", ge=0
    )
    weight_lbs: float | None = Field(None, description="Weight in lbs", ge=0)

    # Requirements
    required_hp_min: float | None = Field(
        None, description="Minimum required horsepower", ge=0
    )
    required_hp_max: float | None = Field(
        None, description="Maximum required horsepower", ge=0
    )

    # Implement type specific
    number_of_rows: int | None = Field(
        None, description="Number of rows (for planters, cultivators, etc.)", ge=0
    )
    row_spacing_inches: float | None = Field(
        None, description="Row spacing in inches", ge=0
    )

    @field_validator("required_hp_max")
    @classmethod
    def validate_hp_range(cls, v: float | None, info: ValidationInfo) -> float | None:
        """Validate that required_hp_max is not less than required_hp_min."""
        if v is not None and info.data.get("required_hp_min") is not None:
            if v < info.data["required_hp_min"]:
                raise ValueError("required_hp_max must be >= required_hp_min")
        return v


# Union type for all equipment types
Equipment = Tractor | Combine | Sprayer | Implement | CommonEquipment


def create_equipment(data: dict) -> Equipment:
    """Create the appropriate equipment model based on category.

    Args:
        data: Dictionary containing equipment data with a 'category' field

    Returns:
        Instantiated equipment model (Tractor, Combine, Sprayer, Implement,
        or CommonEquipment)

    Note:
        For categories other than tractor, combine, sprayer, or implement,
        returns a CommonEquipment instance.
    """
    category = data.get("category")

    if category == EquipmentCategory.TRACTOR:
        return Tractor(**data)
    elif category == EquipmentCategory.COMBINE:
        return Combine(**data)
    elif category == EquipmentCategory.SPRAYER:
        return Sprayer(**data)
    elif category == EquipmentCategory.IMPLEMENT:
        return Implement(**data)
    else:
        # For other categories (harvester, planter, etc.),
        # use CommonEquipment base model
        return CommonEquipment(**data)
