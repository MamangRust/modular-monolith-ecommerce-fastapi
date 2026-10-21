"""review cache keys and TTL. Key layout is verbatim (`review:all:...`, `review:product:...`, `review:merchant:...`, `review:active:...`, `review:trashed:...`, `review:id:%d`). TTL is 5 minutes (`ttlDefault`). NORMALISATION: `DeleteReviewCache` deletes `review:%d`, `reviews:all`, `reviews:active`, `reviews:trashed` — none of which match the keys actually written (the list keys are `review:all:page:...` etc. and the detail key is `review:id:%d`), so invalidation is a silent no-op. invalidates the whole `review:*` namespace instead (see `review_command_cache.py`), matching the product repository's normalisation."""

from __future__ import annotations

REVIEW_ALL_KEY = "review:all:page:%d:pageSize:%d:search:%s"
REVIEW_PRODUCT_KEY = "review:product:%d:page:%d:pageSize:%d:search:%s"
REVIEW_MERCHANT_KEY = "review:merchant:%d:page:%d:pageSize:%d:search:%s"
REVIEW_ACTIVE_KEY = "review:active:page:%d:pageSize:%d:search:%s"
REVIEW_TRASHED_KEY = "review:trashed:page:%d:pageSize:%d:search:%s"
REVIEW_BY_ID_KEY = "review:id:%d"

REVIEW_NAMESPACE_PATTERN = "review:*"

TTL_DEFAULT = 300  # 5 minutes (`ttlDefault`)


def review_all_key(page: int, page_size: int, search: str) -> str:
    return REVIEW_ALL_KEY % (page, page_size, search)


def review_product_key(product_id: int, page: int, page_size: int, search: str) -> str:
    return REVIEW_PRODUCT_KEY % (product_id, page, page_size, search)


def review_merchant_key(merchant_id: int, page: int, page_size: int, search: str) -> str:
    return REVIEW_MERCHANT_KEY % (merchant_id, page, page_size, search)


def review_active_key(page: int, page_size: int, search: str) -> str:
    return REVIEW_ACTIVE_KEY % (page, page_size, search)


def review_trashed_key(page: int, page_size: int, search: str) -> str:
    return REVIEW_TRASHED_KEY % (page, page_size, search)


def review_by_id_key(review_id: int) -> str:
    return REVIEW_BY_ID_KEY % review_id


__all__ = [
    "REVIEW_ACTIVE_KEY",
    "REVIEW_ALL_KEY",
    "REVIEW_BY_ID_KEY",
    "REVIEW_MERCHANT_KEY",
    "REVIEW_NAMESPACE_PATTERN",
    "REVIEW_PRODUCT_KEY",
    "REVIEW_TRASHED_KEY",
    "TTL_DEFAULT",
    "review_active_key",
    "review_all_key",
    "review_by_id_key",
    "review_merchant_key",
    "review_product_key",
    "review_trashed_key",
]
