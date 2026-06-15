from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.v1.chat_routes import get_chat_service
from backend.app.schemas.evaluation_schema import (
    EvaluationQuickTestRequest,
    EvaluationQuickTestResponse,
)
from backend.app.services.chat_service import ChatService
from backend.app.services.evaluation_service import EvaluationService


router = APIRouter()


@router.post("/quick-test", response_model=EvaluationQuickTestResponse)
def quick_test(
    request: EvaluationQuickTestRequest,
    chat_service: ChatService = Depends(get_chat_service),
) -> EvaluationQuickTestResponse:
    try:
        return EvaluationService(chat_service).quick_test(request.queries)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to run the evaluation quick test.",
        ) from exc
