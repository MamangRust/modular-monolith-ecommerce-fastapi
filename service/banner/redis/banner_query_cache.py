"""Banner query cache., every list cache written here is also read (the banner cache did read all of them, so this is a straight port). Reads/writes never raise: `CacheStore` swallows Redis errors so a cache outage degrades to a DB read."""

from __future__ import annotations

from pkg.database.schema.banner import (
    GetBannerRow,
    GetBannersActiveRow,
    GetBannersRow,
)
from pkg.logger.logger import Logger
from service.banner.redis.cache import (
    active_row_from_dict,
    active_row_to_dict,
    banner_by_id_from_dict,
    banner_by_id_to_dict,
    banner_row_from_dict,
    banner_row_to_dict,
)
from service.banner.redis.common import (
    TTL_DEFAULT,
    banner_active_key,
    banner_all_key,
    banner_by_id_key,
    banner_trashed_key,
)
from shared.cache import CacheStore


class BannerQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_banners(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetBannersRow], int] | None:
        payload = await self._store.get_json(banner_all_key(page, page_size, search))
        return _decode_page(payload, banner_row_from_dict)

    async def set_banners(
        self,
        page: int,
        page_size: int,
        search: str,
        banners: list[GetBannersRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            banner_all_key(page, page_size, search),
            _encode_page(banners, total, banner_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_banner_by_id(self, banner_id: int) -> GetBannerRow | None:
        payload = await self._store.get_json(banner_by_id_key(banner_id))
        if not isinstance(payload, dict):
            return None
        return banner_by_id_from_dict(payload)

    async def set_banner_by_id(self, banner: GetBannerRow) -> None:
        await self._store.set_json(
            banner_by_id_key(banner.banner_id),
            banner_by_id_to_dict(banner),
            TTL_DEFAULT,
        )

    async def get_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetBannersActiveRow], int] | None:
        payload = await self._store.get_json(banner_active_key(page, page_size, search))
        return _decode_page(payload, active_row_from_dict)

    async def set_active(
        self,
        page: int,
        page_size: int,
        search: str,
        banners: list[GetBannersActiveRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            banner_active_key(page, page_size, search),
            _encode_page(banners, total, active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetBannersActiveRow], int] | None:
        payload = await self._store.get_json(
            banner_trashed_key(page, page_size, search)
        )
        return _decode_page(payload, active_row_from_dict)

    async def set_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        banners: list[GetBannersActiveRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            banner_trashed_key(page, page_size, search),
            _encode_page(banners, total, active_row_to_dict),
            TTL_DEFAULT,
        )


def _encode_page(rows: list, total: int, to_dict) -> dict:
    return {"data": [to_dict(row) for row in rows], "total_records": total}


def _decode_page(payload, from_dict):
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    if not isinstance(data, list):
        return None
    total = int(payload.get("total_records") or 0)
    return [from_dict(item, total) for item in data], total


__all__ = ["BannerQueryCacheImpl"]
