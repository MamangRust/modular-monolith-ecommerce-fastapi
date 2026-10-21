"""Auth user repository. Two statements queue outbox events in the same CTE as their write: - `create_user` → `auth-register` (`email-service-topic-auth-register`) - `update_user_is_verified` → `auth-verify-code-success`, only when the new value is true (`WHERE:is_verified = true`) `find_by_verification_code` returns `None` on no rows (returns `nil, nil` rather than a 404), so callers must handle the miss. Missing rows elsewhere map to the shared 404."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.errors import NoRowsError
from pkg.database.schema.auth import (
    AuthCreateUserRow,
    GetUserByEmailAndVerifiedRow,
    GetUserByVerificationCodeRow,
    UpdateUserIsVerifiedRow,
)
from pkg.database.schema.user import GetUserByEmailRow, GetUserByIDRow
from shared.domain.requests.auth import RegisterRequest
from shared.errors import (
    AppError,
    err_constraint_or_failed,
    err_no_rows_or_failed,
    err_user_not_found_repo,
    new_bad_request_error,
)

_GET_USER_BY_ID = """
SELECT user_id, firstname, lastname, email, password, created_at, updated_at
FROM users
WHERE user_id = :user_id AND deleted_at IS NULL
"""

_GET_USER_BY_EMAIL = """
SELECT user_id, email FROM users
WHERE email = :email AND deleted_at IS NULL
"""

_GET_USER_BY_EMAIL_AND_VERIFIED = """
SELECT user_id, firstname, lastname, email, password, created_at, updated_at
FROM users
WHERE email = :email AND is_verified = true AND deleted_at IS NULL
"""

_GET_USER_BY_VERIFICATION_CODE = """
SELECT user_id, firstname, lastname, email, password, created_at, updated_at
FROM users
WHERE verification_code = :verification_code
"""

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
SELECT user_id, firstname, lastname, email, password, created_at, updated_at
FROM inserted_user
"""

_UPDATE_USER_IS_VERIFIED = """
WITH updated_user AS (
    UPDATE users
    SET is_verified = :is_verified, updated_at = current_timestamp
    WHERE user_id = :user_id AND deleted_at IS NULL
    RETURNING user_id, firstname, lastname, email, password, created_at, updated_at
), queued_event AS (
    INSERT INTO outbox_events (event_key, topic, message_key, payload)
    SELECT
        'auth-verify:' || user_id::text,
        'email-service-topic-auth-verify-code-success',
        user_id::text,
        jsonb_build_object(
            'event_id', gen_random_uuid()::text,
            'schema_version', 1,
            'event_type', 'auth.verify_code_success',
            'occurred_at', now(),
            'email', email,
            'subject', 'Verification Success',
            'body', 'Your account has been successfully verified.'
        )
    FROM updated_user
    WHERE :is_verified = true
    ON CONFLICT (event_key) DO NOTHING
    RETURNING event_key
)
SELECT user_id, firstname, lastname, email, password, created_at, updated_at
FROM updated_user
"""

_UPDATE_USER_PASSWORD = """
UPDATE users
SET password = :password, updated_at = current_timestamp
WHERE user_id = :user_id AND deleted_at IS NULL
RETURNING user_id, firstname, lastname, email, password, created_at, updated_at
"""


class UserRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_by_id(self, user_id: int) -> GetUserByIDRow:
        if user_id <= 0:
            raise new_bad_request_error("user ID must be greater than zero")
        row = await self._db.scalar(_GET_USER_BY_ID, {"user_id": user_id})
        if row is None:
            raise err_user_not_found_repo
        return GetUserByIDRow.from_row(row)

    async def find_by_email(self, email: str) -> GetUserByEmailRow:
        row = await self._db.scalar(_GET_USER_BY_EMAIL, {"email": email})
        if row is None:
            raise err_user_not_found_repo
        return GetUserByEmailRow.from_row(row)

    async def find_by_email_and_verify(
        self, email: str
    ) -> GetUserByEmailAndVerifiedRow:
        row = await self._db.scalar(
            _GET_USER_BY_EMAIL_AND_VERIFIED, {"email": email}
        )
        if row is None:
            raise err_user_not_found_repo
        return GetUserByEmailAndVerifiedRow.from_row(row)

    async def find_by_verification_code(
        self, verification_code: str
    ) -> GetUserByVerificationCodeRow | None:
        row = await self._db.scalar(
            _GET_USER_BY_VERIFICATION_CODE,
            {"verification_code": verification_code},
        )
        if row is None:
            return None
        return GetUserByVerificationCodeRow.from_row(row)

    async def create_user(self, request: RegisterRequest) -> AuthCreateUserRow:
        params = {
            "firstname": request.firstname,
            "lastname": request.lastname,
            "email": request.email,
            "password": request.password,
            "verification_code": request.verified_code,
            "is_verified": request.is_verified,
        }
        try:
            row = await self._db.execute(_CREATE_USER, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_constraint_or_failed(exc, "User", "create user") from exc
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "User", "create user")
        return AuthCreateUserRow.from_row(row)

    async def update_user_is_verified(
        self, user_id: int, is_verified: bool
    ) -> UpdateUserIsVerifiedRow:
        row = await self._db.execute(
            _UPDATE_USER_IS_VERIFIED,
            {"user_id": user_id, "is_verified": is_verified},
        )
        if row is None:
            raise err_no_rows_or_failed(
                NoRowsError(), "User", "update user verification"
            )
        return UpdateUserIsVerifiedRow.from_row(row)

    async def update_user_password(
        self, user_id: int, password: str
    ) -> UpdateUserIsVerifiedRow:
        row = await self._db.execute(
            _UPDATE_USER_PASSWORD, {"user_id": user_id, "password": password}
        )
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "User", "update user password")
        return UpdateUserIsVerifiedRow.from_row(row)


__all__ = ["UserRepositoryImpl"]
