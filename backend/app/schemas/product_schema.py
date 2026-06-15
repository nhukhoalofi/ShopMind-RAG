from __future__ import annotations

from pydantic import BaseModel, Field


class ProductItem(BaseModel):
    product_id: str
    name: str
    category: str | None = None
    brand: str | None = None
    price: float | None = None
    stock: int | None = None


class ProductDetail(ProductItem):
    description: str | None = None
    warranty: str | None = None
    avg_discount_rate: float | None = None
    transaction_count: int | None = None
    total_units_sold: int | None = None
    regions: list[str] = Field(default_factory=list)
    source: str | None = None


class ProductListResponse(BaseModel):
    items: list[ProductItem]
    count: int
