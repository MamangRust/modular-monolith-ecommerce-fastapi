"""merchant_award response DTOs. Field names match the REST DTOs exactly. Two shapes, the proto: - `MerchantAwardResponse` (Create/Update/FindById, FindAll list); - `MerchantAwardResponseDeleteAt` (active/trashed lists, trash/restore). `merchant_name` exists on both structs but the mappers never copy it, so it always serialises as `""` (no `omitempty` on the field). `deleted_at` is always attached on the DeleteAt shape: the mapper takes the address of a zero string when no wrapper is present, so a live row renders `"deleted_at": ""` (never absent). Timestamps are already formatted by the gRPC handlers, so the mapper passes them through unchanged."""

from __future__ import annotations

import math
from dataclasses import dataclass

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)


@dataclass
class MerchantAwardResponse:
    id: int
    merchant_id: int
    title: str
    description: str
    issued_by: str
    issue_date: str
    expiry_date: str
    certificate_url: str
    created_at: str
    updated_at: str
    merchant_name: str = ""


@dataclass
class MerchantAwardResponseDeleteAt:
    id: int
    merchant_id: int
    title: str
    description: str
    issued_by: str
    issue_date: str
    expiry_date: str
    certificate_url: str
    created_at: str
    updated_at: str
    merchant_name: str = ""
    deleted_at: str = ""


# API response wrappers (kept close to the names) ----

MerchantAwardResponseApi = ApiResponse[MerchantAwardResponse]
MerchantAwardResponseDeleteAtApi = ApiResponse[MerchantAwardResponseDeleteAt]
MerchantAwardsResponse = ApiResponse[list[MerchantAwardResponse]]
MerchantAwardResponsePagination = APIResponsePagination[list[MerchantAwardResponse]]
MerchantAwardResponsePaginationDeleteAt = APIResponsePagination[
    list[MerchantAwardResponseDeleteAt]
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
    "MerchantAwardResponse",
    "MerchantAwardResponseApi",
    "MerchantAwardResponseDeleteAt",
    "MerchantAwardResponseDeleteAtApi",
    "MerchantAwardResponsePagination",
    "MerchantAwardResponsePaginationDeleteAt",
    "MerchantAwardsResponse",
    "pagination_meta",
]
