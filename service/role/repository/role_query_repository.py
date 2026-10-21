"""Role read repository. SQL is kept verbatim from the reference, including the `COUNT(*) OVER` window that supplies `total_count` in the same round trip as the page. Soft-delete is filtered explicitly (`deleted_at`), never by an ORM default scope."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.errors import NoRowsError
from pkg.database.schema.role import GetActiveRolesRow, GetRolesRow, Role
from shared.errors import err_no_rows_or_failed

_GET_ROLES = """
SELECT role_id, role_name, created_at, updated_at, COUNT(*) OVER () AS total_count
FROM roles
WHERE CAST(:search AS TEXT) IS NULL OR role_name ILIKE '%' || :search || '%'
ORDER BY created_at ASC
LIMIT :limit OFFSET :offset
"""

_GET_ACTIVE_ROLES = """
SELECT role_id, role_name, created_at, updated_at, deleted_at, COUNT(*) OVER () AS total_count
FROM roles
WHERE deleted_at IS NULL
  AND (CAST(:search AS TEXT) IS NULL OR role_name ILIKE '%' || :search || '%')
ORDER BY created_at ASC
LIMIT :limit OFFSET :offset
"""

_GET_TRASHED_ROLES = """
SELECT role_id, role_name, created_at, updated_at, deleted_at, COUNT(*) OVER () AS total_count
FROM roles
WHERE deleted_at IS NOT NULL
  AND (CAST(:search AS TEXT) IS NULL OR role_name ILIKE '%' || :search || '%')
ORDER BY deleted_at DESC
LIMIT :limit OFFSET :offset
"""

_GET_ROLE = """
SELECT role_id, role_name, created_at, updated_at, deleted_at
FROM roles WHERE role_id = :role_id
"""

_GET_ROLE_BY_NAME = """
SELECT role_id, role_name, created_at, updated_at, deleted_at
FROM roles WHERE role_name = :role_name
"""

_GET_USER_ROLES = """
SELECT r.role_id, r.role_name, r.created_at, r.updated_at, r.deleted_at
FROM roles r
JOIN user_roles ur ON ur.role_id = r.role_id
WHERE ur.user_id = :user_id
ORDER BY r.created_at ASC
"""


class RoleQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(self, search: str, page: int, page_size: int) -> list[GetRolesRow]:
        offset = (page - 1) * page_size
        rows = await self._db.select(
            _GET_ROLES,
            {"search": search, "limit": page_size, "offset": offset},
        )
        return [GetRolesRow.from_row(row) for row in rows]

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetActiveRolesRow]:
        offset = (page - 1) * page_size
        rows = await self._db.select(
            _GET_ACTIVE_ROLES,
            {"search": search, "limit": page_size, "offset": offset},
        )
        return [GetActiveRolesRow.from_row(row) for row in rows]

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetActiveRolesRow]:
        offset = (page - 1) * page_size
        rows = await self._db.select(
            _GET_TRASHED_ROLES,
            {"search": search, "limit": page_size, "offset": offset},
        )
        return [GetActiveRolesRow.from_row(row) for row in rows]

    async def find_by_id(self, role_id: int) -> Role:
        row = await self._db.scalar(_GET_ROLE, {"role_id": role_id})
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "Role", "find role")
        return Role.from_row(row)

    async def find_by_name(self, role_name: str) -> Role:
        row = await self._db.scalar(_GET_ROLE_BY_NAME, {"role_name": role_name})
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "Role", "find role")
        return Role.from_row(row)

    async def find_by_user_id(self, user_id: int) -> list[Role]:
        rows = await self._db.select(_GET_USER_ROLES, {"user_id": user_id})
        return [Role.from_row(row) for row in rows]


__all__ = ["RoleQueryRepositoryImpl"]
