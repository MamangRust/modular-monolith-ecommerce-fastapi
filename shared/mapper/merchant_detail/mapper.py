"""merchant_detail proto -> response DTO mapping. Two proto shapes, one output family: - `MerchantDetailResponse` (Create/Update/FindById); - `MerchantDetailResponseDeleteAt` (active/trashed lists, trash/restore). `social_media_links` is built by iterating the proto list; an empty list yields `None` (nil slice -> JSON `null`), never `[]`. The gRPC handler never fills the proto list, so it is always `None` in practice. The proto already carries `%Y-%m-%d %H:%M:%S.mmm` strings, so timestamps are passed through unchanged. `deleted_at` renders as `""` when no wrapper is attached (takes the address of a zero string), matching merchant."""

from __future__ import annotations

from typing import Any

from shared.domain.response.merchant_detail import (
    MerchantDetailResponse,
    MerchantDetailResponseDeleteAt,
    MerchantSocialMediaLinkResponse,
)
from shared.domain.response.responses import PaginationMeta


def map_merchant_social_media_link(pb: Any) -> MerchantSocialMediaLinkResponse:
    return MerchantSocialMediaLinkResponse(
        id=int(pb.id),
        platform=pb.platform,
        url=pb.url,
    )


def _map_links(pb: Any) -> list[MerchantSocialMediaLinkResponse] | None:
    links = [map_merchant_social_media_link(item) for item in pb.social_media_links]
    return links or None


def map_merchant_detail_response(pb: Any) -> MerchantDetailResponse:
    """`ToResponseMerchantDetail` — links always nil."""
    return MerchantDetailResponse(
        id=int(pb.id),
        merchant_id=int(pb.merchant_id),
        display_name=pb.display_name,
        cover_image_url=pb.cover_image_url,
        logo_url=pb.logo_url,
        short_description=pb.short_description,
        website_url=pb.website_url,
        social_media_links=None,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
    )


def map_merchant_detail_response_relation(pb: Any) -> MerchantDetailResponse:
    """`ToResponseMerchantDetailRelation` — links built from the proto list."""
    return MerchantDetailResponse(
        id=int(pb.id),
        merchant_id=int(pb.merchant_id),
        display_name=pb.display_name,
        cover_image_url=pb.cover_image_url,
        logo_url=pb.logo_url,
        short_description=pb.short_description,
        website_url=pb.website_url,
        social_media_links=_map_links(pb),
        created_at=pb.created_at,
        updated_at=pb.updated_at,
    )


def map_merchant_detail_response_delete_at(
    pb: Any,
) -> MerchantDetailResponseDeleteAt:
    # takes the address of a zero string when no wrapper is attached, so a
    # live row renders `deleted_at: ""`.
    deleted_at = pb.deleted_at.value if pb.HasField("deleted_at") else ""
    return MerchantDetailResponseDeleteAt(
        id=int(pb.id),
        merchant_id=int(pb.merchant_id),
        display_name=pb.display_name,
        cover_image_url=pb.cover_image_url,
        logo_url=pb.logo_url,
        short_description=pb.short_description,
        website_url=pb.website_url,
        social_media_links=_map_links(pb),
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
    "map_merchant_detail_response",
    "map_merchant_detail_response_delete_at",
    "map_merchant_detail_response_relation",
    "map_merchant_social_media_link",
    "map_pagination_meta",
]
