"""Cart proto -> response DTO mapping.

The proto already carries formatted strings (`%Y-%m-%d`), so this layer only
shapes them into the REST envelopes. `id` is the wire name on both sides;
`image` (proto) maps to `image` (REST)."""

from __future__ import annotations

from typing import Any

from shared.domain.response.cart import CartResponse
from shared.domain.response.responses import PaginationMeta


def map_cart_response(pb: Any) -> CartResponse:
    return CartResponse(
        id=int(pb.id),
        user_id=int(pb.user_id),
        product_id=int(pb.product_id),
        name=pb.name,
        price=int(pb.price),
        image=pb.image,
        quantity=int(pb.quantity),
        weight=int(pb.weight),
        created_at=pb.created_at,
        updated_at=pb.updated_at,
    )


def map_pagination_meta(meta: Any) -> PaginationMeta:
    if meta is None:
        return PaginationMeta()
    return PaginationMeta(
        current_page=int(meta.current_page),
        page_size=int(meta.page_size),
        total_pages=int(meta.total_pages),
        total_records=int(meta.total_records),
    )


__all__ = [
    "map_cart_response",
    "map_pagination_meta",
]
