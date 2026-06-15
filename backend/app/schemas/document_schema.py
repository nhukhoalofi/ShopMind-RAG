from __future__ import annotations

from pydantic import BaseModel


class DocumentItem(BaseModel):
    document_id: str
    document_type: str | None = None
    category: str | None = None
    source: str | None = None
    title: str | None = None


class DocumentListResponse(BaseModel):
    items: list[DocumentItem]
    count: int


class CategoryItem(BaseModel):
    name: str
    document_count: int


class CategoryListResponse(BaseModel):
    categories: list[CategoryItem]
