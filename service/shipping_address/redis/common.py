"""Shipping address cache keys and TTL. The command cache invalidates the whole `shipping_address:*` namespace on every mutation (`InvalidateShippingAddressCache`), so no per-key list patterns are needed."""

from __future__ import annotations

TTL_DEFAULT = 300  # 5 minutes

SHIPPING_ADDRESS_ALL_KEY = "shipping_address:all:page:%d:pageSize:%d:search:%s"
SHIPPING_ADDRESS_ACTIVE_KEY = "shipping_address:active:page:%d:pageSize:%d:search:%s"
SHIPPING_ADDRESS_TRASHED_KEY = "shipping_address:trashed:page:%d:pageSize:%d:search:%s"
SHIPPING_ADDRESS_BY_ORDER_KEY = "shipping_address:order_id:%d"
SHIPPING_ADDRESS_BY_ID_KEY = "shipping_address:id:%d"

# `InvalidateShippingAddressCache` clears the whole namespace with one pattern.
ALL_PATTERN = "shipping_address:*"


def shipping_address_all_key(page: int, page_size: int, search: str) -> str:
    return SHIPPING_ADDRESS_ALL_KEY % (page, page_size, search)


def shipping_address_active_key(page: int, page_size: int, search: str) -> str:
    return SHIPPING_ADDRESS_ACTIVE_KEY % (page, page_size, search)


def shipping_address_trashed_key(page: int, page_size: int, search: str) -> str:
    return SHIPPING_ADDRESS_TRASHED_KEY % (page, page_size, search)


def shipping_address_by_order_key(order_id: int) -> str:
    return SHIPPING_ADDRESS_BY_ORDER_KEY % order_id


def shipping_address_by_id_key(shipping_id: int) -> str:
    return SHIPPING_ADDRESS_BY_ID_KEY % shipping_id


__all__ = [
    "ALL_PATTERN",
    "SHIPPING_ADDRESS_ACTIVE_KEY",
    "SHIPPING_ADDRESS_ALL_KEY",
    "SHIPPING_ADDRESS_BY_ID_KEY",
    "SHIPPING_ADDRESS_BY_ORDER_KEY",
    "SHIPPING_ADDRESS_TRASHED_KEY",
    "TTL_DEFAULT",
    "shipping_address_active_key",
    "shipping_address_all_key",
    "shipping_address_by_id_key",
    "shipping_address_by_order_key",
    "shipping_address_trashed_key",
]
