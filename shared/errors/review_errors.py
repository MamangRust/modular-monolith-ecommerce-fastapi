"""review error catalogue. `err_grpc_invalid_id` is the generic `ErrGrpcInvalidID` name."""

from __future__ import annotations

from shared.errors.core import err_internal, err_not_found, new_grpc_error

err_review_not_found = err_not_found.with_message("review not found")
err_find_all_reviews = err_internal.with_message("failed to find all reviews")
err_find_reviews_by_product = err_internal.with_message(
    "failed to find reviews by product"
)
err_find_reviews_by_merchant = err_internal.with_message(
    "failed to find reviews by merchant"
)
err_find_active_reviews = err_internal.with_message("failed to find active reviews")
err_find_trashed_reviews = err_internal.with_message("failed to find trashed reviews")
err_find_review_by_id = err_internal.with_message("failed to find review by ID")
err_create_review = err_internal.with_message("failed to create review")
err_update_review = err_internal.with_message("failed to update review")
err_trash_review = err_internal.with_message("failed to move review to trash")
err_restore_review = err_internal.with_message("failed to restore review from trash")
err_delete_review_permanent = err_internal.with_message(
    "failed to permanently delete review"
)
err_restore_all_reviews = err_internal.with_message("failed to restore all reviews")
err_delete_all_permanent_review = err_internal.with_message(
    "failed to permanently delete all reviews"
)
err_review_internal = err_internal.with_message("review internal repository error")

err_failed_review_not_found = err_not_found.with_message("Review not found")
err_failed_find_all_reviews = err_internal.with_message("Failed to fetch all reviews")
err_failed_find_active_reviews = err_internal.with_message(
    "Failed to fetch active reviews"
)
err_failed_find_trashed_reviews = err_internal.with_message(
    "Failed to fetch trashed reviews"
)
err_failed_find_by_product_reviews = err_internal.with_message(
    "Failed to fetch reviews by product"
)
err_failed_find_by_merchant_reviews = err_internal.with_message(
    "Failed to fetch reviews by merchant"
)
err_failed_create_review = err_internal.with_message("Failed to create review")
err_failed_update_review = err_internal.with_message("Failed to update review")
err_failed_trashed_review = err_internal.with_message("Failed to move review to trash")
err_failed_restore_review = err_internal.with_message(
    "Failed to restore review from trash"
)
err_failed_delete_permanent_review = err_internal.with_message(
    "Failed to permanently delete review"
)
err_failed_restore_all_reviews = err_internal.with_message(
    "Failed to restore all reviews"
)
err_failed_delete_all_permanent_reviews = err_internal.with_message(
    "Failed to permanently delete all reviews"
)

err_grpc_invalid_id = new_grpc_error("invalid ID", 400)
err_grpc_validate_create_review = new_grpc_error(
    "validation failed: invalid create review request", 400
)
err_grpc_validate_update_review = new_grpc_error(
    "validation failed: invalid update review request", 400
)


__all__ = [
    "err_create_review",
    "err_delete_all_permanent_review",
    "err_delete_review_permanent",
    "err_failed_create_review",
    "err_failed_delete_all_permanent_reviews",
    "err_failed_delete_permanent_review",
    "err_failed_find_active_reviews",
    "err_failed_find_all_reviews",
    "err_failed_find_by_merchant_reviews",
    "err_failed_find_by_product_reviews",
    "err_failed_find_trashed_reviews",
    "err_failed_restore_all_reviews",
    "err_failed_restore_review",
    "err_failed_review_not_found",
    "err_failed_trashed_review",
    "err_failed_update_review",
    "err_find_active_reviews",
    "err_find_all_reviews",
    "err_find_review_by_id",
    "err_find_reviews_by_merchant",
    "err_find_reviews_by_product",
    "err_find_trashed_reviews",
    "err_grpc_invalid_id",
    "err_grpc_validate_create_review",
    "err_grpc_validate_update_review",
    "err_restore_all_reviews",
    "err_restore_review",
    "err_review_internal",
    "err_review_not_found",
    "err_trash_review",
    "err_update_review",
]
