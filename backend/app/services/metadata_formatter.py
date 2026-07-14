"""Format database metadata as text for LLM prompts."""

from app.schemas.metadata import ColumnMetadata, ColumnProfile, DatabaseMetadata, TableMetadata


def format_metadata_for_prompt(tables: list[TableMetadata], schema_name: str) -> str:
    """Render selected table metadata as plain text."""
    lines: list[str] = [f"Schema: {schema_name}", ""]

    for table in tables:
        lines.append(f"Table: {table.name}")

        if table.primary_keys:
            lines.append(f"  Primary key: {', '.join(table.primary_keys)}")

        if table.foreign_keys:
            lines.append("  Foreign keys:")
            for fk in table.foreign_keys:
                lines.append(
                    f"    - {fk.column} -> {fk.references_table}.{fk.references_column}"
                )

        lines.append("  Columns:")
        for col in table.columns:
            lines.append(_format_column(col))
        lines.append("")

    return "\n".join(lines).strip()


def format_subset_metadata(
    metadata: DatabaseMetadata,
    tables: list[TableMetadata],
) -> str:
    return format_metadata_for_prompt(tables, metadata.schema_name)


def _format_column(col: ColumnMetadata) -> str:
    parts = [f"    - {col.name} ({col.data_type})"]

    flags: list[str] = []
    if col.is_primary_key:
        flags.append("PK")
    if col.foreign_key:
        flags.append(
            f"FK->{col.foreign_key.references_table}.{col.foreign_key.references_column}"
        )
    if col.is_nullable:
        flags.append("nullable")
    if flags:
        parts.append(f"[{', '.join(flags)}]")

    if col.profile:
        parts.append(_format_profile(col.profile))

    return " ".join(parts)


def _format_profile(profile: ColumnProfile) -> str:
    if profile.kind == "categorical" and profile.distinct_values:
        values = ", ".join(profile.distinct_values)
        return f"values=[{values}]"
    if profile.kind == "boolean" and profile.distinct_values:
        values = ", ".join(profile.distinct_values)
        return f"values=[{values}]"
    if profile.kind == "numeric" and profile.min_value is not None:
        return f"range={profile.min_value} to {profile.max_value}"
    if profile.kind == "temporal" and profile.min_value is not None:
        return f"range={profile.min_value} to {profile.max_value}"
    return ""
