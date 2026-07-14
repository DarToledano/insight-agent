"""Tests for InsightGenerator."""

import pytest

from app.services.insight_generator import (
    EMPTY_ANSWER_EN,
    EMPTY_ANSWER_HE,
    FALLBACK_ANSWER_EN,
    InsightGenerator,
)
from app.services.llm_service import LLMService
from tests.conftest import MockLLMProvider, make_llm_service


class FailingLLMProvider(MockLLMProvider):
    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        raise RuntimeError("OpenAI API error: simulated failure")


def test_empty_results_english_without_llm_call():
    provider = MockLLMProvider()
    generator = InsightGenerator(llm_service=LLMService(provider=provider))

    answer = generator.generate(
        question="Which companies have the highest revenue?",
        sql="SELECT 1",
        columns=["name"],
        rows=[],
        row_count=0,
    )

    assert answer == EMPTY_ANSWER_EN
    assert provider.calls == []


def test_empty_results_hebrew_without_llm_call():
    provider = MockLLMProvider()
    generator = InsightGenerator(llm_service=LLMService(provider=provider))

    answer = generator.generate(
        question="אילו חברות הניבו את ההכנסה הגבוהה ביותר?",
        sql="SELECT 1",
        columns=["name"],
        rows=[],
        row_count=0,
    )

    assert answer == EMPTY_ANSWER_HE
    assert provider.calls == []


def test_english_answer_generation():
    expected = (
        "Zenith Consulting generated the highest revenue at 47,940, "
        "followed by SecureNet Corp at 28,764."
    )
    generator = InsightGenerator(llm_service=make_llm_service(expected))

    answer = generator.generate(
        question="Which companies have the highest revenue?",
        sql="SELECT name, revenue FROM companies ORDER BY revenue DESC",
        columns=["name", "revenue"],
        rows=[
            ["Zenith Consulting", 47940],
            ["SecureNet Corp", 28764],
        ],
        row_count=2,
    )

    assert answer == expected


def test_hebrew_answer_generation():
    expected = "Zenith Consulting הניבה את ההכנסה הגבוהה ביותר."
    provider = MockLLMProvider(expected)
    generator = InsightGenerator(llm_service=LLMService(provider=provider))

    answer = generator.generate(
        question="אילו חברות הניבו את ההכנסה הגבוהה ביותר?",
        sql="SELECT name FROM companies",
        columns=["name"],
        rows=[["Zenith Consulting"]],
        row_count=1,
    )

    assert answer == expected
    assert "Respond in the same language" in provider.calls[0][0]


def test_single_value_result_prompt_contains_data():
    provider = MockLLMProvider("Total revenue is 150,000.")
    generator = InsightGenerator(llm_service=LLMService(provider=provider))

    answer = generator.generate(
        question="What is the total revenue?",
        sql="SELECT SUM(amount) AS total_revenue FROM payments",
        columns=["total_revenue"],
        rows=[[150000]],
        row_count=1,
    )

    assert answer == "Total revenue is 150,000."
    assert "150,000" in provider.calls[0][1] or "150000" in provider.calls[0][1]


def test_ranking_results_passed_to_llm():
    provider = MockLLMProvider(
        "Northwind Logistics and Apex Analytics were tied for third place at 19,176 each."
    )
    generator = InsightGenerator(llm_service=LLMService(provider=provider))

    answer = generator.generate(
        question="Which companies have the highest revenue?",
        sql="SELECT name, revenue FROM companies ORDER BY revenue DESC",
        columns=["name", "revenue"],
        rows=[
            ["Zenith Consulting", 47940],
            ["SecureNet Corp", 28764],
            ["Northwind Logistics", 19176],
            ["Apex Analytics", 19176],
        ],
        row_count=4,
    )

    assert "tied for third" in answer
    assert "Northwind Logistics" in provider.calls[0][1]


def test_row_limit_sent_to_llm():
    provider = MockLLMProvider("Top companies summarized.")
    generator = InsightGenerator(llm_service=LLMService(provider=provider), max_rows=2)

    rows = [[f"Company {i}", i * 1000] for i in range(10)]
    generator.generate(
        question="Which companies have the highest revenue?",
        sql="SELECT name, revenue FROM companies",
        columns=["name", "revenue"],
        rows=rows,
        row_count=10,
    )

    user_prompt = provider.calls[0][1]
    assert "more_rows_available" in user_prompt or "more rows" in user_prompt.lower()
    assert "Company 0" in user_prompt
    assert "Company 9" not in user_prompt


def test_llm_failure_fallback_single_value():
    generator = InsightGenerator(llm_service=LLMService(provider=FailingLLMProvider()))

    answer = generator.fallback_answer(
        question="What is the total revenue?",
        columns=["total_revenue"],
        rows=[[150000]],
        row_count=1,
    )

    assert "150,000" in answer


def test_llm_failure_fallback_multiple_rows():
    generator = InsightGenerator(llm_service=LLMService(provider=FailingLLMProvider()))

    answer = generator.fallback_answer(
        question="Which companies have the highest revenue?",
        columns=["name", "revenue"],
        rows=[["A", 1], ["B", 2]],
        row_count=2,
    )

    assert "2 rows" in answer
    assert FALLBACK_ANSWER_EN in answer


def test_ask_service_returns_table_and_sql_on_insight_failure():
    from unittest.mock import MagicMock

    from app.services.ask_service import AskService

    failing_insight = InsightGenerator(
        llm_service=LLMService(provider=FailingLLMProvider())
    )
    ask_service = AskService(
        sql_generator=MagicMock(generate=lambda q, m: "SELECT name FROM companies"),
        sql_validator=MagicMock(validate=lambda s: s),
        sql_executor=MagicMock(
            execute=lambda db, s: MagicMock(
                columns=["name"],
                rows=[["Zenith Consulting"]],
                row_count=1,
                execution_time_ms=12,
            )
        ),
        result_formatter=MagicMock(
            format=lambda r: {
                "columns": r.columns,
                "rows": r.rows,
                "row_count": r.row_count,
                "execution_time_ms": r.execution_time_ms,
            }
        ),
        metadata_selector=MagicMock(select_relevant_tables=lambda q, m: []),
        insight_generator=failing_insight,
    )

    from app.services.metadata_cache import MetadataCache
    from app.schemas.metadata import DatabaseMetadata
    from datetime import UTC, datetime

    cache = MetadataCache()
    cache._metadata = DatabaseMetadata(
        schema_name="public",
        tables=[],
        table_count=0,
        generated_at=datetime.now(UTC),
    )

    import app.services.ask_service as ask_module

    original = ask_module.get_metadata_cache
    ask_module.get_metadata_cache = lambda: cache
    try:
        response = ask_service.ask(MagicMock(), "Which company leads revenue?")
    finally:
        ask_module.get_metadata_cache = original

    assert response.table.rows == [["Zenith Consulting"]]
    assert response.debug.sql == "SELECT name FROM companies"
    assert response.metadata.row_count == 1
    assert response.chart.type == "none"
    assert response.answer == "Name is Zenith Consulting."
