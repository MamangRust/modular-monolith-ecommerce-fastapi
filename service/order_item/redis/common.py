"""Order item cache keys and TTL. The command cache invalidates the whole `order_item:*` namespace on every mutation (`InvalidateOrderItemCache`), so no per-key list patterns are needed."""

from __future__ import annotations

TTL_DEFAULT = 300  # 5 minutes

ORDER_ITEM_ALL_KEY = "order_item:all:page:%d:pageSize:%d:search:%s"
ORDER_ITEM_ACTIVE_KEY = "order_item:active:page:%d:pageSize:%d:search:%s"
ORDER_ITEM_TRASHED_KEY = "order_item:trashed:page:%d:pageSize:%d:search:%s"
ORDER_ITEM_BY_ORDER_KEY = "order_item:order:%d"

# `InvalidateOrderItemCache` clears the whole namespace with one pattern.
ALL_PATTERN = "order_item:*"


def order_item_all_key(page: int, page_size: int, search: str) -> str:
    return ORDER_ITEM_ALL_KEY % (page, page_size, search)


def order_item_active_key(page: int, page_size: int, search: str) -> str:
    return ORDER_ITEM_ACTIVE_KEY % (page, page_size, search)


def order_item_trashed_key(page: int, page_size: int, search: str) -> str:
    return ORDER_ITEM_TRASHED_KEY % (page, page_size, search)


def order_item_by_order_key(order_id: int) -> str:
    return ORDER_ITEM_BY_ORDER_KEY % order_id


__all__ = [
    "ALL_PATTERN",
    "ORDER_ITEM_ACTIVE_KEY",
    "ORDER_ITEM_ALL_KEY",
    "ORDER_ITEM_BY_ORDER_KEY",
    "ORDER_ITEM_TRASHED_KEY",
    "TTL_DEFAULT",
    "order_item_active_key",
    "order_item_all_key",
    "order_item_by_order_key",
    "order_item_trashed_key",
]
