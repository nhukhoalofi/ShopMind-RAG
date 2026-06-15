from __future__ import annotations

from backend.app.config import settings
from backend.app.rag.generator import GroqGenerator
from backend.app.rag.guardrails import FALLBACK_MESSAGE, should_fallback
from backend.app.rag.prompt_builder import PromptBuilder
from backend.app.rag.retriever import (
    QdrantRetriever,
    RetrievedChunk,
    get_retriever,
)
from backend.app.schemas.chat_schema import ChatResponse, SourceItem


class ChatService:
    def __init__(self, retriever: QdrantRetriever | None = None) -> None:
        self.retriever = retriever or get_retriever()
        self.prompt_builder = PromptBuilder()
        self._generator: GroqGenerator | None = None

    @property
    def generator(self) -> GroqGenerator:
        if self._generator is None:
            self._generator = GroqGenerator()
        return self._generator

    @staticmethod
    def _build_sources(chunks: list[RetrievedChunk]) -> list[SourceItem]:
        return [
            SourceItem(
                rank=index,
                score=round(chunk.score, 4),
                chunk_id=chunk.chunk_id or None,
                document_id=chunk.document_id or None,
                document_type=chunk.document_type or None,
                category=chunk.category or None,
                source=chunk.source or None,
                title=chunk.title or None,
            )
            for index, chunk in enumerate(chunks, start=1)
        ]

    def answer(self, message: str) -> ChatResponse:
        raw_chunks = self.retriever.retrieve(message, top_k=settings.top_k)
        best_score = raw_chunks[0].score if raw_chunks else 0.0
        relevant_chunks = self.retriever.filter_relevant_chunks(raw_chunks)

        if should_fallback(relevant_chunks):
            return ChatResponse(
                answer=FALLBACK_MESSAGE,
                best_score=best_score,
                sources=[],
                fallback=True,
            )

        messages = self.prompt_builder.build_messages(message, relevant_chunks)
        answer = self.generator.generate(messages)
        return ChatResponse(
            answer=answer,
            best_score=best_score,
            sources=self._build_sources(relevant_chunks),
            fallback=False,
        )
