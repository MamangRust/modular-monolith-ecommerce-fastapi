"""transaction service"""

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
    Transaction,
    TransactionRow,
)
from shared.domain.requests.transaction import (
    CreateTransactionRequest,
    FindAllTransaction,
    FindAllTransactionByMerchant,
    MonthAmountTransaction,
    MonthAmountTransactionMerchant,
    MonthMethodTransaction,
    MonthMethodTransactionMerchant,
    UpdateTransactionRequest,
    YearAmountTransactionMerchant,
    YearMethodTransactionMerchant,
)


class TransactionQueryService(Protocol):
    async def find_all(
        self, request: FindAllTransaction
    ) -> tuple[list[GetTransactionsRow], int]: ...

    async def find_by_merchant(
        self, request: FindAllTransactionByMerchant
    ) -> tuple[list[GetTransactionsRow], int]: ...

    async def find_by_id(self, transaction_id: int) -> GetTransactionByIDRow: ...

    async def find_by_order_id(
        self, order_id: int
    ) -> GetTransactionByOrderIDRow: ...

    async def find_active(
        self, request: FindAllTransaction
    ) -> tuple[list[GetTransactionsRow], int]: ...

    async def find_trashed(
        self, request: FindAllTransaction
    ) -> tuple[list[GetTransactionsRow], int]: ...


class TransactionCommandService(Protocol):
    async def create(self, request: CreateTransactionRequest) -> TransactionRow: ...

    async def update(self, request: UpdateTransactionRequest) -> TransactionRow: ...

    async def trash(self, transaction_id: int) -> Transaction: ...

    async def restore(self, transaction_id: int) -> Transaction: ...

    async def delete_permanent(self, transaction_id: int) -> bool: ...

    async def delete_by_order_id_permanent(self, order_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


class TransactionStatsService(Protocol):
    async def find_monthly_amount_success(
        self, request: MonthAmountTransaction
    ) -> list[GetMonthlyAmountTransactionSuccessRow]: ...

    async def find_yearly_amount_success(
        self, year: int
    ) -> list[GetYearlyAmountTransactionSuccessRow]: ...

    async def find_monthly_amount_failed(
        self, request: MonthAmountTransaction
    ) -> list[GetMonthlyAmountTransactionFailedRow]: ...

    async def find_yearly_amount_failed(
        self, year: int
    ) -> list[GetYearlyAmountTransactionFailedRow]: ...

    async def find_monthly_method_success(
        self, request: MonthMethodTransaction
    ) -> list[GetMonthlyTransactionMethodsRow]: ...

    async def find_yearly_method_success(
        self, year: int
    ) -> list[GetYearlyTransactionMethodsRow]: ...

    async def find_monthly_method_failed(
        self, request: MonthMethodTransaction
    ) -> list[GetMonthlyTransactionMethodsRow]: ...

    async def find_yearly_method_failed(
        self, year: int
    ) -> list[GetYearlyTransactionMethodsRow]: ...


class TransactionStatsByMerchantService(Protocol):
    async def find_monthly_amount_success_by_merchant(
        self, request: MonthAmountTransactionMerchant
    ) -> list[GetMonthlyAmountTransactionSuccessRow]: ...

    async def find_yearly_amount_success_by_merchant(
        self, request: YearAmountTransactionMerchant
    ) -> list[GetYearlyAmountTransactionSuccessRow]: ...

    async def find_monthly_amount_failed_by_merchant(
        self, request: MonthAmountTransactionMerchant
    ) -> list[GetMonthlyAmountTransactionFailedRow]: ...

    async def find_yearly_amount_failed_by_merchant(
        self, request: YearAmountTransactionMerchant
    ) -> list[GetYearlyAmountTransactionFailedRow]: ...

    async def find_monthly_method_success_by_merchant(
        self, request: MonthMethodTransactionMerchant
    ) -> list[GetMonthlyTransactionMethodsRow]: ...

    async def find_yearly_method_success_by_merchant(
        self, request: YearMethodTransactionMerchant
    ) -> list[GetYearlyTransactionMethodsRow]: ...

    async def find_monthly_method_failed_by_merchant(
        self, request: MonthMethodTransactionMerchant
    ) -> list[GetMonthlyTransactionMethodsRow]: ...

    async def find_yearly_method_failed_by_merchant(
        self, request: YearMethodTransactionMerchant
    ) -> list[GetYearlyTransactionMethodsRow]: ...


__all__ = [
    "TransactionCommandService",
    "TransactionQueryService",
    "TransactionStatsByMerchantService",
    "TransactionStatsService",
]
