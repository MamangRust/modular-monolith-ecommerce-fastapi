"""Banner response DTOs. The wire carries the REST field name `id` even though the proto field is `banner_id`; date/time/timestamp strings are already formatted by the gRPC handlers, so the mapper passes them through unchanged."""

from __future__ import annotations

import math
from dataclasses import dataclass

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)


@dataclass
class BannerResponse:
    id: int
    name: str
    start_date: str
    end_date: str
    start_time: str
    end_time: str
    is_active: bool
    created_at: str
    updated_at: str


@dataclass
class BannerResponseDeleteAt:
    id: int
    name: str
    start_date: str
    end_date: str
    start_time: str
    end_time: str
    is_active: bool
    created_at: str
    updated_at: str
    deleted_at: str | None = None


# API response wrappers (kept close to the names) ----

BannerResponseAll = ApiResponse[None]
BannerResponseDelete = ApiResponse[None]
BannerResponseApi = ApiResponse[BannerResponse]
BannerResponseDeleteAtApi = ApiResponse[BannerResponseDeleteAt]
BannersResponse = ApiResponse[list[BannerResponse]]
BannerResponsePagination = APIResponsePagination[list[BannerResponse]]
BannerResponsePaginationDeleteAt = APIResponsePagination[list[BannerResponseDeleteAt]]


def pagination_meta(page: int, page_size: int, total_records: int) -> PaginationMeta:
    total_pages = math.ceil(total_records / page_size) if page_size else 0
    return PaginationMeta(
        current_page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_records=total_records,
    )


__all__ = [
    "BannerResponse",
    "BannerResponseAll",
    "BannerResponseApi",
    "BannerResponseDelete",
    "BannerResponseDeleteAt",
    "BannerResponseDeleteAtApi",
    "BannerResponsePagination",
    "BannerResponsePaginationDeleteAt",
    "BannersResponse",
    "pagination_meta",
]
