"""Tests for Quality Farm Supply API response mapping."""

import json

import pytest

from core.models import EquipmentCategory
from scrapers.spiders.quality_farm_supply import QualityFarmSupplySpider


class TestAPIMapping:
    """Test the API response to Tractor model mapping."""

    @pytest.fixture
    def spider(self) -> QualityFarmSupplySpider:
        """Create a spider instance."""
        return QualityFarmSupplySpider()

    def test_map_complete_api_response(self, spider: QualityFarmSupplySpider) -> None:
        """Test mapping a complete API response."""
        api_data = {
            "spec": json.dumps(
                {
                    "Years manufactured": "1987-1998",
                    "Hp pto": "17",
                    "Hp engine": "20",
                    "Engine make": "SHIBAURA",
                    "Engine fueld type": "DIESEL",
                    "Engine cylinders cid": "3/77.2",
                    "Transmission std": "CM",
                    "Fwd rev standard": "4/2",
                    "Wheelbase inches": "63",
                    "Pto speed": "540",
                    "Hitch lift": "1637",
                    "Hydraulics flow": "9.7",
                    "Weight": "2384",
                }
            ),
            "serial": [["UE24511", "1990", "LEFT SIDE OF TRANS HOUSING"]],
        }

        result = spider._map_api_response_to_tractor(
            api_data, "Kubota", "B7200HST", "https://example.com"
        )

        assert result["make"] == "Kubota"
        assert result["model"] == "B7200HST"
        assert result["category"] == EquipmentCategory.TRACTOR
        assert result["year_start"] == 1987
        assert result["year_end"] == 1998
        assert result["engine_hp"] == 20.0
        assert result["pto_hp"] == 17.0
        assert result["transmission_type"] == "manual"
        assert result["forward_gears"] == 4
        assert result["reverse_gears"] == 2
        assert result["weight_lbs"] == 2384.0
        assert result["wheelbase_inches"] == 63.0
        assert result["hitch_lift_capacity"] == 1637.0
        assert result["hydraulic_flow"] == 9.7
        assert "SHIBAURA" in result["description"]
        assert "DIESEL" in result["description"]
        assert "540" in result["description"]

    def test_map_transmission_types(self, spider: QualityFarmSupplySpider) -> None:
        """Test mapping various transmission type codes."""
        test_cases = [
            ("CM", "manual"),
            ("HYDRO", "hydrostatic"),
            ("HYDROSTAT", "hydrostatic"),
            ("PS", "powershift"),
            ("CVT", "cvt"),
            ("IVT", "ivt"),
        ]

        for trans_code, expected_type in test_cases:
            api_data = {
                "spec": json.dumps(
                    {
                        "Transmission std": trans_code,
                    }
                )
            }
            result = spider._map_api_response_to_tractor(
                api_data, "Test", "Model", "https://example.com"
            )
            assert result["transmission_type"] == expected_type

    def test_map_gear_formats(self, spider: QualityFarmSupplySpider) -> None:
        """Test mapping various gear format patterns."""
        # Pattern: "F/R" format
        api_data = {"spec": json.dumps({"Fwd rev standard": "8F/4R"})}
        result = spider._map_api_response_to_tractor(
            api_data, "Test", "Model", "https://example.com"
        )
        assert result["forward_gears"] == 8
        assert result["reverse_gears"] == 4

        # Pattern: slash-separated
        api_data = {"spec": json.dumps({"Fwd rev standard": "12/6"})}
        result = spider._map_api_response_to_tractor(
            api_data, "Test", "Model", "https://example.com"
        )
        assert result["forward_gears"] == 12
        assert result["reverse_gears"] == 6

        # Pattern: short concatenated (2-3 digits)
        api_data = {"spec": json.dumps({"Fwd rev standard": "42"})}
        result = spider._map_api_response_to_tractor(
            api_data, "Test", "Model", "https://example.com"
        )
        assert result["forward_gears"] == 4
        assert result["reverse_gears"] == 2

    def test_map_null_values(self, spider: QualityFarmSupplySpider) -> None:
        """Test that null values are handled correctly."""
        api_data = {
            "spec": json.dumps(
                {
                    "Hp pto": None,
                    "Hp engine": "null",
                    "Weight": "",
                    "Transmission std": "null",
                }
            )
        }
        result = spider._map_api_response_to_tractor(
            api_data, "Test", "Model", "https://example.com"
        )

        # Should not have these fields if they're null
        assert "pto_hp" not in result
        assert "engine_hp" not in result
        assert "weight_lbs" not in result
        assert "transmission_type" not in result

    def test_map_numeric_extraction(self, spider: QualityFarmSupplySpider) -> None:
        """Test extraction of numeric values with various formats."""
        api_data = {
            "spec": json.dumps(
                {
                    "Hp pto": "25.5 HP",
                    "Hp engine": "30",
                    "Weight": "3,450 lbs",
                    "Wheelbase inches": "72.5 in",
                    "Hitch lift": "2000",
                }
            )
        }
        result = spider._map_api_response_to_tractor(
            api_data, "Test", "Model", "https://example.com"
        )

        assert result["pto_hp"] == 25.5
        assert result["engine_hp"] == 30.0
        assert result["weight_lbs"] == 3450.0
        assert result["wheelbase_inches"] == 72.5
        assert result["hitch_lift_capacity"] == 2000.0

    def test_map_year_range(self, spider: QualityFarmSupplySpider) -> None:
        """Test extraction of year ranges."""
        # Normal range
        api_data = {"spec": json.dumps({"Years manufactured": "2005-2015"})}
        result = spider._map_api_response_to_tractor(
            api_data, "Test", "Model", "https://example.com"
        )
        assert result["year_start"] == 2005
        assert result["year_end"] == 2015

        # Single year
        api_data = {"spec": json.dumps({"Years manufactured": "2020"})}
        result = spider._map_api_response_to_tractor(
            api_data, "Test", "Model", "https://example.com"
        )
        assert result["year_start"] == 2020
        assert "year_end" not in result

    def test_map_invalid_json_spec(self, spider: QualityFarmSupplySpider) -> None:
        """Test handling of invalid JSON in spec field."""
        api_data = {
            "spec": "invalid json {{{",
        }
        result = spider._map_api_response_to_tractor(
            api_data, "Test", "Model", "https://example.com"
        )

        # Should still return basic fields
        assert result["make"] == "Test"
        assert result["model"] == "Model"
        assert result["category"] == EquipmentCategory.TRACTOR

    def test_map_range_values(self, spider: QualityFarmSupplySpider) -> None:
        """Test handling of range values (takes first value)."""
        api_data = {
            "spec": json.dumps(
                {
                    "Hp pto": "17-20",
                    "Weight": "2300-2500",
                }
            )
        }
        result = spider._map_api_response_to_tractor(
            api_data, "Test", "Model", "https://example.com"
        )

        # Should take first value from range
        assert result["pto_hp"] == 17.0
        assert result["weight_lbs"] == 2300.0
