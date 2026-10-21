"""Password reset service. Covers forgot-password, reset-password and verify-code. Deviations from (recorded in the matrix): 1. `reset_password` hashes the new password before persisting it. 2. `verify_code` raises a 404 when the code matches no user. `FindByVerificationCode` returns `(nil, nil)` on a miss and the service then dereferences `res.UserID`, which panics; a typed 404 is the intended behaviour."""

from __future__ import annotations

from datetime import datetime, timedelta

from pkg.hash import Hasher
from pkg.logger.logger import Logger
from pkg.random_string import generate_random_string
from service.auth.redis.common import RESET_TOKEN_TTL
from service.auth.redis.interfaces import PasswordResetCache
from service.auth.repository.interfaces import (
    ResetTokenRepository,
    UserRepository,
)
from shared.domain.requests.auth import CreateResetPasswordRequest, CreateResetTokenRequest
from shared.errors import (
    err_user_not_found_res,
    new_bad_request_error,
)
from shared.observability import Observability

_GO_DATETIME_LAYOUT = "%Y-%m-%d %H:%M:%S"
_RESET_TOKEN_LIFETIME = timedelta(hours=24)
_RESET_TOKEN_LENGTH = 10


class PasswordResetServiceImpl:
    def __init__(
        self,
        cache: PasswordResetCache,
        user: UserRepository,
        reset_token: ResetTokenRepository,
        hasher: Hasher,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._cache = cache
        self._user = user
        self._reset_token = reset_token
        self._hasher = hasher
        self._logger = logger
        self._obs = obs

    async def forgot_password(self, email: str) -> bool:
        with self._obs.span("auth.forgot_password", email=email):
            user = await self._user.find_by_email(email)

            token = generate_random_string(_RESET_TOKEN_LENGTH)
            expired_at = (datetime.now() + _RESET_TOKEN_LIFETIME).strftime(
                _GO_DATETIME_LAYOUT
            )
            await self._reset_token.create_reset_token(
                CreateResetTokenRequest(
                    user_id=user.user_id,
                    reset_token=token,
                    expired_at=expired_at,
                )
            )

            await self._cache.set_reset_token_cache(
                token, user.user_id, RESET_TOKEN_TTL
            )
            self._logger.info("password reset email queued", user_id=user.user_id)
            return True

    async def reset_password(self, request: CreateResetPasswordRequest) -> bool:
        with self._obs.span("auth.reset_password"):
            user_id, found = await self._cache.get_reset_token_cache(
                request.reset_token
            )
            if not found:
                token_row = await self._reset_token.find_by_token(request.reset_token)
                user_id = token_row.user_id
                await self._cache.set_reset_token_cache(
                    request.reset_token, user_id, RESET_TOKEN_TTL
                )

            if request.password != request.confirm_password:
                raise new_bad_request_error(
                    "password and confirm password do not match"
                )

            hashed = self._hasher.hash_password(request.password)
            await self._user.update_user_password(user_id, hashed)

            await self._reset_token.delete_reset_token(user_id)
            await self._cache.delete_reset_token_cache(request.reset_token)

            self._logger.info("password reset", user_id=user_id)
            return True

    async def verify_code(self, code: str) -> bool:
        with self._obs.span("auth.verify_code"):
            user = await self._user.find_by_verification_code(code)
            if user is None:
                raise err_user_not_found_res

            await self._user.update_user_is_verified(user.user_id, True)
            await self._cache.delete_verification_code_cache(user.email)

            self._logger.info("verification code accepted", user_id=user.user_id)
            return True


__all__ = ["PasswordResetServiceImpl"]
