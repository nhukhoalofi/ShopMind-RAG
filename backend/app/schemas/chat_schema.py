from __future__ import annotations

from pydantic import BaseModel, field_validator


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        message = value.strip()
        if not message:
            raise ValueError("Message must not be empty.")
        return message


class SourceItem(BaseModel):
    rank: int
    score: float
    chunk_id: str | None = None
    document_id: str | None = None
    document_type: str | None = None
    category: str | None = None
    source: str | None = None
    title: str | None = None


class ChatResponse(BaseModel):
    answer: str
    best_score: float
    sources: list[SourceItem]
    fallback: bool
