"""Main FastAPI application for OpenAg-DB API.

This API serves agricultural equipment data from Unity Catalog Delta tables
and provides endpoints for user contributions.
"""

import os
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.models import (
    Combine,
    CommonEquipment,
    EquipmentCategory,
    Implement,
    Tractor,
)

# Initialize FastAPI app
app = FastAPI(
    title="OpenAg-DB API",
    description="Public, community-driven agricultural equipment database API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for frontend access
# In development, allow all origins. In production, restrict to specific domains.
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173"
).split(",")

# Allow all origins only in development mode
if os.getenv("ENVIRONMENT") == "development":
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str


class SearchFilters(BaseModel):
    """Search filter parameters."""

    make: str | None = None
    model: str | None = None
    category: EquipmentCategory | None = None
    year_min: int | None = None
    year_max: int | None = None


class ContributionRequest(BaseModel):
    """User contribution/correction request."""

    equipment_id: str | None = None
    field_name: str
    current_value: str | None = None
    proposed_value: str
    notes: str | None = None
    submitter_email: str | None = None


@app.get("/", response_model=HealthResponse)
async def root() -> HealthResponse:
    """Root endpoint - health check.

    Returns:
        Health status information
    """
    return HealthResponse(status="healthy", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns:
        Health status information
    """
    return HealthResponse(status="healthy", version="0.1.0")


@app.get("/equipment", response_model=list[CommonEquipment])
async def list_equipment(
    category: EquipmentCategory | None = Query(None, description="Filter by category"),
    make: str | None = Query(None, description="Filter by manufacturer"),
    model: str | None = Query(None, description="Filter by model"),
    year_min: int | None = Query(None, description="Minimum year"),
    year_max: int | None = Query(None, description="Maximum year"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
) -> list[CommonEquipment]:
    """List equipment with optional filters.

    Args:
        category: Filter by equipment category
        make: Filter by manufacturer
        model: Filter by model
        year_min: Filter by minimum year
        year_max: Filter by maximum year
        limit: Maximum number of results
        offset: Offset for pagination

    Returns:
        List of equipment matching filters

    Note:
        This is a placeholder. Actual implementation would query Unity Catalog
        Delta tables using the databricks_utils module (DuckDB).
    """
    # Placeholder for actual query logic
    # In production, this would:
    # 1. Connect to Unity Catalog using databricks_utils (DuckDB)
    # 2. Build SQL query with filters
    # 3. Execute query and return results
    return []


@app.get("/equipment/tractors", response_model=list[Tractor])
async def list_tractors(
    make: str | None = Query(None),
    hp_min: float | None = Query(None, description="Minimum horsepower"),
    hp_max: float | None = Query(None, description="Maximum horsepower"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> list[Tractor]:
    """List tractors with optional filters.

    Args:
        make: Filter by manufacturer
        hp_min: Minimum horsepower
        hp_max: Maximum horsepower
        limit: Maximum number of results
        offset: Offset for pagination

    Returns:
        List of tractors matching filters
    """
    # Placeholder for tractor-specific query
    return []


@app.get("/equipment/combines", response_model=list[Combine])
async def list_combines(
    make: str | None = Query(None),
    tank_capacity_min: float | None = Query(None, description="Minimum tank capacity"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> list[Combine]:
    """List combines with optional filters.

    Args:
        make: Filter by manufacturer
        tank_capacity_min: Minimum grain tank capacity
        limit: Maximum number of results
        offset: Offset for pagination

    Returns:
        List of combines matching filters
    """
    # Placeholder for combine-specific query
    return []


@app.get("/equipment/implements", response_model=list[Implement])
async def list_implements(
    make: str | None = Query(None),
    width_min: float | None = Query(None, description="Minimum working width"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> list[Implement]:
    """List implements with optional filters.

    Args:
        make: Filter by manufacturer
        width_min: Minimum working width
        limit: Maximum number of results
        offset: Offset for pagination

    Returns:
        List of implements matching filters
    """
    # Placeholder for implement-specific query
    return []


@app.get("/equipment/{equipment_id}", response_model=CommonEquipment)
async def get_equipment(equipment_id: str) -> CommonEquipment:
    """Get a specific equipment item by ID.

    Args:
        equipment_id: Unique equipment identifier

    Returns:
        Equipment details

    Raises:
        HTTPException: If equipment not found
    """
    # Placeholder for single item retrieval
    # In production, query by ID from Unity Catalog Delta table
    raise HTTPException(status_code=404, detail="Equipment not found")


@app.post("/contributions", status_code=202)
async def submit_contribution(contribution: ContributionRequest) -> dict[str, Any]:
    """Submit a correction or contribution.

    Creates a GitHub issue with the suggested change for community review.

    Args:
        contribution: Contribution details

    Returns:
        Contribution submission status

    Note:
        This is a placeholder. Actual implementation would:
        1. Validate the contribution
        2. Use GitHub API to create an issue or PR
        3. Return the issue/PR URL
    """
    # Placeholder for GitHub API integration
    # In production, this would:
    # 1. Create a GitHub issue with structured data
    # 2. Apply labels (e.g., "contribution", "data-correction")
    # 3. Return issue URL for tracking
    return {
        "status": "accepted",
        "message": "Contribution submitted for review",
        "tracking_url": None,  # Would be GitHub issue URL
    }


@app.get("/stats")
async def get_statistics() -> dict[str, Any]:
    """Get database statistics.

    Returns:
        Statistics about the equipment database

    Note:
        This is a placeholder for actual statistics gathering.
    """
    return {
        "total_equipment": 0,
        "tractors": 0,
        "combines": 0,
        "implements": 0,
        "manufacturers": 0,
        "last_updated": None,
    }


def main() -> None:
    """Run the API server (for development).

    In production, this would be deployed as a containerized service.
    """
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
