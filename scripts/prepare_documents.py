"""
scripts/prepare_documents.py

Convert cleaned raw data into RAG-ready documents and chunks.

Input:
- data/raw/faq.csv
- data/raw/products.csv
- data/raw/policies/*.md

Output:
- data/processed/documents.jsonl
- data/processed/chunks.jsonl

Note:
- FAQ, policies, and product descriptions are used for vector search.
- Orders, returns, and shipping records should be handled later by database tools.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

FAQ_PATH = RAW_DIR / "faq.csv"
PRODUCTS_PATH = RAW_DIR / "products.csv"
POLICIES_DIR = RAW_DIR / "policies"

DOCUMENTS_PATH = PROCESSED_DIR / "documents.jsonl"
CHUNKS_PATH = PROCESSED_DIR / "chunks.jsonl"


CHUNK_SIZE = 900
CHUNK_OVERLAP = 150


def ensure_dirs() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def clean_text(text: Any) -> str:
    if text is None or pd.isna(text):
        return ""

    text = str(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def detect_column(df: pd.DataFrame, candidates: List[str]) -> str | None:
    lower_map = {col.lower(): col for col in df.columns}

    for candidate in candidates:
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]

    return None


def build_faq_documents() -> List[Dict[str, Any]]:
    if not FAQ_PATH.exists():
        print(f"[SKIP] Missing FAQ file: {FAQ_PATH}")
        return []

    df = pd.read_csv(FAQ_PATH)

    question_col = detect_column(
        df,
        ["question", "query", "instruction", "customer_question"],
    )
    answer_col = detect_column(
        df,
        ["answer", "response", "output", "agent_answer"],
    )
    category_col = detect_column(
        df,
        ["category", "label", "intent"],
    )
    source_col = detect_column(
        df,
        ["source", "url", "file"],
    )
    language_col = detect_column(
        df,
        ["language", "lang"],
    )

    if question_col is None or answer_col is None:
        raise ValueError(
            f"faq.csv must contain question and answer columns. "
            f"Current columns: {list(df.columns)}"
        )

    documents = []

    for idx, row in df.iterrows():
        question = clean_text(row.get(question_col))
        answer = clean_text(row.get(answer_col))

        if not question or not answer:
            continue

        category = (
            clean_text(row.get(category_col))
            if category_col
            else "general"
        )
        source = (
            clean_text(row.get(source_col))
            if source_col
            else "faq.csv"
        )
        language = (
            clean_text(row.get(language_col))
            if language_col
            else "en"
        )

        document_id = f"faq_{idx + 1:06d}"

        text = (
            f"Question: {question}\n"
            f"Answer: {answer}\n"
            f"Category: {category}"
        )

        documents.append(
            {
                "document_id": document_id,
                "document_type": "faq",
                "source": source or "faq.csv",
                "category": category or "general",
                "language": language or "en",
                "title": question[:120],
                "text": text,
                "metadata": {
                    "row_index": int(idx),
                    "question": question,
                },
            }
        )

    print(f"[OK] FAQ documents: {len(documents)}")
    return documents


def build_policy_documents() -> List[Dict[str, Any]]:
    if not POLICIES_DIR.exists():
        print(f"[SKIP] Missing policies folder: {POLICIES_DIR}")
        return []

    documents = []

    policy_files = sorted(POLICIES_DIR.glob("*.md"))

    for idx, path in enumerate(policy_files, start=1):
        text = clean_text(path.read_text(encoding="utf-8"))

        if not text:
            continue

        category = path.stem.replace("_policy", "").replace("-", "_")

        document_id = f"policy_{idx:06d}"

        documents.append(
            {
                "document_id": document_id,
                "document_type": "policy",
                "source": f"policies/{path.name}",
                "category": category,
                "language": "en",
                "title": path.stem.replace("_", " ").title(),
                "text": text,
                "metadata": {
                    "file_name": path.name,
                },
            }
        )

    print(f"[OK] Policy documents: {len(documents)}")
    return documents


def build_product_documents() -> List[Dict[str, Any]]:
    if not PRODUCTS_PATH.exists():
        print(f"[SKIP] Missing products file: {PRODUCTS_PATH}")
        return []

    df = pd.read_csv(PRODUCTS_PATH)

    product_id_col = detect_column(
        df,
        ["product_id", "id", "sku", "product_code"],
    )
    name_col = detect_column(
        df,
        ["name", "product_name", "title"],
    )
    category_col = detect_column(
        df,
        ["category", "product_category"],
    )
    brand_col = detect_column(
        df,
        ["brand", "manufacturer"],
    )
    price_col = detect_column(
        df,
        ["price", "sale_price", "list_price"],
    )
    description_col = detect_column(
        df,
        ["description", "product_description", "details"],
    )
    warranty_col = detect_column(
        df,
        ["warranty_months", "warranty", "warranty_period"],
    )
    stock_col = detect_column(
        df,
        ["stock_status", "availability", "in_stock"],
    )

    if name_col is None:
        raise ValueError(
            f"products.csv must contain product name/title column. "
            f"Current columns: {list(df.columns)}"
        )

    documents = []

    for idx, row in df.iterrows():
        product_id = (
            clean_text(row.get(product_id_col))
            if product_id_col
            else f"P{idx + 1:06d}"
        )
        name = clean_text(row.get(name_col))
        category = (
            clean_text(row.get(category_col))
            if category_col
            else "product"
        )
        brand = (
            clean_text(row.get(brand_col))
            if brand_col
            else ""
        )
        price = (
            clean_text(row.get(price_col))
            if price_col
            else ""
        )
        description = (
            clean_text(row.get(description_col))
            if description_col
            else ""
        )
        warranty = (
            clean_text(row.get(warranty_col))
            if warranty_col
            else ""
        )
        stock = (
            clean_text(row.get(stock_col))
            if stock_col
            else ""
        )

        if not name:
            continue

        text_parts = [
            f"Product ID: {product_id}",
            f"Product name: {name}",
            f"Category: {category}",
        ]

        if brand:
            text_parts.append(f"Brand: {brand}")
        if price:
            text_parts.append(f"Price: {price}")
        if warranty:
            text_parts.append(f"Warranty: {warranty}")
        if stock:
            text_parts.append(f"Stock status: {stock}")
        if description:
            text_parts.append(f"Description: {description}")

        text = "\n".join(text_parts)

        document_id = f"product_{idx + 1:06d}"

        documents.append(
            {
                "document_id": document_id,
                "document_type": "product",
                "source": "products.csv",
                "category": category or "product",
                "language": "en",
                "title": name[:120],
                "text": text,
                "metadata": {
                    "row_index": int(idx),
                    "product_id": product_id,
                    "product_name": name,
                },
            }
        )

    print(f"[OK] Product documents: {len(documents)}")
    return documents


def split_text_into_chunks(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    text = clean_text(text)

    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - chunk_overlap

        if start < 0:
            start = 0

    return chunks


def build_chunks(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    chunks = []

    for doc in documents:
        text_chunks = split_text_into_chunks(
            text=doc["text"],
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

        for chunk_idx, chunk_text in enumerate(text_chunks):
            chunk_id = f"{doc['document_id']}_chunk_{chunk_idx:03d}"

            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "document_id": doc["document_id"],
                    "document_type": doc["document_type"],
                    "source": doc["source"],
                    "category": doc["category"],
                    "language": doc["language"],
                    "title": doc["title"],
                    "text": chunk_text,
                    "metadata": doc.get("metadata", {}),
                }
            )

    print(f"[OK] Chunks: {len(chunks)}")
    return chunks


def main() -> None:
    ensure_dirs()

    print("Preparing RAG documents...")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Raw data dir: {RAW_DIR}")
    print(f"Processed dir: {PROCESSED_DIR}")
    print()

    documents = []
    documents.extend(build_faq_documents())
    documents.extend(build_policy_documents())
    documents.extend(build_product_documents())

    if not documents:
        raise RuntimeError("No documents were created. Please check data/raw files.")

    chunks = build_chunks(documents)

    write_jsonl(DOCUMENTS_PATH, documents)
    write_jsonl(CHUNKS_PATH, chunks)

    print()
    print("[DONE] RAG preparation completed.")
    print(f"Documents saved to: {DOCUMENTS_PATH}")
    print(f"Chunks saved to: {CHUNKS_PATH}")
    print(f"Total documents: {len(documents)}")
    print(f"Total chunks: {len(chunks)}")


if __name__ == "__main__":
    main()