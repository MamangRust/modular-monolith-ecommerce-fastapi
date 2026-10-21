"""Review detail repository package."""

from service.review_detail.repository.interfaces import (
    ReviewDetailCommandRepository,
    ReviewDetailQueryRepository,
)
from service.review_detail.repository.repository import Repositories, new_repositories

__all__ = [
    "ReviewDetailCommandRepository",
    "ReviewDetailQueryRepository",
    "Repositories",
    "new_repositories",
]
