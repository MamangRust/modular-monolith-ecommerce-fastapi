"""review handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.review.handler.review_command import ReviewCommandHandler
from service.review.handler.review_query import ReviewQueryHandler
from service.review.service.service import Service


@dataclass(frozen=True)
class Handler:
    review_query: ReviewQueryHandler
    review_command: ReviewCommandHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        review_query=ReviewQueryHandler(service.review_query, logger),
        review_command=ReviewCommandHandler(service.review_command, logger),
    )


__all__ = ["Handler", "new_handler"]
