"""Select relevant table metadata for a natural-language question."""

import logging
import re

from app.schemas.metadata import DatabaseMetadata, TableMetadata

logger = logging.getLogger(__name__)

STOP_WORDS = frozenset(
    {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "shall", "can", "need", "dare",
        "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by",
        "from", "as", "into", "through", "during", "before", "after", "above",
        "below", "between", "under", "again", "further", "then", "once", "here",
        "there", "when", "where", "why", "how", "all", "each", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not", "only", "own",
        "same", "so", "than", "too", "very", "just", "and", "but", "if", "or",
        "because", "until", "while", "which", "who", "whom", "this", "that",
        "these", "those", "what", "show", "list", "get", "find", "give", "me",
        "many", "much", "any", "our", "their", "my", "your", "its", "we", "they",
        "it", "he", "she", "i", "you", "last", "first", "top", "highest",
        "lowest", "most", "least", "average", "total", "count", "number",
        "year", "month", "week", "day", "today", "currently", "now",
    }
)


class MetadataSelector:
    """Identify tables relevant to a user question using cached metadata only."""

    def select_relevant_tables(
        self,
        question: str,
        metadata: DatabaseMetadata,
    ) -> list[TableMetadata]:
        tokens = self._tokenize(question)
        if not tokens:
            return metadata.tables

        scores: dict[str, float] = {}

        for table in metadata.tables:
            score = self._score_table(table, tokens)
            if score > 0:
                scores[table.name] = score

        if not scores:
            logger.info("No table matches found; including all tables as fallback")
            return metadata.tables

        max_score = max(scores.values())
        threshold = max_score * 0.5

        selected_names = {
            name for name, score in scores.items() if score >= threshold
        }

        selected_names = self._expand_with_relationships(
            selected_names, metadata
        )

        selected = [t for t in metadata.tables if t.name in selected_names]
        logger.info(
            "Selected %d relevant tables for question: %s",
            len(selected),
            sorted(selected_names),
        )
        return selected

    def _tokenize(self, question: str) -> set[str]:
        words = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", question.lower())
        return {w for w in words if w not in STOP_WORDS and len(w) > 1}

    def _score_table(self, table: TableMetadata, tokens: set[str]) -> float:
        score = 0.0
        table_name = table.name.lower()
        singular = table_name.rstrip("s") if table_name.endswith("s") else table_name

        for token in tokens:
            if token == table_name or token == singular:
                score += 10.0
            elif token in table_name or table_name in token:
                score += 6.0
            elif token in singular or singular in token:
                score += 5.0

            for col in table.columns:
                col_name = col.name.lower()
                if token == col_name:
                    score += 4.0
                elif token in col_name or col_name in token:
                    score += 2.0

                if col.profile and col.profile.distinct_values:
                    for val in col.profile.distinct_values:
                        val_lower = val.lower()
                        if token == val_lower or token in val_lower:
                            score += 3.0

        return score

    def _expand_with_relationships(
        self,
        selected: set[str],
        metadata: DatabaseMetadata,
    ) -> set[str]:
        expanded = set(selected)
        table_map = {t.name: t for t in metadata.tables}

        for name in list(selected):
            table = table_map.get(name)
            if not table:
                continue
            for fk in table.foreign_keys:
                if fk.references_table in table_map:
                    expanded.add(fk.references_table)
            for other in metadata.tables:
                for fk in other.foreign_keys:
                    if fk.references_table == name:
                        expanded.add(other.name)

        return expanded
