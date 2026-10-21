"""Merchant error catalogue. Three layers, matching the three files: - `err_grpc_*` — the gRPC handler's `NewGrpcError` set (bare status errors); - repository errors — `ErrNotFound.WithMessage(...)` / `ErrInternal.WithMessage`; - service errors — the `ErrFailed*` sentinels. Note on the service layer: merchant service forwards every failure through `errorhandler.HandleError`, which returns the `AppError` unchanged, so the `ErrFailed*` sentinels are never actually raised. They are here only to keep the catalogue faithful to (they are dead code in both implementations). Likewise `err_merchant_conflict` is defined but unused by the merchant code paths. Both merchant and merchant_document share `err_merchant_not_found`: the document repositories raise `ErrMerchantNotFound` on a missing row too. the handlers forward failures through `errors.ToGrpcError` (not `NewGrpcError`), so a repository 404 keeps `type = "NOT_FOUND"` on the wire."""

from __future__ import annotations

from shared.errors.core import (
    err_conflict,
    err_internal,
    err_not_found,
    new_grpc_error,
)

err_merchant_not_found = err_not_found.with_message("merchant not found")
err_find_all_merchants = err_internal.with_message("failed to find all merchants")
err_find_active_merchants = err_internal.with_message("failed to find active merchants")
err_find_trashed_merchants = err_internal.with_message("failed to find trashed merchants")
err_merchant_conflict = err_conflict.with_message("merchant already exists")

err_create_merchant = err_internal.with_message("failed to create merchant")
err_update_merchant = err_internal.with_message("failed to update merchant")

err_trashed_merchant = err_internal.with_message("failed to move merchant to trash")
err_restore_merchant = err_internal.with_message("failed to restore merchant from trash")
err_delete_merchant_permanent = err_internal.with_message(
    "failed to permanently delete merchant"
)

err_restore_all_merchants = err_internal.with_message("failed to restore all merchants")
err_delete_all_merchants = err_internal.with_message(
    "failed to permanently delete all merchants"
)

err_merchant_internal = err_internal.with_message("merchant internal repository error")

err_failed_find_all_merchants = err_internal.with_message("Failed to find all merchants")
err_failed_find_active_merchants = err_internal.with_message(
    "Failed to find active merchants"
)
err_failed_find_trashed_merchants = err_internal.with_message(
    "Failed to find trashed merchants"
)
err_failed_find_merchant_by_id = err_internal.with_message("Failed to find merchant by ID")
err_failed_create_merchant = err_internal.with_message("Failed to create merchant")
err_failed_update_merchant = err_internal.with_message("Failed to update merchant")
err_failed_trashed_merchant = err_internal.with_message("Failed to trash merchant")
err_failed_restore_merchant = err_internal.with_message("Failed to restore merchant")
err_failed_delete_merchant_permanent = err_internal.with_message(
    "Failed to permanently delete merchant"
)
err_failed_restore_all_merchants = err_internal.with_message(
    "Failed to restore all merchants"
)
err_failed_delete_all_merchants_permanent = err_internal.with_message(
    "Failed to permanently delete all merchants"
)

err_failed_find_all_merchant_documents = err_internal.with_message(
    "Failed to find all merchant documents"
)
err_failed_find_active_merchant_documents = err_internal.with_message(
    "Failed to find active merchant documents"
)
err_failed_find_trashed_merchant_documents = err_internal.with_message(
    "Failed to find trashed merchant documents"
)
err_failed_find_merchant_document_by_id = err_internal.with_message(
    "Failed to find merchant document by ID"
)
err_failed_create_merchant_document = err_internal.with_message(
    "Failed to create merchant document"
)
err_failed_update_merchant_document = err_internal.with_message(
    "Failed to update merchant document"
)
err_failed_update_merchant_document_status = err_internal.with_message(
    "Failed to update merchant document status"
)
err_failed_trashed_merchant_document = err_internal.with_message(
    "Failed to trash merchant document"
)
err_failed_restore_merchant_document = err_internal.with_message(
    "Failed to restore merchant document"
)
err_failed_delete_merchant_document_permanent = err_internal.with_message(
    "Failed to permanently delete merchant document"
)
err_failed_restore_all_merchant_documents = err_internal.with_message(
    "Failed to restore all merchant documents"
)
err_failed_delete_all_merchant_documents_permanent = err_internal.with_message(
    "Failed to permanently delete all merchant documents"
)

err_merchant_document_not_found_res = err_not_found.with_message(
    "Merchant document not found"
)

err_grpc_invalid_merchant_id = new_grpc_error("invalid merchant ID", 400)
err_grpc_merchant_invalid_id = new_grpc_error("invalid ID provided", 400)

err_grpc_validate_create_merchant = new_grpc_error(
    "Validation failed: invalid create merchant request", 400
)
err_grpc_validate_update_merchant = new_grpc_error(
    "Validation failed: invalid update merchant request", 400
)
err_grpc_validate_update_merchant_status = new_grpc_error(
    "Validation failed: invalid update merchant status request", 400
)
err_grpc_failed_update_merchant_status = new_grpc_error(
    "Failed to update merchant status", 500
)

err_grpc_validate_create_merchant_document = new_grpc_error(
    "Validation failed: invalid create merchant document request", 400
)
err_grpc_failed_update_merchant_document = new_grpc_error(
    "Failed to update merchant document", 500
)

__all__ = [
    # grpc
    "err_grpc_failed_update_merchant_document",
    "err_grpc_failed_update_merchant_status",
    "err_grpc_invalid_merchant_id",
    "err_grpc_merchant_invalid_id",
    "err_grpc_validate_create_merchant",
    "err_grpc_validate_create_merchant_document",
    "err_grpc_validate_update_merchant",
    "err_grpc_validate_update_merchant_status",
    # repository
    "err_create_merchant",
    "err_delete_all_merchants",
    "err_delete_merchant_permanent",
    "err_find_active_merchants",
    "err_find_all_merchants",
    "err_find_trashed_merchants",
    "err_merchant_conflict",
    "err_merchant_internal",
    "err_merchant_not_found",
    "err_restore_all_merchants",
    "err_restore_merchant",
    "err_trashed_merchant",
    "err_update_merchant",
    # service (unused — see module docstring)
    "err_failed_create_merchant",
    "err_failed_create_merchant_document",
    "err_failed_delete_all_merchant_documents_permanent",
    "err_failed_delete_all_merchants_permanent",
    "err_failed_delete_merchant_document_permanent",
    "err_failed_delete_merchant_permanent",
    "err_failed_find_active_merchant_documents",
    "err_failed_find_active_merchants",
    "err_failed_find_all_merchant_documents",
    "err_failed_find_all_merchants",
    "err_failed_find_merchant_by_id",
    "err_failed_find_merchant_document_by_id",
    "err_failed_find_trashed_merchant_documents",
    "err_failed_find_trashed_merchants",
    "err_failed_restore_all_merchant_documents",
    "err_failed_restore_all_merchants",
    "err_failed_restore_merchant",
    "err_failed_restore_merchant_document",
    "err_failed_trashed_merchant",
    "err_failed_trashed_merchant_document",
    "err_failed_update_merchant",
    "err_failed_update_merchant_document",
    "err_failed_update_merchant_document_status",
    "err_merchant_document_not_found_res",
]
