"""Category error catalogue. Three layers, matching the files: - `err_grpc_*` — the gRPC handlers' `NewGrpcError` set (bare status errors); - repository errors — `ErrInternal.WithMessage(...)` / `ErrNotFound`; - service errors — `ErrInternal.WithMessage(...)` with capitalised messages."""

from __future__ import annotations

from shared.errors.core import (
    AppError,
    ErrorType,
    err_internal,
    new_grpc_error,
)

# Repository layer.
err_get_monthly_total_price = err_internal.with_message(
    "failed to get monthly total price for categories"
)
err_get_yearly_total_prices = err_internal.with_message(
    "failed to get yearly total prices for categories"
)
err_get_monthly_total_price_by_id = err_internal.with_message(
    "failed to get monthly total price by category ID"
)
err_get_yearly_total_prices_by_id = err_internal.with_message(
    "failed to get yearly total prices by category ID"
)
err_get_monthly_total_price_by_merchant = err_internal.with_message(
    "failed to get monthly total price by merchant"
)
err_get_yearly_total_prices_by_merchant = err_internal.with_message(
    "failed to get yearly total prices by merchant"
)

err_get_month_price = err_internal.with_message(
    "failed to get month price for categories"
)
err_get_year_price = err_internal.with_message(
    "failed to get year price for categories"
)
err_get_month_price_by_merchant = err_internal.with_message(
    "failed to get month price by merchant"
)
err_get_year_price_by_merchant = err_internal.with_message(
    "failed to get year price by merchant"
)
err_get_month_price_by_id = err_internal.with_message(
    "failed to get month price by category ID"
)
err_get_year_price_by_id = err_internal.with_message(
    "failed to get year price by category ID"
)

err_find_all_category = err_internal.with_message("failed to find all categories")
err_find_by_active_category = err_internal.with_message(
    "failed to find active categories"
)
err_find_by_trashed_category = err_internal.with_message(
    "failed to find trashed categories"
)
err_find_category_by_id = err_internal.with_message("failed to find category by ID")
err_find_category_by_id_trashed = err_internal.with_message(
    "failed to find trashed category by ID"
)
err_category_not_found = AppError(ErrorType.NOT_FOUND.value, 404, "Category not found")

err_create_category = err_internal.with_message("failed to create category")
err_update_category = err_internal.with_message("failed to update category")
err_trashed_category = err_internal.with_message("failed to move category to trash")
err_restore_category = err_internal.with_message("failed to restore category")
err_delete_category_permanently = err_internal.with_message(
    "failed to permanently delete category"
)

err_restore_all_categories = err_internal.with_message(
    "failed to restore all categories"
)
err_delete_all_permanent_categories = err_internal.with_message(
    "failed to permanently delete all categories"
)

# Service layer.
err_failed_find_monthly_total_price = err_internal.with_message(
    "Failed to find monthly total price"
)
err_failed_find_yearly_total_price = err_internal.with_message(
    "Failed to find yearly total price"
)
err_failed_find_monthly_total_price_by_id = err_internal.with_message(
    "Failed to find monthly total price by category ID"
)
err_failed_find_yearly_total_price_by_id = err_internal.with_message(
    "Failed to find yearly total price by category ID"
)
err_failed_find_monthly_total_price_by_merchant = err_internal.with_message(
    "Failed to find monthly total price by merchant"
)
err_failed_find_yearly_total_price_by_merchant = err_internal.with_message(
    "Failed to find yearly total price by merchant"
)

err_failed_find_month_price = err_internal.with_message("Failed to find monthly price")
err_failed_find_year_price = err_internal.with_message("Failed to find yearly price")
err_failed_find_month_price_by_merchant = err_internal.with_message(
    "Failed to find monthly price by merchant"
)
err_failed_find_year_price_by_merchant = err_internal.with_message(
    "Failed to find yearly price by merchant"
)
err_failed_find_month_price_by_id = err_internal.with_message(
    "Failed to find monthly price by category ID"
)
err_failed_find_year_price_by_id = err_internal.with_message(
    "Failed to find yearly price by category ID"
)

err_failed_find_all_categories = err_internal.with_message(
    "Failed to find all categories"
)
err_failed_find_active_categories = err_internal.with_message(
    "Failed to find active categories"
)
err_failed_find_trashed_categories = err_internal.with_message(
    "Failed to find trashed categories"
)
err_failed_find_category_by_id = err_internal.with_message(
    "Failed to find category by ID"
)
err_failed_find_category_id_trashed = err_internal.with_message(
    "Failed to find category ID trashed"
)
err_failed_remove_image_category = err_internal.with_message(
    "Failed to remove image category"
)

err_failed_create_category = err_internal.with_message("Failed to create category")
err_failed_update_category = err_internal.with_message("Failed to update category")
err_failed_trashed_category = err_internal.with_message(
    "Failed to move category to trash"
)
err_failed_restore_category = err_internal.with_message("Failed to restore category")
err_failed_delete_category_permanent = err_internal.with_message(
    "Failed to permanently delete category"
)
err_failed_restore_all_categories = err_internal.with_message(
    "Failed to restore all categories"
)
err_failed_delete_all_categories_permanent = err_internal.with_message(
    "Failed to permanently delete all categories"
)

err_grpc_validate_create_category = new_grpc_error(
    "Validation failed: invalid create category request", 400
)
err_grpc_validate_update_category = new_grpc_error(
    "Validation failed: invalid update category request", 400
)

err_grpc_category_not_found = new_grpc_error("Category not found", 404)
err_grpc_category_invalid_id = new_grpc_error("Invalid category ID", 400)
err_grpc_category_invalid_year = new_grpc_error("Invalid year", 400)
err_grpc_category_invalid_month = new_grpc_error("Invalid month", 400)
err_grpc_category_invalid_merchant_id = new_grpc_error("Invalid merchant ID", 400)

err_grpc_create_category = new_grpc_error("Failed to create category", 500)
err_grpc_update_category = new_grpc_error("Failed to update category", 500)
err_grpc_delete_category = new_grpc_error("Failed to delete category", 500)
err_grpc_find_all_category = new_grpc_error("Failed to fetch categories", 500)
err_grpc_category_stats = new_grpc_error("Failed to fetch category statistics", 500)

__all__ = [
    # grpc
    "err_grpc_category_invalid_id",
    "err_grpc_category_invalid_merchant_id",
    "err_grpc_category_invalid_month",
    "err_grpc_category_invalid_year",
    "err_grpc_category_not_found",
    "err_grpc_category_stats",
    "err_grpc_create_category",
    "err_grpc_delete_category",
    "err_grpc_find_all_category",
    "err_grpc_update_category",
    "err_grpc_validate_create_category",
    "err_grpc_validate_update_category",
    # repository
    "err_category_not_found",
    "err_create_category",
    "err_delete_all_permanent_categories",
    "err_delete_category_permanently",
    "err_find_all_category",
    "err_find_by_active_category",
    "err_find_by_trashed_category",
    "err_find_category_by_id",
    "err_find_category_by_id_trashed",
    "err_get_month_price",
    "err_get_month_price_by_id",
    "err_get_month_price_by_merchant",
    "err_get_monthly_total_price",
    "err_get_monthly_total_price_by_id",
    "err_get_monthly_total_price_by_merchant",
    "err_get_year_price",
    "err_get_year_price_by_id",
    "err_get_year_price_by_merchant",
    "err_get_yearly_total_prices",
    "err_get_yearly_total_prices_by_id",
    "err_get_yearly_total_prices_by_merchant",
    "err_restore_all_categories",
    "err_restore_category",
    "err_trashed_category",
    "err_update_category",
    # service
    "err_failed_create_category",
    "err_failed_delete_all_categories_permanent",
    "err_failed_delete_category_permanent",
    "err_failed_find_active_categories",
    "err_failed_find_all_categories",
    "err_failed_find_category_by_id",
    "err_failed_find_category_id_trashed",
    "err_failed_find_month_price",
    "err_failed_find_month_price_by_id",
    "err_failed_find_month_price_by_merchant",
    "err_failed_find_monthly_total_price",
    "err_failed_find_monthly_total_price_by_id",
    "err_failed_find_monthly_total_price_by_merchant",
    "err_failed_find_trashed_categories",
    "err_failed_find_year_price",
    "err_failed_find_year_price_by_id",
    "err_failed_find_year_price_by_merchant",
    "err_failed_find_yearly_total_price",
    "err_failed_find_yearly_total_price_by_id",
    "err_failed_find_yearly_total_price_by_merchant",
    "err_failed_remove_image_category",
    "err_failed_restore_all_categories",
    "err_failed_restore_category",
    "err_failed_trashed_category",
    "err_failed_update_category",
]
