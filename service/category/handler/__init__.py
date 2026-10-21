"""Category handler package."""

from service.category.handler.command import CategoryCommandHandler
from service.category.handler.handler import Handler, new_handler
from service.category.handler.query import CategoryQueryHandler
from service.category.handler.stats import CategoryStatsHandler
from service.category.handler.stats_by_id import CategoryStatsByIdHandler
from service.category.handler.stats_by_merchant import CategoryStatsByMerchantHandler

__all__ = [
    "CategoryCommandHandler",
    "CategoryQueryHandler",
    "CategoryStatsByIdHandler",
    "CategoryStatsByMerchantHandler",
    "CategoryStatsHandler",
    "Handler",
    "new_handler",
]
