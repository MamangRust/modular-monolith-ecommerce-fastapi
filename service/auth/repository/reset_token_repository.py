"""Auth reset-token repository. `create_reset_token` writes the token and the `auth-forgot-password` outbox event in one CTE, joining `users` so the event carries the email. Expiry is parsed with `"2006-01-02 15:04:05"` layout, not RFC3339."""

from __future__ import annotations

from datetime import datetime

from pkg.database.database import Database
from pkg.database.errors import NoRowsError
from pkg.database.schema.auth import CreateResetTokenRow, GetResetTokenRow
from shared.domain.requests.auth import CreateResetTokenRequest
from shared.errors import (
    AppError,
    err_create_reset_token,
    err_delete_reset_token_by_user_id,
    err_internal,
    err_no_rows_or_failed,
)

_GO_DATETIME_LAYOUT = "%Y-%m-%d %H:%M:%S"

_GET_RESET_TOKEN = """
SELECT user_id, token, expiry_date
FROM reset_tokens
WHERE token = :token
"""

_CREATE_RESET_TOKEN = """
WITH inserted_token AS (
    INSERT INTO reset_tokens (user_id, token, expiry_date)
    VALUES (:user_id, :token, :expiry_date)
    RETURNING user_id, token, expiry_date
), queued_event AS (
    INSERT INTO outbox_events (event_key, topic, message_key, payload)
    SELECT
        'auth-forgot-password:' || it.user_id::text || ':' || it.token,
        'email-service-topic-auth-forgot-password',
        it.user_id::text,
        jsonb_build_object(
            'event_id', gen_random_uuid()::text,
            'schema_version', 1,
            'event_type', 'auth.forgot_password',
            'occurred_at', now(),
            'email', u.email,
            'subject', 'Password Reset Request',
            'body', 'Click the reset link to change your password: https://sanedge.example.com/reset-password?token=' || it.token
        )
    FROM inserted_token it
    JOIN users u ON u.user_id = it.user_id AND u.deleted_at IS NULL
    ON CONFLICT (event_key) DO NOTHING
    RETURNING event_key
)
SELECT user_id, token, expiry_date
FROM inserted_token
"""

_DELETE_RESET_TOKEN = "DELETE FROM reset_tokens WHERE user_id = :user_id"


class ResetTokenRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_by_token(self, code: str) -> GetResetTokenRow:
        row = await self._db.scalar(_GET_RESET_TOKEN, {"token": code})
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "Reset Token", "find reset token")
        return GetResetTokenRow.from_row(row)

    async def create_reset_token(
        self, request: CreateResetTokenRequest
    ) -> CreateResetTokenRow:
        try:
            expiry_date = datetime.strptime(request.expired_at, _GO_DATETIME_LAYOUT)
        except ValueError as exc:
            raise err_internal.with_internal(exc) from exc
        try:
            row = await self._db.execute(
                _CREATE_RESET_TOKEN,
                {
                    "user_id": request.user_id,
                    "token": request.reset_token,
                    "expiry_date": expiry_date,
                },
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_create_reset_token.with_internal(exc) from exc
        if row is None:
            raise err_create_reset_token
        return CreateResetTokenRow.from_row(row)

    async def delete_reset_token(self, user_id: int) -> None:
        try:
            await self._db.execute(_DELETE_RESET_TOKEN, {"user_id": user_id})
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_reset_token_by_user_id.with_internal(exc) from exc


__all__ = ["ResetTokenRepositoryImpl"]
