"""Slider repository"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.slider import (
    CreateSliderRow,
    GetSliderByIDRow,
    GetSlidersActiveRow,
    GetSlidersRow,
    Slider,
    UpdateSliderRow,
)
from shared.domain.requests.slider import CreateSliderRequest, UpdateSliderRequest


class SliderQueryRepository(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetSlidersRow]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetSlidersActiveRow]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetSlidersActiveRow]: ...

    async def find_by_id(self, slider_id: int) -> GetSliderByIDRow: ...


class SliderCommandRepository(Protocol):
    async def create(self, request: CreateSliderRequest) -> CreateSliderRow: ...

    async def update(self, request: UpdateSliderRequest) -> UpdateSliderRow: ...

    async def trash(self, slider_id: int) -> Slider: ...

    async def restore(self, slider_id: int) -> Slider: ...

    async def delete_permanent(self, slider_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all_permanent(self) -> bool: ...


__all__ = ["SliderCommandRepository", "SliderQueryRepository"]
