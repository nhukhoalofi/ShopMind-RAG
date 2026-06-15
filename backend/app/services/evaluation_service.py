from __future__ import annotations

from backend.app.schemas.evaluation_schema import (
    EvaluationQuickTestResponse,
    EvaluationResultItem,
)
from backend.app.services.chat_service import ChatService


class EvaluationService:
    def __init__(self, chat_service: ChatService) -> None:
        self.chat_service = chat_service

    def quick_test(self, queries: list[str]) -> EvaluationQuickTestResponse:
        results: list[EvaluationResultItem] = []
        for query in queries:
            response = self.chat_service.answer(query)
            results.append(
                EvaluationResultItem(
                    query=query,
                    answer=response.answer,
                    best_score=response.best_score,
                    fallback=response.fallback,
                    sources=response.sources,
                )
            )
        return EvaluationQuickTestResponse(results=results)
