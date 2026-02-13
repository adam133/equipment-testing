# OpenAg-DB Data Model Documentation

## Overview

The OpenAg-DB data model is designed to handle agricultural equipment specifications with a flexible, extensible architecture that supports:

1. **Equipment Hierarchy**: Brand → Make → Series → Model → Submodel relationships
2. **Multiple Equipment Types**: Tractors, Combines, Self-Propelled Sprayers, and other agricultural equipment
3. **Attribute Inheritance**: Attributes can be defined at any level and inherited down the hierarchy
4. **Extensibility**: Easy to add new equipment categories without major restructuring

## Architecture Philosophy

The data model follows these core principles:

- **Polymorphic Models**: Equipment types inherit from a common base with type-specific extensions
- **Validation First**: All data validated using Pydantic for type safety and data integrity
- **Flexible Hierarchy**: Attributes can be defined at the brand, make, series, model, or submodel level
- **DRY Principle**: Shared attributes defined once at the appropriate hierarchy level
- **Future-Proof**: New equipment categories can be added by extending the base model

## Equipment Hierarchy

### Hierarchy Levels

The equipment hierarchy represents real-world organizational structures used by manufacturers:

```
Brand/Ownership
  └─ Make (Manufacturer)
      └─ Series (Product Line)
          └─ Model (Specific Product)
              └─ Submodel (Configuration Variant)
```

### Level Definitions

#### 1. Brand/Ownership Level
The highest level representing corporate ownership or brand family.

**Purpose**: Group equipment across corporate acquisitions and brand portfolios

**Examples**:
- CNH Industrial (owns Case IH, New Holland)
- AGCO (owns Massey Ferguson, Fendt, Challenger)
- Deere & Company (John Deere brand)

**Typical Attributes**:
- Corporate policies
- Warranty programs
- Dealer networks
- Manufacturing locations

#### 2. Make Level
The manufacturer or brand name visible to customers.

**Purpose**: Identify the brand identity under which equipment is sold

**Examples**:
- John Deere
- Case IH
- New Holland
- Kubota
- Massey Ferguson

**Typical Attributes**:
- Brand-specific design philosophy
- Color schemes
- Technology platforms (e.g., John Deere's CommandCenter)
- Service programs

#### 3. Series Level
A product line or family of related models.

**Purpose**: Group equipment with shared design, purpose, and target market

**Examples**:
- John Deere 5E Series (utility tractors)
- Case IH Magnum Series (row crop tractors)
- John Deere S-Series (combines)
- New Holland Guardian Series (sprayers)

**Typical Attributes**:
- Engine family
- Transmission family
- Cab design
- Hydraulic system architecture
- Target customer segment
- Price range

#### 4. Model Level
A specific product with defined specifications.

**Purpose**: The primary equipment identifier with concrete specifications

**Examples**:
- John Deere 5075E
- Case IH Magnum 340
- John Deere S780
- New Holland Guardian SP.345F

**Typical Attributes**:
- Exact horsepower rating
- Specific transmission configuration
- Hydraulic specifications
- Weight and dimensions
- Standard features

#### 5. Submodel Level
Configuration variants of a model.

**Purpose**: Represent option packages, regional variants, or year-specific changes

**Examples**:
- John Deere 5075E Premium (cab package)
- Case IH Magnum 340 CVX (CVT transmission option)
- New Holland Guardian SP.345F AirRide (suspension option)

**Typical Attributes**:
- Optional equipment
- Package configurations
- Regional specifications (e.g., EU emissions vs. US)
- Year-specific changes within model lifecycle

## Attribute Inheritance

Attributes can be defined at any hierarchy level and are inherited downward:

### Inheritance Rules

1. **Cascading Attributes**: Attributes defined at higher levels apply to all descendants
2. **Override Capability**: Lower levels can override inherited attributes with specific values
3. **Optional at All Levels**: No level requires all attributes to be defined
4. **Validation Propagation**: Validation rules apply regardless of inheritance level

### Example: John Deere 5E Series

```python
# Series Level (applies to all 5E models)
series_attributes = {
    "series": "5E Series",
    "transmission_type": "PowerShift",  # All have powershift
    "hydraulic_pressure": 3000,  # PSI, common to series
    "rear_remote_valves": 3,  # Base configuration
}

# Model Level (specific to 5075E)
model_5075E = {
    "model": "5075E",
    "pto_hp": 65,  # Specific to this model
    "engine_hp": 75,
    "year_start": 2014,
    "year_end": 2022,
}

# Submodel Level (Premium cab package)
submodel_premium = {
    "submodel": "Premium",
    "rear_remote_valves": 4,  # Override: upgraded package
    "description": "Premium cab with additional hydraulic valve",
}

# Final equipment inherits and merges all levels:
# - Series attributes (transmission, hydraulic pressure)
# - Model attributes (hp ratings, years)
# - Submodel overrides (4 valves instead of 3)
```

### Benefits of Hierarchy

1. **Reduce Data Redundancy**: Define common attributes once at appropriate level
2. **Maintain Consistency**: Changes at higher levels automatically apply to descendants
3. **Flexible Queries**: Query at any hierarchy level (e.g., all 5E Series tractors)
4. **Accurate Representation**: Matches how manufacturers organize products
5. **Easy Updates**: Update entire product lines by modifying series-level attributes

## Equipment Categories

### Current Supported Types

#### 1. Tractors

Tractors are the most diverse category with multiple sub-types (utility, row crop, specialty, compact).

**Key Attributes**:
- **Power**: PTO HP, Engine HP, Rated RPM
- **Transmission**: Type (manual, powershift, CVT, IVT, hydrostatic), gear counts
- **Hydraulics**: Flow rate (GPM), pressure (PSI), remote valve count, lift capacity
- **Physical**: Weight, wheelbase, dimensions
- **Hitch**: Three-point hitch lift capacity, category

**Sub-categories** (handled via attributes):
- Utility tractors: 40-100 HP, general purpose
- Row crop tractors: 100-600 HP, agricultural applications
- Compact tractors: <40 HP, small properties
- Specialty tractors: Orchards, vineyards, etc.

#### 2. Combines (Harvesters)

Combines harvest grain crops with specialized threshing and separation systems.

**Key Attributes**:
- **Power**: Engine HP
- **Separator System**: Type (conventional, rotary, hybrid), dimensions
- **Grain Handling**: Tank capacity (bushels), unloading rate, auger length
- **Physical**: Weight, dimensions
- **Cutting Platform**: Header width compatibility (separate implement)

**Variations**:
- Conventional combines: Traditional straw walker design
- Rotary combines: Rotary separator design
- Hybrid combines: Combined technologies

#### 3. Self-Propelled Sprayers

Self-propelled sprayers for chemical application (herbicides, pesticides, fertilizers).

**Key Attributes**:
- **Power**: Engine HP, rated RPM
- **Tank**: Capacity (gallons), material (polyethylene, stainless)
- **Boom System**: Width (feet), height, type, nozzle count, spacing
- **Application**: Rate (gal/acre), swath width, speed range
- **Pump System**: Type, capacity (GPM)
- **Tires**: Configuration, row-crop capability
- **Physical**: Weight, wheelbase, transport width

**Categories** (via attributes):
- High-clearance sprayers: Tall crops (corn, cotton)
- Low-profile sprayers: Early season applications
- Track sprayers: Difficult terrain

#### 4. Implements

Pulled or mounted equipment (planters, plows, cultivators, spreaders, balers).

**Key Attributes**:
- **Physical**: Working width, transport width, weight
- **Requirements**: HP range required
- **Row Configuration**: Number of rows, spacing (for row-crop implements)
- **Mounting**: Three-point hitch category, pull-type

**Sub-categories** (identified in category or description):
- Planters: Row count, seed hoppers
- Tillage: Type (plow, disk, cultivator), depth
- Hay equipment: Balers, mowers, rakes
- Application: Spreaders, sprayers

### Adding New Equipment Categories

The model is designed for easy extension. To add a new category:

1. **Add to EquipmentCategory Enum**: Define new category identifier
2. **Create Specialized Model**: Extend `CommonEquipment` with category-specific fields
3. **Update Factory Function**: Add case in `create_equipment()` function
4. **Define Validation**: Add custom validators if needed
5. **Update Documentation**: Document new attributes and usage

**Example: Adding Forage Harvesters**

```python
class EquipmentCategory(str, Enum):
    TRACTOR = "tractor"
    COMBINE = "combine"
    SPRAYER = "sprayer"
    IMPLEMENT = "implement"
    FORAGE_HARVESTER = "forage_harvester"  # NEW
    # ... other categories

class ForageHarvester(CommonEquipment):
    """Model for forage harvester equipment."""

    category: Literal[EquipmentCategory.FORAGE_HARVESTER] = (
        EquipmentCategory.FORAGE_HARVESTER
    )

    # Power
    engine_hp: float | None = Field(None, description="Engine horsepower", ge=0)

    # Cutting system
    cutting_width_ft: float | None = Field(
        None, description="Cutting width in feet", ge=0
    )
    header_rows: int | None = Field(
        None, description="Number of rows for row-crop header", ge=0
    )

    # Processing
    chop_length_mm: float | None = Field(
        None, description="Theoretical chop length in mm", ge=0
    )
    number_of_knives: int | None = Field(
        None, description="Number of cutting knives", ge=0
    )

    # Physical
    weight_lbs: float | None = Field(None, description="Operating weight", ge=0)

# Update factory function
def create_equipment(data: dict) -> Equipment:
    category = data.get("category")

    if category == EquipmentCategory.FORAGE_HARVESTER:
        return ForageHarvester(**data)
    # ... other categories
```

## Data Model Classes

### CommonEquipment (Base Class)

The foundation for all equipment types with universal attributes.

```python
class CommonEquipment(BaseModel):
    # Identity
    make: str  # Required: Manufacturer/brand
    model: str  # Required: Model designation
    category: EquipmentCategory  # Required: Equipment type

    # Hierarchy
    series: str | None  # Optional: Model series/family
    submodel: str | None  # Optional: Configuration variant
    brand: str | None  # Optional: Parent brand/ownership

    # Production years
    year_start: int | None  # First production year
    year_end: int | None  # Last production year (None = current)

    # Metadata
    description: str | None
    image_url: str | None
    created_at: datetime  # Auto-generated
    updated_at: datetime  # Auto-generated
    source_url: str | None  # Data source reference
```

**Key Features**:
- Minimal required fields (make, model, category)
- Optional hierarchy support (brand, series, submodel)
- Automatic timestamp management
- Source tracking for data provenance

### Tractor (Specialized Model)

Extends CommonEquipment with tractor-specific attributes.

**Categories of Attributes**:
1. **Power Specifications**: PTO HP, Engine HP, Rated RPM
2. **Transmission**: Type, forward/reverse gear counts
3. **Hydraulic System**: Flow, pressure, remote valves, lift capacity
4. **Physical Specifications**: Weight, wheelbase

See `src/core/models.py` for complete implementation.

### Combine (Specialized Model)

Extends CommonEquipment with combine-specific attributes.

**Categories of Attributes**:
1. **Power**: Engine HP
2. **Separator System**: Type, width, rotor dimensions
3. **Grain Handling**: Tank capacity, unloading rate, auger length
4. **Physical**: Weight

See `src/core/models.py` for complete implementation.

### Sprayer (Specialized Model)

Extends CommonEquipment with sprayer-specific attributes.

**Categories of Attributes**:
1. **Power & Engine**: HP, RPM ratings
2. **Tank System**: Capacity, material
3. **Boom System**: Width, height, configuration, nozzles
4. **Application**: Rates, pump specifications
5. **Chassis**: Tire config, row-crop capability
6. **Physical**: Weight, dimensions

See `src/core/models.py` for complete implementation (to be added).

### Implement (Specialized Model)

Extends CommonEquipment with implement-specific attributes.

**Categories of Attributes**:
1. **Physical**: Working width, transport width, weight
2. **Requirements**: HP range (min/max)
3. **Row Configuration**: Number of rows, spacing

See `src/core/models.py` for complete implementation.

## Extensibility Patterns

### Pattern 1: Adding Equipment Attributes

To add new attributes to existing equipment types:

1. Add field to appropriate specialized model class
2. Include validation constraints (ge=0, ranges, etc.)
3. Add descriptive Field() with description
4. Update tests to cover new fields
5. Update API documentation

**Example**: Adding front PTO to tractors

```python
class Tractor(CommonEquipment):
    # ... existing fields ...

    # Add new field
    front_pto_hp: float | None = Field(
        None,
        description="Front Power Take-Off horsepower",
        ge=0
    )
```

### Pattern 2: Adding Equipment Categories

Follow the process described in "Adding New Equipment Categories" section.

### Pattern 3: Adding Hierarchy Levels

The current hierarchy (Brand → Make → Series → Model → Submodel) covers most use cases. To extend:

1. Add new hierarchy field to CommonEquipment
2. Update queries to support new hierarchy level
3. Update documentation with examples
4. Consider database schema implications

### Pattern 4: Complex Attributes (Enums)

For attributes with specific allowed values:

```python
class SprayerBoomType(str, Enum):
    """Type of boom configuration."""
    RIGID = "rigid"
    FOLDING = "folding"
    TRUSS = "truss"
    HYBRID = "hybrid"

class Sprayer(CommonEquipment):
    boom_type: SprayerBoomType | None = Field(
        None,
        description="Boom configuration type"
    )
```

### Pattern 5: Conditional Validation

Use Pydantic validators for complex validation logic:

```python
@field_validator("boom_width_ft")
@classmethod
def validate_boom_width(cls, v: float | None) -> float | None:
    """Validate boom width is reasonable."""
    if v is not None and v > 200:
        raise ValueError("Boom width cannot exceed 200 feet")
    return v
```

## Usage Examples

### Example 1: Complete Hierarchy - John Deere 5075E

```python
from core.models import Tractor, TransmissionType

# Complete example with hierarchy
tractor = Tractor(
    # Hierarchy
    brand="Deere & Company",
    make="John Deere",
    series="5E Series",
    model="5075E",
    submodel="Premium",

    # Years
    year_start=2014,
    year_end=2022,

    # Power
    pto_hp=65,
    engine_hp=75,
    rated_rpm=2400,

    # Transmission
    transmission_type=TransmissionType.POWERSHIFT,
    forward_gears=12,
    reverse_gears=12,

    # Hydraulics
    hydraulic_flow=16.0,
    hydraulic_pressure=3000,
    rear_remote_valves=4,  # Premium package upgrade
    hitch_lift_capacity=6800,

    # Physical
    weight_lbs=7700,
    wheelbase_inches=87.8,

    # Metadata
    description="Utility tractor with premium cab package",
    source_url="https://www.deere.com/en/tractors/5e-series/",
)
```

### Example 2: Self-Propelled Sprayer

```python
from core.models import Sprayer, SprayerBoomType

sprayer = Sprayer(
    # Identity
    make="John Deere",
    series="R4 Series",
    model="R4045",

    # Years
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
    ground_speed_mph_max=25.0,
    pump_capacity_gal_min=80.0,

    # Physical
    weight_lbs=36000,
    wheelbase_inches=156,
    row_crop_capable=True,
)
```

### Example 3: Combine with Series Attributes

```python
from core.models import Combine, SeparatorType

combine = Combine(
    # Identity & Hierarchy
    make="Case IH",
    series="Axial-Flow 250 Series",
    model="8250",

    # Years
    year_start=2018,

    # Power
    engine_hp=450,

    # Separator (series characteristic)
    separator_type=SeparatorType.ROTARY,
    separator_width_inches=44,

    # Grain handling
    grain_tank_capacity_bu=350,
    unloading_rate_bu_min=4.5,
    unloading_auger_length_ft=28,

    # Physical
    weight_lbs=42000,
)
```

### Example 4: Minimal Equipment Entry

```python
from core.models import CommonEquipment, EquipmentCategory

# Minimal data for unknown equipment type
equipment = CommonEquipment(
    make="Local Manufacturer",
    model="Custom Sprayer",
    category=EquipmentCategory.SPRAYER,
    year_start=2023,
)
```

### Example 5: Using Factory Function

```python
from core.models import create_equipment

# Dynamic creation based on category
data = {
    "make": "Kubota",
    "model": "M7-172",
    "category": "tractor",
    "series": "M7 Series",
    "engine_hp": 170,
    "transmission_type": "cvt",
}

equipment = create_equipment(data)
# Returns: Tractor instance with all fields validated
```

## Querying by Hierarchy

The hierarchy enables powerful queries:

```python
# All equipment from a brand
query = {"brand": "Deere & Company"}

# All equipment from a make
query = {"make": "John Deere"}

# All equipment in a series
query = {"series": "5E Series"}

# Specific model
query = {"model": "5075E"}

# Specific configuration
query = {"model": "5075E", "submodel": "Premium"}

# Range queries
query = {"series": "5E Series", "pto_hp_min": 60, "pto_hp_max": 80}
```

## Data Storage Considerations

### Delta Tables Structure

Equipment data stored in Unity Catalog Delta tables with hierarchy support:

```
catalog.schema.equipment
├── Partitioned by: category, make
├── Indexed by: model, series
└── Supports time-travel queries
```

### Hierarchy Relationships

Options for storing hierarchy:

1. **Denormalized** (Current): All hierarchy fields in equipment record
   - Pros: Fast queries, simple structure
   - Cons: Potential data duplication

2. **Normalized** (Future): Separate hierarchy tables
   - Pros: No duplication, easier updates
   - Cons: Requires joins, more complex queries

Current implementation uses denormalized approach for simplicity and query performance.

## Validation & Data Quality

### Built-in Validation

Pydantic provides automatic validation:

- **Type Checking**: Fields must match declared types
- **Range Validation**: Numeric fields checked against constraints (ge=0, le=max)
- **Enum Validation**: Category and type fields must match allowed values
- **Custom Validation**: Cross-field validation (e.g., year_end >= year_start)

### Data Quality Rules

1. **Required Fields**: make, model, category (minimum for any equipment)
2. **Logical Constraints**: Year ranges, HP ranges validated
3. **Reasonable Limits**: Extreme values trigger validation errors
4. **Type Safety**: Python type hints enforced at runtime

### Example Validation

```python
# This will raise ValidationError
invalid_tractor = Tractor(
    make="Test",
    model="Model",
    pto_hp=-10,  # ERROR: Must be >= 0
    year_start=2020,
    year_end=2010,  # ERROR: year_end < year_start
)
```

## Future Enhancements

### Planned Features

1. **Equipment Relationships**: Link implements to compatible tractors/sprayers
2. **Maintenance Schedules**: Service intervals by equipment
3. **Performance Metrics**: Fuel consumption, productivity data
4. **Geospatial Data**: Regional equipment popularity
5. **Price History**: Market value tracking
6. **Parts Compatibility**: Cross-reference compatible parts
7. **Attachments/Options**: Detailed option packages and configurations

### Extensibility Considerations

The data model is designed to support these enhancements without breaking changes:

- Optional fields allow gradual data enrichment
- Inheritance supports adding specialized attributes
- Factory pattern supports new equipment types
- JSON serialization enables API extensions

## Best Practices

### When Defining Equipment

1. **Use Appropriate Hierarchy Level**: Define attributes at the correct level (series vs. model)
2. **Provide Source URL**: Always include `source_url` for data verification
3. **Complete Core Fields**: Fill in make, model, category at minimum
4. **Validate Before Saving**: Use Pydantic validation to catch errors early
5. **Document Assumptions**: Use description field for clarifications

### When Adding Attributes

1. **Check Existing Models**: Ensure attribute doesn't already exist
2. **Use Consistent Units**: Follow existing patterns (hp, lbs, inches, etc.)
3. **Add Validation**: Include constraints (ge, le, range checks)
4. **Provide Description**: Clear Field() description for API documentation
5. **Consider Inheritance**: Place attributes at appropriate hierarchy level

### When Extending Models

1. **Follow Naming Conventions**: Use snake_case, descriptive names
2. **Maintain Backwards Compatibility**: Make new fields optional
3. **Update Tests**: Add test coverage for new fields
4. **Update Documentation**: This file and API docs
5. **Consider Migration**: Plan for existing data updates

## Conclusion

The OpenAg-DB data model provides a flexible, extensible foundation for agricultural equipment data. The hierarchy system enables efficient data organization and querying, while the polymorphic model structure supports diverse equipment types. The design prioritizes:

- **Flexibility**: Easy to extend and adapt
- **Data Quality**: Strong validation and type safety
- **Performance**: Optimized for common query patterns
- **Maintainability**: Clear structure and documentation
- **Scalability**: Designed for growth

For implementation details, see:
- `src/core/models.py` - Model definitions
- `tests/test_models.py` - Usage examples and tests
- `README.md` - Project overview and setup

## Version History

- **1.0.0** (2026-02-13): Initial comprehensive data model documentation
  - Hierarchy system documentation
  - Extensibility patterns
  - Self-propelled sprayer specification
  - Usage examples and best practices
