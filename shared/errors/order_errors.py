"""order error catalogue. the gRPC names are generic (`ErrGrpcInvalidYear`, `ErrGrpcFailedInvalidId`, …); prefixes them with `order` to avoid collisions in the flat `shared.errors` namespace, following cart/banner."""

from __future__ import annotations

from shared.errors.core import (
    err_bad_request,
    err_internal,
    err_not_found,
    new_grpc_error,
)

err_get_monthly_total_revenue = err_internal.with_message(
    "failed to get monthly total revenue"
)
err_get_yearly_total_revenue = err_internal.with_message(
    "failed to get yearly total revenue"
)
err_get_monthly_total_revenue_by_id = err_internal.with_message(
    "failed to get monthly total revenue by order ID"
)
err_get_yearly_total_revenue_by_id = err_internal.with_message(
    "failed to get yearly total revenue by order ID"
)
err_get_monthly_total_revenue_by_merchant = err_internal.with_message(
    "failed to get monthly total revenue by merchant"
)
err_get_yearly_total_revenue_by_merchant = err_internal.with_message(
    "failed to get yearly total revenue by merchant"
)
err_get_monthly_order = err_internal.with_message("failed to get monthly orders")
err_get_yearly_order = err_internal.with_message("failed to get yearly orders")
err_get_monthly_order_by_merchant = err_internal.with_message(
    "failed to get monthly orders by merchant"
)
err_get_yearly_order_by_merchant = err_internal.with_message(
    "failed to get yearly orders by merchant"
)
err_find_all_orders = err_internal.with_message("failed to find all orders")
err_find_by_active = err_internal.with_message("failed to find active orders")
err_find_by_trashed = err_internal.with_message("failed to find trashed orders")
err_find_by_merchant = err_internal.with_message("failed to find orders by merchant")
err_find_by_id = err_not_found.with_message("failed to find order by ID")
err_create_order = err_internal.with_message("failed to create order")
err_update_order = err_internal.with_message("failed to update order")
err_trashed_order = err_internal.with_message("failed to move order to trash")
err_restore_order = err_internal.with_message("failed to restore order from trash")
err_delete_order_permanent = err_internal.with_message(
    "failed to permanently delete order"
)
err_restore_all_order = err_internal.with_message("failed to restore all trashed orders")
err_delete_all_order_permanent = err_internal.with_message(
    "failed to permanently delete all trashed orders"
)
err_order_item_not_found = err_not_found.with_message(
    "failed to find order items by order"
)
err_order_not_found = err_not_found.with_message("order not found")

err_failed_not_delete_at_order = err_internal.with_message("Failed to delete at order")
err_insufficient_product_stock = err_bad_request.with_message(
    "Insufficient product stock"
)
err_failed_invalid_count_in_stock = err_internal.with_message(
    "Failed to find invalid count in stock"
)
err_failed_find_monthly_total_revenue = err_internal.with_message(
    "Failed to find monthly total revenue"
)
err_failed_find_yearly_total_revenue = err_internal.with_message(
    "Failed to find yearly total revenue"
)
err_failed_find_monthly_total_revenue_by_id = err_internal.with_message(
    "Failed to find monthly total revenue by order ID"
)
err_failed_find_yearly_total_revenue_by_id = err_internal.with_message(
    "Failed to find yearly total revenue by order ID"
)
err_failed_find_monthly_total_revenue_by_merchant = err_internal.with_message(
    "Failed to find monthly total revenue by merchant"
)
err_failed_find_yearly_total_revenue_by_merchant = err_internal.with_message(
    "Failed to find yearly total revenue by merchant"
)
err_failed_find_monthly_order = err_internal.with_message(
    "Failed to find monthly order"
)
err_failed_find_yearly_order = err_internal.with_message("Failed to find yearly order")
err_failed_find_monthly_order_by_merchant = err_internal.with_message(
    "Failed to find monthly order by merchant"
)
err_failed_find_yearly_order_by_merchant = err_internal.with_message(
    "Failed to find yearly order by merchant"
)
err_failed_find_all_orders = err_internal.with_message("Failed to find all orders")
err_failed_find_order_by_id = err_internal.with_message("Failed to find order by ID")
err_failed_find_orders_by_active = err_internal.with_message(
    "Failed to find active orders"
)
err_failed_find_orders_by_trashed = err_internal.with_message(
    "Failed to find trashed orders"
)
err_failed_find_orders_by_merchant = err_internal.with_message(
    "Failed to find orders by merchant"
)
err_failed_create_order = err_internal.with_message("Failed to create order")
err_failed_update_order = err_internal.with_message("Failed to update order")
err_failed_trash_order = err_internal.with_message("Failed to trash order")
err_failed_restore_order = err_internal.with_message("Failed to restore order")
err_failed_delete_order_permanent = err_internal.with_message(
    "Failed to permanently delete order"
)
err_failed_restore_all_order = err_internal.with_message("Failed to restore all orders")
err_failed_delete_all_order_permanent = err_internal.with_message(
    "Failed to permanently delete all orders"
)

err_grpc_order_invalid_year = new_grpc_error("Invalid year", 400)
err_grpc_order_invalid_month = new_grpc_error("Invalid month", 400)
err_grpc_order_invalid_merchant_id = new_grpc_error("Invalid merchant ID", 400)
err_grpc_order_invalid_id = new_grpc_error("Invalid ID", 400)
err_grpc_validate_create_order = new_grpc_error(
    "validation failed: invalid create order request", 400
)
err_grpc_validate_update_order = new_grpc_error(
    "validation failed: invalid update order request", 400
)


__all__ = [
    "err_create_order",
    "err_delete_all_order_permanent",
    "err_delete_order_permanent",
    "err_failed_create_order",
    "err_failed_delete_all_order_permanent",
    "err_failed_delete_order_permanent",
    "err_failed_find_all_orders",
    "err_failed_find_monthly_order",
    "err_failed_find_monthly_order_by_merchant",
    "err_failed_find_monthly_total_revenue",
    "err_failed_find_monthly_total_revenue_by_id",
    "err_failed_find_monthly_total_revenue_by_merchant",
    "err_failed_find_order_by_id",
    "err_failed_find_orders_by_active",
    "err_failed_find_orders_by_merchant",
    "err_failed_find_orders_by_trashed",
    "err_failed_find_yearly_order",
    "err_failed_find_yearly_order_by_merchant",
    "err_failed_find_yearly_total_revenue",
    "err_failed_find_yearly_total_revenue_by_id",
    "err_failed_find_yearly_total_revenue_by_merchant",
    "err_failed_invalid_count_in_stock",
    "err_failed_not_delete_at_order",
    "err_failed_restore_all_order",
    "err_failed_restore_order",
    "err_failed_trash_order",
    "err_failed_update_order",
    "err_find_all_orders",
    "err_find_by_active",
    "err_find_by_id",
    "err_find_by_merchant",
    "err_find_by_trashed",
    "err_get_monthly_order",
    "err_get_monthly_order_by_merchant",
    "err_get_monthly_total_revenue",
    "err_get_monthly_total_revenue_by_id",
    "err_get_monthly_total_revenue_by_merchant",
    "err_get_yearly_order",
    "err_get_yearly_order_by_merchant",
    "err_get_yearly_total_revenue",
    "err_get_yearly_total_revenue_by_id",
    "err_get_yearly_total_revenue_by_merchant",
    "err_grpc_order_invalid_id",
    "err_grpc_order_invalid_merchant_id",
    "err_grpc_order_invalid_month",
    "err_grpc_order_invalid_year",
    "err_grpc_validate_create_order",
    "err_grpc_validate_update_order",
    "err_insufficient_product_stock",
    "err_order_item_not_found",
    "err_order_not_found",
    "err_restore_all_order",
    "err_restore_order",
    "err_trashed_order",
    "err_update_order",
]
