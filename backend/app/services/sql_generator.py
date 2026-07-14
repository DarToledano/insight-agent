"""Natural-language to SQL generation via LLM."""

from app.services.llm_service import LLMService
from app.utils.sql_validation import clean_sql

SYSTEM_PROMPT = """You are a PostgreSQL expert for a SaaS analytics platform.

Rules:
- Generate only PostgreSQL SQL.
- Only SELECT statements are allowed.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, or any DDL/DML.
- Use only tables and columns that exist in the provided database metadata.
- Use the column value hints (categorical values, numeric/temporal ranges) when filtering.
- Prefer explicit JOINs using the documented foreign key relationships.
- When the question refers to business entities (companies, users, plans, etc.), JOIN related
  tables and SELECT human-readable labels such as name, full_name, or title — not raw id or
  foreign-key UUID columns (e.g. company_id) in the final output.
- Only include id columns when the question explicitly asks for identifiers.
- Return only SQL. No markdown, no code fences, no explanation.
"""


class SQLGenerator:
    """Convert natural-language questions into PostgreSQL SELECT queries."""

    def __init__(self, llm_service: LLMService | None = None) -> None:
        self._llm_service = llm_service

    def _get_llm(self) -> LLMService:
        if self._llm_service is None:
            self._llm_service = LLMService()
        return self._llm_service

    def generate(self, question: str, metadata_text: str) -> str:
        """Generate SQL from a question and database metadata (no DB access)."""
        if not question.strip():
            raise ValueError("Question must not be empty.")

        user_prompt = (
            f"Database metadata:\n\n{metadata_text}\n\n"
            f"Question: {question.strip()}\n\n"
            "Write a PostgreSQL SELECT query that answers the question. "
            "Use readable entity names in the result columns whenever applicable."
        )

        raw_sql = self._get_llm().generate_text(SYSTEM_PROMPT, user_prompt)
        return clean_sql(raw_sql)
