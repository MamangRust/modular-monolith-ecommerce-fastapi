"""Database error translation."""

from __future__ import annotations

from typing import Any

import asyncpg
from sqlalchemy.exc import ProgrammingError


class NoRowsError(Exception):

    def __init__(self, message: str = "no rows in result set") -> None:
        super().__init__(message)


def pgcode(err: BaseException) -> str | None:
    """Return the PostgreSQL SQLSTATE of an exception when available."""
    inner: Any = err
    while inner is not None:
        code = getattr(inner, "sqlstate", None)
        if code is not None:
            return str(code)
        inner = inner.__cause__ or getattr(inner, "__context__", None)
    return None


def is_unique_violation(err: BaseException) -> bool:
    return pgcode(err) == "23505"


def is_foreign_key_violation(err: BaseException) -> bool:
    return pgcode(err) == "23503"


def is_db_error(err: BaseException) -> bool:
    return isinstance(err, (asyncpg.PostgresError, ProgrammingError))
