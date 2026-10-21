"""transaction stats cache. Eight get/set pairs over plain row lists; `Set*` methods skip a nil result, which cannot happen in Python (a failed repo call raises instead), so always caches whatever list the service hands it."""

from __future__ import annotations

from typing import Any

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
    TRANSACTION_MONTHLY_AMOUNT_FAILED_KEY,
    TRANSACTION_MONTHLY_AMOUNT_SUCCESS_KEY,
    TRANSACTION_MONTHLY_METHOD_FAILED_KEY,
    TRANSACTION_MONTHLY_METHOD_SUCCESS_KEY,
    TRANSACTION_YEARLY_AMOUNT_FAILED_KEY,
    TRANSACTION_YEARLY_AMOUNT_SUCCESS_KEY,
    TRANSACTION_YEARLY_METHOD_FAILED_KEY,
    TRANSACTION_YEARLY_METHOD_SUCCESS_KEY,
    TTL_DEFAULT,
)
from shared.cache import CacheStore
from shared.domain.requests.transaction import MonthAmountTransaction, MonthMethodTransaction


class _StoreListMixin:
    """Shared get/set plumbing for the plain row-list stats caches."""

    _store: CacheStore
    _logger: Logger

    async def _get_rows(self, key: str, from_dict: Any) -> list[Any] | None:
        payload = await self._store.get_json(key)
        if not isinstance(payload, list):
            return None
        try:
            return [from_dict(item) for item in payload]
        except (KeyError, TypeError, ValueError) as exc:
            self._logger.error(
                "corrupt transaction stats cache payload dropped", error=str(exc)
            )
            return None

    async def _set_rows(self, key: str, rows: list[Any], to_dict: Any) -> None:
        await self._store.set_json(key, [to_dict(row) for row in rows], TTL_DEFAULT)


class TransactionStatsCacheImpl(_StoreListMixin):
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_monthly_amount_success(
        self, request: MonthAmountTransaction
    ) -> list[GetMonthlyAmountTransactionSuccessRow] | None:
        return await self._get_rows(
            TRANSACTION_MONTHLY_AMOUNT_SUCCESS_KEY
            % (request.month, request.year),
            monthly_amount_success_from_dict,
        )

    async def set_monthly_amount_success(
        self,
        request: MonthAmountTransaction,
        rows: list[GetMonthlyAmountTransactionSuccessRow],
    ) -> None:
        await self._set_rows(
            TRANSACTION_MONTHLY_AMOUNT_SUCCESS_KEY % (request.month, request.year),
            rows,
            monthly_amount_success_to_dict,
        )

    async def get_yearly_amount_success(
        self, year: int
    ) -> list[GetYearlyAmountTransactionSuccessRow] | None:
        return await self._get_rows(
            TRANSACTION_YEARLY_AMOUNT_SUCCESS_KEY % year,
            yearly_amount_success_from_dict,
        )

    async def set_yearly_amount_success(
        self, year: int, rows: list[GetYearlyAmountTransactionSuccessRow]
    ) -> None:
        await self._set_rows(
            TRANSACTION_YEARLY_AMOUNT_SUCCESS_KEY % year,
            rows,
            yearly_amount_success_to_dict,
        )

    async def get_monthly_amount_failed(
        self, request: MonthAmountTransaction
    ) -> list[GetMonthlyAmountTransactionFailedRow] | None:
        return await self._get_rows(
            TRANSACTION_MONTHLY_AMOUNT_FAILED_KEY % (request.month, request.year),
            monthly_amount_failed_from_dict,
        )

    async def set_monthly_amount_failed(
        self,
        request: MonthAmountTransaction,
        rows: list[GetMonthlyAmountTransactionFailedRow],
    ) -> None:
        await self._set_rows(
            TRANSACTION_MONTHLY_AMOUNT_FAILED_KEY % (request.month, request.year),
            rows,
            monthly_amount_failed_to_dict,
        )

    async def get_yearly_amount_failed(
        self, year: int
    ) -> list[GetYearlyAmountTransactionFailedRow] | None:
        return await self._get_rows(
            TRANSACTION_YEARLY_AMOUNT_FAILED_KEY % year,
            yearly_amount_failed_from_dict,
        )

    async def set_yearly_amount_failed(
        self, year: int, rows: list[GetYearlyAmountTransactionFailedRow]
    ) -> None:
        await self._set_rows(
            TRANSACTION_YEARLY_AMOUNT_FAILED_KEY % year,
            rows,
            yearly_amount_failed_to_dict,
        )

    async def get_monthly_method_success(
        self, request: MonthMethodTransaction
    ) -> list[GetMonthlyTransactionMethodsRow] | None:
        return await self._get_rows(
            TRANSACTION_MONTHLY_METHOD_SUCCESS_KEY % (request.month, request.year),
            monthly_method_from_dict,
        )

    async def set_monthly_method_success(
        self,
        request: MonthMethodTransaction,
        rows: list[GetMonthlyTransactionMethodsRow],
    ) -> None:
        await self._set_rows(
            TRANSACTION_MONTHLY_METHOD_SUCCESS_KEY % (request.month, request.year),
            rows,
            monthly_method_to_dict,
        )

    async def get_yearly_method_success(
        self, year: int
    ) -> list[GetYearlyTransactionMethodsRow] | None:
        return await self._get_rows(
            TRANSACTION_YEARLY_METHOD_SUCCESS_KEY % year,
            yearly_method_from_dict,
        )

    async def set_yearly_method_success(
        self, year: int, rows: list[GetYearlyTransactionMethodsRow]
    ) -> None:
        await self._set_rows(
            TRANSACTION_YEARLY_METHOD_SUCCESS_KEY % year,
            rows,
            yearly_method_to_dict,
        )

    async def get_monthly_method_failed(
        self, request: MonthMethodTransaction
    ) -> list[GetMonthlyTransactionMethodsRow] | None:
        return await self._get_rows(
            TRANSACTION_MONTHLY_METHOD_FAILED_KEY % (request.month, request.year),
            monthly_method_from_dict,
        )

    async def set_monthly_method_failed(
        self,
        request: MonthMethodTransaction,
        rows: list[GetMonthlyTransactionMethodsRow],
    ) -> None:
        await self._set_rows(
            TRANSACTION_MONTHLY_METHOD_FAILED_KEY % (request.month, request.year),
            rows,
            monthly_method_to_dict,
        )

    async def get_yearly_method_failed(
        self, year: int
    ) -> list[GetYearlyTransactionMethodsRow] | None:
        return await self._get_rows(
            TRANSACTION_YEARLY_METHOD_FAILED_KEY % year,
            yearly_method_from_dict,
        )

    async def set_yearly_method_failed(
        self, year: int, rows: list[GetYearlyTransactionMethodsRow]
    ) -> None:
        await self._set_rows(
            TRANSACTION_YEARLY_METHOD_FAILED_KEY % year,
            rows,
            yearly_method_to_dict,
        )


__all__ = ["TransactionStatsCacheImpl"]
