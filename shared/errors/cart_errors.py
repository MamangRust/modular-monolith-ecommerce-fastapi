"""cart error catalogue. Three layers, matching the three files: - repository errors — `ErrNotFound.WithMessage(...)` / `ErrInternal.WithMessage`; - service/response errors — the `ErrFailed*`/`ErrCart*` sentinels; - `err_grpc_*` — the gRPC handler's `NewGrpcError` set (bare status errors). Two extra sentinels cover the business-rule checks the cart *service* builds inline with `errors.ErrBadRequest.WithMessage(...)` (`quantity <= 0` and insufficient stock). They are hoisted to module-level singletons so tests can assert identity, like the rest of."""

from __future__ import annotations

from shared.errors.core import (
    err_bad_request,
    err_conflict,
    err_internal,
    err_not_found,
    new_grpc_error,
)

err_cart_not_found = err_not_found.with_message("cart not found")
err_find_all_carts = err_internal.with_message("failed to find all carts")
err_cart_conflict = err_conflict.with_message("cart already exists")
err_create_cart = err_internal.with_message("failed to create cart")
err_delete_cart_permanent = err_internal.with_message(
    "failed to permanently delete cart"
)
err_delete_all_carts = err_internal.with_message(
    "failed to permanently delete all carts"
)

err_cart_not_found_res = err_not_found.with_message("Cart not found")
err_cart_already_exists = err_bad_request.with_message("Cart already exists")
err_cart_invalid_data = err_bad_request.with_message("Invalid cart data")
err_failed_find_all_carts = err_internal.with_message("Failed to fetch carts")
err_failed_create_cart = err_internal.with_message("Failed to create cart")
err_failed_delete_cart = err_internal.with_message("Failed to permanently delete cart")
err_failed_delete_all_carts = err_internal.with_message(
    "Failed to permanently delete all carts"
)

err_cart_quantity_zero = err_bad_request.with_message(
    "cart quantity must be greater than zero"
)
err_cart_insufficient_stock = err_bad_request.with_message("Insufficient product stock")

err_grpc_cart_not_found = new_grpc_error("Cart not found", 404)
err_grpc_cart_invalid_id = new_grpc_error("Invalid cart ID", 400)
err_grpc_failed_create_cart = new_grpc_error("Failed to create cart", 500)
err_grpc_validate_create_cart = new_grpc_error(
    "Validation failed: invalid create cart request", 400
)
err_grpc_validate_delete_cart = new_grpc_error(
    "Validation failed: invalid delete cart request", 400
)
err_grpc_validate_delete_all_cart = new_grpc_error(
    "Validation failed: invalid delete all cart request", 400
)


__all__ = [
    "err_cart_already_exists",
    "err_cart_conflict",
    "err_cart_insufficient_stock",
    "err_cart_invalid_data",
    "err_cart_not_found",
    "err_cart_not_found_res",
    "err_cart_quantity_zero",
    "err_create_cart",
    "err_delete_all_carts",
    "err_delete_cart_permanent",
    "err_failed_create_cart",
    "err_failed_delete_all_carts",
    "err_failed_delete_cart",
    "err_failed_find_all_carts",
    "err_find_all_carts",
    "err_grpc_cart_invalid_id",
    "err_grpc_cart_not_found",
    "err_grpc_failed_create_cart",
    "err_grpc_validate_create_cart",
    "err_grpc_validate_delete_all_cart",
    "err_grpc_validate_delete_cart",
]
