"""merchant_social_link error catalogue. Two layers, matching the two files: - repository errors - `ErrNotFound.WithMessage(...)` / `ErrInternal.WithMessage`; - service errors - the `ErrFailed*` sentinels. The `ErrFailed*` service sentinels are never raised (`errorhandler.HandleError` returns the `AppError`); they are only to keep the catalogue faithful."""

from __future__ import annotations

from shared.errors.core import err_internal, err_not_found

err_merchant_social_link_not_found = err_not_found.with_message(
    "merchant social link not found"
)
err_find_all_merchant_social_links = err_internal.with_message(
    "failed to find all merchant social links"
)
err_find_active_merchant_social_links = err_internal.with_message(
    "failed to find active merchant social links"
)
err_find_trashed_merchant_social_links = err_internal.with_message(
    "failed to find trashed merchant social links"
)
err_create_merchant_social_link = err_internal.with_message(
    "failed to create merchant social link"
)
err_update_merchant_social_link = err_internal.with_message(
    "failed to update merchant social link"
)
err_trash_merchant_social_link = err_internal.with_message(
    "failed to move merchant social link to trash"
)
err_restore_merchant_social_link = err_internal.with_message(
    "failed to restore merchant social link from trash"
)
err_delete_permanent_merchant_social_link = err_internal.with_message(
    "failed to permanently delete merchant social link"
)
err_restore_all_merchant_social_links = err_internal.with_message(
    "failed to restore all merchant social links"
)
err_delete_all_permanent_merchant_social_links = err_internal.with_message(
    "failed to permanently delete all merchant social links"
)
err_merchant_social_link_internal = err_internal.with_message(
    "merchant social link internal repository error"
)

err_failed_create_merchant_social_link = err_internal.with_message(
    "failed to create merchant social link"
)
err_failed_update_merchant_social_link = err_internal.with_message(
    "failed to update merchant social link"
)
err_failed_trash_merchant_social_link = err_internal.with_message(
    "failed to trash merchant social link"
)
err_failed_restore_merchant_social_link = err_internal.with_message(
    "failed to restore merchant social link"
)
err_failed_delete_permanent_merchant_social_link = err_internal.with_message(
    "failed to permanently delete merchant social link"
)
err_failed_restore_all_merchant_social_links = err_internal.with_message(
    "failed to restore all merchant social links"
)
err_failed_delete_all_permanent_merchant_social_links = err_internal.with_message(
    "failed to permanently delete all merchant social links"
)
# merchant_social_link service file also declares
# `ErrFailedFindMonthlyTotalPriceByMerchant` / `...YearlyTotalPrice...`; in the
# flattened Python namespace those already live in `category_errors`
# (the category stats catalogue), so they are not duplicated here.


__all__ = [
    # repository
    "err_create_merchant_social_link",
    "err_delete_all_permanent_merchant_social_links",
    "err_delete_permanent_merchant_social_link",
    "err_find_active_merchant_social_links",
    "err_find_all_merchant_social_links",
    "err_find_trashed_merchant_social_links",
    "err_merchant_social_link_internal",
    "err_merchant_social_link_not_found",
    "err_restore_all_merchant_social_links",
    "err_restore_merchant_social_link",
    "err_trash_merchant_social_link",
    "err_update_merchant_social_link",
    # service (unused - see module docstring)
    "err_failed_create_merchant_social_link",
    "err_failed_delete_all_permanent_merchant_social_links",
    "err_failed_delete_permanent_merchant_social_link",
    "err_failed_restore_all_merchant_social_links",
    "err_failed_restore_merchant_social_link",
    "err_failed_trash_merchant_social_link",
    "err_failed_update_merchant_social_link",
]
