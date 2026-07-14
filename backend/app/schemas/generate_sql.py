"""Request/response schemas for SQL generation."""

from pydantic import BaseModel, Field


class GenerateSqlRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        examples=["Which companies generated the most revenue this year?"],
    )


class GenerateSqlResponse(BaseModel):
    sql: str
