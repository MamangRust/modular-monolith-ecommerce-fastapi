"""Merchant query cache.

Every list cache written here is also read. Reads/writes never raise:
`CacheStore` swallows Redis errors so a cache outage degrades to a DB read."""

from __future__ import annotations

from pkg.database.schema.merchant import (
    GetMerchantByIDRow,
    GetMerchantsActiveRow,
    GetMerchantsRow,
)
from pkg.logger.logger import Logger
from service.merchant.redis.cache import (
    decode_page,
    encode_page,
    merchant_active_row_from_dict,
    merchant_active_row_to_dict,
    merchant_by_id_from_dict,
    merchant_by_id_to_dict,
    merchant_row_from_dict,
    merchant_row_to_dict,
)
from service.merchant.redis.common import (
    TTL_DEFAULT,
    merchant_active_key,
    merchant_all_key,
    merchant_by_id_key,
    merchant_trashed_key,
)
from shared.cache import CacheStore


class MerchantQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_merchants(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantsRow], int] | None:
        payload = await self._store.get_json(merchant_all_key(page, page_size, search))
        return decode_page(payload, merchant_row_from_dict)

    async def set_merchants(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantsRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            merchant_all_key(page, page_size, search),
            encode_page(rows, total, merchant_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_merchant_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantsActiveRow], int] | None:
        payload = await self._store.get_json(
            merchant_active_key(page, page_size, search)
        )
        return decode_page(payload, merchant_active_row_from_dict)

    async def set_merchant_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantsActiveRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            merchant_active_key(page, page_size, search),
            encode_page(rows, total, merchant_active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_merchant_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantsActiveRow], int] | None:
        payload = await self._store.get_json(
            merchant_trashed_key(page, page_size, search)
        )
        return decode_page(payload, merchant_active_row_from_dict)

    async def set_merchant_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantsActiveRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            merchant_trashed_key(page, page_size, search),
            encode_page(rows, total, merchant_active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_merchant(self, merchant_id: int) -> GetMerchantByIDRow | None:
        payload = await self._store.get_json(merchant_by_id_key(merchant_id))
        if not isinstance(payload, dict):
            return None
        return merchant_by_id_from_dict(payload)

    async def set_merchant(self, row: GetMerchantByIDRow) -> None:
        await self._store.set_json(
            merchant_by_id_key(row.merchant_id),
            merchant_by_id_to_dict(row),
            TTL_DEFAULT,
        )


__all__ = ["MerchantQueryCacheImpl"]
