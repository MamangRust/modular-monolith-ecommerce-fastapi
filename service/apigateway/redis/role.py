"""Gateway user-role cache."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.apigateway.redis.common import USER_ROLES_TTL, user_roles_key
from shared.cache import CacheStore


class RoleCache:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_user_roles(self, user_id: int) -> list[str] | None:
        cached = await self._store.get_json(user_roles_key(user_id))
        if not isinstance(cached, list):
            return None
        return [str(role) for role in cached]

    async def set_user_roles(self, user_id: int, roles: list[str]) -> None:
        await self._store.set_json(user_roles_key(user_id), roles, USER_ROLES_TTL)


__all__ = ["RoleCache"]
