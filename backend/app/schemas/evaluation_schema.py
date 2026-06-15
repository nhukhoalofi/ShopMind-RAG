from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from backend.app.schemas.chat_schema import SourceItem


class EvaluationQuickTestRequest(BaseModel):
    queries: list[str] = Field(min_length=1, max_length=20)

    @field_validator("queries")
    @classmethod
    def validate_queries(cls, values: list[str]) -> list[str]:
        queries = [value.strip() for value in values]
        if any(not query for query in queries):
            raise ValueError("Queries must not contain empty values.")
        return queries


class EvaluationResultItem(BaseModel):
    query: str
    answer: str
    best_score: float
    fallback: bool
    sources: list[SourceItem]


class EvaluationQuickTestResponse(BaseModel):
    results: list[EvaluationResultItem]
