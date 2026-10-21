"""merchant_business error catalogue. Three layers, matching the three files: - `err_grpc_*` — the gRPC handler's `NewGrpcError` set (bare status errors); - repository errors — `ErrNotFound.WithMessage(...)` / `ErrInternal.WithMessage`; - service errors — the `ErrFailed*` sentinels. `ErrGrpcMerchantBusinessNotFound` is defined but never referenced by the handler (the query service's 404 already carries `NOT_FOUND` through `errors.ToGrpcError`); it is kept for catalogue fidelity."""

from __future__ import annotations

from shared.errors.core import err_internal, err_not_found, new_grpc_error

err_merchant_business_not_found = err_not_found.with_message(
    "merchant business not found"
)
err_find_all_merchant_businesses = err_internal.with_message(
    "failed to find all merchant businesses"
)
err_find_active_merchant_businesses = err_internal.with_message(
    "failed to find active merchant businesses"
)
err_find_trashed_merchant_businesses = err_internal.with_message(
    "failed to find trashed merchant businesses"
)
err_create_merchant_business = err_internal.with_message(
    "failed to create merchant business"
)
err_update_merchant_business = err_internal.with_message(
    "failed to update merchant business"
)
err_trash_merchant_business = err_internal.with_message(
    "failed to move merchant business to trash"
)
err_restore_merchant_business = err_internal.with_message(
    "failed to restore merchant business from trash"
)
err_delete_permanent_merchant_business = err_internal.with_message(
    "failed to permanently delete merchant business"
)
err_restore_all_merchant_businesses = err_internal.with_message(
    "failed to restore all merchant businesses"
)
err_delete_all_permanent_merchant_businesses = err_internal.with_message(
    "failed to permanently delete all merchant businesses"
)
err_merchant_business_internal = err_internal.with_message(
    "merchant business internal repository error"
)

err_failed_find_all_merchant_business = err_internal.with_message(
    "Failed to fetch all merchant businesses"
)
err_failed_find_active_merchant_business = err_internal.with_message(
    "Failed to fetch active merchant businesses"
)
err_failed_find_trashed_merchant_business = err_internal.with_message(
    "Failed to fetch trashed merchant businesses"
)
err_failed_find_merchant_business_by_id = err_internal.with_message(
    "Failed to find merchant business by ID"
)
err_failed_create_merchant_business = err_internal.with_message(
    "Failed to create merchant business"
)
err_failed_update_merchant_business = err_internal.with_message(
    "Failed to update merchant business"
)
err_failed_trashed_merchant_business = err_internal.with_message(
    "Failed to trash merchant business"
)
err_failed_restore_merchant_business = err_internal.with_message(
    "Failed to restore merchant business"
)
err_failed_delete_merchant_business_permanent = err_internal.with_message(
    "Failed to permanently delete merchant business"
)
err_failed_restore_all_merchant_business = err_internal.with_message(
    "Failed to restore all merchant businesses"
)
err_failed_delete_all_merchant_business_permanent = err_internal.with_message(
    "Failed to permanently delete all merchant businesses"
)

err_grpc_validate_create_merchant_business = new_grpc_error(
    "Validation failed: invalid create merchant business request", 400
)
err_grpc_validate_update_merchant_business = new_grpc_error(
    "Validation failed: invalid update merchant business request", 400
)
err_grpc_merchant_business_not_found = new_grpc_error(
    "Merchant business not found", 404
)
err_grpc_invalid_merchant_business_id = new_grpc_error(
    "Invalid merchant business ID", 400
)


__all__ = [
    # grpc
    "err_grpc_invalid_merchant_business_id",
    "err_grpc_merchant_business_not_found",
    "err_grpc_validate_create_merchant_business",
    "err_grpc_validate_update_merchant_business",
    # repository
    "err_create_merchant_business",
    "err_delete_all_permanent_merchant_businesses",
    "err_delete_permanent_merchant_business",
    "err_find_active_merchant_businesses",
    "err_find_all_merchant_businesses",
    "err_find_trashed_merchant_businesses",
    "err_merchant_business_internal",
    "err_merchant_business_not_found",
    "err_restore_all_merchant_businesses",
    "err_restore_merchant_business",
    "err_trash_merchant_business",
    "err_update_merchant_business",
    # service
    "err_failed_create_merchant_business",
    "err_failed_delete_all_merchant_business_permanent",
    "err_failed_delete_merchant_business_permanent",
    "err_failed_find_active_merchant_business",
    "err_failed_find_all_merchant_business",
    "err_failed_find_merchant_business_by_id",
    "err_failed_find_trashed_merchant_business",
    "err_failed_restore_all_merchant_business",
    "err_failed_restore_merchant_business",
    "err_failed_trashed_merchant_business",
    "err_failed_update_merchant_business",
]
