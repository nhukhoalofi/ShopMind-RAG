"""
scripts/test_retrieval.py

Test semantic retrieval from Qdrant.

Run:
python scripts/test_retrieval.py
"""

from __future__ import annotations

from fastembed import TextEmbedding
from qdrant_client import QdrantClient


QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "shopmind_chunks"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

TOP_K = 5


TEST_QUERIES = [
    "How can I return an item?",
    "What payment methods are accepted?",
    "How long does shipping take?",
    "How can I track my order?",
    "Can I cancel my order?",
    "What happens if I receive a damaged product?",
    "Do you offer warranty for products?",
    "I forgot my account password. What should I do?",
]


def to_list(vector):
    if hasattr(vector, "tolist"):
        return vector.tolist()
    return vector


def search(query: str, embedder: TextEmbedding, client: QdrantClient) -> None:
    print("\n" + "=" * 100)
    print(f"QUERY: {query}")
    print("=" * 100)

    query_vector = list(embedder.embed([query]))[0]

    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=to_list(query_vector),
        limit=TOP_K,
        with_payload=True,
    )
    results = response.points

    if not results:
        print("No results found.")
        return

    for rank, result in enumerate(results, start=1):
        payload = result.payload or {}

        print(f"\n--- Result {rank} ---")
        print(f"Score: {result.score:.4f}")
        print(f"Document type: {payload.get('document_type')}")
        print(f"Category: {payload.get('category')}")
        print(f"Source: {payload.get('source')}")
        print(f"Title: {payload.get('title')}")

        text = payload.get("text", "")
        if len(text) > 800:
            text = text[:800] + "..."

        print("Text:")
        print(text)


def main() -> None:
    print("Connecting to Qdrant...")
    client = QdrantClient(url=QDRANT_URL)

    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    embedder = TextEmbedding(model_name=EMBEDDING_MODEL)

    for query in TEST_QUERIES:
        search(query, embedder, client)


if __name__ == "__main__":
    main()
