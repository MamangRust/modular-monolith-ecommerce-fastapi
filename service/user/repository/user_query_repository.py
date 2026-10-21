"""User read repository. SQL is kept verbatim from the reference, including the `COUNT(*) OVER` window and the `deleted_at IS NULL` filters on both the "all" and "active" queries (in they are the same predicate). Missing rows raise the shared 404 mapping, never a bare exception."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.errors import NoRowsError
from pkg.database.schema.user import (
    GetActiveUsersRow,
    GetUserByEmailRow,
    GetUserByIDRow,
    GetUsersRow,
)
from shared.errors import err_no_rows_or_failed

_GET_USERS = """
SELECT user_id, firstname, lastname, email, password, created_at, updated_at,
       COUNT(*) OVER () AS total_count
FROM users
WHERE deleted_at IS NULL
  AND (
      CAST(:search AS TEXT) IS NULL
      OR firstname ILIKE '%' || :search || '%'
      OR lastname ILIKE '%' || :search || '%'
      OR email ILIKE '%' || :search || '%'
  )
ORDER BY created_at DESC
LIMIT :limit OFFSET :offset
"""

_GET_ACTIVE_USERS = """
SELECT user_id, firstname, lastname, email, password, created_at, updated_at,
       deleted_at, COUNT(*) OVER () AS total_count
FROM users
WHERE deleted_at IS NULL
  AND (
      CAST(:search AS TEXT) IS NULL
      OR firstname ILIKE '%' || :search || '%'
      OR lastname ILIKE '%' || :search || '%'
      OR email ILIKE '%' || :search || '%'
  )
ORDER BY created_at DESC
LIMIT :limit OFFSET :offset
"""

_GET_TRASHED_USERS = """
SELECT user_id, firstname, lastname, email, password, created_at, updated_at,
       deleted_at, COUNT(*) OVER () AS total_count
FROM users
WHERE deleted_at IS NOT NULL
  AND (
      CAST(:search AS TEXT) IS NULL
      OR firstname ILIKE '%' || :search || '%'
      OR lastname ILIKE '%' || :search || '%'
      OR email ILIKE '%' || :search || '%'
  )
ORDER BY created_at DESC
LIMIT :limit OFFSET :offset
"""

_GET_USER_BY_ID = """
SELECT user_id, firstname, lastname, email, password, created_at, updated_at
FROM users
WHERE user_id = :user_id AND deleted_at IS NULL
"""

_GET_USER_BY_EMAIL = """
SELECT user_id, email FROM users
WHERE email = :email AND deleted_at IS NULL
"""


class UserQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(self, search: str, page: int, page_size: int) -> list[GetUsersRow]:
        offset = (page - 1) * page_size
        rows = await self._db.select(
            _GET_USERS,
            {"search": search, "limit": page_size, "offset": offset},
        )
        return [GetUsersRow.from_row(row) for row in rows]

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetActiveUsersRow]:
        offset = (page - 1) * page_size
        rows = await self._db.select(
            _GET_ACTIVE_USERS,
            {"search": search, "limit": page_size, "offset": offset},
        )
        return [GetActiveUsersRow.from_row(row) for row in rows]

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetActiveUsersRow]:
        offset = (page - 1) * page_size
        rows = await self._db.select(
            _GET_TRASHED_USERS,
            {"search": search, "limit": page_size, "offset": offset},
        )
        return [GetActiveUsersRow.from_row(row) for row in rows]

    async def find_by_id(self, user_id: int) -> GetUserByIDRow:
        row = await self._db.scalar(_GET_USER_BY_ID, {"user_id": user_id})
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "User", "find user")
        return GetUserByIDRow.from_row(row)

    async def find_by_email(self, email: str) -> GetUserByEmailRow:
        row = await self._db.scalar(_GET_USER_BY_EMAIL, {"email": email})
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "User", "find user")
        return GetUserByEmailRow.from_row(row)


__all__ = ["UserQueryRepositoryImpl"]
