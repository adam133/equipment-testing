"""Pydantic models for agricultural equipment data.

This module defines the base equipment model and polymorphic sub-models
for different types of agricultural equipment (tractors, combines, implements).
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EquipmentCategory(str, Enum):
    """Category of agricultural equipment."""

    TRACTOR = "tractor"
    COMBINE = "combine"
    IMPLEMENT = "implement"
    HARVESTER = "harvester"
    PLANTER = "planter"
    SPRAYER = "sprayer"
    OTHER = "other"


class TransmissionType(str, Enum):
    """Type of transmission for tractors."""

    MANUAL = "manual"
    POWERSHIFT = "powershift"
    CVT = "cvt"
    HYDROSTATIC = "hydrostatic"
    IVT = "ivt"
    OTHER = "other"


class SeparatorType(str, Enum):
    """Type of separator for combines."""

    CONVENTIONAL = "conventional"
    ROTARY = "rotary"
    HYBRID = "hybrid"


class CommonEquipment(BaseModel):
    """Base model for all agricultural equipment.

    This model contains common fields shared across all equipment types.
    """

    # Required fields
    make: str = Field(..., description="Manufacturer/brand name")
    model: str = Field(..., description="Model designation")
    category: EquipmentCategory = Field(..., description="Equipment category")

    # Optional common fields
    series: str | None = Field(None, description="Model series or family")
    year_start: int | None = Field(
        None, description="First year of production", ge=1900, le=2100
    )
    year_end: int | None = Field(
        None, description="Last year of production", ge=1900, le=2100
    )
    description: str | None = Field(None, description="Equipment description")
    image_url: str | None = Field(None, description="URL to equipment image")

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source_url: str | None = Field(None, description="URL of data source")

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("year_end")
    @classmethod
    def validate_year_range(cls, v: int | None, info) -> int | None:
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
    rated_rpm: int | None = Field(
        None, description="Rated engine RPM", ge=0, le=10000
    )

    # Transmission
    transmission_type: TransmissionType | None = Field(
        None, description="Type of transmission"
    )
    forward_gears: int | None = Field(
        None, description="Number of forward gears", ge=0
    )
    reverse_gears: int | None = Field(
        None, description="Number of reverse gears", ge=0
    )

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
    weight_lbs: float | None = Field(
        None, description="Operating weight in lbs", ge=0
    )
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
    weight_lbs: float | None = Field(
        None, description="Operating weight in lbs", ge=0
    )


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


# Union type for all equipment types
Equipment = Tractor | Combine | Implement


def create_equipment(data: dict) -> Equipment:
    """Create the appropriate equipment model based on category.

    Args:
        data: Dictionary containing equipment data with a 'category' field

    Returns:
        Instantiated equipment model (Tractor, Combine, or Implement)

    Raises:
        ValueError: If category is not recognized or supported
    """
    category = data.get("category")

    if category == EquipmentCategory.TRACTOR:
        return Tractor(**data)
    elif category == EquipmentCategory.COMBINE:
        return Combine(**data)
    elif category == EquipmentCategory.IMPLEMENT:
        return Implement(**data)
    else:
        # Default to CommonEquipment for other categories
        return CommonEquipment(**data)
