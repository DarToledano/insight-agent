"""Validate and sanitize LLM-generated SQL."""

import re

MARKDOWN_FENCE = re.compile(
    r"^```(?:sql)?\s*|\s*```$",
    re.IGNORECASE | re.MULTILINE,
)


def clean_sql(raw: str) -> str:
    """Strip markdown fences and surrounding whitespace from LLM output."""
    cleaned = MARKDOWN_FENCE.sub("", raw).strip()
    if ";" in cleaned:
        parts = [part.strip() for part in cleaned.split(";") if part.strip()]
        if parts:
            cleaned = parts[0]
    return cleaned.rstrip(";")
