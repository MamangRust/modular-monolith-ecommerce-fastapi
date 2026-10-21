"""Identity cache. `set_refresh_token` stores the token string as the value (does the same), which means the cache-hit branch in `RefreshToken` cannot recover a user id from it — the value is a JWT, not a number. That is a bug, preserved here so the refresh path still falls through to signature validation; see the."""

from __future__ import annotations

from pkg.database.schema.user import GetUserByIDRow
from pkg.logger.logger import Logger
from service.auth.redis.cache import user_row_from_dict, user_row_to_dict
from service.auth.redis.common import (
    identity_refresh_token_key,
    identity_user_info_key,
)
from shared.cache import CacheStore


class IdentityCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def set_refresh_token(self, token: str, ttl_seconds: int) -> None:
        await self._store.set_json(identity_refresh_token_key(token), token, ttl_seconds)

    async def get_refresh_token(self, token: str) -> tuple[str, bool]:
        payload = await self._store.get_json(identity_refresh_token_key(token))
        if isinstance(payload, str):
            return payload, True
        return "", False

    async def delete_refresh_token(self, token: str) -> None:
        await self._store.delete(identity_refresh_token_key(token))

    async def set_cached_user_info(
        self, user: GetUserByIDRow, ttl_seconds: int
    ) -> None:
        if user is None:
            return
        await self._store.set_json(
            identity_user_info_key(user.user_id),
            user_row_to_dict(user),
            ttl_seconds,
        )

    async def get_cached_user_info(
        self, user_id: str | int
    ) -> GetUserByIDRow | None:
        payload = await self._store.get_json(identity_user_info_key(user_id))
        if not isinstance(payload, dict):
            return None
        try:
            return user_row_from_dict(payload)
        except (KeyError, ValueError) as exc:
            self._logger.warn("cached user payload is malformed", error=str(exc))
            return None

    async def delete_cached_user_info(self, user_id: str | int) -> None:
        await self._store.delete(identity_user_info_key(user_id))


__all__ = ["IdentityCacheImpl"]
