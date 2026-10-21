"""Banner error catalogue."""

from __future__ import annotations

from shared.errors.core import (
    AppError,
    ErrorType,
    err_bad_request,
    err_failed,
    new_bad_request_error,
    new_grpc_error,
)

# Repository layer.
err_banner_start_date = err_bad_request.with_message(
    "banner start date must be less than end date"
)
err_banner_end_date = err_bad_request.with_message(
    "banner end date must be greater than start date"
)
err_banner_start_time = new_bad_request_error(
    "banner start time must be less than end time"
)
err_banner_end_time = new_bad_request_error(
    "banner end time must be greater than start time"
)

err_banner_not_found = AppError(ErrorType.NOT_FOUND.value, 404, "banner not found")
err_find_all_banners = err_failed("find all banners")
err_find_active_banners = err_failed("find active banners")
err_find_trashed_banners = err_failed("find trashed banners")
err_banner_conflict = AppError(ErrorType.CONFLICT.value, 409, "failed banner already exists")

err_create_banner = err_failed("create banner")
err_update_banner = err_failed("update banner")
err_trashed_banner = err_failed("move banner to trash")
err_restore_banner = err_failed("restore banner from trash")
err_delete_banner_permanent = err_failed("permanently delete banner")
err_restore_all_banners = err_failed("restore all banners")
err_delete_all_banners = err_failed("permanently delete all banners")

# Service layer.
err_banner_not_found_res = AppError(ErrorType.NOT_FOUND.value, 404, "Banner not found")
err_banner_invalid_data = AppError(ErrorType.BAD_REQUEST.value, 400, "Invalid banner data")

err_failed_find_all_banners = err_failed("fetch banners")
err_failed_find_active_banners = err_failed("fetch active banners")
err_failed_find_trashed_banners = err_failed("fetch trashed banners")

err_failed_create_banner = err_failed("create banner")
err_failed_update_banner = err_failed("update banner")
err_failed_trashed_banner = err_failed("move banner to trash")
err_failed_restore_banner = err_failed("restore banner")
err_failed_delete_banner = err_failed("permanently delete banner")
err_failed_restore_all_banners = err_failed("restore all banners")
err_failed_delete_all_banners = err_failed("permanently delete all banners")

err_grpc_banner_not_found = new_grpc_error("Banner not found", 404)
err_grpc_banner_invalid_id = new_grpc_error("Invalid Banner ID", 400)
err_grpc_validate_create_banner = new_grpc_error(
    "Validation failed: invalid create banner request", 400
)
err_grpc_validate_update_banner = new_grpc_error(
    "Validation failed: invalid update banner request", 400
)

__all__ = [
    # grpc
    "err_grpc_banner_invalid_id",
    "err_grpc_banner_not_found",
    "err_grpc_validate_create_banner",
    "err_grpc_validate_update_banner",
    # repository
    "err_banner_conflict",
    "err_banner_end_date",
    "err_banner_end_time",
    "err_banner_not_found",
    "err_banner_start_date",
    "err_banner_start_time",
    "err_create_banner",
    "err_delete_all_banners",
    "err_delete_banner_permanent",
    "err_find_active_banners",
    "err_find_all_banners",
    "err_find_trashed_banners",
    "err_restore_all_banners",
    "err_restore_banner",
    "err_trashed_banner",
    "err_update_banner",
    # service
    "err_banner_invalid_data",
    "err_banner_not_found_res",
    "err_failed_create_banner",
    "err_failed_delete_all_banners",
    "err_failed_delete_banner",
    "err_failed_find_active_banners",
    "err_failed_find_all_banners",
    "err_failed_find_trashed_banners",
    "err_failed_restore_all_banners",
    "err_failed_restore_banner",
    "err_failed_trashed_banner",
    "err_failed_update_banner",
]
