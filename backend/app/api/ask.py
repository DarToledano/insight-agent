"""Main InsightAgent question-answering endpoint."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.ask import AskRequest, AskResponse
from app.services.ask_service import AskService
from app.services.exceptions import SQLExecutionError, SQLValidationError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ask"])


def get_ask_service() -> AskService:
    return AskService()


@router.post("/ask", response_model=AskResponse)
async def ask(
    body: AskRequest,
    db: Session = Depends(get_db),
    ask_service: AskService = Depends(get_ask_service),
) -> AskResponse:
    """
    Ask a natural-language business question and receive structured query results.

    This is the main public endpoint of InsightAgent.
    """
    try:
        return ask_service.ask(db, body.question)
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
    except SQLValidationError as exc:
        logger.warning("SQL validation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except SQLExecutionError as exc:
        logger.warning("SQL execution failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        detail = str(exc)
        if "schema" in detail.lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=detail,
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
        ) from exc
