"""Execute validated read-only SQL queries."""

import logging
import time
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.services.exceptions import SQLExecutionError

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    columns: list[str]
    rows: list[list[object]]
    row_count: int
    execution_time_ms: int


class SQLExecutor:
    """Run validated SELECT statements against PostgreSQL."""

    def execute(self, db: Session, sql: str) -> ExecutionResult:
        start = time.perf_counter()

        try:
            result = db.execute(text(sql))
            columns = list(result.keys())
            rows = [list(row) for row in result.fetchall()]
        except SQLAlchemyError as exc:
            logger.exception("SQL execution failed")
            raise SQLExecutionError(f"Database query failed: {exc}") from exc

        elapsed_ms = int((time.perf_counter() - start) * 1000)

        logger.info(
            "SQL executed in %dms, returned %d rows",
            elapsed_ms,
            len(rows),
        )

        return ExecutionResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            execution_time_ms=elapsed_ms,
        )
