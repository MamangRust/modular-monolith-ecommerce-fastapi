"""Slider error catalogue. Three layers, matching the files: - `err_grpc_*` — the gRPC handler's `NewGrpcError` set (bare status errors); - repository errors — `ErrNotFound.WithMessage(...)` / `ErrInternal.WithMessage`; - (no service-layer sentinels) — the slider service forwards repository failures through `errorhandler.HandleError`, which returns the `AppError` unchanged, so the service propagates the repository code rather than collapsing to a 500 sentinel. the handlers forward failures through `errors.ToGrpcError` (not `NewGrpcError`), so a repository 404 keeps `type = "NOT_FOUND"` on the wire."""

from __future__ import annotations

from shared.errors.core import (
    err_internal,
    err_not_found,
    new_grpc_error,
)

# Repository layer.
err_find_all_sliders = err_not_found.with_message("failed to find all sliders")
err_find_active_sliders = err_not_found.with_message("failed to find active sliders")
err_find_trashed_sliders = err_not_found.with_message("failed to find trashed sliders")
err_find_slider_by_id = err_not_found.with_message("failed to find slider by ID")
err_slider_not_found = err_not_found.with_message("slider not found")

err_create_slider = err_internal.with_message("failed to create slider")
err_update_slider = err_internal.with_message("failed to update slider")
err_trash_slider = err_internal.with_message("failed to trash slider")
err_restore_slider = err_internal.with_message("failed to restore slider")
err_delete_permanent_slider = err_internal.with_message(
    "failed to permanently delete slider"
)
err_restore_all_sliders = err_internal.with_message("failed to restore all sliders")
err_delete_all_permanent_sliders = err_internal.with_message(
    "failed to permanently delete all sliders"
)

err_grpc_invalid_id = new_grpc_error("invalid ID", 400)
err_grpc_validate_create_slider = new_grpc_error(
    "validation failed: invalid create slider request", 400
)
err_grpc_validate_update_slider = new_grpc_error(
    "validation failed: invalid update slider request", 400
)

__all__ = [
    # grpc
    "err_grpc_invalid_id",
    "err_grpc_validate_create_slider",
    "err_grpc_validate_update_slider",
    # repository
    "err_create_slider",
    "err_delete_all_permanent_sliders",
    "err_delete_permanent_slider",
    "err_find_active_sliders",
    "err_find_all_sliders",
    "err_find_slider_by_id",
    "err_find_trashed_sliders",
    "err_restore_all_sliders",
    "err_restore_slider",
    "err_slider_not_found",
    "err_trash_slider",
    "err_update_slider",
]
