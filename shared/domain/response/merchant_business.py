"""merchant_business response DTOs. Field names match the REST DTOs exactly. Two shapes, the proto: - `MerchantBusinessResponse` (Create/Update/FindById, FindAll list); - `MerchantBusinessResponseDeleteAt` (active/trashed lists, trash/restore). `merchant_name` exists on both structs. the plain struct is `*string` and the mapper takes the address of the proto's (never-filled) field, so it always serialises as `""`; the DeleteAt struct is a plain `string`, also `""`. models both as `str = ""`. `deleted_at` is always attached on the DeleteAt shape (a zero string when no wrapper is present). Timestamps are already formatted by the gRPC handlers, so the mapper passes them through unchanged."""

from __future__ import annotations

import math
from dataclasses import dataclass

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)


@dataclass
class MerchantBusinessResponse:
    id: int
    merchant_id: int
    business_type: str
    tax_id: str
    established_year: int
    number_of_employees: int
    website_url: str
    created_at: str
    updated_at: str
    merchant_name: str = ""


@dataclass
class MerchantBusinessResponseDeleteAt:
    id: int
    merchant_id: int
    business_type: str
    tax_id: str
    established_year: int
    number_of_employees: int
    website_url: str
    created_at: str
    updated_at: str
    merchant_name: str = ""
    deleted_at: str = ""


# API response wrappers (kept close to the names) ----

MerchantBusinessResponseApi = ApiResponse[MerchantBusinessResponse]
MerchantBusinessResponseDeleteAtApi = ApiResponse[MerchantBusinessResponseDeleteAt]
MerchantBusinessResponses = ApiResponse[list[MerchantBusinessResponse]]
MerchantBusinessResponsePagination = APIResponsePagination[
    list[MerchantBusinessResponse]
]
MerchantBusinessResponsePaginationDeleteAt = APIResponsePagination[
    list[MerchantBusinessResponseDeleteAt]
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
    "MerchantBusinessResponse",
    "MerchantBusinessResponseApi",
    "MerchantBusinessResponseDeleteAt",
    "MerchantBusinessResponseDeleteAtApi",
    "MerchantBusinessResponsePagination",
    "MerchantBusinessResponsePaginationDeleteAt",
    "MerchantBusinessResponses",
    "pagination_meta",
]
