"""Row <-> JSON helpers for the transaction cache.

Each projection has its own encoder/decoder because the column sets differ
(page rows carry the window total and possibly `deleted_at`; by-id/by-order
rows are the bare base; the four stats shapes are plain value rows).
Timestamps are stored as ISO-8601 strings; `total_count` is stored alongside
the page rather than per row.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pkg.database.schema.transaction import (
    GetMonthlyAmountTransactionFailedRow,
    GetMonthlyAmountTransactionSuccessRow,
    GetMonthlyTransactionMethodsRow,
    GetTransactionByIDRow,
    GetTransactionByOrderIDRow,
    GetTransactionsRow,
    GetYearlyAmountTransactionFailedRow,
    GetYearlyAmountTransactionSuccessRow,
    GetYearlyTransactionMethodsRow,
)


def _iso(value: datetime) -> str:
    return value.isoformat()


def _iso_opt(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt_required(value: Any) -> datetime:
    if not value:
        raise ValueError("required timestamp missing from cached transaction payload")
    return datetime.fromisoformat(value)


def _dt_opt(value: Any) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


# ---- page rows (FindAll / Active / Trashed / ByMerchant share the shape) ----


def transactions_row_to_dict(row: GetTransactionsRow) -> dict[str, Any]:
    return {
        "transaction_id": row.transaction_id,
        "order_id": row.order_id,
        "merchant_id": row.merchant_id,
        "payment_method": row.payment_method,
        "amount": row.amount,
        "payment_status": row.payment_status,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
        "deleted_at": _iso_opt(row.deleted_at),
    }


def transactions_row_from_dict(
    data: dict[str, Any], total: int
) -> GetTransactionsRow:
    return GetTransactionsRow(
        transaction_id=int(data["transaction_id"]),
        order_id=int(data["order_id"]),
        merchant_id=int(data["merchant_id"]),
        payment_method=data["payment_method"],
        amount=int(data["amount"]),
        payment_status=data["payment_status"],
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
        deleted_at=_dt_opt(data.get("deleted_at")),
        total_count=total,
    )


# ---- by-id / by-order rows (bare base projection) ----


def transaction_by_id_to_dict(row: GetTransactionByIDRow) -> dict[str, Any]:
    return {
        "transaction_id": row.transaction_id,
        "order_id": row.order_id,
        "merchant_id": row.merchant_id,
        "payment_method": row.payment_method,
        "amount": row.amount,
        "payment_status": row.payment_status,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


def transaction_by_id_from_dict(data: dict[str, Any]) -> GetTransactionByIDRow:
    return GetTransactionByIDRow(
        transaction_id=int(data["transaction_id"]),
        order_id=int(data["order_id"]),
        merchant_id=int(data["merchant_id"]),
        payment_method=data["payment_method"],
        amount=int(data["amount"]),
        payment_status=data["payment_status"],
        created_at=_dt_required(data.get("created_at")),
        updated_at=_dt_required(data.get("updated_at")),
    )


def transaction_by_order_to_dict(row: GetTransactionByOrderIDRow) -> dict[str, Any]:
    return transaction_by_id_to_dict(row)


def transaction_by_order_from_dict(data: dict[str, Any]) -> GetTransactionByOrderIDRow:
    return transaction_by_id_from_dict(data)


# ---- stats rows ----


def monthly_amount_success_to_dict(
    row: GetMonthlyAmountTransactionSuccessRow,
) -> dict[str, Any]:
    return {
        "year": row.year,
        "month": row.month,
        "total_success": row.total_success,
        "total_amount": row.total_amount,
    }


def monthly_amount_success_from_dict(data: dict[str, Any]) -> (
    GetMonthlyAmountTransactionSuccessRow
):
    return GetMonthlyAmountTransactionSuccessRow(
        year=data["year"],
        month=data["month"],
        total_success=int(data["total_success"]),
        total_amount=int(data["total_amount"]),
    )


def monthly_amount_failed_to_dict(
    row: GetMonthlyAmountTransactionFailedRow,
) -> dict[str, Any]:
    return {
        "year": row.year,
        "month": row.month,
        "total_failed": row.total_failed,
        "total_amount": row.total_amount,
    }


def monthly_amount_failed_from_dict(data: dict[str, Any]) -> (
    GetMonthlyAmountTransactionFailedRow
):
    return GetMonthlyAmountTransactionFailedRow(
        year=data["year"],
        month=data["month"],
        total_failed=int(data["total_failed"]),
        total_amount=int(data["total_amount"]),
    )


def yearly_amount_success_to_dict(
    row: GetYearlyAmountTransactionSuccessRow,
) -> dict[str, Any]:
    return {
        "year": row.year,
        "total_success": row.total_success,
        "total_amount": row.total_amount,
    }


def yearly_amount_success_from_dict(data: dict[str, Any]) -> (
    GetYearlyAmountTransactionSuccessRow
):
    return GetYearlyAmountTransactionSuccessRow(
        year=data["year"],
        total_success=int(data["total_success"]),
        total_amount=int(data["total_amount"]),
    )


def yearly_amount_failed_to_dict(
    row: GetYearlyAmountTransactionFailedRow,
) -> dict[str, Any]:
    return {
        "year": row.year,
        "total_failed": row.total_failed,
        "total_amount": row.total_amount,
    }


def yearly_amount_failed_from_dict(data: dict[str, Any]) -> (
    GetYearlyAmountTransactionFailedRow
):
    return GetYearlyAmountTransactionFailedRow(
        year=data["year"],
        total_failed=int(data["total_failed"]),
        total_amount=int(data["total_amount"]),
    )


def monthly_method_to_dict(row: GetMonthlyTransactionMethodsRow) -> dict[str, Any]:
    return {
        "month": row.month,
        "payment_method": row.payment_method,
        "total_transactions": row.total_transactions,
        "total_amount": row.total_amount,
    }


def monthly_method_from_dict(data: dict[str, Any]) -> GetMonthlyTransactionMethodsRow:
    return GetMonthlyTransactionMethodsRow(
        month=data["month"],
        payment_method=data["payment_method"],
        total_transactions=int(data["total_transactions"]),
        total_amount=int(data["total_amount"]),
    )


def yearly_method_to_dict(row: GetYearlyTransactionMethodsRow) -> dict[str, Any]:
    return {
        "year": row.year,
        "payment_method": row.payment_method,
        "total_transactions": row.total_transactions,
        "total_amount": row.total_amount,
    }


def yearly_method_from_dict(data: dict[str, Any]) -> GetYearlyTransactionMethodsRow:
    return GetYearlyTransactionMethodsRow(
        year=data["year"],
        payment_method=data["payment_method"],
        total_transactions=int(data["total_transactions"]),
        total_amount=int(data["total_amount"]),
    )


__all__ = [
    "monthly_amount_failed_from_dict",
    "monthly_amount_failed_to_dict",
    "monthly_amount_success_from_dict",
    "monthly_amount_success_to_dict",
    "monthly_method_from_dict",
    "monthly_method_to_dict",
    "transaction_by_id_from_dict",
    "transaction_by_id_to_dict",
    "transaction_by_order_from_dict",
    "transaction_by_order_to_dict",
    "transactions_row_from_dict",
    "transactions_row_to_dict",
    "yearly_amount_failed_from_dict",
    "yearly_amount_failed_to_dict",
    "yearly_amount_success_from_dict",
    "yearly_amount_success_to_dict",
    "yearly_method_from_dict",
    "yearly_method_to_dict",
]
