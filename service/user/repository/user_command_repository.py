"""User write repository. `create` is a single statement: the user insert and the `auth-register` outbox event share one transaction, so a user can never be created without its welcome-email event being queued. The outbox insert is `ON CONFLICT (event_key) DO NOTHING`, matching the idempotent enqueue. `delete_permanent` and the bulk operations ignore affected rows"""

from __future__ import annotations

import uuid

from pkg.database.database import Database
from pkg.database.errors import NoRowsError
from pkg.database.schema.user import (
    CreateUserRow,
    RestoreUserRow,
    TrashUserRow,
    UpdateUserRow,
)
from shared.errors import AppError, err_constraint_or_failed, err_no_rows_or_failed

_CREATE_USER = """
WITH inserted_user AS (
    INSERT INTO users (
        firstname, lastname, email, password,
        verification_code, is_verified, created_at, updated_at
    )
    VALUES (:firstname, :lastname, :email, :password, :verification_code,
            :is_verified, current_timestamp, current_timestamp)
    RETURNING user_id, firstname, lastname, email, password,
              verification_code, created_at, updated_at
), queued_event AS (
    INSERT INTO outbox_events (event_key, topic, message_key, payload)
    SELECT
        'auth-register:' || user_id::text,
        'email-service-topic-auth-register',
        user_id::text,
        jsonb_build_object(
            'event_id', gen_random_uuid()::text,
            'schema_version', 1,
            'event_type', 'auth.register',
            'occurred_at', now(),
            'email', email,
            'subject', 'Welcome to SanEdge',
            'body', 'Your account has been successfully created. Verify your account here: https://sanedge.example.com/login?verify_code=' || verification_code
        )
    FROM inserted_user
    ON CONFLICT (event_key) DO NOTHING
    RETURNING event_key
)
SELECT user_id, firstname, lastname, email, password, verification_code,
       created_at, updated_at
FROM inserted_user
"""

_UPDATE_USER = """
UPDATE users
SET firstname = :firstname, lastname = :lastname, email = :email,
    password = :password, updated_at = current_timestamp
WHERE user_id = :user_id AND deleted_at IS NULL
RETURNING user_id, firstname, lastname, email, password, created_at, updated_at
"""

_TRASH_USER = """
UPDATE users
SET deleted_at = current_timestamp, updated_at = current_timestamp
WHERE user_id = :user_id AND deleted_at IS NULL
RETURNING user_id, firstname, lastname, email, created_at, updated_at, deleted_at
"""

_RESTORE_USER = """
UPDATE users
SET deleted_at = NULL, updated_at = current_timestamp
WHERE user_id = :user_id AND deleted_at IS NOT NULL
RETURNING user_id, firstname, lastname, email, created_at, updated_at, deleted_at
"""

_DELETE_USER_PERMANENT = "DELETE FROM users WHERE user_id = :user_id AND deleted_at IS NOT NULL"

_RESTORE_ALL_USERS = "UPDATE users SET deleted_at = NULL WHERE deleted_at IS NOT NULL"

_DELETE_ALL_PERMANENT_USERS = "DELETE FROM users WHERE deleted_at IS NOT NULL"


class UserCommandRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def create(
        self, firstname: str, lastname: str, email: str, hashed_password: str
    ) -> CreateUserRow:
        params = {
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "password": hashed_password,
            "verification_code": str(uuid.uuid4()),
            "is_verified": False,
        }
        try:
            row = await self._db.execute(_CREATE_USER, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_constraint_or_failed(exc, "User", "create user") from exc
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "User", "create user")
        return CreateUserRow.from_row(row)

    async def update(
        self, user_id: int, firstname: str, lastname: str, email: str, hashed_password: str
    ) -> UpdateUserRow:
        try:
            row = await self._db.execute(
                _UPDATE_USER,
                {
                    "user_id": user_id,
                    "firstname": firstname,
                    "lastname": lastname,
                    "email": email,
                    "password": hashed_password,
                },
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_constraint_or_failed(exc, "User", "update user") from exc
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "User", "update user")
        return UpdateUserRow.from_row(row)

    async def trash(self, user_id: int) -> TrashUserRow:
        row = await self._db.execute(_TRASH_USER, {"user_id": user_id})
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "User", "trash user")
        return TrashUserRow.from_row(row)

    async def restore(self, user_id: int) -> RestoreUserRow:
        row = await self._db.execute(_RESTORE_USER, {"user_id": user_id})
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "User", "restore user")
        return RestoreUserRow.from_row(row)

    async def delete_permanent(self, user_id: int) -> None:
        # ignores RowsAffected here; see module docstring.
        await self._db.execute(_DELETE_USER_PERMANENT, {"user_id": user_id})

    async def restore_all(self) -> None:
        await self._db.execute(_RESTORE_ALL_USERS)

    async def delete_all_permanent(self) -> None:
        await self._db.execute(_DELETE_ALL_PERMANENT_USERS)


__all__ = ["UserCommandRepositoryImpl"]
