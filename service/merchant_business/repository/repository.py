"""merchant_business repository composition. The merchant service owns the `merchants` table; wires a merchant adapter here even though no merchant_business service path uses it (see the module docstring of `interfaces.py`). wiring."""

from __future__ import annotations

from dataclasses import dataclass

import grpc.aio as grpc_aio

from pkg.adapter.merchant import MerchantQueryAdapter
from pkg.database.database import Database
from pkg.resilience.dependency_guard import DependencyGuard
from service.merchant_business.repository.interfaces import (
    MerchantBusinessCommandRepository,
    MerchantBusinessQueryRepository,
    MerchantQueryRepository,
)
from service.merchant_business.repository.merchant_business_command_repository import (
    MerchantBusinessCommandRepositoryImpl,
)
from service.merchant_business.repository.merchant_business_query_repository import (
    MerchantBusinessQueryRepositoryImpl,
)


@dataclass(frozen=True)
class GuardOptions:
    """Dependency guards for the merchant_business service. merchant_business only reaches the merchant service, so a single guard is enough."""

    merchant: DependencyGuard | None = None


@dataclass(frozen=True)
class Repositories:
    merchant_query: MerchantQueryRepository
    merchant_business_query: MerchantBusinessQueryRepository
    merchant_business_command: MerchantBusinessCommandRepository


def new_repositories(
    db: Database,
    *,
    merchant_channel: grpc_aio.Channel,
    guards: GuardOptions,
) -> Repositories:
    return Repositories(
        merchant_query=MerchantQueryAdapter(merchant_channel, guard=guards.merchant),
        merchant_business_query=MerchantBusinessQueryRepositoryImpl(db),
        merchant_business_command=MerchantBusinessCommandRepositoryImpl(db),
    )


__all__ = ["GuardOptions", "Repositories", "new_repositories"]
