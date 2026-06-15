from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.schemas.product_schema import (
    ProductDetail,
    ProductListResponse,
)
from backend.app.services.product_service import ProductService


router = APIRouter()


@lru_cache
def get_product_service() -> ProductService:
    try:
        return ProductService()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get("/search", response_model=ProductListResponse)
def search_products(
    q: str | None = Query(default=None),
    category: str | None = Query(default=None),
    brand: str | None = Query(default=None),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    limit: int = Query(default=20, ge=1, le=200),
    service: ProductService = Depends(get_product_service),
) -> ProductListResponse:
    try:
        return service.search(
            query=q.strip() if q else None,
            category=category.strip() if category else None,
            brand=brand.strip() if brand else None,
            min_price=min_price,
            max_price=max_price,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc


@router.get("/{product_id}", response_model=ProductDetail)
def get_product(
    product_id: str,
    service: ProductService = Depends(get_product_service),
) -> ProductDetail:
    product = service.get_product(product_id.strip())
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product
