"""Registration service. Flow: reject duplicate email -> hash password -> resolve `ROLE_ADMIN` -> generate a 10-char verification code -> insert user (queues the `auth-register` outbox event in the same statement) -> assign the role -> cache the verification code for 15 minutes. Deviation from (recorded in the matrix): the user insert and the role assignment are two separate statements in (and here), so a failure after the insert leaves a user without a role. This is preserved rather than silently wrapped in a transaction; the outbox event is still atomic with the insert because both live in the same CTE."""

from __future__ import annotations

from pkg.database.schema.auth import AuthCreateUserRow
from pkg.hash import Hasher
from pkg.logger.logger import Logger
from pkg.random_string import generate_random_string
from service.auth.redis.common import VERIFY_CODE_TTL
from service.auth.redis.interfaces import RegisterCache
from service.auth.repository.interfaces import (
    RoleRepository,
    UserRepository,
    UserRoleRepository,
)
from shared.domain.requests.auth import CreateUserRoleRequest, RegisterRequest
from shared.errors import AppError, err_user_email_already
from shared.observability import Observability

_DEFAULT_ROLE_NAME = "ROLE_ADMIN"
_VERIFICATION_CODE_LENGTH = 10


class RegisterServiceImpl:
    def __init__(
        self,
        cache: RegisterCache,
        user: UserRepository,
        role: RoleRepository,
        user_role: UserRoleRepository,
        hasher: Hasher,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._cache = cache
        self._user = user
        self._role = role
        self._user_role = user_role
        self._hasher = hasher
        self._logger = logger
        self._obs = obs

    async def register(self, request: RegisterRequest) -> AuthCreateUserRow:
        with self._obs.span("auth.register", email=request.email):
            # treats *any* lookup error as "email is free" (`err == nil &&
            # existingUser != nil`); mirror that so a transient lookup failure
            # does not change the outcome from the create attempt.
            try:
                await self._user.find_by_email(request.email)
            except AppError:
                pass
            else:
                raise err_user_email_already

            request.password = self._hasher.hash_password(request.password)

            role = await self._role.find_by_name(_DEFAULT_ROLE_NAME)

            request.verified_code = generate_random_string(
                _VERIFICATION_CODE_LENGTH
            )
            request.is_verified = False

            new_user = await self._user.create_user(request)

            await self._user_role.assign_role_to_user(
                CreateUserRoleRequest(
                    user_id=new_user.user_id, role_id=role.role_id
                )
            )

            await self._cache.set_verification_code_cache(
                request.email, request.verified_code, VERIFY_CODE_TTL
            )

            self._logger.info(
                "user registered", user_id=new_user.user_id, email=request.email
            )
            return new_user


__all__ = ["RegisterServiceImpl"]
