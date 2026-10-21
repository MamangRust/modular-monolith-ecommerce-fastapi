"""Review detail handler package."""

from service.review_detail.handler.command import ReviewDetailCommandHandler
from service.review_detail.handler.handler import Handler, new_handler
from service.review_detail.handler.query import ReviewDetailQueryHandler

__all__ = [
    "ReviewDetailCommandHandler",
    "ReviewDetailQueryHandler",
    "Handler",
    "new_handler",
]
