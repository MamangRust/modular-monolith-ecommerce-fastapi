"""merchant_detail query cache.

Every list cache written here is also read. Reads/writes never raise:
`CacheStore` swallows Redis errors so a cache outage degrades to a DB read."""

from __future__ import annotations

from pkg.database.schema.merchant_detail import (
    GetMerchantDetailRow,
    GetMerchantDetailsActiveRow,
    GetMerchantDetailsRow,
    GetMerchantDetailsTrashedRow,
)
from pkg.logger.logger import Logger
from service.merchant_detail.redis.cache import (
    decode_page,
    detail_active_row_from_dict,
    detail_active_row_to_dict,
    detail_by_id_from_dict,
    detail_by_id_to_dict,
    detail_row_from_dict,
    detail_row_to_dict,
    encode_page,
)
from service.merchant_detail.redis.common import (
    TTL_DEFAULT,
    merchant_detail_active_key,
    merchant_detail_all_key,
    merchant_detail_by_id_key,
    merchant_detail_trashed_key,
)
from shared.cache import CacheStore


class MerchantDetailQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_merchant_details(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantDetailsRow], int] | None:
        payload = await self._store.get_json(
            merchant_detail_all_key(page, page_size, search)
        )
        return decode_page(payload, detail_row_from_dict)

    async def set_merchant_details(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantDetailsRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            merchant_detail_all_key(page, page_size, search),
            encode_page(rows, total, detail_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_merchant_details_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantDetailsActiveRow], int] | None:
        payload = await self._store.get_json(
            merchant_detail_active_key(page, page_size, search)
        )
        return decode_page(payload, detail_active_row_from_dict)

    async def set_merchant_details_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantDetailsActiveRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            merchant_detail_active_key(page, page_size, search),
            encode_page(rows, total, detail_active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_merchant_details_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantDetailsTrashedRow], int] | None:
        payload = await self._store.get_json(
            merchant_detail_trashed_key(page, page_size, search)
        )
        return decode_page(payload, detail_active_row_from_dict)

    async def set_merchant_details_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantDetailsTrashedRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            merchant_detail_trashed_key(page, page_size, search),
            encode_page(rows, total, detail_active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_merchant_detail(
        self, merchant_detail_id: int
    ) -> GetMerchantDetailRow | None:
        payload = await self._store.get_json(
            merchant_detail_by_id_key(merchant_detail_id)
        )
        if not isinstance(payload, dict):
            return None
        return detail_by_id_from_dict(payload)

    async def set_merchant_detail(self, row: GetMerchantDetailRow) -> None:
        await self._store.set_json(
            merchant_detail_by_id_key(row.merchant_detail_id),
            detail_by_id_to_dict(row),
            TTL_DEFAULT,
        )


__all__ = ["MerchantDetailQueryCacheImpl"]
