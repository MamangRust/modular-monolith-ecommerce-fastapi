"""User query service. Pagination is normalised once and the normalised values are used for both the cache key and the repository call, the role service."""

from __future__ import annotations

from pkg.database.schema.user import (
    GetActiveUsersRow,
    GetUserByIDRow,
    GetUsersRow,
)
from pkg.logger.logger import Logger
from service.user.redis.interfaces import UserQueryCache
from service.user.repository.interfaces import UserQueryRepository
from shared.observability import Observability


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


class UserQueryServiceImpl:
    def __init__(
        self,
        repo: UserQueryRepository,
        cache: UserQueryCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetUsersRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span("user.query.find_all", page=page, page_size=page_size):
            cached = await self._cache.get_users(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_all(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_users(page, page_size, search, rows, total)
            return rows, total

    async def find_by_id(self, user_id: int) -> GetUserByIDRow:
        with self._obs.span("user.query.find_by_id", user_id=user_id):
            cached = await self._cache.get_user_by_id(user_id)
            if cached is not None:
                return cached
            user = await self._repo.find_by_id(user_id)
            await self._cache.set_user_by_id(user)
            return user

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetActiveUsersRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span("user.query.find_active", page=page, page_size=page_size):
            cached = await self._cache.get_active(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_active(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_active(page, page_size, search, rows, total)
            return rows, total

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetActiveUsersRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span("user.query.find_trashed", page=page, page_size=page_size):
            cached = await self._cache.get_trashed(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_trashed(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_trashed(page, page_size, search, rows, total)
            return rows, total


__all__ = ["UserQueryServiceImpl", "normalize_pagination"]
