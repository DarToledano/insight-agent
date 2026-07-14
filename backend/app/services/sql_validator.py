"""Validate LLM-generated SQL before execution."""

import re

from app.services.exceptions import SQLValidationError
from app.utils.sql_validation import clean_sql

FORBIDDEN_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|"
    r"EXECUTE|CALL|MERGE|REPLACE|UPSERT|COPY|PREPARE|DEALLOCATE)\b",
    re.IGNORECASE,
)

DANGEROUS_PATTERNS = (
    re.compile(r"\bINTO\s+OUTFILE\b", re.IGNORECASE),
    re.compile(r"\bSELECT\b.+\bINTO\b(?!\s*\()", re.IGNORECASE | re.DOTALL),
    re.compile(r"\bpg_read_file\b", re.IGNORECASE),
    re.compile(r"\blo_import\b", re.IGNORECASE),
    re.compile(r"\bdblink\b", re.IGNORECASE),
)


class SQLValidator:
    """Enforce read-only, single-statement SQL safety rules."""

    def validate(self, sql: str) -> str:
        """Validate and return normalized SQL, or raise SQLValidationError."""
        normalized = clean_sql(sql).strip()

        if not normalized:
            raise SQLValidationError("SQL query is empty.")

        if not normalized.upper().startswith("SELECT"):
            raise SQLValidationError("Only SELECT statements are allowed.")

        if ";" in normalized.rstrip(";"):
            raise SQLValidationError("Multiple SQL statements are not allowed.")

        if FORBIDDEN_KEYWORDS.search(normalized):
            raise SQLValidationError(
                "SQL contains forbidden keywords. "
                "Only read-only SELECT queries are permitted."
            )

        for pattern in DANGEROUS_PATTERNS:
            if pattern.search(normalized):
                raise SQLValidationError(
                    "SQL contains dangerous syntax and cannot be executed."
                )

        return normalized
