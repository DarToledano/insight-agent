"""Generate natural-language business answers from query results."""

import json
import logging
import re
from typing import Any

from app.core.config import settings
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a careful business data analyst.
Answer the user's question using only the provided query results.
Do not invent facts, causes, trends, or recommendations.
Mention the most important values and comparisons.
Be concise and clear.
Respond in the same language as the user's question.
Do not mention SQL, databases, queries, or internal systems.
When many rows exist, summarize the top results and note that more rows are available in the full table.
When results show rankings, highlight leaders, ties, and notable gaps using only the provided numbers.
"""

EMPTY_ANSWER_EN = "No matching data was found for this question."
EMPTY_ANSWER_HE = "לא נמצאו נתונים תואמים לשאלה זו."

FALLBACK_ANSWER_EN = (
    "The data was retrieved successfully, but a written summary could not be generated."
)
FALLBACK_ANSWER_HE = "הנתונים נשלפו בהצלחה, אך לא ניתן היה ליצור תשובה מילולית."


class InsightGenerator:
    """Convert executed query results into a human-readable business answer."""

    def __init__(
        self,
        llm_service: LLMService | None = None,
        max_rows: int | None = None,
    ) -> None:
        self._llm_service = llm_service
        self._max_rows = (
            max_rows if max_rows is not None else settings.INSIGHT_MAX_ROWS
        )

    def generate(
        self,
        question: str,
        sql: str,
        columns: list[str],
        rows: list[list[Any]],
        row_count: int,
    ) -> str:
        if row_count == 0 or not rows:
            return self._empty_answer(question)

        llm_rows, truncated = self._limit_rows(rows, row_count)
        user_prompt = self._build_user_prompt(
            question=question,
            sql=sql,
            columns=columns,
            rows=llm_rows,
            row_count=row_count,
            truncated=truncated,
        )

        answer = self._get_llm().generate_text(SYSTEM_PROMPT, user_prompt)
        logger.info("Generated insight answer (%d chars)", len(answer))
        return answer.strip()

    def fallback_answer(
        self,
        question: str,
        columns: list[str],
        rows: list[list[Any]],
        row_count: int,
    ) -> str:
        if row_count == 0 or not rows:
            return self._empty_answer(question)

        if row_count == 1 and len(columns) == 1:
            value = self._format_cell(rows[0][0])
            label = columns[0].replace("_", " ")
            if self._is_hebrew(question):
                return f"{label} הוא {value}."
            return f"{label.capitalize()} is {value}."

        if self._is_hebrew(question):
            return f"נמצאו {row_count} שורות. {FALLBACK_ANSWER_HE}"
        return (
            f"Retrieved {row_count} row{'s' if row_count != 1 else ''}. "
            f"{FALLBACK_ANSWER_EN}"
        )

    def _get_llm(self) -> LLMService:
        if self._llm_service is None:
            self._llm_service = LLMService()
        return self._llm_service

    def _limit_rows(
        self, rows: list[list[Any]], row_count: int
    ) -> tuple[list[list[Any]], bool]:
        limited = rows[: self._max_rows]
        truncated = row_count > len(limited)
        return limited, truncated

    def _build_user_prompt(
        self,
        question: str,
        sql: str,
        columns: list[str],
        rows: list[list[Any]],
        row_count: int,
        truncated: bool,
    ) -> str:
        serializable_rows = [
            [self._format_cell(cell) for cell in row] for row in rows
        ]
        payload = {
            "columns": columns,
            "rows": serializable_rows,
            "row_count": row_count,
            "rows_provided_to_you": len(rows),
            "more_rows_available": truncated,
        }

        parts = [
            f"User question:\n{question.strip()}",
            f"Query results (JSON):\n{json.dumps(payload, ensure_ascii=False, indent=2)}",
        ]
        if truncated:
            parts.append(
                f"Note: the full result set contains {row_count} rows; "
                f"only the first {len(rows)} are shown above. "
                "Summarize the most important findings and mention that additional rows exist."
            )
        parts.append("Write a concise business answer to the user's question.")
        return "\n\n".join(parts)

    def _empty_answer(self, question: str) -> str:
        return EMPTY_ANSWER_HE if self._is_hebrew(question) else EMPTY_ANSWER_EN

    def _is_hebrew(self, text: str) -> bool:
        hebrew_chars = len(re.findall(r"[\u0590-\u05FF]", text))
        latin_chars = len(re.findall(r"[A-Za-z]", text))
        return hebrew_chars > latin_chars

    def _format_cell(self, value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, float):
            formatted = f"{value:,.2f}".rstrip("0").rstrip(".")
            return formatted
        if isinstance(value, int):
            return f"{value:,}"
        return str(value)
