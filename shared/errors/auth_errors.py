"""Auth-domain error catalogue. splits these across three packages; they are flattened into one module here, matching how the role/user catalogues are organised in this code. Names are prefixed per layer to avoid collisions with the existing role and user catalogues in the shared `__init__` namespace. Not: `shared/errors/refresh_token_errors/service` package is entirely unreferenced dead code (verified by grep across `service/` and `shared/`), as are `refresh_token_errors/repository`'s `ErrTokenNotFound` / `ErrFindByToken` / `ErrFindByUserID` — the auth repositories use `ErrNoRowsOrFailed` instead."""

from __future__ import annotations

from shared.errors.core import (
    AppError,
    ErrorType,
    err_failed,
    new_grpc_error,
)

# ---- gRPC handler layer (shared/errors/auth_errors) ----

err_grpc_login = new_grpc_error(
    "Login failed: invalid credentials or arguments provided", 400
)
err_grpc_get_me = new_grpc_error("Failed to fetch user info: unauthenticated", 401)
err_grpc_register_token = new_grpc_error(
    "Registration failed: invalid arguments provided", 400
)

# ---- refresh token repository (shared/errors/refresh_token_errors/repository) ----

err_create_refresh_token = err_failed("create refresh token")
err_update_refresh_token = err_failed("update refresh token")
err_delete_refresh_token = err_failed("delete refresh token")
err_delete_refresh_token_by_user_id = err_failed("delete refresh token by user ID")
err_parse_expiration_date = err_failed("parse expiration date")

# Deviation from (recorded in the matrix): reset-token
# repository reuses `ErrCreateRefreshToken` ("Failed to create refresh
# token") and `ErrDeleteByUserID` ("Failed to delete refresh token by user
# ID") for reset-token operations — a copy-paste bug.
# reset-token-specific messages instead; the HTTP code (500) is unchanged.
err_create_reset_token = err_failed("create reset token")
err_delete_reset_token_by_user_id = err_failed("delete reset token by user ID")

# ---- user-role repository/service (shared/errors/user_role_errors) ----

err_assign_role_to_user = err_failed("assign role to user")
err_remove_role_from_user = err_failed("remove role from user")
err_failed_assign_role_to_user = err_failed("assign role to user")
err_failed_remove_role_from_user = err_failed("remove role from user")

# ---- auth service additions to the user catalogue ----

err_failed_password_no_match = AppError(
    ErrorType.UNAUTHORIZED.value, 401, "Password does not match"
)
err_account_locked = AppError(
    ErrorType.FORBIDDEN.value,
    403,
    "Account temporarily locked due to many failed attempts",
)


__all__ = [
    "err_account_locked",
    "err_assign_role_to_user",
    "err_create_refresh_token",
    "err_create_reset_token",
    "err_delete_refresh_token",
    "err_delete_refresh_token_by_user_id",
    "err_delete_reset_token_by_user_id",
    "err_failed_assign_role_to_user",
    "err_failed_password_no_match",
    "err_failed_remove_role_from_user",
    "err_grpc_get_me",
    "err_grpc_login",
    "err_grpc_register_token",
    "err_parse_expiration_date",
    "err_remove_role_from_user",
    "err_update_refresh_token",
]
