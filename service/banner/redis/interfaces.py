"""Banner cache"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.banner import (
    GetBannerRow,
    GetBannersActiveRow,
    GetBannersRow,
)


class BannerQueryCache(Protocol):
    async def get_banners(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetBannersRow], int] | None: ...

    async def set_banners(
        self,
        page: int,
        page_size: int,
        search: str,
        banners: list[GetBannersRow],
        total: int,
    ) -> None: ...

    async def get_banner_by_id(self, banner_id: int) -> GetBannerRow | None: ...

    async def set_banner_by_id(self, banner: GetBannerRow) -> None: ...

    async def get_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetBannersActiveRow], int] | None: ...

    async def set_active(
        self,
        page: int,
        page_size: int,
        search: str,
        banners: list[GetBannersActiveRow],
        total: int,
    ) -> None: ...

    async def get_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetBannersActiveRow], int] | None: ...

    async def set_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        banners: list[GetBannersActiveRow],
        total: int,
    ) -> None: ...


class BannerCommandCache(Protocol):
    async def delete_cached_banner(self, banner_id: int) -> int: ...

    async def invalidate_lists(self) -> int: ...

    async def invalidate_banner(self, banner_id: int) -> int: ...

    async def invalidate_all(self) -> int: ...


__all__ = ["BannerCommandCache", "BannerQueryCache"]
