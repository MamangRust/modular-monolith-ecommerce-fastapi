"""merchant_policy error catalogue. Three layers, matching the three files: - `err_grpc_*` — the gRPC handler's `NewGrpcError` set (bare status errors); - repository errors — `ErrNotFound.WithMessage(...)` / `ErrInternal.WithMessage`; - service errors — the `ErrFailed*` sentinels. Like merchant_business (and unlike merchant_award), the query service DOES remap read failures to these sentinels. Note the service messages are lowercase (`"failed to fetch all merchant policies"`), unlike merchant_business's capitalised ones — kept verbatim."""

from __future__ import annotations

from shared.errors.core import err_internal, err_not_found, new_grpc_error

err_merchant_policy_not_found = err_not_found.with_message("merchant policy not found")
err_find_all_merchant_policies = err_internal.with_message(
    "failed to find all merchant policies"
)
err_find_active_merchant_policies = err_internal.with_message(
    "failed to find active merchant policies"
)
err_find_trashed_merchant_policies = err_internal.with_message(
    "failed to find trashed merchant policies"
)
err_find_merchant_policy_by_id = err_internal.with_message(
    "failed to find merchant policy by id"
)
err_create_merchant_policy = err_internal.with_message(
    "failed to create merchant policy"
)
err_update_merchant_policy = err_internal.with_message(
    "failed to update merchant policy"
)
err_trashed_merchant_policy = err_internal.with_message(
    "failed to move merchant policy to trash"
)
err_restore_merchant_policy = err_internal.with_message(
    "failed to restore merchant policy from trash"
)
err_delete_merchant_policy_permanent = err_internal.with_message(
    "failed to permanently delete merchant policy"
)
err_restore_all_merchant_policies = err_internal.with_message(
    "failed to restore all merchant policies"
)
err_delete_all_merchant_policies_permanent = err_internal.with_message(
    "failed to permanently delete all merchant policies"
)

err_failed_find_all_merchant_policies = err_internal.with_message(
    "failed to fetch all merchant policies"
)
err_failed_find_active_merchant_policies = err_internal.with_message(
    "failed to fetch active merchant policies"
)
err_failed_find_trashed_merchant_policies = err_internal.with_message(
    "failed to fetch trashed merchant policies"
)
err_failed_find_merchant_policy_by_id = err_internal.with_message(
    "failed to find merchant policy by id"
)
err_failed_create_merchant_policy = err_internal.with_message(
    "failed to create merchant policy"
)
err_failed_update_merchant_policy = err_internal.with_message(
    "failed to update merchant policy"
)
err_failed_trashed_merchant_policy = err_internal.with_message(
    "failed to trash merchant policy"
)
err_failed_restore_merchant_policy = err_internal.with_message(
    "failed to restore merchant policy"
)
err_failed_delete_merchant_policy_permanent = err_internal.with_message(
    "failed to permanently delete merchant policy"
)
err_failed_restore_all_merchant_policies = err_internal.with_message(
    "failed to restore all merchant policies"
)
err_failed_delete_all_merchant_policies_permanent = err_internal.with_message(
    "failed to permanently delete all merchant policies"
)

err_grpc_invalid_merchant_policy_id = new_grpc_error(
    "invalid merchant policy id", 400
)
err_grpc_validate_create_merchant_policy = new_grpc_error(
    "Validation failed: invalid create merchant policy request", 400
)
err_grpc_validate_update_merchant_policy = new_grpc_error(
    "Validation failed: invalid update merchant policy request", 400
)


__all__ = [
    # grpc
    "err_grpc_invalid_merchant_policy_id",
    "err_grpc_validate_create_merchant_policy",
    "err_grpc_validate_update_merchant_policy",
    # repository
    "err_create_merchant_policy",
    "err_delete_all_merchant_policies_permanent",
    "err_delete_merchant_policy_permanent",
    "err_find_active_merchant_policies",
    "err_find_all_merchant_policies",
    "err_find_merchant_policy_by_id",
    "err_find_trashed_merchant_policies",
    "err_merchant_policy_not_found",
    "err_restore_all_merchant_policies",
    "err_restore_merchant_policy",
    "err_trashed_merchant_policy",
    "err_update_merchant_policy",
    # service
    "err_failed_create_merchant_policy",
    "err_failed_delete_all_merchant_policies_permanent",
    "err_failed_delete_merchant_policy_permanent",
    "err_failed_find_active_merchant_policies",
    "err_failed_find_all_merchant_policies",
    "err_failed_find_merchant_policy_by_id",
    "err_failed_find_trashed_merchant_policies",
    "err_failed_restore_all_merchant_policies",
    "err_failed_restore_merchant_policy",
    "err_failed_trashed_merchant_policy",
    "err_failed_update_merchant_policy",
]
