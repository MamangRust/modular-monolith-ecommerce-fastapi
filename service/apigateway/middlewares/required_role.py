"""RBAC dependency.

`require_roles` first resolves role membership through the role
validator (cache -> Kafka), then requires at least one exact match.
An empty allow-list means "any authenticated user with at least one role"."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Request

from shared.errors import (
    new_forbidden_error,
    new_internal_error,
    new_unauthorized_error,
)

RoleDependency = Callable[[Request], Awaitable[list[str]]]


def require_roles(*allowed: str) -> RoleDependency:
    async def dependency(request: Request) -> list[str]:
        roles = getattr(request.state, "role_names", None)
        if roles is None:
            validator = getattr(request.app.state, "role_validator", None)
            if validator is None:
                raise new_internal_error().with_message(
                    "Role validator is not configured"
                )
            user_id = getattr(request.state, "user_id", None)
            if user_id is None:
                raise new_unauthorized_error("Unauthorized")
            roles = await validator.validate(user_id)
            request.state.role_names = roles

        if not allowed:
            return roles
        if any(role in allowed for role in roles):
            return roles
        raise new_forbidden_error("Role not permitted")

    return dependency


__all__ = ["RoleDependency", "require_roles"]
