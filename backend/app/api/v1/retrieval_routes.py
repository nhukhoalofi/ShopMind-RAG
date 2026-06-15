from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.app.rag.retriever import get_retriever
from backend.app.schemas.retrieval_schema import (
    RetrievalResultItem,
    RetrievalSearchRequest,
    RetrievalSearchResponse,
)


router = APIRouter()
TEXT_PREVIEW_CHARS = 500


@router.post("/search", response_model=RetrievalSearchResponse)
def retrieval_search(
    request: RetrievalSearchRequest,
) -> RetrievalSearchResponse:
    try:
        chunks = get_retriever().retrieve(request.query, request.top_k)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to retrieve results from Qdrant.",
        ) from exc

    results = [
        RetrievalResultItem(
            rank=index,
            score=round(chunk.score, 4),
            chunk_id=chunk.chunk_id or None,
            document_id=chunk.document_id or None,
            document_type=chunk.document_type or None,
            category=chunk.category or None,
            source=chunk.source or None,
            title=chunk.title or None,
            text_preview=chunk.text[:TEXT_PREVIEW_CHARS],
        )
        for index, chunk in enumerate(chunks, start=1)
    ]
    return RetrievalSearchResponse(query=request.query, results=results)
