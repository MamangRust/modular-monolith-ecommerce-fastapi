"""Category command service. `create`/`update` generate a slug when the request carries none (`utils.GenerateSlug`). Every mutation invalidates the category cache *after* the repository has committed — by-id plus the list patterns (the deviation called out in the plan; only dropped the by-id key). `delete_permanent` verifies the row is trashed first (`FindByIDTrashed` existence check) so a missing/active category yields 404, then removes the `image_category` file from disk (`os.Remove`), then hard-deletes."""

from __future__ import annotations

import os

from pkg.database.schema.category import (
    Category,
    CreateCategoryRow,
    UpdateCategoryRow,
)
from pkg.logger.logger import Logger
from pkg.utils.slug import generate_slug
from service.category.redis.interfaces import CategoryCommandCache
from service.category.repository.interfaces import (
    CategoryCommandRepository,
    CategoryQueryRepository,
)
from shared.domain.requests.category import CreateCategoryRequest, UpdateCategoryRequest
from shared.errors import err_failed_remove_image_category
from shared.observability import Observability


class CategoryCommandServiceImpl:
    def __init__(
        self,
        repo: CategoryCommandRepository,
        query_repo: CategoryQueryRepository,
        cache: CategoryCommandCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._query_repo = query_repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def create(self, request: CreateCategoryRequest) -> CreateCategoryRow:
        with self._obs.span("category.command.create"):
            if not request.slug_category:
                request.slug_category = generate_slug(request.name)
            category = await self._repo.create(request)
            await self._cache.invalidate_lists()
            self._logger.info("category created", category_id=category.category_id)
            return category

    async def update(self, request: UpdateCategoryRequest) -> UpdateCategoryRow:
        category_id = request.category_id or 0
        with self._obs.span("category.command.update", category_id=category_id):
            if not request.slug_category:
                request.slug_category = generate_slug(request.name)
            category = await self._repo.update(request)
            await self._cache.invalidate_category(category_id)
            self._logger.info("category updated", category_id=category_id)
            return category

    async def trash(self, category_id: int) -> Category:
        with self._obs.span("category.command.trash", category_id=category_id):
            category = await self._repo.trash(category_id)
            await self._cache.invalidate_category(category_id)
            self._logger.info("category trashed", category_id=category_id)
            return category

    async def restore(self, category_id: int) -> Category:
        with self._obs.span("category.command.restore", category_id=category_id):
            category = await self._repo.restore(category_id)
            await self._cache.invalidate_category(category_id)
            self._logger.info("category restored", category_id=category_id)
            return category

    async def delete_permanent(self, category_id: int) -> bool:
        with self._obs.span(
            "category.command.delete_permanent", category_id=category_id
        ):
            # Existence/trashed check (FindByIDTrashed); the returned row
            # carries the image path then removes from disk.
            trashed = await self._query_repo.find_by_id_trashed(category_id)
            self._remove_image(trashed.image_category)
            success = await self._repo.delete_permanent(category_id)
            await self._cache.invalidate_category(category_id)
            self._logger.info("category deleted permanently", category_id=category_id)
            return success

    def _remove_image(self, image_category: str | None) -> None:
        """Remove the stored image file, matching the `os.Remove` guard. skips an empty path, ignores only `os.IsNotExist`, and returns `ErrFailedRemoveImageCategory` for any other failure (aborting the delete). `FileNotFoundError` is the Python equivalent of `IsNotExist`."""
        if not image_category:
            return
        try:
            os.remove(image_category)
        except FileNotFoundError:
            self._logger.debug(
                "category image file not found, continuing", path=image_category
            )
        except OSError as exc:
            self._logger.warn(
                "failed to remove category image", path=image_category, error=str(exc)
            )
            raise err_failed_remove_image_category.with_internal(exc) from exc

    async def restore_all(self) -> bool:
        with self._obs.span("category.command.restore_all"):
            success = await self._repo.restore_all()
            await self._cache.invalidate_all()
            self._logger.info("all categories restored")
            return success

    async def delete_all(self) -> bool:
        with self._obs.span("category.command.delete_all"):
            success = await self._repo.delete_all()
            await self._cache.invalidate_all()
            self._logger.info("all categories deleted permanently")
            return success


__all__ = ["CategoryCommandServiceImpl"]
