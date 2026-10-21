"""Slider query response mapping.

The proto already carries formatted date-only strings, so this layer only
shapes them into the REST envelopes — no reformatting."""

from __future__ import annotations

from typing import Any

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)
from shared.domain.response.slider import (
    SliderResponse,
    SliderResponseDeleteAt,
)
from shared.mapper.slider.mapper import (
    map_slider_response,
    map_slider_response_delete_at,
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


def to_api_response_slider(pb: Any) -> ApiResponse[SliderResponse]:
    return ApiResponse[SliderResponse](
        status=pb.status,
        message=pb.message,
        data=map_slider_response(pb.data),
    )


def to_api_responses_slider(pb: Any) -> ApiResponse[list[SliderResponse]]:
    return ApiResponse[list[SliderResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_slider_response(item) for item in pb.data],
    )


def to_api_response_pagination_slider(
    pb: Any,
) -> APIResponsePagination[list[SliderResponse]]:
    return APIResponsePagination[list[SliderResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_slider_response(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_pagination_slider_delete_at(
    pb: Any,
) -> APIResponsePagination[list[SliderResponseDeleteAt]]:
    return APIResponsePagination[list[SliderResponseDeleteAt]](
        status=pb.status,
        message=pb.message,
        data=[map_slider_response_delete_at(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


__all__ = [
    "map_pagination_meta",
    "to_api_response_pagination_slider",
    "to_api_response_pagination_slider_delete_at",
    "to_api_response_slider",
    "to_api_responses_slider",
]
