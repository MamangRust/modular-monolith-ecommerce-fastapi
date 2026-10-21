"""Auth refresh-token repository. Expiry is parsed with `"2006-01-02 15:04:05"` layout, not RFC3339. `update` targets the newest active row for a user (`WHERE user_id =...`), matching — note the statement can touch more than one row if duplicates exist, which does not guard against either."""

from __future__ import annotations

from datetime import datetime

from pkg.database.database import Database
from pkg.database.errors import NoRowsError
from pkg.database.schema.auth import RefreshToken
from shared.domain.requests.auth import CreateRefreshToken, UpdateRefreshToken
from shared.errors import (
    AppError,
    err_create_refresh_token,
    err_delete_refresh_token,
    err_delete_refresh_token_by_user_id,
    err_no_rows_or_failed,
    err_parse_expiration_date,
    err_update_refresh_token,
)

_GO_DATETIME_LAYOUT = "%Y-%m-%d %H:%M:%S"

_CREATE_REFRESH_TOKEN = """
INSERT INTO refresh_tokens (user_id, token, expiration, created_at, updated_at)
VALUES (:user_id, :token, :expiration, current_timestamp, current_timestamp)
RETURNING refresh_token_id, user_id, token, expiration,
          created_at, updated_at, deleted_at
"""

_FIND_REFRESH_TOKEN_BY_TOKEN = """
SELECT refresh_token_id, user_id, token, expiration,
       created_at, updated_at, deleted_at
FROM refresh_tokens
WHERE token = :token AND deleted_at IS NULL
"""

_FIND_REFRESH_TOKEN_BY_USER_ID = """
SELECT refresh_token_id, user_id, token, expiration,
       created_at, updated_at, deleted_at
FROM refresh_tokens
WHERE user_id = :user_id AND deleted_at IS NULL
ORDER BY created_at DESC
LIMIT 1
"""

_UPDATE_REFRESH_TOKEN_BY_USER_ID = """
UPDATE refresh_tokens
SET token = :token, expiration = :expiration, updated_at = current_timestamp
WHERE user_id = :user_id AND deleted_at IS NULL
RETURNING refresh_token_id, user_id, token, expiration,
          created_at, updated_at, deleted_at
"""

_DELETE_REFRESH_TOKEN = "DELETE FROM refresh_tokens WHERE token = :token"

_DELETE_REFRESH_TOKEN_BY_USER_ID = "DELETE FROM refresh_tokens WHERE user_id = :user_id"


def _parse_go_datetime(value: str) -> datetime:
    try:
        return datetime.strptime(value, _GO_DATETIME_LAYOUT)
    except ValueError as exc:
        raise err_parse_expiration_date.with_internal(exc) from exc


class RefreshTokenRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_by_token(self, token: str) -> RefreshToken:
        row = await self._db.scalar(
            _FIND_REFRESH_TOKEN_BY_TOKEN, {"token": token}
        )
        if row is None:
            raise err_no_rows_or_failed(
                NoRowsError(), "Refresh Token", "find refresh token by token"
            )
        return RefreshToken.from_row(row)

    async def find_by_user_id(self, user_id: int) -> RefreshToken:
        row = await self._db.scalar(
            _FIND_REFRESH_TOKEN_BY_USER_ID, {"user_id": user_id}
        )
        if row is None:
            raise err_no_rows_or_failed(
                NoRowsError(), "Refresh Token", "find refresh token by user ID"
            )
        return RefreshToken.from_row(row)

    async def create_refresh_token(
        self, request: CreateRefreshToken
    ) -> RefreshToken:
        expiration = _parse_go_datetime(request.expires_at)
        try:
            row = await self._db.execute(
                _CREATE_REFRESH_TOKEN,
                {
                    "user_id": request.user_id,
                    "token": request.token,
                    "expiration": expiration,
                },
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_create_refresh_token.with_internal(exc) from exc
        if row is None:
            raise err_create_refresh_token
        return RefreshToken.from_row(row)

    async def update_refresh_token(
        self, request: UpdateRefreshToken
    ) -> RefreshToken:
        expiration = _parse_go_datetime(request.expires_at)
        try:
            row = await self._db.execute(
                _UPDATE_REFRESH_TOKEN_BY_USER_ID,
                {
                    "user_id": request.user_id,
                    "token": request.token,
                    "expiration": expiration,
                },
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_update_refresh_token.with_internal(exc) from exc
        if row is None:
            raise err_update_refresh_token
        return RefreshToken.from_row(row)

    async def delete_refresh_token(self, token: str) -> None:
        try:
            await self._db.execute(_DELETE_REFRESH_TOKEN, {"token": token})
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_refresh_token.with_internal(exc) from exc

    async def delete_refresh_token_by_user_id(self, user_id: int) -> None:
        try:
            await self._db.execute(
                _DELETE_REFRESH_TOKEN_BY_USER_ID, {"user_id": user_id}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_refresh_token_by_user_id.with_internal(exc) from exc


__all__ = ["RefreshTokenRepositoryImpl"]
