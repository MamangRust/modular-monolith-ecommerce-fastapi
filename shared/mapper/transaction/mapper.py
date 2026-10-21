"""Transaction proto -> response DTO mapping. The proto already carries formatted timestamp strings, so this layer only shapes them into the REST envelopes. `TransactionResponseDeleteAt.deleted_at` is always emitted: mapper sets the pointer unconditionally (`""` when the proto `StringValue` wrapper is absent), so passes `""` rather than `None` in that case."""

from __future__ import annotations

from typing import Any

from shared.domain.response.transaction import (
    TransactionMonthlyAmountFailedResponse,
    TransactionMonthlyAmountSuccessResponse,
    TransactionMonthlyMethodResponse,
    TransactionResponse,
    TransactionResponseDeleteAt,
    TransactionYearlyAmountFailedResponse,
    TransactionYearlyAmountSuccessResponse,
    TransactionYearlyMethodResponse,
)
from shared.mapper.order.mapper import map_pagination_meta


def map_transaction_response(pb: Any) -> TransactionResponse:
    return TransactionResponse(
        id=int(pb.id),
        order_id=int(pb.order_id),
        merchant_id=int(pb.merchant_id),
        payment_method=pb.payment_method,
        amount=int(pb.amount),
        payment_status=pb.payment_status,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
    )


def map_transaction_response_delete_at(pb: Any) -> TransactionResponseDeleteAt:
    deleted_at = pb.deleted_at.value if pb.HasField("deleted_at") else ""
    return TransactionResponseDeleteAt(
        id=int(pb.id),
        order_id=int(pb.order_id),
        merchant_id=int(pb.merchant_id),
        payment_method=pb.payment_method,
        amount=int(pb.amount),
        payment_status=pb.payment_status,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
        deleted_at=deleted_at,
    )


def map_monthly_amount_success(
    pb: Any,
) -> TransactionMonthlyAmountSuccessResponse:
    return TransactionMonthlyAmountSuccessResponse(
        year=pb.year,
        month=pb.month,
        total_success=int(pb.total_success),
        total_amount=int(pb.total_amount),
    )


def map_monthly_amount_failed(
    pb: Any,
) -> TransactionMonthlyAmountFailedResponse:
    return TransactionMonthlyAmountFailedResponse(
        year=pb.year,
        month=pb.month,
        total_failed=int(pb.total_failed),
        total_amount=int(pb.total_amount),
    )


def map_yearly_amount_success(
    pb: Any,
) -> TransactionYearlyAmountSuccessResponse:
    return TransactionYearlyAmountSuccessResponse(
        year=pb.year,
        total_success=int(pb.total_success),
        total_amount=int(pb.total_amount),
    )


def map_yearly_amount_failed(
    pb: Any,
) -> TransactionYearlyAmountFailedResponse:
    return TransactionYearlyAmountFailedResponse(
        year=pb.year,
        total_failed=int(pb.total_failed),
        total_amount=int(pb.total_amount),
    )


def map_monthly_method(pb: Any) -> TransactionMonthlyMethodResponse:
    return TransactionMonthlyMethodResponse(
        month=pb.month,
        payment_method=pb.payment_method,
        total_transactions=int(pb.total_transactions),
        total_amount=int(pb.total_amount),
    )


def map_yearly_method(pb: Any) -> TransactionYearlyMethodResponse:
    return TransactionYearlyMethodResponse(
        year=pb.year,
        payment_method=pb.payment_method,
        total_transactions=int(pb.total_transactions),
        total_amount=int(pb.total_amount),
    )


__all__ = [
    "map_monthly_amount_failed",
    "map_monthly_amount_success",
    "map_monthly_method",
    "map_pagination_meta",
    "map_transaction_response",
    "map_transaction_response_delete_at",
    "map_yearly_amount_failed",
    "map_yearly_amount_success",
    "map_yearly_method",
]
