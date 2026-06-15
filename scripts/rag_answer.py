"""
scripts/rag_answer.py

RAG answer generation:
User query -> Qdrant retrieval -> prompt construction -> Groq LLM answer.

Run:
python scripts/rag_answer.py
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastembed import TextEmbedding
from groq import Groq
from qdrant_client import QdrantClient


QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "shopmind_chunks"

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

TOP_K = 5
MIN_SCORE = 0.68
MAX_CONTEXT_CHARS = 4500


TEST_QUERIES = [
    "How can I return an item?",
    "What payment methods are accepted?",
    "How long does shipping take?",
    "Can I cancel my order?",
    "What happens if I receive a damaged product?",
    "Do you offer warranty for products?",
    "I forgot my account password. What should I do?",
    "Do you have a physical store in Japan?",
]


@dataclass
class RetrievedChunk:
    score: float
    chunk_id: str
    document_type: str
    category: str
    source: str
    title: str
    text: str


def to_list(vector):
    if hasattr(vector, "tolist"):
        return vector.tolist()
    return vector


def retrieve(
    query: str,
    embedder: TextEmbedding,
    qdrant_client: QdrantClient,
    top_k: int = TOP_K,
) -> List[RetrievedChunk]:
    query_vector = list(embedder.embed([query]))[0]

    response = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=to_list(query_vector),
        limit=top_k,
        with_payload=True,
    )
    results = response.points

    chunks: List[RetrievedChunk] = []

    for result in results:
        payload = result.payload or {}

        chunks.append(
            RetrievedChunk(
                score=float(result.score),
                chunk_id=str(payload.get("chunk_id", "")),
                document_type=str(payload.get("document_type", "")),
                category=str(payload.get("category", "")),
                source=str(payload.get("source", "")),
                title=str(payload.get("title", "")),
                text=str(payload.get("text", "")),
            )
        )

    return chunks

def filter_relevant_chunks(
    chunks: List[RetrievedChunk],
    min_score: float = MIN_SCORE,
    max_score_gap: float = 0.12,
) -> List[RetrievedChunk]:
    """
    Keep only chunks that are likely relevant.

    Rules:
    - Remove chunks below min_score.
    - Remove chunks too far from the best score.
    """
    if not chunks:
        return []

    best_score = chunks[0].score

    filtered = [
        chunk
        for chunk in chunks
        if chunk.score >= min_score and (best_score - chunk.score) <= max_score_gap
    ]

    return filtered
def build_context(chunks: List[RetrievedChunk]) -> str:
    context_blocks = []
    total_chars = 0

    for idx, chunk in enumerate(chunks, start=1):
        block = (
            f"[Source {idx}]\n"
            f"Score: {chunk.score:.4f}\n"
            f"Type: {chunk.document_type}\n"
            f"Category: {chunk.category}\n"
            f"Source: {chunk.source}\n"
            f"Title: {chunk.title}\n"
            f"Content:\n{chunk.text}\n"
        )

        if total_chars + len(block) > MAX_CONTEXT_CHARS:
            break

        context_blocks.append(block)
        total_chars += len(block)

    return "\n\n".join(context_blocks)


def build_sources(chunks: List[RetrievedChunk]) -> List[Dict[str, Any]]:
    sources = []

    for idx, chunk in enumerate(chunks, start=1):
        sources.append(
            {
                "rank": idx,
                "score": round(chunk.score, 4),
                "chunk_id": chunk.chunk_id,
                "document_type": chunk.document_type,
                "category": chunk.category,
                "source": chunk.source,
                "title": chunk.title,
            }
        )

    return sources


def build_prompt(query: str, chunks: List[RetrievedChunk]) -> List[Dict[str, str]]:
    context = build_context(chunks)

    system_prompt = """
You are ShopMind, an e-commerce customer support assistant.

You must follow these rules:
1. Answer only using the provided context.
2. If the context is not enough, say you do not have enough verified information.
3. Do not invent policies, prices, warranty terms, shipping times, or order status.
4. Be concise, helpful, and professional.
5. If multiple sources are relevant, synthesize them carefully.
6. At the end of the answer, cite the actual source filenames or titles, not generic labels like "Source 1".
""".strip()

    user_prompt = f"""
Context:
{context}

Customer question:
{query}

Write the answer:
""".strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def generate_answer(
    query: str,
    chunks: List[RetrievedChunk],
    groq_client: Groq,
    model: str,
) -> str:
    if not chunks:
        return (
            "I do not have enough verified information to answer this question."
        )

    best_score = chunks[0].score

    if best_score < MIN_SCORE:
        return (
            "I do not have enough verified information in the ShopMind knowledge base "
            "to answer this question. Please contact customer support for confirmation."
        )

    messages = build_prompt(query, chunks)

    response = groq_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.1,
        max_tokens=500,
    )

    return response.choices[0].message.content.strip()


def answer_query(
    query: str,
    embedder: TextEmbedding,
    qdrant_client: QdrantClient,
    groq_client: Groq,
    model: str,
) -> Dict[str, Any]:
    retrieved_chunks = retrieve(
        query=query,
        embedder=embedder,
        qdrant_client=qdrant_client,
        top_k=TOP_K,
    )

    relevant_chunks = filter_relevant_chunks(retrieved_chunks)

    answer = generate_answer(
        query=query,
        chunks=relevant_chunks,
        groq_client=groq_client,
        model=model,
    )

    return {
        "query": query,
        "answer": answer,
        "best_score": retrieved_chunks[0].score if retrieved_chunks else 0.0,
        "sources": build_sources(relevant_chunks),
        "retrieved_sources": build_sources(retrieved_chunks),
    }

def print_result(result: Dict[str, Any]) -> None:
    print("\n" + "=" * 100)
    print(f"QUERY: {result['query']}")
    print("=" * 100)

    print("\nANSWER:")
    print(result["answer"])

    print("\nBEST SCORE:")
    print(round(result["best_score"], 4))

    print("\nSOURCES:")
    for source in result["sources"]:
        print(
            f"- rank={source['rank']} | "
            f"score={source['score']} | "
            f"type={source['document_type']} | "
            f"category={source['category']} | "
            f"source={source['source']} | "
            f"title={source['title']}"
        )


def main() -> None:
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    if not api_key:
        raise RuntimeError(
            "Missing GROQ_API_KEY. Please add it to your .env file."
        )

    print("Connecting to Qdrant...")
    qdrant_client = QdrantClient(url=QDRANT_URL)

    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    embedder = TextEmbedding(model_name=EMBEDDING_MODEL)

    print(f"Using Groq model: {model}")
    groq_client = Groq(api_key=api_key)

    for query in TEST_QUERIES:
        result = answer_query(
            query=query,
            embedder=embedder,
            qdrant_client=qdrant_client,
            groq_client=groq_client,
            model=model,
        )

        print_result(result)


if __name__ == "__main__":
    main()
