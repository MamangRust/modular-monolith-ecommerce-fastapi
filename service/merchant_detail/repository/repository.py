"""merchant_detail repository composition. The merchant service owns the `merchants` table, so merchant_detail resolves the parent merchant over gRPC through the shared merchant adapter instead of reading that table directly."""

from __future__ import annotations

from dataclasses import dataclass

import grpc.aio as grpc_aio

from pkg.adapter.merchant import MerchantQueryAdapter
from pkg.database.database import Database
from pkg.resilience.dependency_guard import DependencyGuard
from service.merchant_detail.repository.interfaces import (
    MerchantDetailCommandRepository,
    MerchantDetailQueryRepository,
    MerchantQueryRepository,
    MerchantSocialLinkCommandRepository,
)
from service.merchant_detail.repository.merchant_detail_command_repository import (
    MerchantDetailCommandRepositoryImpl,
)
from service.merchant_detail.repository.merchant_detail_query_repository import (
    MerchantDetailQueryRepositoryImpl,
)
from service.merchant_detail.repository.merchant_social_link_command_repository import (
    MerchantSocialLinkCommandRepositoryImpl,
)


@dataclass(frozen=True)
class GuardOptions:
    """Dependency guards for the merchant_detail service. merchant_detail only reaches the merchant service, so a single guard is enough."""

    merchant: DependencyGuard | None = None


@dataclass(frozen=True)
class Repositories:
    merchant_query: MerchantQueryRepository
    merchant_detail_query: MerchantDetailQueryRepository
    merchant_detail_command: MerchantDetailCommandRepository
    merchant_social_link_command: MerchantSocialLinkCommandRepository


def new_repositories(
    db: Database,
    *,
    merchant_channel: grpc_aio.Channel,
    guards: GuardOptions,
) -> Repositories:
    return Repositories(
        merchant_query=MerchantQueryAdapter(
            merchant_channel, guard=guards.merchant
        ),
        merchant_detail_query=MerchantDetailQueryRepositoryImpl(db),
        merchant_detail_command=MerchantDetailCommandRepositoryImpl(db),
        merchant_social_link_command=MerchantSocialLinkCommandRepositoryImpl(db),
    )


__all__ = ["GuardOptions", "Repositories", "new_repositories"]
