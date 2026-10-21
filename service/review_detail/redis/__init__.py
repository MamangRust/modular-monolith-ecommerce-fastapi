"""Review detail caches."""

from service.review_detail.redis.common import TTL_DEFAULT, review_detail_by_id_key
from service.review_detail.redis.interfaces import (
    ReviewDetailCommandCache,
    ReviewDetailQueryCache,
)
from service.review_detail.redis.review_detail_command_cache import (
    ReviewDetailCommandCacheImpl,
)
from service.review_detail.redis.review_detail_query_cache import (
    ReviewDetailQueryCacheImpl,
)

__all__ = [
    "ReviewDetailCommandCache",
    "ReviewDetailCommandCacheImpl",
    "ReviewDetailQueryCache",
    "ReviewDetailQueryCacheImpl",
    "TTL_DEFAULT",
    "review_detail_by_id_key",
]
