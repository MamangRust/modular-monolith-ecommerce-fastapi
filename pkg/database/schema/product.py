"""Row types for the products table. `description`/`brand`/`weight`/`rating`/`slug_product`/`image_product` are nullable in the DDL; `deleted_at` is nullable too. All other columns are `NOT NULL`. Timestamps are formatted `%Y-%m-%d %H:%M:%S.mmm` by the handler (`formatTimestamp`), matching every other domain."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Product:

    product_id: int
    merchant_id: int
    category_id: int
    name: str
    description: str | None
    price: int
    count_in_stock: int
    brand: str | None
    weight: int | None
    rating: float | None
    slug_product: str | None
    image_product: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> Product:
        return cls(
            product_id=row["product_id"],
            merchant_id=row["merchant_id"],
            category_id=row["category_id"],
            name=row["name"],
            description=row.get("description"),
            price=row["price"],
            count_in_stock=row["count_in_stock"],
            brand=row.get("brand"),
            weight=row.get("weight"),
            rating=row.get("rating"),
            slug_product=row.get("slug_product"),
            image_product=row.get("image_product"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class ProductRow:
    """Base projection: Create/Update/GetByID/Trash/Restore RETURNING columns."""

    product_id: int
    merchant_id: int
    category_id: int
    name: str
    description: str | None
    price: int
    count_in_stock: int
    brand: str | None
    weight: int | None
    rating: float | None
    slug_product: str | None
    image_product: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> ProductRow:
        return cls(
            product_id=row["product_id"],
            merchant_id=row["merchant_id"],
            category_id=row["category_id"],
            name=row["name"],
            description=row.get("description"),
            price=row["price"],
            count_in_stock=row["count_in_stock"],
            brand=row.get("brand"),
            weight=row.get("weight"),
            rating=row.get("rating"),
            slug_product=row.get("slug_product"),
            image_product=row.get("image_product"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


# declares a distinct struct per query even though the fields are identical.
CreateProductRow = ProductRow
UpdateProductRow = ProductRow
GetProductByIDRow = ProductRow
TrashProductRow = ProductRow
RestoreProductRow = ProductRow


@dataclass
class GetProductsRow:
    """`GetProducts` (FindAll) projection with window total count."""

    product_id: int
    merchant_id: int
    category_id: int
    name: str
    description: str | None
    price: int
    count_in_stock: int
    brand: str | None
    weight: int | None
    rating: float | None
    slug_product: str | None
    image_product: str | None
    created_at: datetime
    updated_at: datetime
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetProductsRow:
        return cls(
            product_id=row["product_id"],
            merchant_id=row["merchant_id"],
            category_id=row["category_id"],
            name=row["name"],
            description=row.get("description"),
            price=row["price"],
            count_in_stock=row["count_in_stock"],
            brand=row.get("brand"),
            weight=row.get("weight"),
            rating=row.get("rating"),
            slug_product=row.get("slug_product"),
            image_product=row.get("image_product"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            total_count=int(row["total_count"]),
        )


@dataclass
class GetProductsActiveRow:
    """`GetProductsActive`/`...Trashed`: base + `deleted_at` + total."""

    product_id: int
    merchant_id: int
    category_id: int
    name: str
    description: str | None
    price: int
    count_in_stock: int
    brand: str | None
    weight: int | None
    rating: float | None
    slug_product: str | None
    image_product: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetProductsActiveRow:
        return cls(
            product_id=row["product_id"],
            merchant_id=row["merchant_id"],
            category_id=row["category_id"],
            name=row["name"],
            description=row.get("description"),
            price=row["price"],
            count_in_stock=row["count_in_stock"],
            brand=row.get("brand"),
            weight=row.get("weight"),
            rating=row.get("rating"),
            slug_product=row.get("slug_product"),
            image_product=row.get("image_product"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            total_count=int(row["total_count"]),
        )


GetProductsTrashedRow = GetProductsActiveRow


@dataclass
class GetProductsByMerchantRow:
    """`GetProductsByMerchant`/`...ByCategoryName`: base + `category_name` + total."""

    product_id: int
    merchant_id: int
    category_id: int
    name: str
    description: str | None
    price: int
    count_in_stock: int
    brand: str | None
    weight: int | None
    rating: float | None
    slug_product: str | None
    image_product: str | None
    created_at: datetime
    updated_at: datetime
    category_name: str
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetProductsByMerchantRow:
        return cls(
            product_id=row["product_id"],
            merchant_id=row["merchant_id"],
            category_id=row["category_id"],
            name=row["name"],
            description=row.get("description"),
            price=row["price"],
            count_in_stock=row["count_in_stock"],
            brand=row.get("brand"),
            weight=row.get("weight"),
            rating=row.get("rating"),
            slug_product=row.get("slug_product"),
            image_product=row.get("image_product"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            category_name=row["category_name"],
            total_count=int(row["total_count"]),
        )


GetProductsByCategoryNameRow = GetProductsByMerchantRow


@dataclass
class AdjustProductStockRow:
    """`AdjustProductStock`/`UpdateProductCountStock` projection."""

    product_id: int
    count_in_stock: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> AdjustProductStockRow:
        return cls(
            product_id=row["product_id"],
            count_in_stock=row["count_in_stock"],
        )


UpdateProductCountStockRow = AdjustProductStockRow


__all__ = [
    "AdjustProductStockRow",
    "CreateProductRow",
    "GetProductByIDRow",
    "GetProductsActiveRow",
    "GetProductsByCategoryNameRow",
    "GetProductsByMerchantRow",
    "GetProductsRow",
    "GetProductsTrashedRow",
    "Product",
    "ProductRow",
    "RestoreProductRow",
    "TrashProductRow",
    "UpdateProductCountStockRow",
    "UpdateProductRow",
]
