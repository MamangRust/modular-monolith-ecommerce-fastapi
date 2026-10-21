"""transaction service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.database.database import Database
from pkg.logger.logger import Logger
from service.transaction.redis import Mencache
from service.transaction.repository.repository import Repositories
from service.transaction.service.interfaces import (
    TransactionCommandService,
    TransactionQueryService,
    TransactionStatsByMerchantService,
    TransactionStatsService,
)
from service.transaction.service.transaction_command_service import (
    TransactionCommandServiceImpl,
)
from service.transaction.service.transaction_query_service import (
    TransactionQueryServiceImpl,
)
from service.transaction.service.transaction_stats_by_merchant_service import (
    TransactionStatsByMerchantServiceImpl,
)
from service.transaction.service.transaction_stats_service import (
    TransactionStatsServiceImpl,
)
from shared.observability import Observability

SERVICE_NAME = "transaction-service"


@dataclass(frozen=True)
class Service:
    transaction_query: TransactionQueryService
    transaction_command: TransactionCommandService
    transaction_stats: TransactionStatsService
    transaction_stats_by_merchant: TransactionStatsByMerchantService


def new_service(
    repos: Repositories,
    mencache: Mencache,
    db: Database,
    logger: Logger,
) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    return Service(
        transaction_query=TransactionQueryServiceImpl(
            repos.transaction_query,
            mencache.transaction_query,
            logger,
            obs,
        ),
        transaction_command=TransactionCommandServiceImpl(
            transaction_query=repos.transaction_query,
            transaction_command=repos.transaction_command,
            user_query=repos.user_query,
            merchant_query=repos.merchant_query,
            order_query=repos.order_query,
            order_item=repos.order_item,
            shipping_address=repos.shipping_address,
            cache=mencache.transaction_command,
            db=db,
            logger=logger,
            obs=obs,
        ),
        transaction_stats=TransactionStatsServiceImpl(
            repos.transaction_stats,
            mencache.transaction_stats,
            logger,
            obs,
        ),
        transaction_stats_by_merchant=TransactionStatsByMerchantServiceImpl(
            repos.transaction_stats_by_merchant,
            mencache.transaction_stats_by_merchant,
            logger,
            obs,
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]
