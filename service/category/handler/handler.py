"""Category handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.category.handler.command import CategoryCommandHandler
from service.category.handler.query import CategoryQueryHandler
from service.category.handler.stats import CategoryStatsHandler
from service.category.handler.stats_by_id import CategoryStatsByIdHandler
from service.category.handler.stats_by_merchant import CategoryStatsByMerchantHandler
from service.category.service.service import Service


@dataclass(frozen=True)
class Handler:
    category_query: CategoryQueryHandler
    category_command: CategoryCommandHandler
    category_stats: CategoryStatsHandler
    category_stats_by_id: CategoryStatsByIdHandler
    category_stats_by_merchant: CategoryStatsByMerchantHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        category_query=CategoryQueryHandler(service.category_query, logger),
        category_command=CategoryCommandHandler(service.category_command, logger),
        category_stats=CategoryStatsHandler(service.category_stats, logger),
        category_stats_by_id=CategoryStatsByIdHandler(
            service.category_stats_by_id, logger
        ),
        category_stats_by_merchant=CategoryStatsByMerchantHandler(
            service.category_stats_by_merchant, logger
        ),
    )


__all__ = ["Handler", "new_handler"]
