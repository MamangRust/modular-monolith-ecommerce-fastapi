"""Role command service. Every mutation invalidates the role cache *after* the repository has committed. This is the deviation called out in the plan: the service held a `RoleCommandCache` but never invoked it, so reads stayed stale for up to the 5-minute TTL."""

from __future__ import annotations

from pkg.database.schema.auth import UserRole
from pkg.database.schema.role import Role
from pkg.logger.logger import Logger
from service.role.redis.interfaces import RoleCommandCache
from service.role.repository.interfaces import RoleCommandRepository
from shared.domain.requests.auth import CreateUserRoleRequest
from shared.observability import Observability


class RoleCommandServiceImpl:
    def __init__(
        self,
        repo: RoleCommandRepository,
        cache: RoleCommandCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def create(self, role_name: str) -> Role:
        with self._obs.span("role.command.create"):
            role = await self._repo.create(role_name)
            await self._cache.invalidate_lists()
            self._logger.info("role created", role_id=role.role_id, name=role.role_name)
            return role

    async def update(self, role_id: int, role_name: str) -> Role:
        with self._obs.span("role.command.update", role_id=role_id):
            role = await self._repo.update(role_id, role_name)
            await self._cache.invalidate_role(role_id)
            self._logger.info("role updated", role_id=role_id, name=role.role_name)
            return role

    async def trash(self, role_id: int) -> Role:
        with self._obs.span("role.command.trash", role_id=role_id):
            role = await self._repo.trash(role_id)
            await self._cache.invalidate_role(role_id)
            self._logger.info("role trashed", role_id=role_id)
            return role

    async def restore(self, role_id: int) -> Role:
        with self._obs.span("role.command.restore", role_id=role_id):
            role = await self._repo.restore(role_id)
            await self._cache.invalidate_role(role_id)
            self._logger.info("role restored", role_id=role_id)
            return role

    async def delete_permanent(self, role_id: int) -> None:
        with self._obs.span("role.command.delete_permanent", role_id=role_id):
            await self._repo.delete_permanent(role_id)
            await self._cache.invalidate_role(role_id)
            self._logger.info("role deleted permanently", role_id=role_id)

    async def restore_all(self) -> None:
        with self._obs.span("role.command.restore_all"):
            await self._repo.restore_all()
            await self._cache.invalidate_all()
            self._logger.info("all roles restored")

    async def delete_all_permanent(self) -> None:
        with self._obs.span("role.command.delete_all_permanent"):
            await self._repo.delete_all_permanent()
            await self._cache.invalidate_all()
            self._logger.info("all roles deleted permanently")

    async def assign_role_to_user(self, request: CreateUserRoleRequest) -> UserRole:
        with self._obs.span(
            "role.command.assign_role_to_user",
            user_id=request.user_id,
            role_id=request.role_id,
        ):
            user_role = await self._repo.assign_role_to_user(request)
            self._logger.info(
                "role assigned to user",
                user_id=request.user_id,
                role_id=request.role_id,
            )
            return user_role


__all__ = ["RoleCommandServiceImpl"]
