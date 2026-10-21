"""- **SQL-backed transaction repositories** — query, command, stats and stats-by-merchant. - the command repository splits `create` from `create_in_tx`: the latter runs inside the caller's `Database.transaction` connection so the business row and its two outbox events commit atomically (`CreateInTx(*)`)."""

from __future__ import annotations

from typing import Any, Protocol

from pkg.database.schema.order import Order
from pkg.database.schema.order_item import GetOrderItemsByOrderRow
from pkg.database.schema.transaction import (
    GetMonthlyAmountTransactionFailedRow,
    GetMonthlyAmountTransactionSuccessRow,
    GetMonthlyTransactionMethodsRow,
    GetTransactionByIDRow,
    GetTransactionByMerchantRow,
    GetTransactionByOrderIDRow,
    GetTransactionsActiveRow,
    GetTransactionsRow,
    GetTransactionsTrashedRow,
    GetYearlyAmountTransactionFailedRow,
    GetYearlyAmountTransactionSuccessRow,
    GetYearlyTransactionMethodsRow,
    Transaction,
    TransactionRow,
)
from shared.domain.requests.transaction import (
    CreateTransactionRecordRequest,
    FindAllTransaction,
    FindAllTransactionByMerchant,
    MonthAmountTransaction,
    MonthAmountTransactionMerchant,
    MonthMethodTransaction,
    MonthMethodTransactionMerchant,
    UpdateTransactionRecordRequest,
    YearAmountTransactionMerchant,
    YearMethodTransactionMerchant,
)


class UserQueryRepository(Protocol):
    async def find_by_id(self, user_id: int) -> Any: ...


class MerchantQueryRepository(Protocol):
    async def find_by_id(self, merchant_id: int) -> Any: ...


class OrderQueryRepository(Protocol):
    async def find_by_id(self, order_id: int) -> Order: ...


class OrderItemRepository(Protocol):
    async def find_order_item_by_order(
        self, order_id: int
    ) -> list[GetOrderItemsByOrderRow]: ...


class ShippingAddressQueryRepository(Protocol):
    """Returns the raw `ShippingResponse` proto (the order service precedent)."""

    async def find_by_order(self, order_id: int) -> Any: ...


class TransactionQueryRepository(Protocol):
    async def find_all(
        self, request: FindAllTransaction
    ) -> list[GetTransactionsRow]: ...

    async def find_active(
        self, request: FindAllTransaction
    ) -> list[GetTransactionsActiveRow]: ...

    async def find_trashed(
        self, request: FindAllTransaction
    ) -> list[GetTransactionsTrashedRow]: ...

    async def find_by_merchant(
        self, request: FindAllTransactionByMerchant
    ) -> list[GetTransactionByMerchantRow]: ...

    async def find_by_id(self, transaction_id: int) -> GetTransactionByIDRow: ...

    async def find_by_order_id(
        self, order_id: int
    ) -> GetTransactionByOrderIDRow: ...


class TransactionCommandRepository(Protocol):
    async def create(
        self, request: CreateTransactionRecordRequest
    ) -> TransactionRow: ...

    async def create_in_tx(
        self, conn: Any, request: CreateTransactionRecordRequest
    ) -> TransactionRow: ...

    async def update(
        self, request: UpdateTransactionRecordRequest
    ) -> TransactionRow: ...

    async def trash(self, transaction_id: int) -> Transaction: ...

    async def restore(self, transaction_id: int) -> Transaction: ...

    async def delete_permanent(self, transaction_id: int) -> bool: ...

    async def delete_by_order_id_permanent(self, order_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


class TransactionStatsRepository(Protocol):
    async def get_monthly_amount_success(
        self, request: MonthAmountTransaction
    ) -> list[GetMonthlyAmountTransactionSuccessRow]: ...

    async def get_yearly_amount_success(
        self, year: int
    ) -> list[GetYearlyAmountTransactionSuccessRow]: ...

    async def get_monthly_amount_failed(
        self, request: MonthAmountTransaction
    ) -> list[GetMonthlyAmountTransactionFailedRow]: ...

    async def get_yearly_amount_failed(
        self, year: int
    ) -> list[GetYearlyAmountTransactionFailedRow]: ...

    async def get_monthly_transaction_method_success(
        self, request: MonthMethodTransaction
    ) -> list[GetMonthlyTransactionMethodsRow]: ...

    async def get_yearly_transaction_method_success(
        self, year: int
    ) -> list[GetYearlyTransactionMethodsRow]: ...

    async def get_monthly_transaction_method_failed(
        self, request: MonthMethodTransaction
    ) -> list[GetMonthlyTransactionMethodsRow]: ...

    async def get_yearly_transaction_method_failed(
        self, year: int
    ) -> list[GetYearlyTransactionMethodsRow]: ...


class TransactionStatsByMerchantRepository(Protocol):
    async def get_monthly_amount_success_by_merchant(
        self, request: MonthAmountTransactionMerchant
    ) -> list[GetMonthlyAmountTransactionSuccessRow]: ...

    async def get_yearly_amount_success_by_merchant(
        self, request: YearAmountTransactionMerchant
    ) -> list[GetYearlyAmountTransactionSuccessRow]: ...

    async def get_monthly_amount_failed_by_merchant(
        self, request: MonthAmountTransactionMerchant
    ) -> list[GetMonthlyAmountTransactionFailedRow]: ...

    async def get_yearly_amount_failed_by_merchant(
        self, request: YearAmountTransactionMerchant
    ) -> list[GetYearlyAmountTransactionFailedRow]: ...

    async def get_monthly_transaction_method_by_merchant_success(
        self, request: MonthMethodTransactionMerchant
    ) -> list[GetMonthlyTransactionMethodsRow]: ...

    async def get_yearly_transaction_method_by_merchant_success(
        self, request: YearMethodTransactionMerchant
    ) -> list[GetYearlyTransactionMethodsRow]: ...

    async def get_monthly_transaction_method_by_merchant_failed(
        self, request: MonthMethodTransactionMerchant
    ) -> list[GetMonthlyTransactionMethodsRow]: ...

    async def get_yearly_transaction_method_by_merchant_failed(
        self, request: YearMethodTransactionMerchant
    ) -> list[GetYearlyTransactionMethodsRow]: ...


__all__ = [
    "MerchantQueryRepository",
    "OrderItemRepository",
    "OrderQueryRepository",
    "ShippingAddressQueryRepository",
    "TransactionCommandRepository",
    "TransactionQueryRepository",
    "TransactionStatsByMerchantRepository",
    "TransactionStatsRepository",
    "UserQueryRepository",
]
