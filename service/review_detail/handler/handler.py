"""Review detail handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.review_detail.handler.command import ReviewDetailCommandHandler
from service.review_detail.handler.query import ReviewDetailQueryHandler
from service.review_detail.service.service import Service


@dataclass(frozen=True)
class Handler:
    review_detail_query: ReviewDetailQueryHandler
    review_detail_command: ReviewDetailCommandHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        review_detail_query=ReviewDetailQueryHandler(service.review_detail_query, logger),
        review_detail_command=ReviewDetailCommandHandler(
            service.review_detail_command, logger
        ),
    )


__all__ = ["Handler", "new_handler"]
