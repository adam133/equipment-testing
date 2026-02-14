-- Generated migration script: 2026-02-14T12:46:05.607787
-- Run this script in Databricks to create all required tables
-- for equipment data in Unity Catalog

-- Create catalog (if not exists)
-- CREATE CATALOG IF NOT EXISTS equip;

-- Create schema
CREATE SCHEMA IF NOT EXISTS equip.ag_equipment;

-- Main equipment tables

CREATE TABLE IF NOT EXISTS equip.ag_equipment.tractors (
    make STRING,
    model STRING,
    category STRING,
    brand STRING,
    series STRING,
    submodel STRING,
    year_start INT,
    year_end INT,
    description STRING,
    image_url STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    source_url STRING,
    pto_hp DOUBLE,
    engine_hp DOUBLE,
    rated_rpm INT,
    transmission_type STRING,
    forward_gears INT,
    reverse_gears INT,
    hydraulic_flow DOUBLE,
    hydraulic_pressure DOUBLE,
    rear_remote_valves INT,
    weight_lbs DOUBLE,
    wheelbase_inches DOUBLE,
    hitch_lift_capacity DOUBLE
)
USING DELTA;

CREATE TABLE IF NOT EXISTS equip.ag_equipment.combines (
    make STRING,
    model STRING,
    category STRING,
    brand STRING,
    series STRING,
    submodel STRING,
    year_start INT,
    year_end INT,
    description STRING,
    image_url STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    source_url STRING,
    engine_hp DOUBLE,
    separator_type STRING,
    separator_width_inches DOUBLE,
    rotor_width_inches DOUBLE,
    grain_tank_capacity_bu DOUBLE,
    unloading_rate_bu_min DOUBLE,
    unloading_auger_length_ft DOUBLE,
    weight_lbs DOUBLE
)
USING DELTA;

CREATE TABLE IF NOT EXISTS equip.ag_equipment.sprayers (
    make STRING,
    model STRING,
    category STRING,
    brand STRING,
    series STRING,
    submodel STRING,
    year_start INT,
    year_end INT,
    description STRING,
    image_url STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    source_url STRING,
    engine_hp DOUBLE,
    rated_rpm INT,
    tank_capacity_gal DOUBLE,
    tank_material STRING,
    boom_width_ft DOUBLE,
    boom_height_ft DOUBLE,
    boom_type STRING,
    nozzle_spacing_inches DOUBLE,
    number_of_nozzles INT,
    application_rate_gal_per_acre DOUBLE,
    swath_width_ft DOUBLE,
    ground_speed_mph_min DOUBLE,
    ground_speed_mph_max DOUBLE,
    pump_type STRING,
    pump_capacity_gal_min DOUBLE,
    tire_type STRING,
    number_of_wheels INT,
    row_crop_capable BOOLEAN,
    weight_lbs DOUBLE,
    wheelbase_inches DOUBLE,
    transport_width_ft DOUBLE
)
USING DELTA;

CREATE TABLE IF NOT EXISTS equip.ag_equipment.implements (
    make STRING,
    model STRING,
    category STRING,
    brand STRING,
    series STRING,
    submodel STRING,
    year_start INT,
    year_end INT,
    description STRING,
    image_url STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    source_url STRING,
    working_width_ft DOUBLE,
    working_width_inches DOUBLE,
    transport_width_ft DOUBLE,
    weight_lbs DOUBLE,
    required_hp_min DOUBLE,
    required_hp_max DOUBLE,
    number_of_rows INT,
    row_spacing_inches DOUBLE
)
USING DELTA;

-- Error tables (for validation failures)

CREATE TABLE IF NOT EXISTS equip.ag_equipment.tractors_error (
    make STRING,
    model STRING,
    category STRING,
    brand STRING,
    series STRING,
    submodel STRING,
    year_start INT,
    year_end INT,
    description STRING,
    image_url STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    source_url STRING,
    pto_hp DOUBLE,
    engine_hp DOUBLE,
    rated_rpm INT,
    transmission_type STRING,
    forward_gears INT,
    reverse_gears INT,
    hydraulic_flow DOUBLE,
    hydraulic_pressure DOUBLE,
    rear_remote_valves INT,
    weight_lbs DOUBLE,
    wheelbase_inches DOUBLE,
    hitch_lift_capacity DOUBLE,
    _validation_error STRING,
    _error_type STRING
)
USING DELTA;

CREATE TABLE IF NOT EXISTS equip.ag_equipment.combines_error (
    make STRING,
    model STRING,
    category STRING,
    brand STRING,
    series STRING,
    submodel STRING,
    year_start INT,
    year_end INT,
    description STRING,
    image_url STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    source_url STRING,
    engine_hp DOUBLE,
    separator_type STRING,
    separator_width_inches DOUBLE,
    rotor_width_inches DOUBLE,
    grain_tank_capacity_bu DOUBLE,
    unloading_rate_bu_min DOUBLE,
    unloading_auger_length_ft DOUBLE,
    weight_lbs DOUBLE,
    _validation_error STRING,
    _error_type STRING
)
USING DELTA;

CREATE TABLE IF NOT EXISTS equip.ag_equipment.sprayers_error (
    make STRING,
    model STRING,
    category STRING,
    brand STRING,
    series STRING,
    submodel STRING,
    year_start INT,
    year_end INT,
    description STRING,
    image_url STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    source_url STRING,
    engine_hp DOUBLE,
    rated_rpm INT,
    tank_capacity_gal DOUBLE,
    tank_material STRING,
    boom_width_ft DOUBLE,
    boom_height_ft DOUBLE,
    boom_type STRING,
    nozzle_spacing_inches DOUBLE,
    number_of_nozzles INT,
    application_rate_gal_per_acre DOUBLE,
    swath_width_ft DOUBLE,
    ground_speed_mph_min DOUBLE,
    ground_speed_mph_max DOUBLE,
    pump_type STRING,
    pump_capacity_gal_min DOUBLE,
    tire_type STRING,
    number_of_wheels INT,
    row_crop_capable BOOLEAN,
    weight_lbs DOUBLE,
    wheelbase_inches DOUBLE,
    transport_width_ft DOUBLE,
    _validation_error STRING,
    _error_type STRING
)
USING DELTA;

CREATE TABLE IF NOT EXISTS equip.ag_equipment.implements_error (
    make STRING,
    model STRING,
    category STRING,
    brand STRING,
    series STRING,
    submodel STRING,
    year_start INT,
    year_end INT,
    description STRING,
    image_url STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    source_url STRING,
    working_width_ft DOUBLE,
    working_width_inches DOUBLE,
    transport_width_ft DOUBLE,
    weight_lbs DOUBLE,
    required_hp_min DOUBLE,
    required_hp_max DOUBLE,
    number_of_rows INT,
    row_spacing_inches DOUBLE,
    _validation_error STRING,
    _error_type STRING
)
USING DELTA;

-- Verification: List all tables
SELECT table_name FROM equip.ag_equipment
WHERE table_catalog = 'equip' AND table_schema = 'ag_equipment'
ORDER BY table_name;
