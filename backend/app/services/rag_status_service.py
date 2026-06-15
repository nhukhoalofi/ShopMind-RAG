from __future__ import annotations

from pydantic import BaseModel
from qdrant_client import QdrantClient

from backend.app.config import settings


class RagStatusResponse(BaseModel):
    qdrant_url: str
    collection: str
    collection_exists: bool
    embedding_model: str
    top_k: int
    min_score: float
    max_score_gap: float


class RagStatusService:
    def __init__(self) -> None:
        self.client = QdrantClient(url=settings.qdrant_url)

    def get_status(self) -> RagStatusResponse:
        try:
            collections = self.client.get_collections().collections
        except Exception as exc:
            raise RuntimeError(
                f"Unable to connect to Qdrant at {settings.qdrant_url}."
            ) from exc

        collection_names = {collection.name for collection in collections}
        return RagStatusResponse(
            qdrant_url=settings.qdrant_url,
            collection=settings.qdrant_collection,
            collection_exists=settings.qdrant_collection in collection_names,
            embedding_model=settings.embedding_model,
            top_k=settings.top_k,
            min_score=settings.min_score,
            max_score_gap=settings.max_score_gap,
        )
