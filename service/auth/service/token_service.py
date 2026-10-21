"""Token service. Creating a refresh token first deletes any existing row for the user, so at most one active refresh token exists per user."""

from __future__ import annotations

from datetime import datetime, timedelta

from pkg.auth import TokenManager
from pkg.logger.logger import Logger
from service.auth.repository.interfaces import RefreshTokenRepository
from shared.domain.requests.auth import CreateRefreshToken
from shared.observability import Observability

_GO_DATETIME_LAYOUT = "%Y-%m-%d %H:%M:%S"
_REFRESH_TOKEN_LIFETIME = timedelta(hours=24)


class TokenService:
    def __init__(
        self,
        token: TokenManager,
        refresh_token: RefreshTokenRepository,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._token = token
        self._refresh_token = refresh_token
        self._logger = logger
        self._obs = obs

    async def create_access_token(self, user_id: int) -> str:
        with self._obs.span("auth.token.create_access", user_id=user_id):
            return self._token.generate_token(user_id, "access")

    async def create_refresh_token(self, user_id: int) -> str:
        with self._obs.span("auth.token.create_refresh", user_id=user_id):
            token = self._token.generate_token(user_id, "refresh")

            await self._refresh_token.delete_refresh_token_by_user_id(user_id)
            expires_at = (datetime.now() + _REFRESH_TOKEN_LIFETIME).strftime(
                _GO_DATETIME_LAYOUT
            )
            await self._refresh_token.create_refresh_token(
                CreateRefreshToken(
                    user_id=user_id, token=token, expires_at=expires_at
                )
            )
            return token


__all__ = ["TokenService"]
