"""Database metadata models for the Metadata Engine."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ForeignKeyRef(BaseModel):
    column: str
    references_table: str
    references_column: str


class ColumnProfile(BaseModel):
    kind: Literal["categorical", "numeric", "temporal", "boolean"]
    distinct_values: list[str] | None = None
    min_value: str | None = None
    max_value: str | None = None


class ColumnMetadata(BaseModel):
    name: str
    data_type: str
    is_nullable: bool
    is_primary_key: bool = False
    foreign_key: ForeignKeyRef | None = None
    profile: ColumnProfile | None = None


class TableMetadata(BaseModel):
    name: str
    columns: list[ColumnMetadata]
    primary_keys: list[str] = Field(default_factory=list)
    foreign_keys: list[ForeignKeyRef] = Field(default_factory=list)


class DatabaseMetadata(BaseModel):
    schema_name: str
    tables: list[TableMetadata]
    table_count: int
    generated_at: datetime
