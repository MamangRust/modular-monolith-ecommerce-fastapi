"""merchant_award error catalogue. Three layers, matching the three files: - `err_grpc_*` — the gRPC handler's `NewGrpcError` set (bare status errors); - repository errors — `ErrNotFound.WithMessage(...)` / `ErrInternal.WithMessage`; - service errors — the `ErrFailed*` sentinels. The message stays verbatim ("Invalid merchant ID"). Like merchant, the handlers forward failures through `errors.ToGrpcError` (not `NewGrpcError`), so a repository 404 keeps `type = "NOT_FOUND"` on the wire. The `ErrFailed*` service sentinels are the ones `errorhandler.HandleError` returns in the command service's Create/Update/ RestoreAll paths (it returns the passed sentinel unchanged), so they DO surface — unlike merchant_detail, whose service remaps far more paths."""

from __future__ import annotations

from shared.errors.core import err_internal, err_not_found, new_grpc_error

err_merchant_award_not_found = err_not_found.with_message("merchant award not found")
err_find_all_merchant_awards = err_internal.with_message(
    "failed to find all merchant awards"
)
err_find_active_merchant_awards = err_internal.with_message(
    "failed to find active merchant awards"
)
err_find_trashed_merchant_awards = err_internal.with_message(
    "failed to find trashed merchant awards"
)
err_find_by_id_merchant_award = err_internal.with_message(
    "failed to find merchant award by ID"
)
err_create_merchant_award = err_internal.with_message(
    "failed to create merchant award"
)
err_update_merchant_award = err_internal.with_message(
    "failed to update merchant award"
)
err_trashed_merchant_award = err_internal.with_message(
    "failed to move merchant award to trash"
)
err_restore_merchant_award = err_internal.with_message(
    "failed to restore merchant award from trash"
)
err_delete_merchant_award_permanent = err_internal.with_message(
    "failed to permanently delete merchant award"
)
err_restore_all_merchant_awards = err_internal.with_message(
    "failed to restore all merchant awards"
)
err_delete_all_merchant_awards_permanent = err_internal.with_message(
    "failed to permanently delete all merchant awards"
)
err_merchant_award_internal = err_internal.with_message(
    "merchant award internal repository error"
)

err_failed_find_all_merchant_awards = err_internal.with_message(
    "Failed to find all merchant awards"
)
err_failed_find_active_merchant_awards = err_internal.with_message(
    "Failed to find active merchant awards"
)
err_failed_find_trashed_merchant_awards = err_internal.with_message(
    "Failed to find trashed merchant awards"
)
err_failed_find_merchant_award_by_id = err_internal.with_message(
    "Failed to find merchant award by ID"
)
err_failed_create_merchant_award = err_internal.with_message(
    "Failed to create merchant award"
)
err_failed_update_merchant_award = err_internal.with_message(
    "Failed to update merchant award"
)
err_failed_trashed_merchant_award = err_internal.with_message(
    "Failed to trash merchant award"
)
err_failed_restore_merchant_award = err_internal.with_message(
    "Failed to restore merchant award"
)
err_failed_delete_merchant_award_permanent = err_internal.with_message(
    "Failed to permanently delete merchant award"
)
err_failed_restore_all_merchant_awards = err_internal.with_message(
    "Failed to restore all merchant awards"
)
err_failed_delete_all_merchant_awards_permanent = err_internal.with_message(
    "Failed to permanently delete all merchant awards"
)

err_grpc_merchant_award_invalid_id = new_grpc_error("Invalid merchant ID", 400)
err_grpc_validate_create_merchant_award = new_grpc_error(
    "Validation failed: invalid create merchant award request", 400
)
err_grpc_validate_update_merchant_award = new_grpc_error(
    "Validation failed: invalid update merchant award request", 400
)


__all__ = [
    # grpc
    "err_grpc_merchant_award_invalid_id",
    "err_grpc_validate_create_merchant_award",
    "err_grpc_validate_update_merchant_award",
    # repository
    "err_create_merchant_award",
    "err_delete_all_merchant_awards_permanent",
    "err_delete_merchant_award_permanent",
    "err_find_active_merchant_awards",
    "err_find_all_merchant_awards",
    "err_find_by_id_merchant_award",
    "err_find_trashed_merchant_awards",
    "err_merchant_award_internal",
    "err_merchant_award_not_found",
    "err_restore_all_merchant_awards",
    "err_restore_merchant_award",
    "err_trashed_merchant_award",
    "err_update_merchant_award",
    # service
    "err_failed_create_merchant_award",
    "err_failed_delete_all_merchant_awards_permanent",
    "err_failed_delete_merchant_award_permanent",
    "err_failed_find_active_merchant_awards",
    "err_failed_find_all_merchant_awards",
    "err_failed_find_merchant_award_by_id",
    "err_failed_find_trashed_merchant_awards",
    "err_failed_restore_all_merchant_awards",
    "err_failed_restore_merchant_award",
    "err_failed_trashed_merchant_award",
    "err_failed_update_merchant_award",
]
