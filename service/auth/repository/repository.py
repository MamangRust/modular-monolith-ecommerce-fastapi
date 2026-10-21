"""Auth repository composition. The role service owns the roles and user_roles tables, so auth reaches them over gRPC through the shared role adapters instead of reading those tables directly — where `Repositories` carries `RoleAdapter`/`UserRoleAdapter` in place of SQL repositories."""

from __future__ import annotations

from dataclasses import dataclass

import grpc.aio as grpc_aio

from pkg.adapter.role import RoleAdapter, UserRoleAdapter
from pkg.database.database import Database
from pkg.resilience.dependency_guard import DependencyGuard
from service.auth.repository.interfaces import (
    RefreshTokenRepository,
    ResetTokenRepository,
    RoleRepository,
    UserRepository,
    UserRoleRepository,
)
from service.auth.repository.refresh_token_repository import (
    RefreshTokenRepositoryImpl,
)
from service.auth.repository.reset_token_repository import ResetTokenRepositoryImpl
from service.auth.repository.user_repository import UserRepositoryImpl


@dataclass(frozen=True)
class GuardOptions:
    """Dependency guards for the role service. Role reads and user_role writes get separate breakers so one failure mode cannot starve the other."""

    role: DependencyGuard | None = None
    user_role: DependencyGuard | None = None


@dataclass(frozen=True)
class Repositories:
    user: UserRepository
    user_role: UserRoleRepository
    refresh_token: RefreshTokenRepository
    role: RoleRepository
    reset_token: ResetTokenRepository


def new_repositories(
    db: Database,
    *,
    role_channel: grpc_aio.Channel,
    guards: GuardOptions,
) -> Repositories:
    return Repositories(
        user=UserRepositoryImpl(db),
        user_role=UserRoleAdapter(role_channel, guard=guards.user_role),
        refresh_token=RefreshTokenRepositoryImpl(db),
        role=RoleAdapter(role_channel, guard=guards.role),
        reset_token=ResetTokenRepositoryImpl(db),
    )


__all__ = ["GuardOptions", "Repositories", "new_repositories"]
