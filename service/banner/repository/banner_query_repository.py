"""Banner read repository. SQL is kept verbatim from the reference, including the `COUNT(*) OVER` window that supplies `total_count` in the same round trip as the page."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.errors import NoRowsError
from pkg.database.schema.banner import (
    GetBannerRow,
    GetBannersActiveRow,
    GetBannersRow,
)
from shared.errors import err_no_rows_or_failed

_GET_BANNERS = """
SELECT
    b.banner_id,
    b.name,
    b.start_date,
    b.end_date,
    b.start_time,
    b.end_time,
    b.is_active,
    b.created_at,
    b.updated_at,
    COUNT(*) OVER () AS total_count
FROM banners b
WHERE
    LOWER(name) LIKE LOWER('%' || :search || '%')
LIMIT :limit
OFFSET :offset
"""

_GET_BANNERS_ACTIVE = """
SELECT
    b.banner_id,
    b.name,
    b.start_date,
    b.end_date,
    b.start_time,
    b.end_time,
    b.is_active,
    b.created_at,
    b.updated_at,
    b.deleted_at,
    COUNT(*) OVER () AS total_count
FROM banners b
WHERE
    deleted_at IS NULL
    AND LOWER(name) LIKE LOWER('%' || :search || '%')
LIMIT :limit
OFFSET :offset
"""

_GET_BANNERS_TRASHED = """
SELECT
    b.banner_id,
    b.name,
    b.start_date,
    b.end_date,
    b.start_time,
    b.end_time,
    b.is_active,
    b.created_at,
    b.updated_at,
    b.deleted_at,
    COUNT(*) OVER () AS total_count
FROM banners b
WHERE
    deleted_at IS NOT NULL
    AND LOWER(name) LIKE LOWER('%' || :search || '%')
LIMIT :limit
OFFSET :offset
"""

_GET_BANNER = """
SELECT b.banner_id, b.name, b.start_date, b.end_date, b.start_time, b.end_time,
       b.is_active, b.created_at, b.updated_at
FROM banners b
WHERE
    banner_id = :banner_id
    AND deleted_at IS NULL
"""


class BannerQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetBannersRow]:
        offset = (page - 1) * page_size
        rows = await self._db.select(
            _GET_BANNERS,
            {"search": search, "limit": page_size, "offset": offset},
        )
        return [GetBannersRow.from_row(row) for row in rows]

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetBannersActiveRow]:
        offset = (page - 1) * page_size
        rows = await self._db.select(
            _GET_BANNERS_ACTIVE,
            {"search": search, "limit": page_size, "offset": offset},
        )
        return [GetBannersActiveRow.from_row(row) for row in rows]

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetBannersActiveRow]:
        offset = (page - 1) * page_size
        rows = await self._db.select(
            _GET_BANNERS_TRASHED,
            {"search": search, "limit": page_size, "offset": offset},
        )
        return [GetBannersActiveRow.from_row(row) for row in rows]

    async def find_by_id(self, banner_id: int) -> GetBannerRow:
        row = await self._db.scalar(_GET_BANNER, {"banner_id": banner_id})
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "Banner", "find banner")
        return GetBannerRow.from_row(row)


__all__ = ["BannerQueryRepositoryImpl"]
