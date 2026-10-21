"""Slider write repository. `create`/`update` parse the request's fields into the SQL params and map a failure to the matching error. Soft delete uses `deleted_at`; `delete_permanent` and the bulk operations are hard deletes., `delete_permanent` and the bulk restore/delete ignore affected rows, so operating on a missing slider still reports success."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.slider import CreateSliderRow, Slider, UpdateSliderRow
from shared.domain.requests.slider import CreateSliderRequest, UpdateSliderRequest
from shared.errors import (
    AppError,
    err_create_slider,
    err_delete_all_permanent_sliders,
    err_delete_permanent_slider,
    err_restore_all_sliders,
    err_restore_slider,
    err_slider_not_found,
    err_trash_slider,
    err_update_slider,
)

_CREATE_SLIDER = """
INSERT INTO sliders (name, image)
VALUES (:name, :image)
RETURNING
    slider_id, name, image, created_at, updated_at
"""

_UPDATE_SLIDER = """
UPDATE sliders
SET
    name = :name,
    image = :image,
    updated_at = CURRENT_TIMESTAMP
WHERE
    slider_id = :slider_id
    AND deleted_at IS NULL
RETURNING
    slider_id, name, image, created_at, updated_at
"""

_TRASH_SLIDER = """
UPDATE sliders
SET
    deleted_at = CURRENT_TIMESTAMP
WHERE
    slider_id = :slider_id
    AND deleted_at IS NULL
RETURNING
    slider_id, name, image, created_at, updated_at, deleted_at
"""

_RESTORE_SLIDER = """
UPDATE sliders
SET
    deleted_at = NULL
WHERE
    slider_id = :slider_id
    AND deleted_at IS NOT NULL
RETURNING
    slider_id, name, image, created_at, updated_at, deleted_at
"""

_DELETE_SLIDER_PERMANENT = """
DELETE FROM sliders
WHERE slider_id = :slider_id AND deleted_at IS NOT NULL
"""

_RESTORE_ALL_SLIDERS = "UPDATE sliders SET deleted_at = NULL WHERE deleted_at IS NOT NULL"

_DELETE_ALL_PERMANENT_SLIDERS = "DELETE FROM sliders WHERE deleted_at IS NOT NULL"


class SliderCommandRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def create(self, request: CreateSliderRequest) -> CreateSliderRow:
        params = {"name": request.name, "image": request.image}
        try:
            row = await self._db.execute(_CREATE_SLIDER, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_create_slider.with_internal(exc) from exc
        if row is None:
            raise err_create_slider
        return CreateSliderRow.from_row(row)

    async def update(self, request: UpdateSliderRequest) -> UpdateSliderRow:
        if request.slider_id is None:
            raise err_slider_not_found
        params = {
            "slider_id": request.slider_id,
            "name": request.name,
            "image": request.image,
        }
        try:
            row = await self._db.execute(_UPDATE_SLIDER, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_update_slider.with_internal(exc) from exc
        if row is None:
            raise err_slider_not_found
        return UpdateSliderRow.from_row(row)

    async def trash(self, slider_id: int) -> Slider:
        try:
            row = await self._db.execute(_TRASH_SLIDER, {"slider_id": slider_id})
        except AppError:
            raise
        except Exception as exc:
            raise err_trash_slider.with_internal(exc) from exc
        if row is None:
            raise err_slider_not_found
        return Slider.from_row(row)

    async def restore(self, slider_id: int) -> Slider:
        try:
            row = await self._db.execute(_RESTORE_SLIDER, {"slider_id": slider_id})
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_slider.with_internal(exc) from exc
        if row is None:
            raise err_slider_not_found
        return Slider.from_row(row)

    async def delete_permanent(self, slider_id: int) -> bool:
        # ignores RowsAffected here; see module docstring.
        try:
            await self._db.execute(
                _DELETE_SLIDER_PERMANENT, {"slider_id": slider_id}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_permanent_slider.with_internal(exc) from exc
        return True

    async def restore_all(self) -> bool:
        try:
            await self._db.execute(_RESTORE_ALL_SLIDERS)
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_all_sliders.with_internal(exc) from exc
        return True

    async def delete_all_permanent(self) -> bool:
        try:
            await self._db.execute(_DELETE_ALL_PERMANENT_SLIDERS)
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_all_permanent_sliders.with_internal(exc) from exc
        return True


__all__ = ["SliderCommandRepositoryImpl"]
