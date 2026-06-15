from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.schemas.document_schema import (
    CategoryListResponse,
    DocumentListResponse,
)
from backend.app.services.document_service import DocumentService


router = APIRouter()
categories_router = APIRouter()


@lru_cache
def get_document_service() -> DocumentService:
    try:
        return DocumentService()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get("", response_model=DocumentListResponse)
def list_documents(
    document_type: str | None = Query(default=None),
    category: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    service: DocumentService = Depends(get_document_service),
) -> DocumentListResponse:
    return service.list_documents(
        document_type=document_type.strip() if document_type else None,
        category=category.strip() if category else None,
        limit=limit,
    )


@categories_router.get("/categories", response_model=CategoryListResponse)
def list_categories(
    service: DocumentService = Depends(get_document_service),
) -> CategoryListResponse:
    return service.list_categories()
