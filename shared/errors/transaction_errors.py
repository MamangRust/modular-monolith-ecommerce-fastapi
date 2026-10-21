"""transaction error catalogue."""

from __future__ import annotations

from shared.errors.core import (
    err_bad_request,
    err_internal,
    err_not_found,
    new_grpc_error,
)

err_get_monthly_amount_success = err_internal.with_message(
    "failed to get monthly amount success"
)
err_get_yearly_amount_success = err_internal.with_message(
    "failed to get yearly amount success"
)
err_get_monthly_amount_failed = err_internal.with_message(
    "failed to get monthly amount failed"
)
err_get_yearly_amount_failed = err_internal.with_message(
    "failed to get yearly amount failed"
)

err_get_monthly_amount_success_by_merchant = err_internal.with_message(
    "failed to get monthly amount success by merchant"
)
err_get_yearly_amount_success_by_merchant = err_internal.with_message(
    "failed to get yearly amount success by merchant"
)
err_get_monthly_amount_failed_by_merchant = err_internal.with_message(
    "failed to get monthly amount failed by merchant"
)
err_get_yearly_amount_failed_by_merchant = err_internal.with_message(
    "failed to get yearly amount failed by merchant"
)

err_get_monthly_transaction_method = err_internal.with_message(
    "failed to get monthly transaction method"
)
err_get_yearly_transaction_method = err_internal.with_message(
    "failed to get yearly transaction method"
)
err_get_monthly_transaction_method_by_merchant = err_internal.with_message(
    "failed to get monthly transaction method by merchant"
)
err_get_yearly_transaction_method_by_merchant = err_internal.with_message(
    "failed to get yearly transaction method by merchant"
)

err_find_all_transactions = err_internal.with_message(
    "failed to find all transactions"
)
err_find_by_active = err_internal.with_message("failed to find active transactions")
err_find_by_trashed = err_internal.with_message(
    "failed to find trashed transactions"
)
err_find_by_merchant = err_internal.with_message(
    "failed to find transactions by merchant"
)
err_find_by_id = err_not_found.with_message("failed to find transaction by ID")
err_find_by_order_id = err_not_found.with_message(
    "failed to find transaction by order ID"
)

err_create_transaction = err_internal.with_message("failed to create transaction")
err_update_transaction = err_internal.with_message("failed to update transaction")
err_trashed_transaction = err_internal.with_message(
    "failed to move transaction to trash"
)
err_restore_transaction = err_internal.with_message("failed to restore transaction")
err_delete_transaction_permanently = err_internal.with_message(
    "failed to permanently delete transaction"
)
err_restore_all_transactions = err_internal.with_message(
    "failed to restore all transactions"
)
err_delete_all_transaction_permanent = err_internal.with_message(
    "failed to permanently delete all transactions"
)

err_transaction_not_found = err_not_found.with_message("transaction not found")

err_failed_payment_status_cannot_be_modified = err_bad_request.with_message(
    "Cannot modify payment status"
)
err_failed_payment_status_invalid = err_bad_request.with_message(
    "Invalid payment status"
)
err_failed_payment_insufficient_balance = err_bad_request.with_message(
    "Insufficient balance"
)
err_failed_order_item_empty = err_internal.with_message("Failed to order item empty")

err_failed_find_monthly_amount_success = err_internal.with_message(
    "Failed to find monthly amount success"
)
err_failed_find_yearly_amount_success = err_internal.with_message(
    "Failed to find yearly amount success"
)
err_failed_find_monthly_amount_failed = err_internal.with_message(
    "Failed to find monthly amount failed"
)
err_failed_find_yearly_amount_failed = err_internal.with_message(
    "Failed to find yearly amount failed"
)

err_failed_find_monthly_amount_success_by_merchant = err_internal.with_message(
    "Failed to find monthly amount success by merchant"
)
err_failed_find_yearly_amount_success_by_merchant = err_internal.with_message(
    "Failed to find yearly amount success by merchant"
)
err_failed_find_monthly_amount_failed_by_merchant = err_internal.with_message(
    "Failed to find monthly amount failed by merchant"
)
err_failed_find_yearly_amount_failed_by_merchant = err_internal.with_message(
    "Failed to find yearly amount failed by merchant"
)

err_failed_find_monthly_method = err_internal.with_message(
    "Failed to find monthly method"
)
err_failed_find_yearly_method = err_internal.with_message(
    "Failed to find yearly method"
)
err_failed_find_monthly_method_by_merchant = err_internal.with_message(
    "Failed to find monthly method by merchant"
)
err_failed_find_yearly_method_by_merchant = err_internal.with_message(
    "Failed to find yearly method by merchant"
)

err_failed_find_all_transactions = err_internal.with_message(
    "Failed to find all transactions"
)
err_failed_find_transactions_by_merchant = err_internal.with_message(
    "Failed to find transactions by merchant"
)
err_failed_find_transactions_by_active = err_internal.with_message(
    "Failed to find active transactions"
)
err_failed_find_transactions_by_trashed = err_internal.with_message(
    "Failed to find trashed transactions"
)
err_failed_find_transaction_by_id = err_internal.with_message(
    "Failed to find transaction by ID"
)
err_failed_find_transaction_by_order_id = err_internal.with_message(
    "Failed to find transaction by order ID"
)

err_failed_create_transaction = err_internal.with_message(
    "Failed to create transaction"
)
err_failed_update_transaction = err_internal.with_message(
    "Failed to update transaction"
)
err_failed_trashed_transaction = err_internal.with_message(
    "Failed to trash transaction"
)
err_failed_restore_transaction = err_internal.with_message(
    "Failed to restore transaction"
)
err_failed_delete_transaction_permanently = err_internal.with_message(
    "Failed to permanently delete transaction"
)
err_failed_restore_all_transactions = err_internal.with_message(
    "Failed to restore all transactions"
)
err_failed_delete_all_transaction_permanent = err_internal.with_message(
    "Failed to permanently delete all transactions"
)

err_grpc_invalid_id = new_grpc_error("invalid ID", 400)
err_grpc_invalid_month = new_grpc_error("invalid month", 400)
err_grpc_invalid_year = new_grpc_error("invalid year", 400)
err_grpc_invalid_merchant_id = new_grpc_error("invalid merchant ID", 400)

err_grpc_validate_create_transaction = new_grpc_error(
    "validation failed: invalid create transaction request", 400
)
err_grpc_validate_update_transaction = new_grpc_error(
    "validation failed: invalid update transaction request", 400
)


__all__ = [
    "err_create_transaction",
    "err_delete_all_transaction_permanent",
    "err_delete_transaction_permanently",
    "err_failed_create_transaction",
    "err_failed_delete_all_transaction_permanent",
    "err_failed_delete_transaction_permanently",
    "err_failed_find_all_transactions",
    "err_failed_find_monthly_amount_failed",
    "err_failed_find_monthly_amount_failed_by_merchant",
    "err_failed_find_monthly_amount_success",
    "err_failed_find_monthly_amount_success_by_merchant",
    "err_failed_find_monthly_method",
    "err_failed_find_monthly_method_by_merchant",
    "err_failed_find_transaction_by_id",
    "err_failed_find_transaction_by_order_id",
    "err_failed_find_transactions_by_active",
    "err_failed_find_transactions_by_merchant",
    "err_failed_find_transactions_by_trashed",
    "err_failed_find_yearly_amount_failed",
    "err_failed_find_yearly_amount_failed_by_merchant",
    "err_failed_find_yearly_amount_success",
    "err_failed_find_yearly_amount_success_by_merchant",
    "err_failed_find_yearly_method",
    "err_failed_find_yearly_method_by_merchant",
    "err_failed_order_item_empty",
    "err_failed_payment_insufficient_balance",
    "err_failed_payment_status_cannot_be_modified",
    "err_failed_payment_status_invalid",
    "err_failed_restore_all_transactions",
    "err_failed_restore_transaction",
    "err_failed_trashed_transaction",
    "err_failed_update_transaction",
    "err_find_all_transactions",
    "err_find_by_active",
    "err_find_by_id",
    "err_find_by_merchant",
    "err_find_by_order_id",
    "err_find_by_trashed",
    "err_get_monthly_amount_failed",
    "err_get_monthly_amount_failed_by_merchant",
    "err_get_monthly_amount_success",
    "err_get_monthly_amount_success_by_merchant",
    "err_get_monthly_transaction_method",
    "err_get_monthly_transaction_method_by_merchant",
    "err_get_yearly_amount_failed",
    "err_get_yearly_amount_failed_by_merchant",
    "err_get_yearly_amount_success",
    "err_get_yearly_amount_success_by_merchant",
    "err_get_yearly_transaction_method",
    "err_get_yearly_transaction_method_by_merchant",
    "err_grpc_invalid_id",
    "err_grpc_invalid_merchant_id",
    "err_grpc_invalid_month",
    "err_grpc_invalid_year",
    "err_grpc_validate_create_transaction",
    "err_grpc_validate_update_transaction",
    "err_restore_all_transactions",
    "err_restore_transaction",
    "err_trashed_transaction",
    "err_transaction_not_found",
    "err_update_transaction",
]
