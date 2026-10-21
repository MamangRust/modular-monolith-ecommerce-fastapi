"""Row types for the carts table. `db.Cart` model also carries `deleted_at`, but no query ever sets it and `CreateCart`'s projection omits it; the `Cart` Matches the expected model and keeps `deleted_at` optional. `GetCartsRow` is the list projection (base + `total_count`). Cart timestamps are formatted `%Y-%m-%d` (date only) by the handler (`mapToProtoCartResponse`), unlike product (`%H:%M:%S.mmm`)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Cart:

    cart_id: int
    user_id: int
    product_id: int
    name: str
    price: int
    image: str
    quantity: int
    weight: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> Cart:
        return cls(
            cart_id=row["cart_id"],
            user_id=row["user_id"],
            product_id=row["product_id"],
            name=row["name"],
            price=row["price"],
            image=row["image"],
            quantity=row["quantity"],
            weight=row["weight"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class CartRow:
    """`CreateCart` RETURNING projection (base columns, no `deleted_at`)."""

    cart_id: int
    user_id: int
    product_id: int
    name: str
    price: int
    image: str
    quantity: int
    weight: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> CartRow:
        return cls(
            cart_id=row["cart_id"],
            user_id=row["user_id"],
            product_id=row["product_id"],
            name=row["name"],
            price=row["price"],
            image=row["image"],
            quantity=row["quantity"],
            weight=row["weight"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


# declares a distinct struct name (`CreateCartRow`); the fields are identical.
CreateCartRow = CartRow


@dataclass
class GetCartsRow:
    """`GetCarts` (FindAll) projection with the window total count."""

    cart_id: int
    user_id: int
    product_id: int
    name: str
    price: int
    image: str
    quantity: int
    weight: int
    created_at: datetime
    updated_at: datetime
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetCartsRow:
        return cls(
            cart_id=row["cart_id"],
            user_id=row["user_id"],
            product_id=row["product_id"],
            name=row["name"],
            price=row["price"],
            image=row["image"],
            quantity=row["quantity"],
            weight=row["weight"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            total_count=int(row["total_count"]),
        )


__all__ = [
    "Cart",
    "CartRow",
    "CreateCartRow",
    "GetCartsRow",
]
