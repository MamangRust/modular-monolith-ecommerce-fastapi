"""Slider read repository. SQL is kept verbatim from the reference, including the `COUNT(*) OVER` window that supplies `total_count` in the same round trip as the page. Unlike banner, slider's queries **do** filter `deleted_at IS NULL` (FindAll / FindActive) or `deleted_at IS NOT NULL` (FindTrashed) and `ORDER BY created_at DESC` — matching the `slider` SQL. `FindById` only returns live rows."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.slider import (
    GetSliderByIDRow,
    GetSlidersActiveRow,
    GetSlidersRow,
)
from shared.errors import (
    err_find_active_sliders,
    err_find_all_sliders,
    err_find_slider_by_id,
    err_find_trashed_sliders,
)

_GET_SLIDERS = """
SELECT
    slider_id,
    name,
    image,
    created_at,
    updated_at,
    COUNT(*) OVER () AS total_count
FROM sliders
WHERE
    deleted_at IS NULL
    AND (name ILIKE '%' || :search || '%')
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_SLIDERS_ACTIVE = """
SELECT
    slider_id,
    name,
    image,
    created_at,
    updated_at,
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM sliders
WHERE
    deleted_at IS NULL
    AND (name ILIKE '%' || :search || '%')
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_SLIDERS_TRASHED = """
SELECT
    slider_id,
    name,
    image,
    created_at,
    updated_at,
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM sliders
WHERE
    deleted_at IS NOT NULL
    AND (name ILIKE '%' || :search || '%')
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_SLIDER = """
SELECT
    slider_id,
    name,
    image,
    created_at,
    updated_at
FROM sliders
WHERE
    slider_id = :slider_id
    AND deleted_at IS NULL
"""


class SliderQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetSlidersRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_SLIDERS,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_all_sliders.with_internal(exc) from exc
        return [GetSlidersRow.from_row(row) for row in rows]

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetSlidersActiveRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_SLIDERS_ACTIVE,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_active_sliders.with_internal(exc) from exc
        return [GetSlidersActiveRow.from_row(row) for row in rows]

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetSlidersActiveRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_SLIDERS_TRASHED,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_trashed_sliders.with_internal(exc) from exc
        return [GetSlidersActiveRow.from_row(row) for row in rows]

    async def find_by_id(self, slider_id: int) -> GetSliderByIDRow:
        try:
            row = await self._db.scalar(_GET_SLIDER, {"slider_id": slider_id})
        except Exception as exc:
            raise err_find_slider_by_id.with_internal(exc) from exc
        if row is None:
            raise err_find_slider_by_id
        return GetSliderByIDRow.from_row(row)


__all__ = ["SliderQueryRepositoryImpl"]
