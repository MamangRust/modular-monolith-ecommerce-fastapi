"""product error catalogue. Three layers, matching the three files: - `err_grpc_*` — the gRPC handler's `NewGrpcError` set (bare status errors); - repository errors — `ErrNotFound.WithMessage(...)` / `ErrInternal.WithMessage`; - service errors — the `ErrFailed*` sentinels. Error-handling shape (differs from merchant_policy): the product service passes the *repository* error to `errorhandler.HandleError`, which returns it unchanged, so read/write failures surface as the repository sentinels. Only three service sentinels are actually referenced by the service — `ErrFailedCountStock` (the count-stock/adjust guards), `ErrFailedDeleteImageProduct`, and `ErrFailedDeleteAllProductsPermanent` (hard-coded on `DeleteAll`); the rest are dead in but."""

from __future__ import annotations

from shared.errors.core import err_conflict, err_internal, err_not_found, new_grpc_error

err_product_not_found = err_not_found.with_message("product not found")
err_find_all_products = err_internal.with_message("failed to find all products")
err_find_active_products = err_internal.with_message("failed to find active products")
err_find_trashed_products = err_internal.with_message("failed to find trashed products")
err_product_conflict = err_conflict.with_message("product already exists")
err_create_product = err_internal.with_message("failed to create product")
err_update_product = err_internal.with_message("failed to update product")
err_find_products_by_merchant = err_internal.with_message(
    "failed to find products by merchant"
)
err_find_products_by_category = err_internal.with_message(
    "failed to find products by category"
)
err_trashed_product = err_internal.with_message("failed to move product to trash")
err_restore_product = err_internal.with_message("failed to restore product from trash")
err_delete_product_permanent = err_internal.with_message(
    "failed to permanently delete product"
)
err_restore_all_products = err_internal.with_message("failed to restore all products")
err_delete_all_products = err_internal.with_message(
    "failed to permanently delete all products"
)
err_product_internal = err_internal.with_message("product internal repository error")
err_update_product_count_stock = err_internal.with_message(
    "failed to update product count stock"
)

err_failed_count_stock = err_internal.with_message("Failed to count stock")
err_failed_deleting_not_found_product = err_not_found.with_message("Product not found")
err_failed_delete_image_product = err_internal.with_message(
    "Failed to delete image product"
)
err_failed_find_all_products = err_internal.with_message("Failed to find all products")
err_failed_find_products_by_merchant = err_internal.with_message(
    "Failed to find products by merchant"
)
err_failed_find_products_by_category = err_internal.with_message(
    "Failed to find products by category"
)
err_failed_find_product_by_id = err_internal.with_message("Failed to find product by ID")
err_failed_find_product_trashed_by_id = err_internal.with_message(
    "Failed to find trashed product by ID"
)
err_failed_find_product_by_trashed = err_internal.with_message(
    "Failed to find product by trashed"
)
err_failed_find_products_by_active = err_internal.with_message(
    "Failed to find active products"
)
err_failed_find_products_by_trashed = err_internal.with_message(
    "Failed to find trashed products"
)
err_failed_create_product = err_internal.with_message("Failed to create product")
err_failed_update_product = err_internal.with_message("Failed to update product")
err_failed_trash_product = err_internal.with_message("Failed to trash product")
err_failed_restore_product = err_internal.with_message("Failed to restore product")
err_failed_delete_product_permanent = err_internal.with_message(
    "Failed to permanently delete product"
)
err_failed_restore_all_products = err_internal.with_message(
    "Failed to restore all products"
)
err_failed_delete_all_products_permanent = err_internal.with_message(
    "Failed to permanently delete all products"
)

err_grpc_invalid_id = new_grpc_error("invalid ID", 400)
err_grpc_validate_create_product = new_grpc_error(
    "validation failed: invalid create product request", 400
)
err_grpc_validate_update_product = new_grpc_error(
    "validation failed: invalid update product request", 400
)


__all__ = [
    # grpc
    "err_grpc_invalid_id",
    "err_grpc_validate_create_product",
    "err_grpc_validate_update_product",
    # repository
    "err_create_product",
    "err_delete_all_products",
    "err_delete_product_permanent",
    "err_find_active_products",
    "err_find_all_products",
    "err_find_products_by_category",
    "err_find_products_by_merchant",
    "err_find_trashed_products",
    "err_product_conflict",
    "err_product_internal",
    "err_product_not_found",
    "err_restore_all_products",
    "err_restore_product",
    "err_trashed_product",
    "err_update_product",
    "err_update_product_count_stock",
    # service
    "err_failed_count_stock",
    "err_failed_create_product",
    "err_failed_delete_all_products_permanent",
    "err_failed_delete_image_product",
    "err_failed_delete_product_permanent",
    "err_failed_deleting_not_found_product",
    "err_failed_find_all_products",
    "err_failed_find_product_by_id",
    "err_failed_find_product_by_trashed",
    "err_failed_find_product_trashed_by_id",
    "err_failed_find_products_by_active",
    "err_failed_find_products_by_category",
    "err_failed_find_products_by_merchant",
    "err_failed_find_products_by_trashed",
    "err_failed_restore_all_products",
    "err_failed_restore_product",
    "err_failed_trash_product",
    "err_failed_update_product",
]
