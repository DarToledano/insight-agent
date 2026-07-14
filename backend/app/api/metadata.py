"""Metadata cache management endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.metadata import DatabaseMetadata
from app.services.metadata_cache import MetadataCache, get_metadata_cache

logger = logging.getLogger(__name__)

router = APIRouter(tags=["metadata"])


def get_cache() -> MetadataCache:
    return get_metadata_cache()


@router.get("/metadata", response_model=DatabaseMetadata)
async def get_metadata(
    cache: MetadataCache = Depends(get_cache),
) -> DatabaseMetadata:
    """Return the full in-memory metadata cache."""
    try:
        return cache.get_metadata()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.post("/metadata/refresh", response_model=DatabaseMetadata)
async def refresh_metadata(
    db: Session = Depends(get_db),
    cache: MetadataCache = Depends(get_cache),
) -> DatabaseMetadata:
    """Explicitly rebuild the metadata cache from the connected database."""
    try:
        return cache.refresh_metadata(db)
    except SQLAlchemyError as exc:
        logger.exception("Metadata refresh failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to refresh metadata: {exc}",
        ) from exc
