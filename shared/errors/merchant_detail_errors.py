"""merchant_detail error catalogue. Three layers, matching the three files: - `err_grpc_*` — the gRPC handler's `NewGrpcError` set (bare status errors); - repository errors — `ErrNotFound.WithMessage(...)` / `ErrInternal.WithMessage`; - service errors — the `ErrFailed*` sentinels. Like merchant, the handlers forward failures through `errors.ToGrpcError` (not `NewGrpcError`), so a repository 404 keeps `type = "NOT_FOUND"` on the wire. The `ErrFailed*` service sentinels are never actually raised — `errorhandler.HandleError` returns the `AppError` unchanged — and are only to keep the catalogue faithful (they are dead code in both implementations)."""

from __future__ import annotations

from shared.errors.core import err_internal, err_not_found, new_grpc_error

err_merchant_detail_not_found = err_not_found.with_message("merchant detail not found")
err_find_all_merchant_details = err_internal.with_message(
    "failed to find all merchant details"
)
err_find_active_merchant_details = err_internal.with_message(
    "failed to find active merchant details"
)
err_find_trashed_merchant_details = err_internal.with_message(
    "failed to find trashed merchant details"
)
err_find_by_id_trashed_merchant_detail = err_internal.with_message(
    "failed to find trashed merchant detail by ID"
)
err_create_merchant_detail = err_internal.with_message(
    "failed to create merchant detail"
)
err_update_merchant_detail = err_internal.with_message(
    "failed to update merchant detail"
)
err_trash_merchant_detail = err_internal.with_message(
    "failed to move merchant detail to trash"
)
err_restore_merchant_detail = err_internal.with_message(
    "failed to restore merchant detail from trash"
)
err_delete_permanent_merchant_detail = err_internal.with_message(
    "failed to permanently delete merchant detail"
)
err_restore_all_merchant_details = err_internal.with_message(
    "failed to restore all merchant details"
)
err_delete_all_permanent_merchant_details = err_internal.with_message(
    "failed to permanently delete all merchant details"
)
err_merchant_detail_internal = err_internal.with_message(
    "merchant detail internal repository error"
)

err_failed_image_not_found = err_not_found.with_message("Image not found")
err_failed_remove_image_merchant_detail = err_internal.with_message(
    "Failed to remove image merchant detail"
)
err_failed_logo_not_found = err_internal.with_message(
    "Failed to upload logo merchant detail"
)
err_failed_remove_logo_merchant_detail = err_internal.with_message(
    "Failed to remove logo merchant detail"
)
err_failed_find_all_merchant_detail = err_internal.with_message(
    "Failed to find all merchant details"
)
err_failed_find_active_merchant_detail = err_internal.with_message(
    "Failed to find active merchant details"
)
err_failed_find_trashed_merchant_detail = err_internal.with_message(
    "Failed to find trashed merchant details"
)
err_failed_find_merchant_detail_by_id = err_internal.with_message(
    "Failed to find merchant detail by ID"
)
err_failed_create_merchant_detail = err_internal.with_message(
    "Failed to create merchant detail"
)
err_failed_update_merchant_detail = err_internal.with_message(
    "Failed to update merchant detail"
)
err_failed_trashed_merchant_detail = err_internal.with_message(
    "Failed to trash merchant detail"
)
err_failed_restore_merchant_detail = err_internal.with_message(
    "Failed to restore merchant detail"
)
err_failed_delete_merchant_detail_permanent = err_internal.with_message(
    "Failed to permanently delete merchant detail"
)
err_failed_restore_all_merchant_detail = err_internal.with_message(
    "Failed to restore all merchant details"
)
err_failed_delete_all_merchant_detail_permanent = err_internal.with_message(
    "Failed to permanently delete all merchant details"
)

err_grpc_invalid_merchant_detail_id = new_grpc_error(
    "invalid merchant detail ID", 400
)
err_grpc_validate_create_merchant_detail = new_grpc_error(
    "Validation failed: invalid create merchant detail request", 400
)
err_grpc_validate_update_merchant_detail = new_grpc_error(
    "Validation failed: invalid update merchant detail request", 400
)


__all__ = [
    # grpc
    "err_grpc_invalid_merchant_detail_id",
    "err_grpc_validate_create_merchant_detail",
    "err_grpc_validate_update_merchant_detail",
    # repository
    "err_create_merchant_detail",
    "err_delete_all_permanent_merchant_details",
    "err_delete_permanent_merchant_detail",
    "err_find_active_merchant_details",
    "err_find_all_merchant_details",
    "err_find_by_id_trashed_merchant_detail",
    "err_find_trashed_merchant_details",
    "err_merchant_detail_internal",
    "err_merchant_detail_not_found",
    "err_restore_all_merchant_details",
    "err_restore_merchant_detail",
    "err_trash_merchant_detail",
    "err_update_merchant_detail",
    # service (unused — see module docstring)
    "err_failed_create_merchant_detail",
    "err_failed_delete_all_merchant_detail_permanent",
    "err_failed_delete_merchant_detail_permanent",
    "err_failed_find_active_merchant_detail",
    "err_failed_find_all_merchant_detail",
    "err_failed_find_merchant_detail_by_id",
    "err_failed_find_trashed_merchant_detail",
    "err_failed_image_not_found",
    "err_failed_logo_not_found",
    "err_failed_remove_image_merchant_detail",
    "err_failed_remove_logo_merchant_detail",
    "err_failed_restore_all_merchant_detail",
    "err_failed_restore_merchant_detail",
    "err_failed_trashed_merchant_detail",
    "err_failed_update_merchant_detail",
]
