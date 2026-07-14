"""Orchestrate the InsightAgent question-answering pipeline."""

import logging

from sqlalchemy.orm import Session

from app.schemas.ask import AskDebug, AskMetadata, AskResponse, ChartConfig, TableData
from app.services.chart_selector import ChartSelector
from app.services.insight_generator import InsightGenerator
from app.services.metadata_cache import get_metadata_cache
from app.services.metadata_formatter import format_subset_metadata
from app.services.metadata_selector import MetadataSelector
from app.services.result_formatter import ResultFormatter
from app.services.sql_executor import SQLExecutor
from app.services.sql_generator import SQLGenerator
from app.services.sql_validator import SQLValidator

logger = logging.getLogger(__name__)


class AskService:
    """End-to-end pipeline: question → metadata → SQL → validate → execute → format → insight."""

    def __init__(
        self,
        sql_generator: SQLGenerator | None = None,
        sql_validator: SQLValidator | None = None,
        sql_executor: SQLExecutor | None = None,
        result_formatter: ResultFormatter | None = None,
        metadata_selector: MetadataSelector | None = None,
        insight_generator: InsightGenerator | None = None,
        chart_selector: ChartSelector | None = None,
    ) -> None:
        self._sql_generator = sql_generator or SQLGenerator()
        self._sql_validator = sql_validator or SQLValidator()
        self._sql_executor = sql_executor or SQLExecutor()
        self._result_formatter = result_formatter or ResultFormatter()
        self._metadata_selector = metadata_selector or MetadataSelector()
        self._insight_generator = insight_generator or InsightGenerator()
        self._chart_selector = chart_selector or ChartSelector()

    def ask(self, db: Session, question: str) -> AskResponse:
        logger.info("Received question: %s", question.strip())

        metadata = get_metadata_cache().get_metadata()
        relevant_tables = self._metadata_selector.select_relevant_tables(
            question, metadata
        )
        metadata_text = format_subset_metadata(metadata, relevant_tables)
        logger.info(
            "Using metadata for %d table(s): %s",
            len(relevant_tables),
            [t.name for t in relevant_tables],
        )

        generated_sql = self._sql_generator.generate(question, metadata_text)
        logger.info("Generated SQL: %s", generated_sql)

        validated_sql = self._sql_validator.validate(generated_sql)
        logger.info("SQL validation passed")

        execution = self._sql_executor.execute(db, validated_sql)
        formatted = self._result_formatter.format(execution)

        answer = self._generate_insight(
            question=question,
            sql=validated_sql,
            columns=formatted["columns"],
            rows=formatted["rows"],
            row_count=formatted["row_count"],
        )

        chart_selection = self._chart_selector.select(
            question=question,
            columns=formatted["columns"],
            rows=formatted["rows"],
        )

        logger.info(
            "Pipeline complete: row_count=%d execution_time_ms=%d chart=%s",
            formatted["row_count"],
            formatted["execution_time_ms"],
            chart_selection.type,
        )

        return AskResponse(
            answer=answer,
            table=TableData(
                columns=formatted["columns"],
                rows=formatted["rows"],
            ),
            chart=ChartConfig(**chart_selection.to_dict()),
            metadata=AskMetadata(
                row_count=formatted["row_count"],
                execution_time_ms=formatted["execution_time_ms"],
            ),
            debug=AskDebug(sql=validated_sql),
        )

    def _generate_insight(
        self,
        question: str,
        sql: str,
        columns: list[str],
        rows: list[list[object]],
        row_count: int,
    ) -> str:
        try:
            return self._insight_generator.generate(
                question=question,
                sql=sql,
                columns=columns,
                rows=rows,
                row_count=row_count,
            )
        except Exception:
            logger.exception("Insight generation failed")
            return self._insight_generator.fallback_answer(
                question=question,
                columns=columns,
                rows=rows,
                row_count=row_count,
            )
