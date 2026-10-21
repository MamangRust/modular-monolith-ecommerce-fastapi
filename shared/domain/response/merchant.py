"""Merchant response DTOs. Field names match the REST DTOs exactly: - merchant proto `id` / REST `id` — read directly, no translation; - document proto `document_id` / REST `id`, proto `document_url` / REST `document_url` — the mapper translates `document_id` -> `id` and passes `document_url` through. Timestamps are already formatted by the gRPC handlers (`%Y-%m-%d %H:%M:%S`, matching the `2006-01-02 15:04:05` layout), so the mapper passes them through unchanged. `deleted_at` is absent (no wrapper) for a live row, so it defaults to `None`."""

from __future__ import annotations

import math
from dataclasses import dataclass

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)


@dataclass
class MerchantResponse:
    id: int
    user_id: int
    name: str
    description: str
    address: str
    contact_email: str
    contact_phone: str
    status: str
    created_at: str
    updated_at: str


@dataclass
class MerchantResponseDeleteAt:
    id: int
    user_id: int
    name: str
    description: str
    address: str
    contact_email: str
    contact_phone: str
    status: str
    created_at: str
    updated_at: str
    deleted_at: str | None = None


@dataclass
class MerchantDocumentResponse:
    id: int
    merchant_id: int
    document_type: str
    document_url: str
    status: str
    note: str
    created_at: str
    updated_at: str


@dataclass
class MerchantDocumentResponseDeleteAt:
    id: int
    merchant_id: int
    document_type: str
    document_url: str
    status: str
    note: str
    created_at: str
    updated_at: str
    deleted_at: str | None = None


# API response wrappers (kept close to the names) ----

MerchantResponseAll = ApiResponse[None]
MerchantResponseDelete = ApiResponse[None]
MerchantResponseApi = ApiResponse[MerchantResponse]
MerchantResponseDeleteAtApi = ApiResponse[MerchantResponseDeleteAt]
MerchantsResponse = ApiResponse[list[MerchantResponse]]
MerchantResponsePagination = APIResponsePagination[list[MerchantResponse]]
MerchantResponsePaginationDeleteAt = APIResponsePagination[
    list[MerchantResponseDeleteAt]
]

MerchantDocumentResponseAll = ApiResponse[None]
MerchantDocumentResponseDelete = ApiResponse[None]
MerchantDocumentResponseApi = ApiResponse[MerchantDocumentResponse]
MerchantDocumentResponseDeleteAtApi = ApiResponse[MerchantDocumentResponseDeleteAt]
MerchantDocumentsResponse = ApiResponse[list[MerchantDocumentResponse]]
MerchantDocumentResponsePagination = APIResponsePagination[
    list[MerchantDocumentResponse]
]
MerchantDocumentResponsePaginationDeleteAt = APIResponsePagination[
    list[MerchantDocumentResponseDeleteAt]
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
    "MerchantDocumentResponse",
    "MerchantDocumentResponseAll",
    "MerchantDocumentResponseApi",
    "MerchantDocumentResponseDelete",
    "MerchantDocumentResponseDeleteAt",
    "MerchantDocumentResponseDeleteAtApi",
    "MerchantDocumentResponsePagination",
    "MerchantDocumentResponsePaginationDeleteAt",
    "MerchantDocumentsResponse",
    "MerchantResponse",
    "MerchantResponseAll",
    "MerchantResponseApi",
    "MerchantResponseDelete",
    "MerchantResponseDeleteAt",
    "MerchantResponseDeleteAtApi",
    "MerchantResponsePagination",
    "MerchantResponsePaginationDeleteAt",
    "MerchantsResponse",
    "pagination_meta",
]
