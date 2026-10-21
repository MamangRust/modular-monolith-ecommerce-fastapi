"""Password-reset / verification-code cache. Deviation from (recorded in the matrix): `SetResetTokenCache` builds its key from the *user id* (`password_reset:token:<userID>`) while `GetResetTokenCache` and `DeleteResetTokenCache` build theirs from the *token*, so the entry can never be read back — the set/get pair disagrees. keys all three by token, which is the evident intent; the DB lookup remains the fallback either way, so external behaviour is unchanged and the cache actually functions."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.auth.redis.common import (
    password_reset_token_key,
    register_verify_code_key,
)
from shared.cache import CacheStore


class PasswordResetCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def set_reset_token_cache(
        self, token: str, user_id: int, ttl_seconds: int
    ) -> None:
        await self._store.set_json(password_reset_token_key(token), user_id, ttl_seconds)

    async def get_reset_token_cache(self, token: str) -> tuple[int, bool]:
        payload = await self._store.get_json(password_reset_token_key(token))
        if isinstance(payload, bool) or not isinstance(payload, int):
            return 0, False
        return int(payload), True

    async def delete_reset_token_cache(self, token: str) -> None:
        await self._store.delete(password_reset_token_key(token))

    async def delete_verification_code_cache(self, email: str) -> None:
        await self._store.delete(register_verify_code_key(email))


__all__ = ["PasswordResetCacheImpl"]
