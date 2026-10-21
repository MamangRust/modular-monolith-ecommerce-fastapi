"""Row types for the order_items table. All columns are non-nullable in (`int32`), so they surface as plain `int`. Timestamps are `pgtype.Timestamp`; the order_item handlers format them with the millisecond layout `2006-01-02 15:04:05.000` (same as banner — do not unify with category's `%Y-%m-%d`)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class OrderItem:

    order_item_id: int
    order_id: int
    product_id: int
    quantity: int
    price: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> OrderItem:
        return cls(
            order_item_id=row["order_item_id"],
            order_id=row["order_id"],
            product_id=row["product_id"],
            quantity=row["quantity"],
            price=row["price"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class CreateOrderItemRow:
    order_item_id: int
    order_id: int
    product_id: int
    quantity: int
    price: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> CreateOrderItemRow:
        return cls(
            order_item_id=row["order_item_id"],
            order_id=row["order_id"],
            product_id=row["product_id"],
            quantity=row["quantity"],
            price=row["price"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


UpdateOrderItemRow = CreateOrderItemRow


@dataclass
class GetOrderItemsRow:
    """`FindAll` projection with a window total count."""

    order_item_id: int
    order_id: int
    product_id: int
    quantity: int
    price: int
    created_at: datetime
    updated_at: datetime
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetOrderItemsRow:
        return cls(
            order_item_id=row["order_item_id"],
            order_id=row["order_id"],
            product_id=row["product_id"],
            quantity=row["quantity"],
            price=row["price"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            total_count=int(row["total_count"]),
        )


@dataclass
class GetOrderItemsActiveRow:
    order_item_id: int
    order_id: int
    product_id: int
    quantity: int
    price: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetOrderItemsActiveRow:
        return cls(
            order_item_id=row["order_item_id"],
            order_id=row["order_id"],
            product_id=row["product_id"],
            quantity=row["quantity"],
            price=row["price"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            total_count=int(row["total_count"]),
        )


GetOrderItemsTrashedRow = GetOrderItemsActiveRow


@dataclass
class GetOrderItemsByOrderRow:
    """`FindOrderItemByOrder` projection — no `deleted_at`, no total count."""

    order_item_id: int
    order_id: int
    product_id: int
    quantity: int
    price: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetOrderItemsByOrderRow:
        return cls(
            order_item_id=row["order_item_id"],
            order_id=row["order_id"],
            product_id=row["product_id"],
            quantity=row["quantity"],
            price=row["price"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


__all__ = [
    "CreateOrderItemRow",
    "GetOrderItemsActiveRow",
    "GetOrderItemsByOrderRow",
    "GetOrderItemsRow",
    "GetOrderItemsTrashedRow",
    "OrderItem",
    "UpdateOrderItemRow",
]
