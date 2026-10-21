"""Row -> proto mapping for the cart gRPC handlers. `mapToProtoCartResponse` type-switches over two row shapes that project the same base columns (`*db.Cart` and `*db.GetCartsRow`); a single attribute-driven filler reproduces both branches, since `cart_id` is the only rename (`id` on the wire). Cart timestamps are formatted `%Y-%m-%d` (date only), unlike product's `%H:%M:%S.mmm` — `format_date` supplies exactly that. mapper never emits `deleted_at` (neither case sets it), so the deleted-at response variant is not produced here."""

from __future__ import annotations

import math
from typing import Any

from pb.common import api_pb2 as common_pb2
from shared.convert.convert import format_date


def normalize_page(page: int, page_size: int) -> tuple[int, int]:
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


def pagination_meta(page: int, page_size: int, total: int) -> Any:
    total_pages = math.ceil(total / page_size) if page_size else 0
    return common_pb2.PaginationMeta(
        current_page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_records=total,
    )


def fill_cart_response(message: Any, row: Any) -> None:
    message.id = getattr(row, "cart_id", 0)
    message.user_id = getattr(row, "user_id", 0)
    message.product_id = getattr(row, "product_id", 0)
    message.name = getattr(row, "name", "") or ""
    message.price = getattr(row, "price", 0)
    message.image = getattr(row, "image", "") or ""
    message.quantity = getattr(row, "quantity", 0)
    message.weight = getattr(row, "weight", 0)
    message.created_at = format_date(getattr(row, "created_at", None))
    message.updated_at = format_date(getattr(row, "updated_at", None))


__all__ = [
    "fill_cart_response",
    "normalize_page",
    "pagination_meta",
]
