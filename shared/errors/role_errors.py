"""Role error catalogue."""

from __future__ import annotations

from shared.errors.core import AppError, ErrorType, err_failed, new_grpc_error

# Repository layer.
err_find_all_roles = err_failed("find all roles")
err_find_active_roles = err_failed("find active roles")
err_find_trashed_roles = err_failed("find trashed roles")
err_role_conflict = AppError(ErrorType.CONFLICT.value, 409, "Role already exists")
err_create_role = err_failed("create role")
err_update_role = err_failed("update role")
err_trashed_role = err_failed("move role to trash")
err_restore_role = err_failed("restore role from trash")
err_delete_role_permanent = err_failed("permanently delete role")
err_restore_all_roles = err_failed("restore all roles")
err_delete_all_roles = err_failed("permanently delete all roles")

# Service layer.
err_role_not_found_res = AppError(ErrorType.NOT_FOUND.value, 404, "Role not found")
# `err_failed_find_all`/`_active`/`_trashed` predate the user catalogue;
# user_errors prefixes its equivalents for that reason.
err_failed_find_all = err_failed("fetch roles")
err_failed_find_active = err_failed("fetch active roles")
err_failed_find_trashed = err_failed("fetch trashed roles")
err_failed_create_role = err_failed("create role")
err_failed_update_role = err_failed("update role")
err_failed_trashed_role = err_failed("move role to trash")
err_failed_restore_role = err_failed("restore role")
err_failed_delete_permanent_role = err_failed("delete role permanently")
err_failed_restore_all_roles = err_failed("restore all roles")
err_failed_delete_all_roles = err_failed("delete all roles permanently")

err_grpc_role_invalid_id = new_grpc_error("Invalid Role ID", 400)
err_grpc_role_invalid_name = new_grpc_error("Invalid Role Name", 400)
err_grpc_validate_create_role = new_grpc_error(
    "validation failed: invalid create Role request", 400
)
err_grpc_validate_update_role = new_grpc_error(
    "validation failed: invalid update Role request", 400
)

__all__ = [
    # grpc
    "err_grpc_role_invalid_id",
    "err_grpc_role_invalid_name",
    "err_grpc_validate_create_role",
    "err_grpc_validate_update_role",
    # repository
    "err_create_role",
    "err_delete_all_roles",
    "err_delete_role_permanent",
    "err_find_active_roles",
    "err_find_all_roles",
    "err_find_trashed_roles",
    "err_restore_all_roles",
    "err_restore_role",
    "err_role_conflict",
    "err_trashed_role",
    "err_update_role",
    # service
    "err_failed_create_role",
    "err_failed_delete_all_roles",
    "err_failed_delete_permanent_role",
    "err_failed_find_active",
    "err_failed_find_all",
    "err_failed_find_trashed",
    "err_failed_restore_all_roles",
    "err_failed_restore_role",
    "err_failed_trashed_role",
    "err_failed_update_role",
    "err_role_not_found_res",
]
