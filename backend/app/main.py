"""FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import api_router
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.metadata_cache import get_metadata_cache

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.on_event("startup")
async def startup_build_metadata_cache() -> None:
    """Build metadata cache once at application startup."""
    cache = get_metadata_cache()
    db = SessionLocal()
    try:
        metadata = cache.refresh_metadata(db)
        logger.info(
            "Metadata cache initialized with %d tables",
            metadata.table_count,
        )
    except SQLAlchemyError as exc:
        logger.error("Failed to initialize metadata cache: %s", exc)
        raise
    finally:
        db.close()
