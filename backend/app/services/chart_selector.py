"""Rule-based chart type selection for query results."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

ChartType = Literal["bar", "line", "pie", "kpi", "none"]

ISO_DATE_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$"
)

MAX_TABLE_COLUMNS = 5
MAX_BAR_ROWS = 40
MAX_PIE_ROWS = 8
MIN_LINE_ROWS = 3

PIE_KEYWORDS = (
    "by",
    "share",
    "distribution",
    "breakdown",
    "split",
    "proportion",
    "percent",
    "percentage",
)

PIE_X_HINTS = ("plan", "category", "type", "status", "country", "industry", "segment")

METRIC_HINTS = (
    "total",
    "sum",
    "count",
    "avg",
    "average",
    "revenue",
    "amount",
    "price",
    "value",
    "score",
    "rate",
)


@dataclass(frozen=True)
class ChartSelection:
    type: ChartType
    x_key: str
    y_key: str
    title: str

    def to_dict(self) -> dict[str, str]:
        return {
            "type": self.type,
            "x_key": self.x_key,
            "y_key": self.y_key,
            "title": self.title,
        }


class ChartSelector:
    """Choose an appropriate chart type using deterministic heuristics."""

    def select(
        self,
        question: str,
        columns: list[str],
        rows: list[list[Any]],
        column_types: dict[str, str] | None = None,
    ) -> ChartSelection:
        if not columns or not rows:
            return self._none()

        if len(columns) > MAX_TABLE_COLUMNS:
            return self._none()

        kinds = [
            self._column_kind(column, col_index, rows, column_types)
            for col_index, column in enumerate(columns)
        ]

        numeric_indices = [i for i, kind in enumerate(kinds) if kind == "numeric"]
        if not numeric_indices:
            return self._none()

        if self._is_kpi(columns, rows, numeric_indices):
            y_key = self._pick_metric_column(columns, numeric_indices)
            return ChartSelection(
                type="kpi",
                x_key="",
                y_key=y_key,
                title=self._build_title(question, "", y_key, "kpi"),
            )

        y_index = self._pick_metric_index(columns, numeric_indices)
        y_key = columns[y_index]

        temporal_indices = [i for i, kind in enumerate(kinds) if kind == "temporal"]
        label_indices = [
            i
            for i, kind in enumerate(kinds)
            if kind == "categorical" and i != y_index
        ]

        if temporal_indices:
            x_index = temporal_indices[0]
            if len(rows) >= MIN_LINE_ROWS:
                x_key = columns[x_index]
                return ChartSelection(
                    type="line",
                    x_key=x_key,
                    y_key=y_key,
                    title=self._build_title(question, x_key, y_key, "line"),
                )

        if not label_indices:
            return self._none()

        x_index = self._pick_label_index(columns, label_indices)
        x_key = columns[x_index]
        row_count = len(rows)

        if row_count > MAX_BAR_ROWS:
            return self._none()

        if (
            2 <= row_count <= MAX_PIE_ROWS
            and self._is_pie_appropriate(question, x_key, row_count)
            and not self._is_heavily_skewed(rows, y_index)
        ):
            return ChartSelection(
                type="pie",
                x_key=x_key,
                y_key=y_key,
                title=self._build_title(question, x_key, y_key, "pie"),
            )

        if row_count >= 2:
            return ChartSelection(
                type="bar",
                x_key=x_key,
                y_key=y_key,
                title=self._build_title(question, x_key, y_key, "bar"),
            )

        return self._none()

    def _none(self) -> ChartSelection:
        return ChartSelection(type="none", x_key="", y_key="", title="")

    def _is_kpi(
        self,
        columns: list[str],
        rows: list[list[Any]],
        numeric_indices: list[int],
    ) -> bool:
        if len(rows) != 1 or len(numeric_indices) != 1:
            return False
        return len(columns) <= 2

    def _column_kind(
        self,
        column: str,
        col_index: int,
        rows: list[list[Any]],
        column_types: dict[str, str] | None,
    ) -> str:
        if column_types and column in column_types:
            declared = column_types[column].lower()
            if declared in {"integer", "numeric", "decimal", "float", "double", "real"}:
                return "numeric"
            if declared in {"date", "timestamp", "timestamptz", "time"}:
                return "temporal"

        values = [row[col_index] for row in rows if col_index < len(row)]
        if not values:
            return "unknown"

        if all(self._is_numeric_value(value) or value is None for value in values):
            return "numeric"

        non_null = [value for value in values if value is not None]
        if non_null and all(self._is_temporal_value(value) for value in non_null):
            return "temporal"

        return "categorical"

    def _is_numeric_value(self, value: Any) -> bool:
        if isinstance(value, bool):
            return False
        if isinstance(value, (int, float, Decimal)):
            return True
        if isinstance(value, str):
            try:
                float(value)
                return True
            except ValueError:
                return False
        return False

    def _is_temporal_value(self, value: Any) -> bool:
        if isinstance(value, (datetime, date)):
            return True
        if isinstance(value, str) and ISO_DATE_PATTERN.match(value):
            return True
        return False

    def _pick_metric_index(self, columns: list[str], numeric_indices: list[int]) -> int:
        for index in numeric_indices:
            lower = columns[index].lower()
            if any(hint in lower for hint in METRIC_HINTS):
                return index
        return numeric_indices[-1]

    def _pick_metric_column(self, columns: list[str], numeric_indices: list[int]) -> str:
        return columns[self._pick_metric_index(columns, numeric_indices)]

    def _pick_label_index(self, columns: list[str], label_indices: list[int]) -> int:
        preferred = ("name", "title", "label", "plan", "category", "country")
        for index in label_indices:
            lower = columns[index].lower()
            if lower in preferred or lower.endswith("_name"):
                return index
        for index in label_indices:
            lower = columns[index].lower()
            if lower != "id" and not lower.endswith("_id"):
                return index
        return label_indices[0]

    def _is_pie_appropriate(self, question: str, x_key: str, row_count: int) -> bool:
        lower_question = question.lower()
        lower_x = x_key.lower()
        if any(keyword in lower_question for keyword in PIE_KEYWORDS):
            return row_count <= MAX_PIE_ROWS
        if any(hint in lower_x for hint in PIE_X_HINTS):
            return row_count <= MAX_PIE_ROWS
        return False

    def _is_heavily_skewed(self, rows: list[list[Any]], y_index: int) -> bool:
        """Pie charts hide tiny slices; use bar when one value dominates."""
        values: list[float] = []
        for row in rows:
            if y_index >= len(row):
                continue
            value = row[y_index]
            if self._is_numeric_value(value):
                values.append(float(value))
        if len(values) < 2:
            return False
        total = sum(values)
        if total <= 0:
            return False
        return max(values) / total > 0.85

    def _humanize(self, key: str) -> str:
        if not key:
            return ""
        return key.replace("_", " ").strip().title()

    def _build_title(
        self,
        question: str,
        x_key: str,
        y_key: str,
        chart_type: ChartType,
    ) -> str:
        if chart_type == "kpi":
            return self._humanize(y_key)

        y_label = self._humanize(y_key)
        x_label = self._humanize(x_key)

        if x_label and y_label:
            return f"{y_label} by {x_label}"

        cleaned = question.strip().rstrip("?")
        if cleaned:
            return cleaned[0].upper() + cleaned[1:]

        return "Results"
