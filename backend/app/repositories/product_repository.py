from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PRODUCTS_PATH = PROJECT_ROOT / "data" / "raw" / "products.csv"


def _optional_float(value: str | None) -> float | None:
    if value is None or not value.strip():
        return None
    return float(value)


def _optional_int(value: str | None) -> int | None:
    if value is None or not value.strip():
        return None
    return int(float(value))


@dataclass(frozen=True)
class ProductRecord:
    product_id: str
    name: str
    category: str | None
    brand: str | None
    price: float | None
    stock: int | None
    description: str | None
    warranty: str | None
    avg_discount_rate: float | None
    transaction_count: int | None
    total_units_sold: int | None
    regions: list[str]
    source: str | None


class ProductRepository:
    def __init__(self, path: Path = PRODUCTS_PATH) -> None:
        self.path = path
        self._products = self._load_products()

    def _load_products(self) -> list[ProductRecord]:
        if not self.path.exists():
            raise RuntimeError(f"Products file not found: {self.path}")

        products: list[ProductRecord] = []
        try:
            with self.path.open("r", encoding="utf-8-sig", newline="") as file:
                for row in csv.DictReader(file):
                    product_id = (row.get("product_id") or "").strip()
                    name = (row.get("name") or "").strip()
                    if not product_id or not name:
                        continue

                    regions = [
                        region.strip()
                        for region in (row.get("regions") or "").split("|")
                        if region.strip()
                    ]
                    products.append(
                        ProductRecord(
                            product_id=product_id,
                            name=name,
                            category=(row.get("category") or "").strip() or None,
                            brand=(row.get("brand") or "").strip() or None,
                            price=_optional_float(
                                row.get("price") or row.get("unit_price")
                            ),
                            stock=_optional_int(row.get("stock")),
                            description=(
                                (row.get("description") or "").strip() or None
                            ),
                            warranty=(row.get("warranty") or "").strip() or None,
                            avg_discount_rate=_optional_float(
                                row.get("avg_discount_rate")
                            ),
                            transaction_count=_optional_int(
                                row.get("transaction_count")
                            ),
                            total_units_sold=_optional_int(
                                row.get("total_units_sold")
                            ),
                            regions=regions,
                            source=(row.get("source") or "").strip() or None,
                        )
                    )
        except (OSError, ValueError, csv.Error) as exc:
            raise RuntimeError(
                f"Unable to read products file: {self.path}"
            ) from exc

        return products

    def search(
        self,
        query: str | None = None,
        category: str | None = None,
        brand: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        limit: int = 20,
    ) -> list[ProductRecord]:
        query_value = query.casefold() if query else None
        category_value = category.casefold() if category else None
        brand_value = brand.casefold() if brand else None
        results: list[ProductRecord] = []

        for product in self._products:
            if query_value and query_value not in (
                f"{product.product_id} {product.name}".casefold()
            ):
                continue
            if category_value and (product.category or "").casefold() != category_value:
                continue
            if brand_value and (product.brand or "").casefold() != brand_value:
                continue
            if min_price is not None and (
                product.price is None or product.price < min_price
            ):
                continue
            if max_price is not None and (
                product.price is None or product.price > max_price
            ):
                continue

            results.append(product)
            if len(results) >= limit:
                break

        return results

    def get_by_id(self, product_id: str) -> ProductRecord | None:
        target = product_id.casefold()
        return next(
            (
                product
                for product in self._products
                if product.product_id.casefold() == target
            ),
            None,
        )
