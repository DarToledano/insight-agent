"""Debug endpoint for SQL generation only (no validation or execution)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.generate_sql import GenerateSqlRequest, GenerateSqlResponse
from app.services.metadata_cache import get_metadata_cache
from app.services.metadata_formatter import format_subset_metadata
from app.services.metadata_selector import MetadataSelector
from app.services.sql_generator import SQLGenerator

router = APIRouter(tags=["debug"])


def get_sql_generator() -> SQLGenerator:
    return SQLGenerator()


def get_metadata_selector() -> MetadataSelector:
    return MetadataSelector()


@router.post(
    "/generate-sql",
    response_model=GenerateSqlResponse,
    summary="[Debug] Generate SQL only",
    description=(
        "Development/debug endpoint. Generates SQL from a question but does "
        "not validate or execute it. Use POST /ask for the full pipeline."
    ),
)
async def generate_sql(
    body: GenerateSqlRequest,
    db: Session = Depends(get_db),
    sql_generator: SQLGenerator = Depends(get_sql_generator),
    metadata_selector: MetadataSelector = Depends(get_metadata_selector),
) -> GenerateSqlResponse:
    _ = db  # SQL generation uses metadata cache only, not live DB queries
    try:
        metadata = get_metadata_cache().get_metadata()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    relevant_tables = metadata_selector.select_relevant_tables(
        body.question, metadata
    )
    metadata_text = format_subset_metadata(metadata, relevant_tables)

    try:
        sql = sql_generator.generate(body.question, metadata_text)
    except ValueError as exc:
        detail = str(exc)
        if "OPENAI_API_KEY" in detail:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=detail,
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return GenerateSqlResponse(sql=sql)
