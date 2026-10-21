"""transaction cache"""

from __future__ import annotations

from typing import Protocol

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
from shared.domain.requests.transaction import (
    FindAllTransaction,
    FindAllTransactionByMerchant,
    MonthAmountTransaction,
    MonthAmountTransactionMerchant,
    MonthMethodTransaction,
    MonthMethodTransactionMerchant,
    YearAmountTransactionMerchant,
    YearMethodTransactionMerchant,
)


class TransactionQueryCache(Protocol):
    async def get_all(
        self, request: FindAllTransaction
    ) -> tuple[list[GetTransactionsRow], int] | None: ...

    async def set_all(
        self, request: FindAllTransaction, rows: list[GetTransactionsRow], total: int
    ) -> None: ...

    async def get_by_merchant(
        self, request: FindAllTransactionByMerchant
    ) -> tuple[list[GetTransactionsRow], int] | None: ...

    async def set_by_merchant(
        self,
        request: FindAllTransactionByMerchant,
        rows: list[GetTransactionsRow],
        total: int,
    ) -> None: ...

    async def get_active(
        self, request: FindAllTransaction
    ) -> tuple[list[GetTransactionsRow], int] | None: ...

    async def set_active(
        self, request: FindAllTransaction, rows: list[GetTransactionsRow], total: int
    ) -> None: ...

    async def get_trashed(
        self, request: FindAllTransaction
    ) -> tuple[list[GetTransactionsRow], int] | None: ...

    async def set_trashed(
        self, request: FindAllTransaction, rows: list[GetTransactionsRow], total: int
    ) -> None: ...

    async def get_by_id(self, transaction_id: int) -> GetTransactionByIDRow | None: ...

    async def set_by_id(self, row: GetTransactionByIDRow) -> None: ...

    async def get_by_order(
        self, order_id: int
    ) -> GetTransactionByOrderIDRow | None: ...

    async def set_by_order(self, order_id: int, row: GetTransactionByOrderIDRow) -> None: ...


class TransactionCommandCache(Protocol):
    async def delete_transaction_cache(self, transaction_id: int) -> int: ...

    async def invalidate_transaction_cache(self) -> int: ...


class TransactionStatsCache(Protocol):
    async def get_monthly_amount_success(
        self, request: MonthAmountTransaction
    ) -> list[GetMonthlyAmountTransactionSuccessRow] | None: ...

    async def set_monthly_amount_success(
        self, request: MonthAmountTransaction, rows: list[GetMonthlyAmountTransactionSuccessRow]
    ) -> None: ...

    async def get_yearly_amount_success(
        self, year: int
    ) -> list[GetYearlyAmountTransactionSuccessRow] | None: ...

    async def set_yearly_amount_success(
        self, year: int, rows: list[GetYearlyAmountTransactionSuccessRow]
    ) -> None: ...

    async def get_monthly_amount_failed(
        self, request: MonthAmountTransaction
    ) -> list[GetMonthlyAmountTransactionFailedRow] | None: ...

    async def set_monthly_amount_failed(
        self, request: MonthAmountTransaction, rows: list[GetMonthlyAmountTransactionFailedRow]
    ) -> None: ...

    async def get_yearly_amount_failed(
        self, year: int
    ) -> list[GetYearlyAmountTransactionFailedRow] | None: ...

    async def set_yearly_amount_failed(
        self, year: int, rows: list[GetYearlyAmountTransactionFailedRow]
    ) -> None: ...

    async def get_monthly_method_success(
        self, request: MonthMethodTransaction
    ) -> list[GetMonthlyTransactionMethodsRow] | None: ...

    async def set_monthly_method_success(
        self, request: MonthMethodTransaction, rows: list[GetMonthlyTransactionMethodsRow]
    ) -> None: ...

    async def get_yearly_method_success(
        self, year: int
    ) -> list[GetYearlyTransactionMethodsRow] | None: ...

    async def set_yearly_method_success(
        self, year: int, rows: list[GetYearlyTransactionMethodsRow]
    ) -> None: ...

    async def get_monthly_method_failed(
        self, request: MonthMethodTransaction
    ) -> list[GetMonthlyTransactionMethodsRow] | None: ...

    async def set_monthly_method_failed(
        self, request: MonthMethodTransaction, rows: list[GetMonthlyTransactionMethodsRow]
    ) -> None: ...

    async def get_yearly_method_failed(
        self, year: int
    ) -> list[GetYearlyTransactionMethodsRow] | None: ...

    async def set_yearly_method_failed(
        self, year: int, rows: list[GetYearlyTransactionMethodsRow]
    ) -> None: ...


class TransactionStatsByMerchantCache(Protocol):
    async def get_monthly_amount_success_by_merchant(
        self, request: MonthAmountTransactionMerchant
    ) -> list[GetMonthlyAmountTransactionSuccessRow] | None: ...

    async def set_monthly_amount_success_by_merchant(
        self, request: MonthAmountTransactionMerchant, rows: list[GetMonthlyAmountTransactionSuccessRow]
    ) -> None: ...

    async def get_yearly_amount_success_by_merchant(
        self, request: YearAmountTransactionMerchant
    ) -> list[GetYearlyAmountTransactionSuccessRow] | None: ...

    async def set_yearly_amount_success_by_merchant(
        self, request: YearAmountTransactionMerchant, rows: list[GetYearlyAmountTransactionSuccessRow]
    ) -> None: ...

    async def get_monthly_amount_failed_by_merchant(
        self, request: MonthAmountTransactionMerchant
    ) -> list[GetMonthlyAmountTransactionFailedRow] | None: ...

    async def set_monthly_amount_failed_by_merchant(
        self, request: MonthAmountTransactionMerchant, rows: list[GetMonthlyAmountTransactionFailedRow]
    ) -> None: ...

    async def get_yearly_amount_failed_by_merchant(
        self, request: YearAmountTransactionMerchant
    ) -> list[GetYearlyAmountTransactionFailedRow] | None: ...

    async def set_yearly_amount_failed_by_merchant(
        self, request: YearAmountTransactionMerchant, rows: list[GetYearlyAmountTransactionFailedRow]
    ) -> None: ...

    async def get_monthly_method_success_by_merchant(
        self, request: MonthMethodTransactionMerchant
    ) -> list[GetMonthlyTransactionMethodsRow] | None: ...

    async def set_monthly_method_success_by_merchant(
        self, request: MonthMethodTransactionMerchant, rows: list[GetMonthlyTransactionMethodsRow]
    ) -> None: ...

    async def get_yearly_method_success_by_merchant(
        self, request: YearMethodTransactionMerchant
    ) -> list[GetYearlyTransactionMethodsRow] | None: ...

    async def set_yearly_method_success_by_merchant(
        self, request: YearMethodTransactionMerchant, rows: list[GetYearlyTransactionMethodsRow]
    ) -> None: ...

    async def get_monthly_method_failed_by_merchant(
        self, request: MonthMethodTransactionMerchant
    ) -> list[GetMonthlyTransactionMethodsRow] | None: ...

    async def set_monthly_method_failed_by_merchant(
        self, request: MonthMethodTransactionMerchant, rows: list[GetMonthlyTransactionMethodsRow]
    ) -> None: ...

    async def get_yearly_method_failed_by_merchant(
        self, request: YearMethodTransactionMerchant
    ) -> list[GetYearlyTransactionMethodsRow] | None: ...

    async def set_yearly_method_failed_by_merchant(
        self, request: YearMethodTransactionMerchant, rows: list[GetYearlyTransactionMethodsRow]
    ) -> None: ...


__all__ = [
    "TransactionCommandCache",
    "TransactionQueryCache",
    "TransactionStatsByMerchantCache",
    "TransactionStatsCache",
]
