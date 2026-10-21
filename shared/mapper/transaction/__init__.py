"""Transaction REST mappers."""

from __future__ import annotations

from typing import Any

from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.domain.response.transaction import (
    TransactionMonthlyAmountFailedApi,
    TransactionMonthlyAmountSuccessApi,
    TransactionMonthlyMethodApi,
    TransactionResponse,
    TransactionResponseAll,
    TransactionResponseApi,
    TransactionResponseDelete,
    TransactionResponseDeleteAt,
    TransactionResponseDeleteAtApi,
    TransactionResponsePagination,
    TransactionResponsePaginationDeleteAt,
    TransactionYearlyAmountFailedApi,
    TransactionYearlyAmountSuccessApi,
    TransactionYearlyMethodApi,
)
from shared.mapper.transaction.mapper import (
    map_monthly_amount_failed,
    map_monthly_amount_success,
    map_monthly_method,
    map_pagination_meta,
    map_transaction_response,
    map_transaction_response_delete_at,
    map_yearly_amount_failed,
    map_yearly_amount_success,
    map_yearly_method,
)


def to_api_response_transaction(pb: Any) -> TransactionResponseApi:
    return ApiResponse[TransactionResponse](
        status=pb.status,
        message=pb.message,
        data=map_transaction_response(pb.data),
    )


def to_api_response_transaction_delete_at(
    pb: Any,
) -> TransactionResponseDeleteAtApi:
    return ApiResponse[TransactionResponseDeleteAt](
        status=pb.status,
        message=pb.message,
        data=map_transaction_response_delete_at(pb.data),
    )


def to_api_response_transaction_delete(pb: Any) -> TransactionResponseDelete:
    return TransactionResponseDelete(status=pb.status, message=pb.message)


def to_api_response_transaction_all(pb: Any) -> TransactionResponseAll:
    return TransactionResponseAll(status=pb.status, message=pb.message)


def to_api_response_pagination_transaction(
    pb: Any,
) -> TransactionResponsePagination:
    return APIResponsePagination[list[TransactionResponse]](
        status=pb.status,
        message=pb.message,
        data=[map_transaction_response(row) for row in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_pagination_transaction_delete_at(
    pb: Any,
) -> TransactionResponsePaginationDeleteAt:
    return APIResponsePagination[list[TransactionResponseDeleteAt]](
        status=pb.status,
        message=pb.message,
        data=[map_transaction_response_delete_at(row) for row in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_monthly_amount_success(
    pb: Any,
) -> TransactionMonthlyAmountSuccessApi:
    return TransactionMonthlyAmountSuccessApi(
        status=pb.status,
        message=pb.message,
        data=[map_monthly_amount_success(row) for row in pb.data],
    )


def to_api_response_monthly_amount_failed(
    pb: Any,
) -> TransactionMonthlyAmountFailedApi:
    return TransactionMonthlyAmountFailedApi(
        status=pb.status,
        message=pb.message,
        data=[map_monthly_amount_failed(row) for row in pb.data],
    )


def to_api_response_yearly_amount_success(
    pb: Any,
) -> TransactionYearlyAmountSuccessApi:
    return TransactionYearlyAmountSuccessApi(
        status=pb.status,
        message=pb.message,
        data=[map_yearly_amount_success(row) for row in pb.data],
    )


def to_api_response_yearly_amount_failed(
    pb: Any,
) -> TransactionYearlyAmountFailedApi:
    return TransactionYearlyAmountFailedApi(
        status=pb.status,
        message=pb.message,
        data=[map_yearly_amount_failed(row) for row in pb.data],
    )


def to_api_response_monthly_method(pb: Any) -> TransactionMonthlyMethodApi:
    return TransactionMonthlyMethodApi(
        status=pb.status,
        message=pb.message,
        data=[map_monthly_method(row) for row in pb.data],
    )


def to_api_response_yearly_method(pb: Any) -> TransactionYearlyMethodApi:
    return TransactionYearlyMethodApi(
        status=pb.status,
        message=pb.message,
        data=[map_yearly_method(row) for row in pb.data],
    )


__all__ = [
    "to_api_response_monthly_amount_failed",
    "to_api_response_monthly_amount_success",
    "to_api_response_monthly_method",
    "to_api_response_pagination_transaction",
    "to_api_response_pagination_transaction_delete_at",
    "to_api_response_transaction",
    "to_api_response_transaction_all",
    "to_api_response_transaction_delete",
    "to_api_response_transaction_delete_at",
    "to_api_response_yearly_amount_failed",
    "to_api_response_yearly_amount_success",
    "to_api_response_yearly_method",
]
