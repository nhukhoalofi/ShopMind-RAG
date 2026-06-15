from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class RetrievalSearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=100)

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        query = value.strip()
        if not query:
            raise ValueError("Query must not be empty.")
        return query


class RetrievalResultItem(BaseModel):
    rank: int
    score: float
    chunk_id: str | None = None
    document_id: str | None = None
    document_type: str | None = None
    category: str | None = None
    source: str | None = None
    title: str | None = None
    text_preview: str


class RetrievalSearchResponse(BaseModel):
    query: str
    results: list[RetrievalResultItem]
