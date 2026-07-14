"""Request/response schemas for POST /ask."""

from typing import Any

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        examples=["Which companies generated the highest revenue this year?"],
    )


class TableData(BaseModel):
    columns: list[str]
    rows: list[list[Any]]


class AskMetadata(BaseModel):
    row_count: int
    execution_time_ms: int


class AskDebug(BaseModel):
    sql: str


class AskResponse(BaseModel):
    answer: str
    table: TableData
    metadata: AskMetadata
    debug: AskDebug
