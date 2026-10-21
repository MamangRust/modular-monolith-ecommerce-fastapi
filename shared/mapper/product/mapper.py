"""product proto -> response DTO mapping. Two proto shapes, one output family: - `ProductResponse` (Create/Update/FindById, FindAll list); - `ProductResponseDeleteAt` (active/trashed lists, trash/restore). The proto already carries formatted strings (`%Y-%m-%d %H:%M:%S.mmm`), so this layer only shapes them into the REST envelopes. always takes the address of its `deletedAt` local, so a live row serialises `deleted_at: ""`; normalised to the conditional convention (`""` only when no wrapper is attached)."""

from __future__ import annotations

from typing import Any

from shared.domain.response.product import (
    ProductResponse,
    ProductResponseDeleteAt,
)
from shared.domain.response.responses import PaginationMeta


def map_product_response(pb: Any) -> ProductResponse:
    return ProductResponse(
        id=int(pb.id),
        merchant_id=int(pb.merchant_id),
        category_id=int(pb.category_id),
        name=pb.name,
        description=pb.description,
        price=int(pb.price),
        count_in_stock=int(pb.count_in_stock),
        brand=pb.brand,
        weight=int(pb.weight),
        rating=float(pb.rating),
        slug_product=pb.slug_product,
        image_product=pb.image_product,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
    )


def map_product_response_delete_at(pb: Any) -> ProductResponseDeleteAt:
    deleted_at = pb.deleted_at.value if pb.HasField("deleted_at") else ""
    return ProductResponseDeleteAt(
        id=int(pb.id),
        merchant_id=int(pb.merchant_id),
        category_id=int(pb.category_id),
        name=pb.name,
        description=pb.description,
        price=int(pb.price),
        count_in_stock=int(pb.count_in_stock),
        brand=pb.brand,
        weight=int(pb.weight),
        rating=float(pb.rating),
        slug_product=pb.slug_product,
        image_product=pb.image_product,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
        deleted_at=deleted_at,
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
    "map_pagination_meta",
    "map_product_response",
    "map_product_response_delete_at",
]
