"""Inspect PostgreSQL and build statistical/semantic metadata."""

import logging
import re
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.metadata import (
    ColumnMetadata,
    ColumnProfile,
    DatabaseMetadata,
    ForeignKeyRef,
    TableMetadata,
)

logger = logging.getLogger(__name__)

IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

TEXT_TYPES = frozenset({"character varying", "varchar", "character", "char", "text"})
NUMERIC_TYPES = frozenset(
    {
        "smallint",
        "integer",
        "bigint",
        "numeric",
        "decimal",
        "real",
        "double precision",
    }
)
TEMPORAL_TYPES = frozenset(
    {"date", "timestamp without time zone", "timestamp with time zone", "time without time zone", "time with time zone"}
)
BOOLEAN_TYPES = frozenset({"boolean"})

SKIP_COLUMN_PATTERNS = (
    re.compile(r"^id$", re.I),
    re.compile(r"_id$", re.I),
    re.compile(r"uuid", re.I),
    re.compile(r"email", re.I),
    re.compile(r"^name$", re.I),
    re.compile(r"full_name", re.I),
    re.compile(r"first_name", re.I),
    re.compile(r"last_name", re.I),
    re.compile(r"description", re.I),
    re.compile(r"subject", re.I),
    re.compile(r"website", re.I),
    re.compile(r"title", re.I),
    re.compile(r"password", re.I),
    re.compile(r"url", re.I),
    re.compile(r"address", re.I),
    re.compile(r"notes?", re.I),
    re.compile(r"comment", re.I),
    re.compile(r"body", re.I),
    re.compile(r"message", re.I),
)


class MetadataGenerator:
    """Database-driven metadata generator for any PostgreSQL public schema."""

    def __init__(
        self,
        schema_name: str = "public",
        low_cardinality_threshold: int | None = None,
    ) -> None:
        self._schema = schema_name
        self._threshold = (
            low_cardinality_threshold
            if low_cardinality_threshold is not None
            else settings.METADATA_LOW_CARDINALITY_THRESHOLD
        )

    def generate(self, db: Session) -> DatabaseMetadata:
        logger.info("Generating database metadata for schema '%s'", self._schema)

        table_names = self._fetch_table_names(db)
        columns_by_table = self._fetch_columns(db)
        primary_keys = self._fetch_primary_keys(db)
        foreign_keys = self._fetch_foreign_keys(db)

        tables: list[TableMetadata] = []
        for table_name in table_names:
            table_columns = columns_by_table.get(table_name, [])
            table_pks = primary_keys.get(table_name, [])
            table_fks = foreign_keys.get(table_name, [])

            fk_by_column = {fk.column: fk for fk in table_fks}

            column_metadata: list[ColumnMetadata] = []
            for col in table_columns:
                col_name = col["column_name"]
                data_type = col["data_type"]
                is_pk = col_name in table_pks

                profile = None
                if not self._should_skip_profiling(col_name, data_type):
                    profile = self._profile_column(db, table_name, col_name, data_type)

                column_metadata.append(
                    ColumnMetadata(
                        name=col_name,
                        data_type=data_type,
                        is_nullable=col["is_nullable"] == "YES",
                        is_primary_key=is_pk,
                        foreign_key=fk_by_column.get(col_name),
                        profile=profile,
                    )
                )

            tables.append(
                TableMetadata(
                    name=table_name,
                    columns=column_metadata,
                    primary_keys=table_pks,
                    foreign_keys=table_fks,
                )
            )

        metadata = DatabaseMetadata(
            schema_name=self._schema,
            tables=tables,
            table_count=len(tables),
            generated_at=datetime.now(UTC),
        )
        logger.info("Metadata generation complete: %d tables", metadata.table_count)
        return metadata

    def _fetch_table_names(self, db: Session) -> list[str]:
        rows = db.execute(
            text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = :schema
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """),
            {"schema": self._schema},
        ).mappings().all()
        return [row["table_name"] for row in rows]

    def _fetch_columns(self, db: Session) -> dict[str, list[dict[str, str]]]:
        rows = db.execute(
            text("""
                SELECT table_name, column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = :schema
                ORDER BY table_name, ordinal_position
            """),
            {"schema": self._schema},
        ).mappings().all()

        result: dict[str, list[dict[str, str]]] = {}
        for row in rows:
            result.setdefault(row["table_name"], []).append(dict(row))
        return result

    def _fetch_primary_keys(self, db: Session) -> dict[str, list[str]]:
        rows = db.execute(
            text("""
                SELECT tc.table_name, kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                  ON tc.constraint_name = kcu.constraint_name
                 AND tc.table_schema = kcu.table_schema
                WHERE tc.table_schema = :schema
                  AND tc.constraint_type = 'PRIMARY KEY'
                ORDER BY tc.table_name, kcu.ordinal_position
            """),
            {"schema": self._schema},
        ).mappings().all()

        result: dict[str, list[str]] = {}
        for row in rows:
            result.setdefault(row["table_name"], []).append(row["column_name"])
        return result

    def _fetch_foreign_keys(self, db: Session) -> dict[str, list[ForeignKeyRef]]:
        rows = db.execute(
            text("""
                SELECT
                    kcu.table_name,
                    kcu.column_name,
                    ccu.table_name AS references_table,
                    ccu.column_name AS references_column
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                  ON tc.constraint_name = kcu.constraint_name
                 AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage ccu
                  ON tc.constraint_name = ccu.constraint_name
                 AND tc.table_schema = ccu.table_schema
                WHERE tc.table_schema = :schema
                  AND tc.constraint_type = 'FOREIGN KEY'
                ORDER BY kcu.table_name, kcu.column_name
            """),
            {"schema": self._schema},
        ).mappings().all()

        result: dict[str, list[ForeignKeyRef]] = {}
        for row in rows:
            fk = ForeignKeyRef(
                column=row["column_name"],
                references_table=row["references_table"],
                references_column=row["references_column"],
            )
            result.setdefault(row["table_name"], []).append(fk)
        return result

    def _should_skip_profiling(self, column_name: str, data_type: str) -> bool:
        if data_type == "uuid":
            return True
        if data_type in TEXT_TYPES and any(
            pattern.search(column_name) for pattern in SKIP_COLUMN_PATTERNS
        ):
            return True
        if column_name == "id" or column_name.endswith("_id"):
            return True
        return False

    def _profile_column(
        self,
        db: Session,
        table_name: str,
        column_name: str,
        data_type: str,
    ) -> ColumnProfile | None:
        self._validate_identifier(table_name)
        self._validate_identifier(column_name)

        qualified = f'"{table_name}"."{column_name}"'

        if data_type in BOOLEAN_TYPES:
            return self._profile_boolean(db, qualified)
        if data_type in NUMERIC_TYPES:
            return self._profile_numeric(db, qualified)
        if data_type in TEMPORAL_TYPES:
            return self._profile_temporal(db, qualified)
        if data_type in TEXT_TYPES or data_type == "USER-DEFINED":
            return self._profile_text(db, qualified)

        return None

    def _profile_boolean(self, db: Session, qualified: str) -> ColumnProfile | None:
        table_ref, col_ref = qualified.rsplit(".", 1)
        rows = db.execute(
            text(
                f"SELECT DISTINCT {col_ref} AS value "
                f"FROM {table_ref} "
                f"WHERE {col_ref} IS NOT NULL"
            )
        ).fetchall()
        values = sorted({self._serialize_value(row[0]) for row in rows})
        if not values:
            return None
        return ColumnProfile(kind="boolean", distinct_values=values)

    def _profile_numeric(self, db: Session, qualified: str) -> ColumnProfile | None:
        table_ref, col_ref = qualified.rsplit(".", 1)
        row = db.execute(
            text(
                f"SELECT MIN({col_ref}) AS min_val, MAX({col_ref}) AS max_val "
                f"FROM {table_ref} "
                f"WHERE {col_ref} IS NOT NULL"
            )
        ).mappings().one()
        if row["min_val"] is None:
            return None
        return ColumnProfile(
            kind="numeric",
            min_value=self._serialize_value(row["min_val"]),
            max_value=self._serialize_value(row["max_val"]),
        )

    def _profile_temporal(self, db: Session, qualified: str) -> ColumnProfile | None:
        table_ref, col_ref = qualified.rsplit(".", 1)
        row = db.execute(
            text(
                f"SELECT MIN({col_ref}) AS min_val, MAX({col_ref}) AS max_val "
                f"FROM {table_ref} "
                f"WHERE {col_ref} IS NOT NULL"
            )
        ).mappings().one()
        if row["min_val"] is None:
            return None
        return ColumnProfile(
            kind="temporal",
            min_value=self._serialize_value(row["min_val"]),
            max_value=self._serialize_value(row["max_val"]),
        )

    def _profile_text(self, db: Session, qualified: str) -> ColumnProfile | None:
        table_ref, col_ref = qualified.rsplit(".", 1)

        count_row = db.execute(
            text(
                f"SELECT COUNT(DISTINCT {col_ref}) AS distinct_count "
                f"FROM {table_ref} "
                f"WHERE {col_ref} IS NOT NULL"
            )
        ).mappings().one()
        distinct_count = count_row["distinct_count"]

        if distinct_count == 0:
            return None
        if distinct_count > self._threshold:
            return None

        rows = db.execute(
            text(
                f"SELECT DISTINCT {col_ref} AS value "
                f"FROM {table_ref} "
                f"WHERE {col_ref} IS NOT NULL "
                f"ORDER BY 1 "
                f"LIMIT :limit"
            ),
            {"limit": self._threshold},
        ).fetchall()

        values = [self._serialize_value(row[0]) for row in rows]
        return ColumnProfile(kind="categorical", distinct_values=values)

    def _validate_identifier(self, name: str) -> None:
        if not IDENTIFIER_PATTERN.match(name):
            raise ValueError(f"Invalid SQL identifier: {name}")

    def _serialize_value(self, value: object) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, Decimal):
            return format(value, "f").rstrip("0").rstrip(".") or "0"
        if isinstance(value, bool):
            return str(value).lower()
        return str(value)
