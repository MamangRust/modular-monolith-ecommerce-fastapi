"""transaction handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.transaction.handler.transaction_command import TransactionCommandHandler
from service.transaction.handler.transaction_query import TransactionQueryHandler
from service.transaction.handler.transaction_stats import TransactionStatsHandler
from service.transaction.service.service import Service


@dataclass(frozen=True)
class Handler:
    transaction_query: TransactionQueryHandler
    transaction_command: TransactionCommandHandler
    transaction_stats: TransactionStatsHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        transaction_query=TransactionQueryHandler(
            service.transaction_query, logger
        ),
        transaction_command=TransactionCommandHandler(
            service.transaction_command, logger
        ),
        transaction_stats=TransactionStatsHandler(
            service.transaction_stats,
            service.transaction_stats_by_merchant,
            logger,
        ),
    )


__all__ = ["Handler", "new_handler"]
