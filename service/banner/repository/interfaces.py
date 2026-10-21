"""Banner repository"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.banner import (
    Banner,
    CreateBannerRow,
    GetBannerRow,
    GetBannersActiveRow,
    GetBannersRow,
    UpdateBannerRow,
)
from shared.domain.requests.banner import CreateBannerRequest, UpdateBannerRequest


class BannerQueryRepository(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetBannersRow]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetBannersActiveRow]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetBannersActiveRow]: ...

    async def find_by_id(self, banner_id: int) -> GetBannerRow: ...


class BannerCommandRepository(Protocol):
    async def create(self, request: CreateBannerRequest) -> CreateBannerRow: ...

    async def update(self, request: UpdateBannerRequest) -> UpdateBannerRow: ...

    async def trash(self, banner_id: int) -> Banner: ...

    async def restore(self, banner_id: int) -> Banner: ...

    async def delete_permanent(self, banner_id: int) -> None: ...

    async def restore_all(self) -> None: ...

    async def delete_all_permanent(self) -> None: ...


__all__ = ["BannerCommandRepository", "BannerQueryRepository"]
