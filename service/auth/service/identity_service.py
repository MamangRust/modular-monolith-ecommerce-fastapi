"""Identity service. `refresh_token` rotates the refresh token: the presented token is validated, deleted from Redis and the DB, and replaced by a freshly generated pair. The new refresh token is persisted and cached for 24 hours. Note on the cache-hit branch: stores the *token string* under `identity:refresh_token:<token>` and then tries to parse the cached value as a user id, so the branch never succeeds and every refresh validates the JWT. preserves that shape (and therefore the fall-through), rather than "fixing" the cache to store a user id — see the. `get_me` caches the full user row for 5 minutes."""

from __future__ import annotations

from datetime import datetime, timedelta

from pkg.auth import TokenExpiredError, TokenManager
from pkg.database.schema.user import GetUserByIDRow
from pkg.logger.logger import Logger
from service.auth.redis.common import REFRESH_TOKEN_TTL, USER_INFO_TTL
from service.auth.redis.interfaces import IdentityCache
from service.auth.repository.interfaces import (
    RefreshTokenRepository,
    UserRepository,
)
from service.auth.service.token_service import TokenService
from shared.domain.requests.auth import UpdateRefreshToken
from shared.domain.response.auth import TokenResponse
from shared.errors import err_internal
from shared.observability import Observability

_GO_DATETIME_LAYOUT = "%Y-%m-%d %H:%M:%S"
_REFRESH_TOKEN_LIFETIME = timedelta(hours=24)


class IdentityServiceImpl:
    def __init__(
        self,
        cache: IdentityCache,
        token: TokenManager,
        refresh_token: RefreshTokenRepository,
        user: UserRepository,
        token_service: TokenService,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._cache = cache
        self._token = token
        self._refresh_token = refresh_token
        self._user = user
        self._token_service = token_service
        self._logger = logger
        self._obs = obs

    async def refresh_token(self, token: str) -> TokenResponse:
        with self._obs.span("auth.refresh_token"):
            cached, found = await self._cache.get_refresh_token(token)
            if found:
                try:
                    user_id = int(cached)
                except (TypeError, ValueError):
                    user_id = None
                if user_id is not None:
                    await self._cache.delete_refresh_token(token)
                    return await self._issue_pair(user_id)

            try:
                user_id_str = self._token.validate_token(token)
            except TokenExpiredError as exc:
                await self._cache.delete_refresh_token(token)
                await self._refresh_token.delete_refresh_token(token)
                raise err_internal.with_internal(exc) from exc

            try:
                user_id = int(user_id_str)
            except (TypeError, ValueError) as exc:
                raise err_internal.with_internal(exc) from exc

            await self._cache.delete_refresh_token(token)
            await self._refresh_token.delete_refresh_token(token)

            access_token = await self._token_service.create_access_token(user_id)
            refresh_token = await self._token_service.create_refresh_token(user_id)

            expires_at = (datetime.now() + _REFRESH_TOKEN_LIFETIME).strftime(
                _GO_DATETIME_LAYOUT
            )
            await self._refresh_token.update_refresh_token(
                UpdateRefreshToken(
                    user_id=user_id, token=refresh_token, expires_at=expires_at
                )
            )

            await self._cache.set_refresh_token(refresh_token, REFRESH_TOKEN_TTL)
            self._logger.info("refresh token rotated", user_id=user_id)
            return TokenResponse(
                access_token=access_token, refresh_token=refresh_token
            )

    async def _issue_pair(self, user_id: int) -> TokenResponse:
        """Cache-hit path: skips the DB update here. `create_refresh_token` itself replaces the stored row, so only the cache entry for the presented token needs clearing (the caller does that before calling this)."""
        access_token = await self._token_service.create_access_token(user_id)
        refresh_token = await self._token_service.create_refresh_token(user_id)
        await self._cache.set_refresh_token(refresh_token, REFRESH_TOKEN_TTL)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def get_me(self, user_id: int) -> GetUserByIDRow:
        with self._obs.span("auth.get_me", user_id=user_id):
            cached = await self._cache.get_cached_user_info(user_id)
            if cached is not None:
                return cached

            user = await self._user.find_by_id(user_id)
            await self._cache.set_cached_user_info(user, USER_INFO_TTL)
            return user


__all__ = ["IdentityServiceImpl"]
