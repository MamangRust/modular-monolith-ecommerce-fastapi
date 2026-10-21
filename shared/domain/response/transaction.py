"""transaction response DTOs. Field names match the REST DTOs. Timestamp strings are already formatted by the gRPC handlers (`%Y-%m-%d %H:%M:%S`, seconds — no millis) and passed through unchanged. `TransactionResponseDeleteAt.deleted_at` is a nullable string: gateway mapper always sets the pointer (`""` when the proto wrapper is absent), so the REST key is always emitted."""

from __future__ import annotations

from dataclasses import dataclass

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
)


@dataclass
class TransactionResponse:
    id: int
    order_id: int
    merchant_id: int
    payment_method: str
    amount: int
    payment_status: str
    created_at: str
    updated_at: str


@dataclass
class TransactionResponseDeleteAt:
    id: int
    order_id: int
    merchant_id: int
    payment_method: str
    amount: int
    payment_status: str
    created_at: str
    updated_at: str
    deleted_at: str | None = None


@dataclass
class TransactionMonthlyAmountSuccessResponse:
    year: str
    month: str
    total_success: int
    total_amount: int


@dataclass
class TransactionMonthlyAmountFailedResponse:
    year: str
    month: str
    total_failed: int
    total_amount: int


@dataclass
class TransactionYearlyAmountSuccessResponse:
    year: str
    total_success: int
    total_amount: int


@dataclass
class TransactionYearlyAmountFailedResponse:
    year: str
    total_failed: int
    total_amount: int


@dataclass
class TransactionMonthlyMethodResponse:
    month: str
    payment_method: str
    total_transactions: int
    total_amount: int


@dataclass
class TransactionYearlyMethodResponse:
    year: str
    payment_method: str
    total_transactions: int
    total_amount: int


# API response wrappers (kept close to the names) ----

TransactionResponseApi = ApiResponse[TransactionResponse]
TransactionResponseDeleteAtApi = ApiResponse[TransactionResponseDeleteAt]
TransactionResponseDelete = ApiResponse[None]
TransactionResponseAll = ApiResponse[None]
TransactionResponsePagination = APIResponsePagination[list[TransactionResponse]]
TransactionResponsePaginationDeleteAt = APIResponsePagination[
    list[TransactionResponseDeleteAt]
]
TransactionMonthlyAmountSuccessApi = ApiResponse[
    list[TransactionMonthlyAmountSuccessResponse]
]
TransactionMonthlyAmountFailedApi = ApiResponse[
    list[TransactionMonthlyAmountFailedResponse]
]
TransactionYearlyAmountSuccessApi = ApiResponse[
    list[TransactionYearlyAmountSuccessResponse]
]
TransactionYearlyAmountFailedApi = ApiResponse[
    list[TransactionYearlyAmountFailedResponse]
]
TransactionMonthlyMethodApi = ApiResponse[list[TransactionMonthlyMethodResponse]]
TransactionYearlyMethodApi = ApiResponse[list[TransactionYearlyMethodResponse]]


__all__ = [
    "TransactionMonthlyAmountFailedApi",
    "TransactionMonthlyAmountFailedResponse",
    "TransactionMonthlyAmountSuccessApi",
    "TransactionMonthlyAmountSuccessResponse",
    "TransactionMonthlyMethodApi",
    "TransactionMonthlyMethodResponse",
    "TransactionResponse",
    "TransactionResponseAll",
    "TransactionResponseApi",
    "TransactionResponseDelete",
    "TransactionResponseDeleteAt",
    "TransactionResponseDeleteAtApi",
    "TransactionResponsePagination",
    "TransactionResponsePaginationDeleteAt",
    "TransactionYearlyAmountFailedApi",
    "TransactionYearlyAmountFailedResponse",
    "TransactionYearlyAmountSuccessApi",
    "TransactionYearlyAmountSuccessResponse",
    "TransactionYearlyMethodApi",
    "TransactionYearlyMethodResponse",
]
