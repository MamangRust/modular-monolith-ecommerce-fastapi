"""Role query service. Pagination is normalised once and the normalised values are used for both the cache key and the repository call. normalised for the repository only, which could key the cache with the caller's raw page; keeps them consistent."""

from __future__ import annotations

from pkg.database.schema.role import GetActiveRolesRow, GetRolesRow, Role
from pkg.logger.logger import Logger
from service.role.redis.interfaces import RoleQueryCache
from service.role.repository.interfaces import RoleQueryRepository
from shared.observability import Observability


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


class RoleQueryServiceImpl:
    def __init__(
        self,
        repo: RoleQueryRepository,
        cache: RoleQueryCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetRolesRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span("role.query.find_all", page=page, page_size=page_size):
            cached = await self._cache.get_roles(page, page_size, search)
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_all(search, page, page_size)
            except Exception as exc:
                self._logger.error("failed to fetch roles", error=str(exc))
                raise
            total = rows[0].total_count if rows else 0
            await self._cache.set_roles(page, page_size, search, rows, total)
            return rows, total

    async def find_by_id(self, role_id: int) -> Role:
        with self._obs.span("role.query.find_by_id", role_id=role_id):
            cached = await self._cache.get_role_by_id(role_id)
            if cached is not None:
                return cached
            role = await self._repo.find_by_id(role_id)
            await self._cache.set_role_by_id(role)
            return role

    async def find_by_name(self, role_name: str) -> Role:
        with self._obs.span("role.query.find_by_name", name=role_name):
            return await self._repo.find_by_name(role_name)

    async def find_by_user_id(self, user_id: int) -> list[Role]:
        with self._obs.span("role.query.find_by_user_id", user_id=user_id):
            cached = await self._cache.get_role_by_user_id(user_id)
            if cached is not None:
                return cached
            roles = await self._repo.find_by_user_id(user_id)
            await self._cache.set_role_by_user_id(user_id, roles)
            return roles

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetActiveRolesRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span("role.query.find_active", page=page, page_size=page_size):
            cached = await self._cache.get_active(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_active(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_active(page, page_size, search, rows, total)
            return rows, total

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetActiveRolesRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span("role.query.find_trashed", page=page, page_size=page_size):
            cached = await self._cache.get_trashed(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_trashed(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_trashed(page, page_size, search, rows, total)
            return rows, total


__all__ = ["RoleQueryServiceImpl", "normalize_pagination"]
