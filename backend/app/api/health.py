"""Health check endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.core.database import check_database_connection
from app.schemas.health import DbHealthResponse, HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return API liveness status (no database dependency)."""
    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
    )


@router.get("/db-health", response_model=DbHealthResponse)
async def db_health_check() -> DbHealthResponse:
    """Verify PostgreSQL connectivity with SELECT 1."""
    try:
        check_database_connection()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {exc}",
        ) from exc

    return DbHealthResponse(
        status="ok",
        database="postgresql",
        message="Connection successful",
    )
