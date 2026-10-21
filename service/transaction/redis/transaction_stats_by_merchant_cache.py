"""transaction stats-by-merchant cache. Same plumbing as the global stats cache; the keys carry the merchant id (`transacton...` key-name typos are not reproducible in Python — the key *strings* themselves are verbatim)."""

from __future__ import annotations

from pkg.database.schema.transaction import (
    GetMonthlyAmountTransactionFailedRow,
    GetMonthlyAmountTransactionSuccessRow,
    GetMonthlyTransactionMethodsRow,
    GetYearlyAmountTransactionFailedRow,
    GetYearlyAmountTransactionSuccessRow,
    GetYearlyTransactionMethodsRow,
)
from pkg.logger.logger import Logger
from service.transaction.redis.cache import (
    monthly_amount_failed_from_dict,
    monthly_amount_failed_to_dict,
    monthly_amount_success_from_dict,
    monthly_amount_success_to_dict,
    monthly_method_from_dict,
    monthly_method_to_dict,
    yearly_amount_failed_from_dict,
    yearly_amount_failed_to_dict,
    yearly_amount_success_from_dict,
    yearly_amount_success_to_dict,
    yearly_method_from_dict,
    yearly_method_to_dict,
)
from service.transaction.redis.common import (
    TRANSACTION_MONTHLY_AMOUNT_FAILED_BY_MERCHANT_KEY,
    TRANSACTION_MONTHLY_AMOUNT_SUCCESS_BY_MERCHANT_KEY,
    TRANSACTION_MONTHLY_METHOD_FAILED_BY_MERCHANT_KEY,
    TRANSACTION_MONTHLY_METHOD_SUCCESS_BY_MERCHANT_KEY,
    TRANSACTION_YEARLY_AMOUNT_FAILED_BY_MERCHANT_KEY,
    TRANSACTION_YEARLY_AMOUNT_SUCCESS_BY_MERCHANT_KEY,
    TRANSACTION_YEARLY_METHOD_FAILED_BY_MERCHANT_KEY,
    TRANSACTION_YEARLY_METHOD_SUCCESS_BY_MERCHANT_KEY,
)
from service.transaction.redis.transaction_stats_cache import _StoreListMixin
from shared.cache import CacheStore
from shared.domain.requests.transaction import (
    MonthAmountTransactionMerchant,
    MonthMethodTransactionMerchant,
    YearAmountTransactionMerchant,
    YearMethodTransactionMerchant,
)


class TransactionStatsByMerchantCacheImpl(_StoreListMixin):
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_monthly_amount_success_by_merchant(
        self, request: MonthAmountTransactionMerchant
    ) -> list[GetMonthlyAmountTransactionSuccessRow] | None:
        return await self._get_rows(
            TRANSACTION_MONTHLY_AMOUNT_SUCCESS_BY_MERCHANT_KEY
            % (request.merchant_id, request.month, request.year),
            monthly_amount_success_from_dict,
        )

    async def set_monthly_amount_success_by_merchant(
        self,
        request: MonthAmountTransactionMerchant,
        rows: list[GetMonthlyAmountTransactionSuccessRow],
    ) -> None:
        await self._set_rows(
            TRANSACTION_MONTHLY_AMOUNT_SUCCESS_BY_MERCHANT_KEY
            % (request.merchant_id, request.month, request.year),
            rows,
            monthly_amount_success_to_dict,
        )

    async def get_yearly_amount_success_by_merchant(
        self, request: YearAmountTransactionMerchant
    ) -> list[GetYearlyAmountTransactionSuccessRow] | None:
        return await self._get_rows(
            TRANSACTION_YEARLY_AMOUNT_SUCCESS_BY_MERCHANT_KEY
            % (request.merchant_id, request.year),
            yearly_amount_success_from_dict,
        )

    async def set_yearly_amount_success_by_merchant(
        self,
        request: YearAmountTransactionMerchant,
        rows: list[GetYearlyAmountTransactionSuccessRow],
    ) -> None:
        await self._set_rows(
            TRANSACTION_YEARLY_AMOUNT_SUCCESS_BY_MERCHANT_KEY
            % (request.merchant_id, request.year),
            rows,
            yearly_amount_success_to_dict,
        )

    async def get_monthly_amount_failed_by_merchant(
        self, request: MonthAmountTransactionMerchant
    ) -> list[GetMonthlyAmountTransactionFailedRow] | None:
        return await self._get_rows(
            TRANSACTION_MONTHLY_AMOUNT_FAILED_BY_MERCHANT_KEY
            % (request.merchant_id, request.month, request.year),
            monthly_amount_failed_from_dict,
        )

    async def set_monthly_amount_failed_by_merchant(
        self,
        request: MonthAmountTransactionMerchant,
        rows: list[GetMonthlyAmountTransactionFailedRow],
    ) -> None:
        await self._set_rows(
            TRANSACTION_MONTHLY_AMOUNT_FAILED_BY_MERCHANT_KEY
            % (request.merchant_id, request.month, request.year),
            rows,
            monthly_amount_failed_to_dict,
        )

    async def get_yearly_amount_failed_by_merchant(
        self, request: YearAmountTransactionMerchant
    ) -> list[GetYearlyAmountTransactionFailedRow] | None:
        return await self._get_rows(
            TRANSACTION_YEARLY_AMOUNT_FAILED_BY_MERCHANT_KEY
            % (request.merchant_id, request.year),
            yearly_amount_failed_from_dict,
        )

    async def set_yearly_amount_failed_by_merchant(
        self,
        request: YearAmountTransactionMerchant,
        rows: list[GetYearlyAmountTransactionFailedRow],
    ) -> None:
        await self._set_rows(
            TRANSACTION_YEARLY_AMOUNT_FAILED_BY_MERCHANT_KEY
            % (request.merchant_id, request.year),
            rows,
            yearly_amount_failed_to_dict,
        )

    async def get_monthly_method_success_by_merchant(
        self, request: MonthMethodTransactionMerchant
    ) -> list[GetMonthlyTransactionMethodsRow] | None:
        return await self._get_rows(
            TRANSACTION_MONTHLY_METHOD_SUCCESS_BY_MERCHANT_KEY
            % (request.merchant_id, request.month, request.year),
            monthly_method_from_dict,
        )

    async def set_monthly_method_success_by_merchant(
        self,
        request: MonthMethodTransactionMerchant,
        rows: list[GetMonthlyTransactionMethodsRow],
    ) -> None:
        await self._set_rows(
            TRANSACTION_MONTHLY_METHOD_SUCCESS_BY_MERCHANT_KEY
            % (request.merchant_id, request.month, request.year),
            rows,
            monthly_method_to_dict,
        )

    async def get_yearly_method_success_by_merchant(
        self, request: YearMethodTransactionMerchant
    ) -> list[GetYearlyTransactionMethodsRow] | None:
        return await self._get_rows(
            TRANSACTION_YEARLY_METHOD_SUCCESS_BY_MERCHANT_KEY
            % (request.merchant_id, request.year),
            yearly_method_from_dict,
        )

    async def set_yearly_method_success_by_merchant(
        self,
        request: YearMethodTransactionMerchant,
        rows: list[GetYearlyTransactionMethodsRow],
    ) -> None:
        await self._set_rows(
            TRANSACTION_YEARLY_METHOD_SUCCESS_BY_MERCHANT_KEY
            % (request.merchant_id, request.year),
            rows,
            yearly_method_to_dict,
        )

    async def get_monthly_method_failed_by_merchant(
        self, request: MonthMethodTransactionMerchant
    ) -> list[GetMonthlyTransactionMethodsRow] | None:
        return await self._get_rows(
            TRANSACTION_MONTHLY_METHOD_FAILED_BY_MERCHANT_KEY
            % (request.merchant_id, request.month, request.year),
            monthly_method_from_dict,
        )

    async def set_monthly_method_failed_by_merchant(
        self,
        request: MonthMethodTransactionMerchant,
        rows: list[GetMonthlyTransactionMethodsRow],
    ) -> None:
        await self._set_rows(
            TRANSACTION_MONTHLY_METHOD_FAILED_BY_MERCHANT_KEY
            % (request.merchant_id, request.month, request.year),
            rows,
            monthly_method_to_dict,
        )

    async def get_yearly_method_failed_by_merchant(
        self, request: YearMethodTransactionMerchant
    ) -> list[GetYearlyTransactionMethodsRow] | None:
        return await self._get_rows(
            TRANSACTION_YEARLY_METHOD_FAILED_BY_MERCHANT_KEY
            % (request.merchant_id, request.year),
            yearly_method_from_dict,
        )

    async def set_yearly_method_failed_by_merchant(
        self,
        request: YearMethodTransactionMerchant,
        rows: list[GetYearlyTransactionMethodsRow],
    ) -> None:
        await self._set_rows(
            TRANSACTION_YEARLY_METHOD_FAILED_BY_MERCHANT_KEY
            % (request.merchant_id, request.year),
            rows,
            yearly_method_to_dict,
        )


__all__ = ["TransactionStatsByMerchantCacheImpl"]
