"""
scripts/build_index.py

Build Qdrant vector index from data/processed/chunks.jsonl.

Input:
- data/processed/chunks.jsonl

Output:
- Qdrant collection: shopmind_chunks

Run:
python scripts/build_index.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Iterable

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from tqdm import tqdm


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CHUNKS_PATH = PROJECT_ROOT / "data" / "processed" / "chunks.jsonl"

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "shopmind_chunks"

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
BATCH_SIZE = 64


def load_chunks() -> List[Dict[str, Any]]:
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(f"Missing chunks file: {CHUNKS_PATH}")

    chunks: List[Dict[str, Any]] = []

    with CHUNKS_PATH.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON at line {line_number} in {CHUNKS_PATH}"
                ) from exc

            text = str(item.get("text", "")).strip()

            if not text:
                continue

            chunks.append(item)

    if not chunks:
        raise RuntimeError("No valid chunks found in chunks.jsonl.")

    return chunks


def batch_items(
    items: List[Dict[str, Any]],
    batch_size: int,
) -> Iterable[List[Dict[str, Any]]]:
    for start in range(0, len(items), batch_size):
        yield items[start : start + batch_size]


def recreate_collection(
    client: QdrantClient,
    vector_size: int,
) -> None:
    existing_collections = {
        collection.name
        for collection in client.get_collections().collections
    }

    if COLLECTION_NAME in existing_collections:
        print(f"[INFO] Deleting existing collection: {COLLECTION_NAME}")
        client.delete_collection(collection_name=COLLECTION_NAME)

    print(f"[INFO] Creating collection: {COLLECTION_NAME}")

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )


def build_payload(chunk: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "chunk_id": chunk.get("chunk_id"),
        "document_id": chunk.get("document_id"),
        "document_type": chunk.get("document_type"),
        "source": chunk.get("source"),
        "category": chunk.get("category"),
        "language": chunk.get("language"),
        "title": chunk.get("title"),
        "text": chunk.get("text"),
        "metadata": chunk.get("metadata", {}),
    }


def main() -> None:
    print("Loading chunks...")
    chunks = load_chunks()
    print(f"Total chunks: {len(chunks)}")

    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    print("The first run may take a while because the model needs to be downloaded.")
    embedding_model = TextEmbedding(model_name=EMBEDDING_MODEL)

    print("Detecting vector size...")
    sample_text = chunks[0]["text"]
    sample_vector = list(embedding_model.embed([sample_text]))[0]
    vector_size = len(sample_vector)
    print(f"Vector size: {vector_size}")

    print(f"Connecting to Qdrant: {QDRANT_URL}")
    client = QdrantClient(url=QDRANT_URL)

    recreate_collection(
        client=client,
        vector_size=vector_size,
    )

    total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE
    point_id = 0

    for batch in tqdm(
        batch_items(chunks, BATCH_SIZE),
        total=total_batches,
        desc="Indexing chunks",
    ):
        texts = [str(item["text"]) for item in batch]
        vectors = list(embedding_model.embed(texts))

        points: List[PointStruct] = []

        for chunk, vector in zip(batch, vectors):
            if hasattr(vector, "tolist"):
                vector = vector.tolist()

            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=build_payload(chunk),
                )
            )

            point_id += 1

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

    print()
    print("[DONE] Qdrant index built successfully.")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Indexed points: {point_id}")
    print(f"Dashboard: {QDRANT_URL}/dashboard")


if __name__ == "__main__":
    main()