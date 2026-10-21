"""Role write repository. `trash`/`restore` are soft (`deleted_at`), `delete_permanent` and the bulk deletes are hard. Changing those would alter REST responses, so keeps them."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.errors import NoRowsError
from pkg.database.schema.auth import UserRole
from pkg.database.schema.role import Role
from shared.domain.requests.auth import CreateUserRoleRequest
from shared.errors import AppError, err_constraint_or_failed, err_no_rows_or_failed

_RETURNING = "role_id, role_name, created_at, updated_at, deleted_at"

_CREATE_ROLE = f"""
INSERT INTO roles (role_name, created_at, updated_at)
VALUES (:role_name, current_timestamp, current_timestamp)
RETURNING {_RETURNING}
"""

_UPDATE_ROLE = f"""
UPDATE roles SET role_name = :role_name, updated_at = current_timestamp
WHERE role_id = :role_id
RETURNING {_RETURNING}
"""

_TRASH_ROLE = f"""
UPDATE roles SET deleted_at = current_timestamp
WHERE role_id = :role_id
RETURNING {_RETURNING}
"""

_RESTORE_ROLE = f"""
UPDATE roles SET deleted_at = NULL
WHERE role_id = :role_id
RETURNING {_RETURNING}
"""

_DELETE_PERMANENT = """
DELETE FROM roles WHERE role_id = :role_id AND deleted_at IS NOT NULL
RETURNING role_id
"""

_RESTORE_ALL = """
UPDATE roles SET deleted_at = NULL WHERE deleted_at IS NOT NULL
"""

_DELETE_ALL_PERMANENT = """
DELETE FROM roles WHERE deleted_at IS NOT NULL
"""

_ASSIGN_ROLE_TO_USER = """
INSERT INTO user_roles (user_id, role_id, created_at, updated_at)
VALUES (:user_id, :role_id, current_timestamp, current_timestamp)
RETURNING user_role_id, user_id, role_id, created_at, updated_at, deleted_at
"""


class RoleCommandRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def create(self, role_name: str) -> Role:
        try:
            row = await self._db.execute(_CREATE_ROLE, {"role_name": role_name})
        except AppError:
            raise
        except Exception as exc:
            raise err_constraint_or_failed(exc, "Role", "create role") from exc
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "Role", "create role")
        return Role.from_row(row)

    async def update(self, role_id: int, role_name: str) -> Role:
        try:
            row = await self._db.execute(
                _UPDATE_ROLE, {"role_id": role_id, "role_name": role_name}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_constraint_or_failed(exc, "Role", "update role") from exc
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "Role", "update role")
        return Role.from_row(row)

    async def trash(self, role_id: int) -> Role:
        row = await self._db.execute(_TRASH_ROLE, {"role_id": role_id})
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "Role", "trash role")
        return Role.from_row(row)

    async def restore(self, role_id: int) -> Role:
        row = await self._db.execute(_RESTORE_ROLE, {"role_id": role_id})
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "Role", "restore role")
        return Role.from_row(row)

    async def delete_permanent(self, role_id: int) -> None:
        # ignores RowsAffected here; see module docstring.
        await self._db.execute(_DELETE_PERMANENT, {"role_id": role_id})

    async def restore_all(self) -> None:
        await self._db.execute(_RESTORE_ALL)

    async def delete_all_permanent(self) -> None:
        await self._db.execute(_DELETE_ALL_PERMANENT)

    async def assign_role_to_user(self, request: CreateUserRoleRequest) -> UserRole:
        try:
            row = await self._db.execute(
                _ASSIGN_ROLE_TO_USER,
                {"user_id": request.user_id, "role_id": request.role_id},
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_constraint_or_failed(
                exc, "UserRole", "assign role to user"
            ) from exc
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "UserRole", "assign role to user")
        return UserRole.from_row(row)


__all__ = ["RoleCommandRepositoryImpl"]
