"""Login / lockout cache. Failed-login counting and the lockout flag use raw Redis `INCR`/`SET`/ `EXISTS` rather than the JSON helpers, because they are counters, not documents. `INCR` initialises the 1-hour TTL on the first failure and the account is locked for 15 minutes once the threshold is reached. returns errors from these methods and the login service logs-and-continues; swallows them here (returning a safe default) so the observable behaviour is identical while keeping the cache out of the failure path."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.auth.redis.cache import (
    token_response_from_dict,
    token_response_to_dict,
)
from service.auth.redis.common import (
    FAILED_LOGIN_TTL,
    LOCKOUT_TTL,
    MAX_FAILED_ATTEMPTS,
    auth_account_locked_key,
    auth_failed_login_key,
    auth_login_key,
)
from shared.cache import CacheStore
from shared.domain.response.auth import TokenResponse


class LoginCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_cached_login(self, email: str) -> TokenResponse | None:
        payload = await self._store.get_json(auth_login_key(email))
        if not isinstance(payload, dict):
            return None
        return token_response_from_dict(payload)

    async def set_cached_login(
        self, email: str, data: TokenResponse, ttl_seconds: int
    ) -> None:
        if data is None:
            return
        await self._store.set_json(
            auth_login_key(email), token_response_to_dict(data), ttl_seconds
        )

    async def increment_failed_login(self, email: str) -> int:
        key = auth_failed_login_key(email)
        try:
            value = int(await self._store.redis.incr(self._store.key(key)))
            if value == 1:
                await self._store.redis.expire(self._store.key(key), FAILED_LOGIN_TTL)
            if value >= MAX_FAILED_ATTEMPTS:
                await self._store.redis.set(
                    self._store.key(auth_account_locked_key(email)),
                    "true",
                    ex=LOCKOUT_TTL,
                )
            return value
        except Exception as exc:
            self._logger.warn("failed to increment failed login counter", error=str(exc))
            return 0

    async def reset_failed_login(self, email: str) -> None:
        try:
            await self._store.redis.delete(
                self._store.key(auth_failed_login_key(email)),
                self._store.key(auth_account_locked_key(email)),
            )
        except Exception as exc:
            self._logger.warn("failed to reset failed login data", error=str(exc))

    async def is_account_locked(self, email: str) -> bool:
        try:
            exists = await self._store.redis.exists(
                self._store.key(auth_account_locked_key(email))
            )
            return int(exists) > 0
        except Exception as exc:
            self._logger.warn("failed to check account lock status", error=str(exc))
            return False


__all__ = ["LoginCacheImpl"]
