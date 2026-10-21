"""merchant_award repository composition. The merchant service owns the `merchants` table; wires a merchant adapter here even though no merchant_award service path uses it (see the module docstring of `interfaces.py`). wiring."""

from __future__ import annotations

from dataclasses import dataclass

import grpc.aio as grpc_aio

from pkg.adapter.merchant import MerchantQueryAdapter
from pkg.database.database import Database
from pkg.resilience.dependency_guard import DependencyGuard
from service.merchant_award.repository.interfaces import (
    MerchantAwardCommandRepository,
    MerchantAwardQueryRepository,
    MerchantQueryRepository,
)
from service.merchant_award.repository.merchant_award_command_repository import (
    MerchantAwardCommandRepositoryImpl,
)
from service.merchant_award.repository.merchant_award_query_repository import (
    MerchantAwardQueryRepositoryImpl,
)


@dataclass(frozen=True)
class GuardOptions:
    """Dependency guards for the merchant_award service. merchant_award only reaches the merchant service, so a single guard is enough."""

    merchant: DependencyGuard | None = None


@dataclass(frozen=True)
class Repositories:
    merchant_query: MerchantQueryRepository
    merchant_award_query: MerchantAwardQueryRepository
    merchant_award_command: MerchantAwardCommandRepository


def new_repositories(
    db: Database,
    *,
    merchant_channel: grpc_aio.Channel,
    guards: GuardOptions,
) -> Repositories:
    return Repositories(
        merchant_query=MerchantQueryAdapter(merchant_channel, guard=guards.merchant),
        merchant_award_query=MerchantAwardQueryRepositoryImpl(db),
        merchant_award_command=MerchantAwardCommandRepositoryImpl(db),
    )


__all__ = ["GuardOptions", "Repositories", "new_repositories"]
