from __future__ import annotations

from backend.app.repositories.product_repository import (
    ProductRecord,
    ProductRepository,
)
from backend.app.schemas.product_schema import (
    ProductDetail,
    ProductItem,
    ProductListResponse,
)


class ProductService:
    def __init__(self, repository: ProductRepository | None = None) -> None:
        self.repository = repository or ProductRepository()

    @staticmethod
    def _to_item(product: ProductRecord) -> ProductItem:
        return ProductItem(
            product_id=product.product_id,
            name=product.name,
            category=product.category,
            brand=product.brand,
            price=product.price,
            stock=product.stock,
        )

    @staticmethod
    def _to_detail(product: ProductRecord) -> ProductDetail:
        return ProductDetail(
            product_id=product.product_id,
            name=product.name,
            category=product.category,
            brand=product.brand,
            price=product.price,
            stock=product.stock,
            description=product.description,
            warranty=product.warranty,
            avg_discount_rate=product.avg_discount_rate,
            transaction_count=product.transaction_count,
            total_units_sold=product.total_units_sold,
            regions=product.regions,
            source=product.source,
        )

    def search(
        self,
        query: str | None = None,
        category: str | None = None,
        brand: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        limit: int = 20,
    ) -> ProductListResponse:
        if (
            min_price is not None
            and max_price is not None
            and min_price > max_price
        ):
            raise ValueError("min_price must be less than or equal to max_price.")

        products = self.repository.search(
            query=query,
            category=category,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            limit=limit,
        )
        items = [self._to_item(product) for product in products]
        return ProductListResponse(items=items, count=len(items))

    def get_product(self, product_id: str) -> ProductDetail | None:
        product = self.repository.get_by_id(product_id)
        return self._to_detail(product) if product else None
