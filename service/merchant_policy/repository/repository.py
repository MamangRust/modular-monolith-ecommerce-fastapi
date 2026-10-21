"""merchant_policy repository composition. The merchant service owns the `merchants` table; wires a merchant adapter here even though no merchant_policy service path uses it (see the module docstring of `interfaces.py`). wiring."""

from __future__ import annotations

from dataclasses import dataclass

import grpc.aio as grpc_aio

from pkg.adapter.merchant import MerchantQueryAdapter
from pkg.database.database import Database
from pkg.resilience.dependency_guard import DependencyGuard
from service.merchant_policy.repository.interfaces import (
    MerchantPolicyCommandRepository,
    MerchantPolicyQueryRepository,
    MerchantQueryRepository,
)
from service.merchant_policy.repository.merchant_policy_command_repository import (
    MerchantPolicyCommandRepositoryImpl,
)
from service.merchant_policy.repository.merchant_policy_query_repository import (
    MerchantPolicyQueryRepositoryImpl,
)


@dataclass(frozen=True)
class GuardOptions:
    """Dependency guards for the merchant_policy service. merchant_policy only reaches the merchant service, so a single guard is enough."""

    merchant: DependencyGuard | None = None


@dataclass(frozen=True)
class Repositories:
    merchant_query: MerchantQueryRepository
    merchant_policy_query: MerchantPolicyQueryRepository
    merchant_policy_command: MerchantPolicyCommandRepository


def new_repositories(
    db: Database,
    *,
    merchant_channel: grpc_aio.Channel,
    guards: GuardOptions,
) -> Repositories:
    return Repositories(
        merchant_query=MerchantQueryAdapter(merchant_channel, guard=guards.merchant),
        merchant_policy_query=MerchantPolicyQueryRepositoryImpl(db),
        merchant_policy_command=MerchantPolicyCommandRepositoryImpl(db),
    )


__all__ = ["GuardOptions", "Repositories", "new_repositories"]
