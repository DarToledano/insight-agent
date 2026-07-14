"""In-memory cache for database metadata."""

import logging
import threading

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.schemas.metadata import DatabaseMetadata
from app.services.metadata_generator import MetadataGenerator

logger = logging.getLogger(__name__)


class MetadataCache:
    """
    Thread-safe in-memory metadata cache.

    Built once at application startup; normal requests read from cache only.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._metadata: DatabaseMetadata | None = None
        self._generator = MetadataGenerator()

    def get_metadata(self) -> DatabaseMetadata:
        if self._metadata is None:
            raise RuntimeError(
                "Metadata cache is not initialized. "
                "Wait for application startup to complete."
            )
        return self._metadata

    def is_initialized(self) -> bool:
        return self._metadata is not None

    def refresh_metadata(self, db: Session | None = None) -> DatabaseMetadata:
        """Rebuild metadata from the connected database."""
        logger.info("Refreshing metadata cache")

        if db is not None:
            metadata = self._generator.generate(db)
        else:
            session = SessionLocal()
            try:
                metadata = self._generator.generate(session)
            finally:
                session.close()

        with self._lock:
            self._metadata = metadata

        logger.info(
            "Metadata cache refreshed: %d tables at %s",
            metadata.table_count,
            metadata.generated_at.isoformat(),
        )
        return metadata


_cache: MetadataCache | None = None
_cache_lock = threading.Lock()


def get_metadata_cache() -> MetadataCache:
    global _cache
    if _cache is None:
        with _cache_lock:
            if _cache is None:
                _cache = MetadataCache()
    return _cache
