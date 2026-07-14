"""Format SQL execution results for JSON API responses."""

from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from app.services.sql_executor import ExecutionResult


class ResultFormatter:
    """Convert database values into JSON-serializable structures."""

    def format(self, result: ExecutionResult) -> dict[str, object]:
        return {
            "columns": result.columns,
            "rows": [
                [self._serialize_value(cell) for cell in row]
                for row in result.rows
            ],
            "row_count": result.row_count,
            "execution_time_ms": result.execution_time_ms,
        }

    def _serialize_value(self, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, (datetime, date, time)):
            return value.isoformat()
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, (bytes, bytearray)):
            return value.decode("utf-8", errors="replace")
        if isinstance(value, memoryview):
            return value.tobytes().decode("utf-8", errors="replace")
        return str(value)
