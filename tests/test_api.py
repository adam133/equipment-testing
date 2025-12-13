"""Tests for the FastAPI application."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_equipment():
    """Test listing equipment."""
    response = client.get("/equipment")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_equipment_with_filters():
    """Test listing equipment with filters."""
    response = client.get("/equipment?category=tractor&make=John Deere&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_tractors():
    """Test listing tractors."""
    response = client.get("/equipment/tractors")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_combines():
    """Test listing combines."""
    response = client.get("/equipment/combines")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_implements():
    """Test listing implements."""
    response = client.get("/equipment/implements")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_equipment_not_found():
    """Test getting non-existent equipment."""
    response = client.get("/equipment/nonexistent")
    assert response.status_code == 404


def test_submit_contribution():
    """Test submitting a contribution."""
    contribution = {
        "field_name": "engine_hp",
        "current_value": "100",
        "proposed_value": "105",
        "notes": "Manufacturer specs show 105 HP",
    }
    response = client.post("/contributions", json=contribution)
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"


def test_get_statistics():
    """Test getting database statistics."""
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_equipment" in data
    assert "tractors" in data
    assert "combines" in data
    assert "implements" in data


def test_openapi_docs():
    """Test that OpenAPI documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_pagination():
    """Test pagination parameters."""
    response = client.get("/equipment?limit=5&offset=10")
    assert response.status_code == 200


def test_invalid_limit():
    """Test that invalid limit is rejected."""
    response = client.get("/equipment?limit=2000")
    assert response.status_code == 422  # Validation error
