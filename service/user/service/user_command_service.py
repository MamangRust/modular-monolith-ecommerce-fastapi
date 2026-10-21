"""User command service. Every mutation invalidates the cache after the repository has committed. Deviation from (recorded in the matrix): `UpdateUser` hashes the new password into a local variable but then calls the repository with the *original* request, so the plaintext password is persisted. passes the hash to the repository instead; storing plaintext would break login and is a security defect, not a wire behaviour worth preserving."""

from __future__ import annotations

from pkg.database.schema.user import (
    CreateUserRow,
    RestoreUserRow,
    TrashUserRow,
    UpdateUserRow,
)
from pkg.hash import Hasher
from pkg.logger.logger import Logger
from service.user.redis.interfaces import UserCommandCache
from service.user.repository.interfaces import UserCommandRepository, UserQueryRepository
from shared.errors import (
    AppError,
    err_user_email_already,
    err_user_password,
)
from shared.observability import Observability


class UserCommandServiceImpl:
    def __init__(
        self,
        query_repo: UserQueryRepository,
        command_repo: UserCommandRepository,
        cache: UserCommandCache,
        hasher: Hasher,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._query_repo = query_repo
        self._command_repo = command_repo
        self._cache = cache
        self._hasher = hasher
        self._logger = logger
        self._obs = obs

    async def create(
        self, firstname: str, lastname: str, email: str, password: str
    ) -> CreateUserRow:
        with self._obs.span("user.command.create", email=email):
            existing = await self._find_existing_email(email)
            if existing is not None:
                raise err_user_email_already

            hashed = self._hash_password(password)
            user = await self._command_repo.create(
                firstname, lastname, email, hashed
            )
            await self._cache.invalidate_lists()
            self._logger.info("user created", user_id=user.user_id, email=user.email)
            return user

    async def update(
        self, user_id: int, firstname: str, lastname: str, email: str, password: str
    ) -> UpdateUserRow:
        with self._obs.span("user.command.update", user_id=user_id):
            existing = await self._query_repo.find_by_id(user_id)

            if email and email != existing.email:
                duplicate = await self._find_existing_email(email)
                if duplicate is not None:
                    raise err_user_email_already

            hashed = self._hash_password(password)
            user = await self._command_repo.update(
                user_id, firstname, lastname, email, hashed
            )
            await self._cache.invalidate_user(user_id)
            self._logger.info("user updated", user_id=user_id)
            return user

    async def trash(self, user_id: int) -> TrashUserRow:
        with self._obs.span("user.command.trash", user_id=user_id):
            user = await self._command_repo.trash(user_id)
            await self._cache.invalidate_user(user_id)
            self._logger.info("user trashed", user_id=user_id)
            return user

    async def restore(self, user_id: int) -> RestoreUserRow:
        with self._obs.span("user.command.restore", user_id=user_id):
            user = await self._command_repo.restore(user_id)
            await self._cache.invalidate_user(user_id)
            self._logger.info("user restored", user_id=user_id)
            return user

    async def delete_permanent(self, user_id: int) -> None:
        with self._obs.span("user.command.delete_permanent", user_id=user_id):
            await self._command_repo.delete_permanent(user_id)
            await self._cache.invalidate_user(user_id)
            self._logger.info("user deleted permanently", user_id=user_id)

    async def restore_all(self) -> None:
        with self._obs.span("user.command.restore_all"):
            await self._command_repo.restore_all()
            await self._cache.invalidate_lists()
            self._logger.info("all users restored")

    async def delete_all_permanent(self) -> None:
        with self._obs.span("user.command.delete_all_permanent"):
            await self._command_repo.delete_all_permanent()
            await self._cache.invalidate_lists()
            self._logger.info("all users deleted permanently")

    async def _find_existing_email(self, email: str):
        """Return the existing row for `email`, or None when it is free. treats a not-found error as "email available" and propagates any other error; that distinction is preserved here."""
        try:
            return await self._query_repo.find_by_email(email)
        except AppError as exc:
            if exc.code == 404:
                return None
            raise

    def _hash_password(self, password: str) -> str:
        try:
            return self._hasher.hash_password(password)
        except Exception as exc:
            raise err_user_password.with_internal(exc) from exc


__all__ = ["UserCommandServiceImpl"]
