"""product cache keys and TTL. NORMALISATION: the merchant/category keys omit the extra filters, so two requests with different `category_id`/`min_price`/`max_price` (same merchant/page/search) share one cache entry and can return the wrong page. includes every filter in the key."""

from __future__ import annotations

PRODUCT_ALL_KEY = "product:all:page:%d:pageSize:%d:search:%s"
PRODUCT_BY_ID_KEY = "product:id:%d"
PRODUCT_ACTIVE_KEY = "product:active:page:%d:pageSize:%d:search:%s"
PRODUCT_TRASHED_KEY = "product:trashed:page:%d:pageSize:%d:search:%s"
PRODUCT_MERCHANT_KEY = (
    "product:merchant:%d:category:%d:min:%d:max:%d:page:%d:pageSize:%d:search:%s"
)
PRODUCT_CATEGORY_KEY = (
    "product:category:%s:min:%d:max:%d:page:%d:pageSize:%d:search:%s"
)

TTL_DEFAULT = 300  # 5 minutes (`ttlDefault`)


def product_all_key(page: int, page_size: int, search: str) -> str:
    return PRODUCT_ALL_KEY % (page, page_size, search)


def product_by_id_key(product_id: int) -> str:
    return PRODUCT_BY_ID_KEY % product_id


def product_active_key(page: int, page_size: int, search: str) -> str:
    return PRODUCT_ACTIVE_KEY % (page, page_size, search)


def product_trashed_key(page: int, page_size: int, search: str) -> str:
    return PRODUCT_TRASHED_KEY % (page, page_size, search)


def product_merchant_key(
    merchant_id: int,
    category_id: int,
    min_price: int,
    max_price: int,
    page: int,
    page_size: int,
    search: str,
) -> str:
    return PRODUCT_MERCHANT_KEY % (
        merchant_id,
        category_id,
        min_price,
        max_price,
        page,
        page_size,
        search,
    )


def product_category_key(
    category_name: str,
    min_price: int,
    max_price: int,
    page: int,
    page_size: int,
    search: str,
) -> str:
    return PRODUCT_CATEGORY_KEY % (
        category_name,
        min_price,
        max_price,
        page,
        page_size,
        search,
    )


__all__ = [
    "PRODUCT_ACTIVE_KEY",
    "PRODUCT_ALL_KEY",
    "PRODUCT_BY_ID_KEY",
    "PRODUCT_CATEGORY_KEY",
    "PRODUCT_MERCHANT_KEY",
    "PRODUCT_TRASHED_KEY",
    "TTL_DEFAULT",
    "product_active_key",
    "product_all_key",
    "product_by_id_key",
    "product_category_key",
    "product_merchant_key",
    "product_trashed_key",
]
