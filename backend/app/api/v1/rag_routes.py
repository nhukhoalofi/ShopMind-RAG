from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.services.rag_status_service import (
    RagStatusResponse,
    RagStatusService,
)


router = APIRouter()


@lru_cache
def get_rag_status_service() -> RagStatusService:
    return RagStatusService()


@router.get("/status", response_model=RagStatusResponse)
def rag_status(
    service: RagStatusService = Depends(get_rag_status_service),
) -> RagStatusResponse:
    try:
        return service.get_status()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
