"""Category command response mapping.

`Create`/`Update` reuse the query-side `to_api_response_category` (identical
shape), so only the command-only envelopes live here."""

from __future__ import annotations

from typing import Any

from shared.domain.response.category import CategoryResponseDeleteAt
from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
)
from shared.mapper.category.mapper import map_category_response_delete_at
from shared.mapper.category.query import map_pagination_meta


def to_api_response_category_delete_at(
    pb: Any,
) -> ApiResponse[CategoryResponseDeleteAt]:
    return ApiResponse[CategoryResponseDeleteAt](
        status=pb.status,
        message=pb.message,
        data=map_category_response_delete_at(pb.data),
    )


def to_api_response_category_delete(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


def to_api_response_category_all(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


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
    "to_api_response_category_all",
    "to_api_response_category_delete",
    "to_api_response_category_delete_at",
    "to_api_response_pagination_category_delete_at",
]
