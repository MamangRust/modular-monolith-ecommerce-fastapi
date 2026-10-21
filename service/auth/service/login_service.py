"""Login service.

Lockout policy: five failed attempts within an hour lock the account for
15 minutes (enforced by `LoginCacheImpl`). A successful login clears both
the counter and the lock."""

from __future__ import annotations

from pkg.hash import Hasher, InvalidCredentialsError
from pkg.logger.logger import Logger
from service.auth.redis.interfaces import LoginCache
from service.auth.repository.interfaces import UserRepository
from service.auth.service.token_service import TokenService
from shared.domain.requests.auth import AuthRequest
from shared.domain.response.auth import TokenResponse
from shared.errors import err_account_locked, err_failed_password_no_match
from shared.observability import Observability


class LoginServiceImpl:
    def __init__(
        self,
        cache: LoginCache,
        user: UserRepository,
        hasher: Hasher,
        token_service: TokenService,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._cache = cache
        self._user = user
        self._hasher = hasher
        self._token_service = token_service
        self._logger = logger
        self._obs = obs

    async def login(self, request: AuthRequest) -> TokenResponse:
        with self._obs.span("auth.login", email=request.email):
            if await self._cache.is_account_locked(request.email):
                raise err_account_locked

            user = await self._user.find_by_email_and_verify(request.email)

            try:
                self._hasher.compare_password(user.password, request.password)
            except InvalidCredentialsError:
                await self._cache.increment_failed_login(request.email)
                raise err_failed_password_no_match from None

            access_token = await self._token_service.create_access_token(user.user_id)
            refresh_token = await self._token_service.create_refresh_token(
                user.user_id
            )

            await self._cache.reset_failed_login(request.email)

            self._logger.info("user logged in", user_id=user.user_id)
            return TokenResponse(
                access_token=access_token, refresh_token=refresh_token
            )


__all__ = ["LoginServiceImpl"]
