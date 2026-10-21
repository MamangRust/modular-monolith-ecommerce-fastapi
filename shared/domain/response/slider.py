"""Slider response DTOs. The wire carries the REST field name `id` even though the proto field is `slider_id`; date/timestamp strings are already formatted by the gRPC handlers (date-only `%Y-%m-%d` to match the `2006-01-02` layout), so the mapper passes them through unchanged."""

from __future__ import annotations

import math
from dataclasses import dataclass

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)


@dataclass
class SliderResponse:
    id: int
    name: str
    image: str
    created_at: str
    updated_at: str


@dataclass
class SliderResponseDeleteAt:
    id: int
    name: str
    image: str
    created_at: str
    updated_at: str
    deleted_at: str | None = None


# API response wrappers (kept close to the names) ----

SliderResponseAll = ApiResponse[None]
SliderResponseDelete = ApiResponse[None]
SliderResponseApi = ApiResponse[SliderResponse]
SliderResponseDeleteAtApi = ApiResponse[SliderResponseDeleteAt]
SlidersResponse = ApiResponse[list[SliderResponse]]
SliderResponsePagination = APIResponsePagination[list[SliderResponse]]
SliderResponsePaginationDeleteAt = APIResponsePagination[
    list[SliderResponseDeleteAt]
]


def pagination_meta(page: int, page_size: int, total_records: int) -> PaginationMeta:
    total_pages = math.ceil(total_records / page_size) if page_size else 0
    return PaginationMeta(
        current_page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_records=total_records,
    )


__all__ = [
    "SliderResponse",
    "SliderResponseAll",
    "SliderResponseApi",
    "SliderResponseDelete",
    "SliderResponseDeleteAt",
    "SliderResponseDeleteAtApi",
    "SliderResponsePagination",
    "SliderResponsePaginationDeleteAt",
    "SlidersResponse",
    "pagination_meta",
]
