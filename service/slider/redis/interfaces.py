"""Slider cache"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.slider import (
    GetSliderByIDRow,
    GetSlidersActiveRow,
    GetSlidersRow,
)


class SliderQueryCache(Protocol):
    async def get_sliders(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetSlidersRow], int] | None: ...

    async def set_sliders(
        self,
        page: int,
        page_size: int,
        search: str,
        sliders: list[GetSlidersRow],
        total: int,
    ) -> None: ...

    async def get_slider_by_id(self, slider_id: int) -> GetSliderByIDRow | None: ...

    async def set_slider_by_id(self, slider: GetSliderByIDRow) -> None: ...

    async def get_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetSlidersActiveRow], int] | None: ...

    async def set_active(
        self,
        page: int,
        page_size: int,
        search: str,
        sliders: list[GetSlidersActiveRow],
        total: int,
    ) -> None: ...

    async def get_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetSlidersActiveRow], int] | None: ...

    async def set_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        sliders: list[GetSlidersActiveRow],
        total: int,
    ) -> None: ...


class SliderCommandCache(Protocol):
    async def delete_slider_cache(self, slider_id: int) -> int: ...

    async def invalidate_slider_cache(self) -> int: ...


__all__ = ["SliderCommandCache", "SliderQueryCache"]
