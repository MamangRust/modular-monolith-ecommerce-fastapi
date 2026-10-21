"""Shipping address error catalogue. Three layers, matching the files: - `err_grpc_*` — the gRPC handler's `NewGrpcError` set (bare status errors); - repository errors — `ErrInternal.WithMessage(...)` / `ErrNotFound.WithMessage`; - service errors — `ErrInternal.WithMessage(...)`. the handlers forward service failures through `errors.ToGrpcError` (not `NewGrpcError`), so a repository 404 keeps `type = "NOT_FOUND"` on the wire."""

from __future__ import annotations

from shared.errors.core import (
    err_internal,
    err_not_found,
    new_grpc_error,
)

# Repository layer.
err_find_all_shipping_address = err_internal.with_message(
    "failed to find all shipping addresses"
)
err_find_active_shipping_address = err_internal.with_message(
    "failed to find active shipping addresses"
)
err_find_trashed_shipping_address = err_internal.with_message(
    "failed to find trashed shipping addresses"
)
err_find_shipping_address_by_id = err_not_found.with_message(
    "failed to find shipping address by ID"
)
err_find_shipping_address_by_order = err_not_found.with_message(
    "failed to find shipping address by order ID"
)
err_create_shipping_address = err_internal.with_message(
    "failed to create shipping address"
)
err_update_shipping_address = err_internal.with_message(
    "failed to update shipping address"
)
err_trash_shipping_address = err_internal.with_message(
    "failed to trash shipping address"
)
err_restore_shipping_address = err_internal.with_message(
    "failed to restore shipping address"
)
err_delete_shipping_address_permanent = err_internal.with_message(
    "failed to permanently delete shipping address"
)
err_restore_all_shipping_addresses = err_internal.with_message(
    "failed to restore all shipping addresses"
)
err_delete_all_permanent_shipping_address = err_internal.with_message(
    "failed to permanently delete all shipping addresses"
)
err_shipping_address_not_found = err_not_found.with_message(
    "shipping address not found"
)

# Service layer.
err_failed_create_shipping_address = err_internal.with_message(
    "Failed to create shipping address"
)
err_failed_update_shipping_address = err_internal.with_message(
    "Failed to update shipping address"
)
err_failed_find_all_shipping_addresses = err_internal.with_message(
    "Failed to fetch all shipping addresses"
)
err_failed_find_active_shipping_addresses = err_internal.with_message(
    "Failed to fetch active shipping addresses"
)
err_failed_find_trashed_shipping_addresses = err_internal.with_message(
    "Failed to fetch trashed shipping addresses"
)
err_failed_find_shipping_address_by_id = err_internal.with_message(
    "Failed to find shipping address by ID"
)
err_failed_find_shipping_address_by_order = err_internal.with_message(
    "Failed to find shipping address by order ID"
)
err_failed_trash_shipping_address = err_internal.with_message(
    "Failed to trash shipping address"
)
err_failed_restore_shipping_address = err_internal.with_message(
    "Failed to restore shipping address"
)
err_failed_delete_shipping_address_permanent = err_internal.with_message(
    "Failed to permanently delete shipping address"
)
err_failed_restore_all_shipping_addresses = err_internal.with_message(
    "Failed to restore all shipping addresses"
)
err_failed_delete_all_shipping_addresses_permanent = err_internal.with_message(
    "Failed to permanently delete all shipping addresses"
)

err_grpc_invalid_id = new_grpc_error("invalid ID", 400)

__all__ = [
    # grpc
    "err_grpc_invalid_id",
    # repository
    "err_create_shipping_address",
    "err_delete_all_permanent_shipping_address",
    "err_delete_shipping_address_permanent",
    "err_find_active_shipping_address",
    "err_find_all_shipping_address",
    "err_find_shipping_address_by_id",
    "err_find_shipping_address_by_order",
    "err_find_trashed_shipping_address",
    "err_restore_all_shipping_addresses",
    "err_restore_shipping_address",
    "err_shipping_address_not_found",
    "err_trash_shipping_address",
    "err_update_shipping_address",
    # service
    "err_failed_create_shipping_address",
    "err_failed_delete_all_shipping_addresses_permanent",
    "err_failed_delete_shipping_address_permanent",
    "err_failed_find_active_shipping_addresses",
    "err_failed_find_all_shipping_addresses",
    "err_failed_find_shipping_address_by_id",
    "err_failed_find_shipping_address_by_order",
    "err_failed_find_trashed_shipping_addresses",
    "err_failed_restore_all_shipping_addresses",
    "err_failed_restore_shipping_address",
    "err_failed_trash_shipping_address",
    "err_failed_update_shipping_address",
]
