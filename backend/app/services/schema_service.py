"""Fetch database schema metadata from PostgreSQL."""

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas.schema_info import ColumnInfo, SchemaResponse, TableInfo


def fetch_database_schema(db: Session) -> SchemaResponse:
    """Return all tables and columns from the public schema."""
    query = text("""
        SELECT
            table_name,
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
    """)

    rows = db.execute(query).mappings().all()

    tables: dict[str, list[ColumnInfo]] = {}
    for row in rows:
        table_name = row["table_name"]
        tables.setdefault(table_name, []).append(
            ColumnInfo(
                name=row["column_name"],
                data_type=row["data_type"],
                is_nullable=row["is_nullable"] == "YES",
                column_default=row["column_default"],
            )
        )

    table_list = [
        TableInfo(name=name, columns=columns) for name, columns in tables.items()
    ]

    return SchemaResponse(
        schema_name="public",
        tables=table_list,
        table_count=len(table_list),
    )


def format_schema_for_prompt(schema: SchemaResponse) -> str:
    """Render schema metadata as plain text for LLM prompts."""
    lines: list[str] = [f"Schema: {schema.schema_name}", ""]

    for table in schema.tables:
        lines.append(f"Table: {table.name}")
        for column in table.columns:
            nullable = "NULL" if column.is_nullable else "NOT NULL"
            default = (
                f", default={column.column_default}"
                if column.column_default is not None
                else ""
            )
            lines.append(
                f"  - {column.name}: {column.data_type} {nullable}{default}"
            )
        lines.append("")

    return "\n".join(lines).strip()


def get_schema_or_raise(db: Session) -> SchemaResponse:
    """Load schema metadata, raising SQLAlchemyError on failure."""
    try:
        return fetch_database_schema(db)
    except SQLAlchemyError:
        raise
