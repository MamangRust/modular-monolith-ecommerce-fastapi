"""Slider query cache. Every list cache written here is also read (the slider cache reads all of them, so this is a straight port). Reads/writes never raise: `CacheStore` swallows Redis errors so a cache outage degrades to a DB read."""

from __future__ import annotations

from pkg.database.schema.slider import (
    GetSliderByIDRow,
    GetSlidersActiveRow,
    GetSlidersRow,
)
from pkg.logger.logger import Logger
from service.slider.redis.cache import (
    active_row_from_dict,
    active_row_to_dict,
    slider_by_id_from_dict,
    slider_by_id_to_dict,
    slider_row_from_dict,
    slider_row_to_dict,
)
from service.slider.redis.common import (
    TTL_DEFAULT,
    slider_active_key,
    slider_all_key,
    slider_by_id_key,
    slider_trashed_key,
)
from shared.cache import CacheStore


class SliderQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_sliders(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetSlidersRow], int] | None:
        payload = await self._store.get_json(slider_all_key(page, page_size, search))
        return _decode_page(payload, slider_row_from_dict)

    async def set_sliders(
        self,
        page: int,
        page_size: int,
        search: str,
        sliders: list[GetSlidersRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            slider_all_key(page, page_size, search),
            _encode_page(sliders, total, slider_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_slider_by_id(self, slider_id: int) -> GetSliderByIDRow | None:
        payload = await self._store.get_json(slider_by_id_key(slider_id))
        if not isinstance(payload, dict):
            return None
        return slider_by_id_from_dict(payload)

    async def set_slider_by_id(self, slider: GetSliderByIDRow) -> None:
        await self._store.set_json(
            slider_by_id_key(slider.slider_id),
            slider_by_id_to_dict(slider),
            TTL_DEFAULT,
        )

    async def get_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetSlidersActiveRow], int] | None:
        payload = await self._store.get_json(
            slider_active_key(page, page_size, search)
        )
        return _decode_page(payload, active_row_from_dict)

    async def set_active(
        self,
        page: int,
        page_size: int,
        search: str,
        sliders: list[GetSlidersActiveRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            slider_active_key(page, page_size, search),
            _encode_page(sliders, total, active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetSlidersActiveRow], int] | None:
        payload = await self._store.get_json(
            slider_trashed_key(page, page_size, search)
        )
        return _decode_page(payload, active_row_from_dict)

    async def set_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        sliders: list[GetSlidersActiveRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            slider_trashed_key(page, page_size, search),
            _encode_page(sliders, total, active_row_to_dict),
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


__all__ = ["SliderQueryCacheImpl"]
