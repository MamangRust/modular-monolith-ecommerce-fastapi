"""Category query response mapping.

The proto already carries formatted strings, so this layer only shapes them
into the REST envelopes — no reformatting."""

from __future__ import annotations

from typing import Any

from shared.domain.response.category import (
    CategoryResponse,
    CategoryResponseDeleteAt,
)
from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)
from shared.mapper.category.mapper import (
    map_category_response,
    map_category_response_delete_at,
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


def to_api_response_category(pb: Any) -> ApiResponse[CategoryResponse]:
    return ApiResponse[CategoryResponse](
        status=pb.status,
        message=pb.message,
        data=map_category_response(pb.data),
    )


def to_api_responses_category(pb: Any) -> ApiResponse[list[CategoryResponse]]:
    return ApiResponse[list[CategoryResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_category_response(item) for item in pb.data],
    )


def to_api_response_pagination_category(
    pb: Any,
) -> APIResponsePagination[list[CategoryResponse]]:
    return APIResponsePagination[list[CategoryResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_category_response(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_pagination_category_delete_at(
    pb: Any,
) -> APIResponsePagination[list[CategoryResponseDeleteAt]]:
    return APIResponsePagination[list[CategoryResponseDeleteAt]](
        status=pb.status,
        message=pb.message,
        data=[map_category_response_delete_at(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


__all__ = [
    "map_pagination_meta",
    "to_api_response_pagination_category",
    "to_api_response_pagination_category_delete_at",
    "to_api_response_category",
    "to_api_responses_category",
]
