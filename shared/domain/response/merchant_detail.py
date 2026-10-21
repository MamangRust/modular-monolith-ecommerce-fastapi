"""merchant_detail response DTOs. Field names match the REST DTOs exactly: - merchant detail proto `id` / REST `id` — read directly; - `social_media_links` is a `list[MerchantSocialMediaLinkResponse]`. the mapper builds it by iterating the proto list, so an empty proto list yields a nil slice and renders as JSON `null` (never `[]`). The gRPC handler never fills the proto list, so in practice it is always `null` here too. Timestamps are already formatted by the gRPC handlers (`%Y-%m-%d %H:%M:%S.mmm`), so the mapper passes them through unchanged. `deleted_at` is absent (no wrapper) for a live row, so it defaults to `None`."""

from __future__ import annotations

import math
from dataclasses import dataclass

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)


@dataclass
class MerchantSocialMediaLinkResponse:
    """Nested link inside a merchant detail (REST `social_media_links[]`)."""

    id: int
    platform: str
    url: str


@dataclass
class MerchantDetailResponse:
    id: int
    merchant_id: int
    display_name: str
    cover_image_url: str
    logo_url: str
    short_description: str
    website_url: str
    created_at: str
    updated_at: str
    social_media_links: list[MerchantSocialMediaLinkResponse] | None = None


@dataclass
class MerchantDetailResponseDeleteAt:
    id: int
    merchant_id: int
    display_name: str
    cover_image_url: str
    logo_url: str
    short_description: str
    website_url: str
    created_at: str
    updated_at: str
    social_media_links: list[MerchantSocialMediaLinkResponse] | None = None
    deleted_at: str | None = None


@dataclass
class MerchantSocialLinkResponse:
    """REST DTO for the standalone social-link command routes. the command mapper copies only `id`/`merchant_detail_id`/`platform`/`url` (it ignores the proto `created_at`/`updated_at`), but its response struct declares those two fields **without** `omitempty`, so the JSON still carries `"created_at": ""` / `"updated_at": ""`.: the two fields exist and stay empty."""

    id: int
    merchant_detail_id: int
    platform: str
    url: str
    created_at: str = ""
    updated_at: str = ""


# API response wrappers (kept close to the names) ----

MerchantDetailResponseAll = ApiResponse[None]
MerchantDetailResponseDelete = ApiResponse[None]
MerchantDetailResponseApi = ApiResponse[MerchantDetailResponse]
MerchantDetailResponseDeleteAtApi = ApiResponse[MerchantDetailResponseDeleteAt]
MerchantDetailsResponse = ApiResponse[list[MerchantDetailResponse]]
MerchantDetailResponsePagination = APIResponsePagination[list[MerchantDetailResponse]]
MerchantDetailResponsePaginationDeleteAt = APIResponsePagination[
    list[MerchantDetailResponseDeleteAt]
]

MerchantSocialLinkResponseApi = ApiResponse[MerchantSocialLinkResponse]


def pagination_meta(page: int, page_size: int, total_records: int) -> PaginationMeta:
    total_pages = math.ceil(total_records / page_size) if page_size else 0
    return PaginationMeta(
        current_page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_records=total_records,
    )


__all__ = [
    "MerchantDetailResponse",
    "MerchantDetailResponseAll",
    "MerchantDetailResponseApi",
    "MerchantDetailResponseDelete",
    "MerchantDetailResponseDeleteAt",
    "MerchantDetailResponseDeleteAtApi",
    "MerchantDetailResponsePagination",
    "MerchantDetailResponsePaginationDeleteAt",
    "MerchantDetailsResponse",
    "MerchantSocialLinkResponse",
    "MerchantSocialLinkResponseApi",
    "MerchantSocialMediaLinkResponse",
    "pagination_meta",
]
