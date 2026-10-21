"""cart cache keys and TTL. The service cache is namespaced `cart:svc:...` so it never collides with the gateway's `cart:all:...` response cache (drops the gateway cache, but keeps the service namespace verbatim)."""

from __future__ import annotations

CART_SVC_ALL_KEY = "cart:svc:all:user:%d:page:%d:pageSize:%d:search:%s"

TTL_DEFAULT = 300  # 5 minutes (`ttlDefault`)


def cart_svc_all_key(
    user_id: int, page: int, page_size: int, search: str
) -> str:
    return CART_SVC_ALL_KEY % (user_id, page, page_size, search)


def cart_user_pattern(user_id: int) -> str:
    """Invalidation pattern for every cached listing of one user."""
    return f"cart:svc:all:user:{user_id}:*"


__all__ = [
    "CART_SVC_ALL_KEY",
    "TTL_DEFAULT",
    "cart_svc_all_key",
    "cart_user_pattern",
]
