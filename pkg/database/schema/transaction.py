"""Row types for the `transactions` table. Stats rows keep the SQL column types exactly (`total_amount` is `::integer` on the amount rows but `::NUMERIC` on the method rows; the row coercion Matches the expected handlers' `int32(...)` casts). Transaction timestamps are formatted `%Y-%m-%d %H:%M:%S` (seconds, NO millis) by the handler — unlike order/order_item which keep `.mmm`."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Transaction:

    transaction_id: int
    order_id: int
    merchant_id: int
    payment_method: str
    amount: int
    payment_status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> Transaction:
        return cls(
            transaction_id=row["transaction_id"],
            order_id=row["order_id"],
            merchant_id=row["merchant_id"],
            payment_method=row["payment_method"],
            amount=int(row["amount"]),
            payment_status=row["payment_status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class TransactionRow:
    """Base projection (`CreateTransaction` / `UpdateTransaction` / by-id)."""

    transaction_id: int
    order_id: int
    merchant_id: int
    payment_method: str
    amount: int
    payment_status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> TransactionRow:
        return cls(
            transaction_id=row["transaction_id"],
            order_id=row["order_id"],
            merchant_id=row["merchant_id"],
            payment_method=row["payment_method"],
            amount=int(row["amount"]),
            payment_status=row["payment_status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


# declares distinct names with identical fields.
CreateTransactionRow = TransactionRow
UpdateTransactionRow = TransactionRow
GetTransactionByIDRow = TransactionRow
GetTransactionByOrderIDRow = TransactionRow


@dataclass
class GetTransactionsRow:
    """`GetTransactions` (FindAll) projection: `SELECT *` + window total."""

    transaction_id: int
    order_id: int
    merchant_id: int
    payment_method: str
    amount: int
    payment_status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    total_count: int = 0

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetTransactionsRow:
        return cls(
            transaction_id=row["transaction_id"],
            order_id=row["order_id"],
            merchant_id=row["merchant_id"],
            payment_method=row["payment_method"],
            amount=int(row["amount"]),
            payment_status=row["payment_status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            total_count=int(row["total_count"]),
        )


# `GetTransactionsActive` / `GetTransactionsTrashed` / `GetTransactionByMerchant`
# have the same projection as `GetTransactions` (declares distinct names).
GetTransactionsActiveRow = GetTransactionsRow
GetTransactionsTrashedRow = GetTransactionsRow
GetTransactionByMerchantRow = GetTransactionsRow


@dataclass
class GetMonthlyAmountTransactionSuccessRow:
    """Monthly success amount (`GetMonthlyAmountTransactionSuccessRow`)."""

    year: str
    month: str
    total_success: int
    total_amount: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMonthlyAmountTransactionSuccessRow:
        return cls(
            year=str(row["year"]),
            month=str(row["month"]),
            total_success=int(row["total_success"]),
            total_amount=int(row["total_amount"]),
        )


@dataclass
class GetMonthlyAmountTransactionFailedRow:
    """Monthly failed amount (`GetMonthlyAmountTransactionFailedRow`)."""

    year: str
    month: str
    total_failed: int
    total_amount: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMonthlyAmountTransactionFailedRow:
        return cls(
            year=str(row["year"]),
            month=str(row["month"]),
            total_failed=int(row["total_failed"]),
            total_amount=int(row["total_amount"]),
        )


@dataclass
class GetYearlyAmountTransactionSuccessRow:
    """Yearly success amount (`GetYearlyAmountTransactionSuccessRow`)."""

    year: str
    total_success: int
    total_amount: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetYearlyAmountTransactionSuccessRow:
        return cls(
            year=str(row["year"]),
            total_success=int(row["total_success"]),
            total_amount=int(row["total_amount"]),
        )


@dataclass
class GetYearlyAmountTransactionFailedRow:
    """Yearly failed amount (`GetYearlyAmountTransactionFailedRow`)."""

    year: str
    total_failed: int
    total_amount: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetYearlyAmountTransactionFailedRow:
        return cls(
            year=str(row["year"]),
            total_failed=int(row["total_failed"]),
            total_amount=int(row["total_amount"]),
        )


@dataclass
class GetMonthlyTransactionMethodsRow:
    """Monthly method breakdown (`GetMonthlyTransactionMethods{Success,Failed}Row`). types `total_amount` as `float64` because the SQL casts to `::NUMERIC`; the handler immediately truncates to int32 for the proto, so coerces to int at the row boundary instead."""

    month: str
    payment_method: str
    total_transactions: int
    total_amount: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMonthlyTransactionMethodsRow:
        return cls(
            month=str(row["month"]),
            payment_method=row["payment_method"],
            total_transactions=int(row["total_transactions"]),
            total_amount=int(row["total_amount"]),
        )


@dataclass
class GetYearlyTransactionMethodsRow:
    """Yearly method breakdown (`GetYearlyTransactionMethods{Success,Failed}Row`)."""

    year: str
    payment_method: str
    total_transactions: int
    total_amount: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetYearlyTransactionMethodsRow:
        return cls(
            year=str(row["year"]),
            payment_method=row["payment_method"],
            total_transactions=int(row["total_transactions"]),
            total_amount=int(row["total_amount"]),
        )


# The by-merchant stats SQL selects the same columns as the global stats
# (declares distinct struct names with identical fields).
GetMonthlyAmountTransactionSuccessByMerchantRow = (
    GetMonthlyAmountTransactionSuccessRow
)
GetMonthlyAmountTransactionFailedByMerchantRow = (
    GetMonthlyAmountTransactionFailedRow
)
GetYearlyAmountTransactionSuccessByMerchantRow = GetYearlyAmountTransactionSuccessRow
GetYearlyAmountTransactionFailedByMerchantRow = GetYearlyAmountTransactionFailedRow
GetMonthlyTransactionMethodsByMerchantSuccessRow = GetMonthlyTransactionMethodsRow
GetMonthlyTransactionMethodsByMerchantFailedRow = GetMonthlyTransactionMethodsRow
GetYearlyTransactionMethodsByMerchantSuccessRow = GetYearlyTransactionMethodsRow
GetYearlyTransactionMethodsByMerchantFailedRow = GetYearlyTransactionMethodsRow


__all__ = [
    "CreateTransactionRow",
    "GetMonthlyAmountTransactionFailedByMerchantRow",
    "GetMonthlyAmountTransactionFailedRow",
    "GetMonthlyAmountTransactionSuccessByMerchantRow",
    "GetMonthlyAmountTransactionSuccessRow",
    "GetMonthlyTransactionMethodsByMerchantFailedRow",
    "GetMonthlyTransactionMethodsByMerchantSuccessRow",
    "GetMonthlyTransactionMethodsRow",
    "GetTransactionByMerchantRow",
    "GetTransactionByOrderIDRow",
    "GetTransactionsActiveRow",
    "GetTransactionsRow",
    "GetTransactionsTrashedRow",
    "GetTransactionByIDRow",
    "GetYearlyAmountTransactionFailedByMerchantRow",
    "GetYearlyAmountTransactionFailedRow",
    "GetYearlyAmountTransactionSuccessByMerchantRow",
    "GetYearlyAmountTransactionSuccessRow",
    "GetYearlyTransactionMethodsByMerchantFailedRow",
    "GetYearlyTransactionMethodsByMerchantSuccessRow",
    "GetYearlyTransactionMethodsRow",
    "Transaction",
    "TransactionRow",
    "UpdateTransactionRow",
]
