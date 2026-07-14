"""Database schema introspection endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.schema_info import SchemaResponse
from app.services.schema_service import get_schema_or_raise

router = APIRouter(tags=["schema"])


@router.get("/schema", response_model=SchemaResponse)
async def get_database_schema(db: Session = Depends(get_db)) -> SchemaResponse:
    """Return all tables and columns from the public schema."""
    try:
        return get_schema_or_raise(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to read database schema: {exc}",
        ) from exc
