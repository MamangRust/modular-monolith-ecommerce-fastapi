"""Review detail error catalogue. Three layers, matching the files: - `err_grpc_*` — the gRPC handler's `NewGrpcError` set (bare status errors); - repository errors — `ErrNotFound.WithMessage(...)` / `ErrInternal.WithMessage`; - (no service-layer sentinels) — the review_detail service forwards repository failures through `errorhandler.HandleError`, which returns the `AppError` unchanged, so the service propagates the repository code rather than collapsing to a 500 sentinel. the handlers forward failures through `errors.ToGrpcError` (not `NewGrpcError`), so a repository 404 keeps `type = "NOT_FOUND"` on the wire."""

from __future__ import annotations

from shared.errors.core import (
    err_internal,
    err_not_found,
    new_grpc_error,
)

# Repository layer.
err_find_all_review_details = err_not_found.with_message(
    "failed to find all review details"
)
err_find_active_review_details = err_not_found.with_message(
    "failed to find active review details"
)
err_find_trashed_review_details = err_not_found.with_message(
    "failed to find trashed review details"
)
err_find_review_detail_by_id = err_not_found.with_message(
    "failed to find review detail by ID"
)
err_find_review_detail_by_id_trashed = err_not_found.with_message(
    "failed to find trashed review detail by ID"
)
err_review_detail_not_found = err_not_found.with_message("review detail not found")

err_create_review_detail = err_internal.with_message("failed to create review detail")
err_update_review_detail = err_internal.with_message("failed to update review detail")
err_trash_review_detail = err_internal.with_message("failed to trash review detail")
err_restore_review_detail = err_internal.with_message("failed to restore review detail")
err_delete_permanent_review_detail = err_internal.with_message(
    "failed to permanently delete review detail"
)
err_restore_all_review_details = err_internal.with_message(
    "failed to restore all review details"
)
err_delete_all_permanent_review_details = err_internal.with_message(
    "failed to permanently delete all review details"
)

err_grpc_invalid_id = new_grpc_error("invalid ID", 400)
err_grpc_validate_create_review_detail = new_grpc_error(
    "validation failed: invalid create review detail request", 400
)
err_grpc_validate_update_review_detail = new_grpc_error(
    "validation failed: invalid update review detail request", 400
)

__all__ = [
    # grpc
    "err_grpc_validate_create_review_detail",
    "err_grpc_validate_update_review_detail",
    # repository
    "err_create_review_detail",
    "err_delete_all_permanent_review_details",
    "err_delete_permanent_review_detail",
    "err_find_active_review_details",
    "err_find_all_review_details",
    "err_find_review_detail_by_id",
    "err_find_review_detail_by_id_trashed",
    "err_find_trashed_review_details",
    "err_restore_all_review_details",
    "err_restore_review_detail",
    "err_review_detail_not_found",
    "err_trash_review_detail",
    "err_update_review_detail",
]
