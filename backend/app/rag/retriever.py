from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from fastembed import TextEmbedding
from qdrant_client import QdrantClient

from backend.app.config import settings


@dataclass
class RetrievedChunk:
    score: float
    chunk_id: str
    document_id: str
    document_type: str
    category: str
    source: str
    title: str
    text: str


def _to_list(vector: Any) -> list[float]:
    if hasattr(vector, "tolist"):
        return vector.tolist()
    return list(vector)


class QdrantRetriever:
    def __init__(self) -> None:
        self.embedder = TextEmbedding(model_name=settings.embedding_model)
        self.client = QdrantClient(url=settings.qdrant_url)

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        limit = top_k or settings.top_k
        query_vector = next(iter(self.embedder.embed([query])))
        vector = _to_list(query_vector)

        if hasattr(self.client, "search"):
            results = self.client.search(
                collection_name=settings.qdrant_collection,
                query_vector=vector,
                limit=limit,
                with_payload=True,
            )
        elif hasattr(self.client, "query_points"):
            response = self.client.query_points(
                collection_name=settings.qdrant_collection,
                query=vector,
                limit=limit,
                with_payload=True,
            )
            results = response.points
        else:
            raise RuntimeError(
                "The installed qdrant-client does not provide a supported search API."
            )

        chunks: list[RetrievedChunk] = []
        for result in results:
            payload = result.payload or {}
            chunks.append(
                RetrievedChunk(
                    score=float(result.score),
                    chunk_id=str(payload.get("chunk_id") or ""),
                    document_id=str(payload.get("document_id") or ""),
                    document_type=str(payload.get("document_type") or ""),
                    category=str(payload.get("category") or ""),
                    source=str(payload.get("source") or ""),
                    title=str(payload.get("title") or ""),
                    text=str(payload.get("text") or ""),
                )
            )

        return chunks

    def filter_relevant_chunks(
        self,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        if not chunks:
            return []

        best_score = chunks[0].score
        return [
            chunk
            for chunk in chunks
            if chunk.score >= settings.min_score
            and best_score - chunk.score <= settings.max_score_gap
        ]


@lru_cache
def get_retriever() -> QdrantRetriever:
    return QdrantRetriever()
