"""Test basic functionality of the equipment_testing package."""

import equipment_testing


def test_version():
    """Test that version is defined."""
    assert hasattr(equipment_testing, "__version__")
    assert equipment_testing.__version__ == "0.1.0"


def test_imports():
    """Test that package can be imported."""
    assert equipment_testing is not None
