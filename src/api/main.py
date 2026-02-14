"""Main FastAPI application for OpenAg-DB API.

This API serves agricultural equipment data from Unity Catalog Delta tables
and provides endpoints for user contributions.
"""

import logging
import os
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.databricks_utils import get_table_manager
from core.models import (
    Combine,
    CommonEquipment,
    EquipmentCategory,
    Implement,
    Tractor,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global table manager instance (will be None if Unity Catalog is not configured)
_table_manager = None


def get_unity_catalog_manager() -> Any:
    """Get or create Unity Catalog table manager.

    Returns:
        TableManager instance if Unity Catalog is configured, None otherwise
    """
    global _table_manager
    if _table_manager is None:
        try:
            _table_manager = get_table_manager()
            logger.info("Unity Catalog connection established")
        except (ValueError, Exception) as e:
            logger.warning(
                f"Unity Catalog not configured or connection failed: {e}. "
                "API will return empty results."
            )
            _table_manager = None
    return _table_manager

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
    """
    manager = get_unity_catalog_manager()
    if manager is None:
        logger.warning("Unity Catalog not configured, returning empty list")
        return []

    try:
        # Build filters dictionary
        filters: dict[str, Any] = {}
        if make:
            filters["make"] = make
        if model:
            filters["model"] = model

        # Determine which tables to query based on category
        results: list[CommonEquipment] = []

        if category is None or category == EquipmentCategory.TRACTOR:
            try:
                tractor_data = manager.query_table("tractors", filters)
                results.extend([Tractor(**record) for record in tractor_data])
            except Exception as e:
                logger.warning(f"Failed to query tractors table: {e}")

        if category is None or category == EquipmentCategory.COMBINE:
            try:
                combine_data = manager.query_table("combines", filters)
                results.extend([Combine(**record) for record in combine_data])
            except Exception as e:
                logger.warning(f"Failed to query combines table: {e}")

        if category is None or category == EquipmentCategory.IMPLEMENT:
            try:
                implement_data = manager.query_table("implements", filters)
                results.extend([Implement(**record) for record in implement_data])
            except Exception as e:
                logger.warning(f"Failed to query implements table: {e}")

        # Apply year filters if provided
        if year_min or year_max:
            results = [
                item
                for item in results
                if (
                    year_min is None
                    or (item.year_start and item.year_start >= year_min)
                )
                and (
                    year_max is None
                    or (item.year_end and item.year_end <= year_max)
                    or (item.year_start and item.year_start <= year_max)
                )
            ]

        # Apply pagination
        total = len(results)
        results = results[offset : offset + limit]

        logger.info(
            f"Returning {len(results)} of {total} equipment items "
            f"(limit={limit}, offset={offset})"
        )
        return results

    except Exception as e:
        logger.error(f"Error querying equipment: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to query equipment database"
        ) from e


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
    manager = get_unity_catalog_manager()
    if manager is None:
        logger.warning("Unity Catalog not configured, returning empty list")
        return []

    try:
        filters: dict[str, Any] = {}
        if make:
            filters["make"] = make

        tractor_data = manager.query_table("tractors", filters)
        tractors = [Tractor(**record) for record in tractor_data]

        # Apply horsepower filters
        if hp_min or hp_max:
            tractors = [
                t
                for t in tractors
                if (hp_min is None or (t.engine_hp and t.engine_hp >= hp_min))
                and (hp_max is None or (t.engine_hp and t.engine_hp <= hp_max))
            ]

        # Apply pagination
        total = len(tractors)
        tractors = tractors[offset : offset + limit]

        logger.info(f"Returning {len(tractors)} of {total} tractors")
        return tractors

    except Exception as e:
        logger.error(f"Error querying tractors: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to query tractors database"
        ) from e


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
    manager = get_unity_catalog_manager()
    if manager is None:
        logger.warning("Unity Catalog not configured, returning empty list")
        return []

    try:
        filters: dict[str, Any] = {}
        if make:
            filters["make"] = make

        combine_data = manager.query_table("combines", filters)
        combines = [Combine(**record) for record in combine_data]

        # Apply tank capacity filter
        if tank_capacity_min:
            combines = [
                c
                for c in combines
                if c.grain_tank_capacity_bu
                and c.grain_tank_capacity_bu >= tank_capacity_min
            ]

        # Apply pagination
        total = len(combines)
        combines = combines[offset : offset + limit]

        logger.info(f"Returning {len(combines)} of {total} combines")
        return combines

    except Exception as e:
        logger.error(f"Error querying combines: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to query combines database"
        ) from e


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
    manager = get_unity_catalog_manager()
    if manager is None:
        logger.warning("Unity Catalog not configured, returning empty list")
        return []

    try:
        filters: dict[str, Any] = {}
        if make:
            filters["make"] = make

        implement_data = manager.query_table("implements", filters)
        implements = [Implement(**record) for record in implement_data]

        # Apply width filter
        if width_min:
            implements = [
                i
                for i in implements
                if i.working_width_ft and i.working_width_ft >= width_min
            ]

        # Apply pagination
        total = len(implements)
        implements = implements[offset : offset + limit]

        logger.info(f"Returning {len(implements)} of {total} implements")
        return implements

    except Exception as e:
        logger.error(f"Error querying implements: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to query implements database"
        ) from e


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
    """
    manager = get_unity_catalog_manager()
    if manager is None:
        logger.warning("Unity Catalog not configured, returning zero stats")
        return {
            "total_equipment": 0,
            "tractors": 0,
            "combines": 0,
            "implements": 0,
            "manufacturers": 0,
            "last_updated": None,
        }

    try:
        # Query each table to get counts
        tractor_count = 0
        combine_count = 0
        implement_count = 0

        try:
            tractors = manager.query_table("tractors")
            tractor_count = len(tractors)
        except Exception as e:
            logger.warning(f"Failed to count tractors: {e}")

        try:
            combines = manager.query_table("combines")
            combine_count = len(combines)
        except Exception as e:
            logger.warning(f"Failed to count combines: {e}")

        try:
            implements = manager.query_table("implements")
            implement_count = len(implements)
        except Exception as e:
            logger.warning(f"Failed to count implements: {e}")

        total = tractor_count + combine_count + implement_count

        return {
            "total_equipment": total,
            "tractors": tractor_count,
            "combines": combine_count,
            "implements": implement_count,
            "manufacturers": 0,  # TODO: Calculate unique manufacturers
            "last_updated": None,  # TODO: Get last update timestamp
        }

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get database statistics"
        ) from e


def main() -> None:
    """Run the API server (for development).

    In production, this would be deployed as a containerized service.
    """
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
