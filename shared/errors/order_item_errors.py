"""Order item error catalogue. Three layers, matching the files: - `err_grpc_*` — the gRPC handler's `NewGrpcError` set (bare status errors); - repository errors — `ErrInternal.WithMessage(...)` / `ErrNotFound.WithMessage`; - service errors — `ErrInternal.WithMessage(...)` / `ErrBadRequest.WithMessage`. the handlers forward service failures through `errors.ToGrpcError` (not `NewGrpcError`), so a repository 404 keeps `type = "NOT_FOUND"` on the wire — unlike category, which remaps to `"Not Found"`."""

from __future__ import annotations

from shared.errors.core import (
    err_bad_request,
    err_internal,
    err_not_found,
    new_grpc_error,
)

# Repository layer.
err_find_all_order_items = err_internal.with_message("failed to find all order items")
err_find_by_active_order_item = err_internal.with_message(
    "failed to find active order items"
)
err_find_by_trashed_order_item = err_internal.with_message(
    "failed to find trashed order items"
)
err_find_order_item_by_order = err_not_found.with_message(
    "failed to find order items by order ID"
)
err_calculate_total_price = err_internal.with_message("failed to calculate total price")
err_create_order_item = err_internal.with_message("failed to create order item")
err_update_order_item = err_internal.with_message("failed to update order item")
err_trashed_order_item = err_internal.with_message("failed to move order item to trash")
err_restore_order_item = err_internal.with_message(
    "failed to restore order item from trash"
)
err_delete_order_item_permanent = err_internal.with_message(
    "failed to permanently delete order item"
)
err_restore_all_order_item = err_internal.with_message(
    "failed to restore all trashed order items"
)
err_delete_all_order_permanent = err_internal.with_message(
    "failed to permanently delete all trashed order items"
)
err_order_item_not_found = err_not_found.with_message("order item not found")

# Service layer.
err_failed_order_item_empty_id = err_bad_request.with_message("Order item ID is empty")
err_failed_not_delete_at_order_item = err_internal.with_message(
    "Failed to delete at order item"
)
err_failed_order_item_empty = err_internal.with_message("Failed to find order item")
err_failed_invalid_quantity = err_bad_request.with_message("Invalid quantity")

err_failed_order_item_not_found = err_not_found.with_message("Order item not found")
err_failed_trashed_order_item = err_bad_request.with_message(
    "Order item is already trashed"
)
err_failed_restore_order_item = err_internal.with_message("Failed to restore order item")
err_failed_delete_order_item = err_internal.with_message("Failed to delete order item")

err_failed_create_order_item = err_internal.with_message("Failed to create order item")
err_failed_update_order_item = err_internal.with_message("Failed to update order item")
err_failed_calculate_total = err_internal.with_message("Failed to calculate total")

err_failed_find_all_order_items = err_internal.with_message(
    "Failed to find all order items"
)
err_failed_find_order_items_by_active = err_internal.with_message(
    "Failed to find active order items"
)
err_failed_find_order_items_by_trashed = err_internal.with_message(
    "Failed to find trashed order items"
)
err_failed_find_order_item_by_order = err_internal.with_message(
    "Failed to find order items by order ID"
)

err_failed_restore_all_order_item = err_internal.with_message(
    "Failed to restore all order items"
)
err_failed_delete_all_order_item = err_internal.with_message(
    "Failed to delete all order items"
)

err_grpc_invalid_id = new_grpc_error("invalid ID", 400)

__all__ = [
    # grpc
    "err_grpc_invalid_id",
    # repository
    "err_calculate_total_price",
    "err_create_order_item",
    "err_delete_all_order_permanent",
    "err_delete_order_item_permanent",
    "err_find_all_order_items",
    "err_find_by_active_order_item",
    "err_find_by_trashed_order_item",
    "err_find_order_item_by_order",
    "err_order_item_not_found",
    "err_restore_all_order_item",
    "err_restore_order_item",
    "err_trashed_order_item",
    "err_update_order_item",
    # service
    "err_failed_calculate_total",
    "err_failed_create_order_item",
    "err_failed_delete_all_order_item",
    "err_failed_delete_order_item",
    "err_failed_find_all_order_items",
    "err_failed_find_order_item_by_order",
    "err_failed_find_order_items_by_active",
    "err_failed_find_order_items_by_trashed",
    "err_failed_invalid_quantity",
    "err_failed_not_delete_at_order_item",
    "err_failed_order_item_empty",
    "err_failed_order_item_empty_id",
    "err_failed_order_item_not_found",
    "err_failed_restore_all_order_item",
    "err_failed_restore_order_item",
    "err_failed_trashed_order_item",
    "err_failed_update_order_item",
]
