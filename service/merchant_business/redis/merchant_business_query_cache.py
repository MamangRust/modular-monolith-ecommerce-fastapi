"""merchant_business query cache.

Every list cache written here is also read. Reads/writes never raise:
`CacheStore` swallows Redis errors so a cache outage degrades to a DB read."""

from __future__ import annotations

from pkg.database.schema.merchant_business import (
    GetMerchantBusinessInformationRow,
    GetMerchantsBusinessInformationActiveRow,
    GetMerchantsBusinessInformationRow,
    GetMerchantsBusinessInformationTrashedRow,
)
from pkg.logger.logger import Logger
from service.merchant_business.redis.cache import (
    business_active_row_from_dict,
    business_active_row_to_dict,
    business_by_id_from_dict,
    business_by_id_to_dict,
    business_row_from_dict,
    business_row_to_dict,
    decode_page,
    encode_page,
)
from service.merchant_business.redis.common import (
    TTL_DEFAULT,
    merchant_business_active_key,
    merchant_business_all_key,
    merchant_business_by_id_key,
    merchant_business_trashed_key,
)
from shared.cache import CacheStore


class MerchantBusinessQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_merchant_businesses(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantsBusinessInformationRow], int] | None:
        payload = await self._store.get_json(
            merchant_business_all_key(page, page_size, search)
        )
        return decode_page(payload, business_row_from_dict)

    async def set_merchant_businesses(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantsBusinessInformationRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            merchant_business_all_key(page, page_size, search),
            encode_page(rows, total, business_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_merchant_businesses_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantsBusinessInformationActiveRow], int] | None:
        payload = await self._store.get_json(
            merchant_business_active_key(page, page_size, search)
        )
        return decode_page(payload, business_active_row_from_dict)

    async def set_merchant_businesses_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantsBusinessInformationActiveRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            merchant_business_active_key(page, page_size, search),
            encode_page(rows, total, business_active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_merchant_businesses_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantsBusinessInformationTrashedRow], int] | None:
        payload = await self._store.get_json(
            merchant_business_trashed_key(page, page_size, search)
        )
        return decode_page(payload, business_active_row_from_dict)

    async def set_merchant_businesses_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantsBusinessInformationTrashedRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            merchant_business_trashed_key(page, page_size, search),
            encode_page(rows, total, business_active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_merchant_business(
        self, merchant_business_info_id: int
    ) -> GetMerchantBusinessInformationRow | None:
        payload = await self._store.get_json(
            merchant_business_by_id_key(merchant_business_info_id)
        )
        if not isinstance(payload, dict):
            return None
        return business_by_id_from_dict(payload)

    async def set_merchant_business(
        self, row: GetMerchantBusinessInformationRow
    ) -> None:
        await self._store.set_json(
            merchant_business_by_id_key(row.merchant_business_info_id),
            business_by_id_to_dict(row),
            TTL_DEFAULT,
        )


__all__ = ["MerchantBusinessQueryCacheImpl"]
