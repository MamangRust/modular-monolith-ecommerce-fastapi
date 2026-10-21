"""Banner query response mapping.

The proto already carries formatted strings, so this layer only shapes
them into the REST envelopes — no reformatting."""

from __future__ import annotations

from typing import Any

from shared.domain.response.banner import (
    BannerResponse,
    BannerResponseDeleteAt,
)
from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)
from shared.mapper.banner.mapper import (
    map_banner_response,
    map_banner_response_delete_at,
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


def to_api_response_banner(pb: Any) -> ApiResponse[BannerResponse]:
    return ApiResponse[BannerResponse](
        status=pb.status,
        message=pb.message,
        data=map_banner_response(pb.data),
    )


def to_api_responses_banner(pb: Any) -> ApiResponse[list[BannerResponse]]:
    return ApiResponse[list[BannerResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_banner_response(item) for item in pb.data],
    )


def to_api_response_pagination_banner(
    pb: Any,
) -> APIResponsePagination[list[BannerResponse]]:
    return APIResponsePagination[list[BannerResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_banner_response(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_pagination_banner_delete_at(
    pb: Any,
) -> APIResponsePagination[list[BannerResponseDeleteAt]]:
    return APIResponsePagination[list[BannerResponseDeleteAt]](
        status=pb.status,
        message=pb.message,
        data=[map_banner_response_delete_at(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


__all__ = [
    "map_pagination_meta",
    "to_api_response_pagination_banner",
    "to_api_response_pagination_banner_delete_at",
    "to_api_response_banner",
    "to_api_responses_banner",
]
