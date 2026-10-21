"""review service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.review.redis import Mencache
from service.review.repository.repository import Repositories
from service.review.service.interfaces import (
    ReviewCommandService,
    ReviewQueryService,
)
from service.review.service.review_command_service import (
    ReviewCommandServiceImpl,
)
from service.review.service.review_query_service import ReviewQueryServiceImpl
from shared.observability import Observability

SERVICE_NAME = "review-service"


@dataclass(frozen=True)
class Service:
    review_query: ReviewQueryService
    review_command: ReviewCommandService


def new_service(
    repos: Repositories,
    mencache: Mencache,
    logger: Logger,
) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    return Service(
        review_query=ReviewQueryServiceImpl(
            repos.review_query,
            mencache.review_query,
            logger,
            obs,
        ),
        review_command=ReviewCommandServiceImpl(
            repos.review_command,
            repos.review_query,
            repos.user_query,
            repos.product_query,
            mencache.review_command,
            logger,
            obs,
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]
