from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from backend.app.schemas.document_schema import (
    CategoryItem,
    CategoryListResponse,
    DocumentItem,
    DocumentListResponse,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOCUMENTS_PATH = PROJECT_ROOT / "data" / "processed" / "documents.jsonl"


class DocumentService:
    def __init__(self, path: Path = DOCUMENTS_PATH) -> None:
        self.path = path
        self._documents = self._load_documents()

    def _load_documents(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            raise RuntimeError(f"Documents file not found: {self.path}")

        documents: list[dict[str, Any]] = []
        try:
            with self.path.open("r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    if not line.strip():
                        continue
                    try:
                        document = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise RuntimeError(
                            f"Invalid JSON in {self.path} at line {line_number}."
                        ) from exc
                    if document.get("document_id"):
                        documents.append(document)
        except OSError as exc:
            raise RuntimeError(
                f"Unable to read documents file: {self.path}"
            ) from exc

        return documents

    def list_documents(
        self,
        document_type: str | None = None,
        category: str | None = None,
        limit: int = 50,
    ) -> DocumentListResponse:
        type_filter = document_type.casefold() if document_type else None
        category_filter = category.casefold() if category else None
        items: list[DocumentItem] = []

        for document in self._documents:
            if type_filter and (
                str(document.get("document_type") or "").casefold()
                != type_filter
            ):
                continue
            if category_filter and (
                str(document.get("category") or "").casefold()
                != category_filter
            ):
                continue

            items.append(
                DocumentItem(
                    document_id=str(document["document_id"]),
                    document_type=document.get("document_type"),
                    category=document.get("category"),
                    source=document.get("source"),
                    title=document.get("title"),
                )
            )
            if len(items) >= limit:
                break

        return DocumentListResponse(items=items, count=len(items))

    def list_categories(self) -> CategoryListResponse:
        counts = Counter(
            str(document.get("category")).strip()
            for document in self._documents
            if document.get("category")
        )
        categories = [
            CategoryItem(name=name, document_count=count)
            for name, count in sorted(counts.items())
        ]
        return CategoryListResponse(categories=categories)
