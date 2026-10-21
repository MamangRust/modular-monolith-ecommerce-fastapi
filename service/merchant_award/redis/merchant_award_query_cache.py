"""merchant_award query cache.

Every list cache written here is also read. Reads/writes never raise:
`CacheStore` swallows Redis errors so a cache outage degrades to a DB read."""

from __future__ import annotations

from pkg.database.schema.merchant_award import (
    GetMerchantCertificationOrAwardRow,
    GetMerchantCertificationsAndAwardsActiveRow,
    GetMerchantCertificationsAndAwardsRow,
    GetMerchantCertificationsAndAwardsTrashedRow,
)
from pkg.logger.logger import Logger
from service.merchant_award.redis.cache import (
    award_active_row_from_dict,
    award_active_row_to_dict,
    award_by_id_from_dict,
    award_by_id_to_dict,
    award_row_from_dict,
    award_row_to_dict,
    decode_page,
    encode_page,
)
from service.merchant_award.redis.common import (
    TTL_DEFAULT,
    merchant_award_active_key,
    merchant_award_all_key,
    merchant_award_by_id_key,
    merchant_award_trashed_key,
)
from shared.cache import CacheStore


class MerchantAwardQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_merchant_awards(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantCertificationsAndAwardsRow], int] | None:
        payload = await self._store.get_json(
            merchant_award_all_key(page, page_size, search)
        )
        return decode_page(payload, award_row_from_dict)

    async def set_merchant_awards(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantCertificationsAndAwardsRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            merchant_award_all_key(page, page_size, search),
            encode_page(rows, total, award_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_merchant_awards_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantCertificationsAndAwardsActiveRow], int] | None:
        payload = await self._store.get_json(
            merchant_award_active_key(page, page_size, search)
        )
        return decode_page(payload, award_active_row_from_dict)

    async def set_merchant_awards_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantCertificationsAndAwardsActiveRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            merchant_award_active_key(page, page_size, search),
            encode_page(rows, total, award_active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_merchant_awards_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantCertificationsAndAwardsTrashedRow], int] | None:
        payload = await self._store.get_json(
            merchant_award_trashed_key(page, page_size, search)
        )
        return decode_page(payload, award_active_row_from_dict)

    async def set_merchant_awards_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantCertificationsAndAwardsTrashedRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            merchant_award_trashed_key(page, page_size, search),
            encode_page(rows, total, award_active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_merchant_award(
        self, merchant_certification_id: int
    ) -> GetMerchantCertificationOrAwardRow | None:
        payload = await self._store.get_json(
            merchant_award_by_id_key(merchant_certification_id)
        )
        if not isinstance(payload, dict):
            return None
        return award_by_id_from_dict(payload)

    async def set_merchant_award(
        self, row: GetMerchantCertificationOrAwardRow
    ) -> None:
        await self._store.set_json(
            merchant_award_by_id_key(row.merchant_certification_id),
            award_by_id_to_dict(row),
            TTL_DEFAULT,
        )


__all__ = ["MerchantAwardQueryCacheImpl"]
