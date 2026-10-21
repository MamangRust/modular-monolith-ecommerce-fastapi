"""User-domain error catalogue. Messages Matches the expected reference exactly, including the 409 for a duplicate email (`ErrUserEmailAlready`) which the source explicitly notes is a resource conflict rather than a malformed request."""

from __future__ import annotations

from shared.errors.core import (
    AppError,
    ErrorType,
    err_failed,
    new_grpc_error,
)

# Repository layer.
err_user_not_found_repo = AppError(ErrorType.NOT_FOUND.value, 404, "User not found")
err_user_conflict = AppError(ErrorType.CONFLICT.value, 409, "User already exists")
err_find_all_users = err_failed("find all users")
err_find_active_users = err_failed("find active users")
err_find_trashed_users = err_failed("find trashed users")
err_create_user = err_failed("create user")
err_update_user = err_failed("update user")
err_trashed_user = err_failed("move user to trash")
err_restore_user = err_failed("restore user from trash")
err_delete_user_permanent = err_failed("permanently delete user")
err_restore_all_users = err_failed("restore all users")
err_delete_all_users = err_failed("permanently delete all users")

# Service layer.
err_user_id_invalid = AppError(ErrorType.BAD_REQUEST.value, 400, "Invalid user ID")
err_user_not_found_res = AppError(ErrorType.NOT_FOUND.value, 404, "User not found")
err_user_email_already = AppError(
    ErrorType.CONFLICT.value, 409, "User email already exists"
)
err_user_password = AppError(ErrorType.UNAUTHORIZED.value, 401, "Invalid password")
# `err_failed_find_all`/`_active`/`_trashed` already exist in the role
# catalogue; this flattened namespace needs distinct names.
err_user_failed_find_all = err_failed("fetch users")
err_user_failed_find_active = err_failed("fetch active users")
err_user_failed_find_trashed = err_failed("fetch trashed users")
err_failed_create_user = err_failed("create user")
err_failed_update_user = err_failed("update user")
err_failed_trashed_user = err_failed("move user to trash")
err_failed_restore_user = err_failed("restore user")
err_failed_delete_permanent = err_failed("delete user permanently")
err_failed_restore_all = err_failed("restore all users")
err_failed_delete_all = err_failed("delete all users permanently")

err_grpc_user_invalid_id = new_grpc_error("Invalid user ID", 400)
err_grpc_validate_create_user = new_grpc_error(
    "Validation failed: invalid create user request", 400
)
err_grpc_validate_update_user = new_grpc_error(
    "Validation failed: invalid update user request", 400
)


__all__ = [
    "err_create_user",
    "err_delete_all_users",
    "err_delete_user_permanent",
    "err_failed_create_user",
    "err_failed_delete_all",
    "err_failed_delete_permanent",
    "err_failed_restore_all",
    "err_failed_restore_user",
    "err_failed_trashed_user",
    "err_failed_update_user",
    "err_find_active_users",
    "err_find_all_users",
    "err_find_trashed_users",
    "err_grpc_user_invalid_id",
    "err_grpc_validate_create_user",
    "err_grpc_validate_update_user",
    "err_restore_all_users",
    "err_restore_user",
    "err_trashed_user",
    "err_update_user",
    "err_user_conflict",
    "err_user_email_already",
    "err_user_failed_find_active",
    "err_user_failed_find_all",
    "err_user_failed_find_trashed",
    "err_user_id_invalid",
    "err_user_not_found_repo",
    "err_user_not_found_res",
    "err_user_password",
]
