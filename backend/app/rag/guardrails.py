from __future__ import annotations

from backend.app.config import settings
from backend.app.rag.retriever import RetrievedChunk


FALLBACK_MESSAGE = (
    "I do not have enough verified information in the ShopMind knowledge "
    "base to answer this question. Please contact customer support for "
    "confirmation."
)


def should_fallback(chunks: list[RetrievedChunk]) -> bool:
    return not chunks or chunks[0].score < settings.min_score
