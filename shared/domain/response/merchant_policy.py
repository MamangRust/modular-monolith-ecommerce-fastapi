"""merchant_policy response DTOs. Field names match the REST DTOs exactly. Two shapes, the proto: - `MerchantPoliciesResponse` (Create/Update/FindById, FindAll list); - `MerchantPoliciesResponseDeleteAt` (active/trashed lists, trash/restore). always takes the address of the mapper's `deletedAt` local, so the DeleteAt shape always serialises `deleted_at` (a zero string when no wrapper is attached). Normalised to the convention (merchant_award/merchant_business): `deleted_at` is a plain `str` that is `""` when the row is live and carries the formatted timestamp only when actually trashed. `merchant_name` is `""` because the gRPC handler never fills it. Timestamps are already formatted by the gRPC handlers (`.mmm`), so the mapper passes them through unchanged."""

from __future__ import annotations

import math
from dataclasses import dataclass

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)


@dataclass
class MerchantPoliciesResponse:
    id: int
    merchant_id: int
    policy_type: str
    title: str
    description: str
    created_at: str
    updated_at: str
    merchant_name: str = ""


@dataclass
class MerchantPoliciesResponseDeleteAt:
    id: int
    merchant_id: int
    policy_type: str
    title: str
    description: str
    created_at: str
    updated_at: str
    deleted_at: str = ""
    merchant_name: str = ""


# API response wrappers (kept close to the names) ----

MerchantPoliciesResponseApi = ApiResponse[MerchantPoliciesResponse]
MerchantPoliciesResponseDeleteAtApi = ApiResponse[MerchantPoliciesResponseDeleteAt]
MerchantPoliciesResponses = ApiResponse[list[MerchantPoliciesResponse]]
MerchantPoliciesResponsePagination = APIResponsePagination[
    list[MerchantPoliciesResponse]
]
MerchantPoliciesResponsePaginationDeleteAt = APIResponsePagination[
    list[MerchantPoliciesResponseDeleteAt]
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
    "MerchantPoliciesResponse",
    "MerchantPoliciesResponseApi",
    "MerchantPoliciesResponseDeleteAt",
    "MerchantPoliciesResponseDeleteAtApi",
    "MerchantPoliciesResponsePagination",
    "MerchantPoliciesResponsePaginationDeleteAt",
    "MerchantPoliciesResponses",
    "pagination_meta",
]
