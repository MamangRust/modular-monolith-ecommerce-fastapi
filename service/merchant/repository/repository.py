"""Merchant repository composition. The user service owns the `users` table, so merchant resolves owners over gRPC through the shared user adapter instead of reading that table directly. The adapter is given merchant's own `GetUserByIDRow` copy so the remote proto maps onto the shape the merchant service expects."""

from __future__ import annotations

from dataclasses import dataclass

import grpc.aio as grpc_aio

from pkg.adapter.user import UserQueryAdapter
from pkg.database.database import Database
from pkg.database.schema.merchant import GetUserByIDRow
from pkg.resilience.dependency_guard import DependencyGuard
from service.merchant.repository.interfaces import (
    MerchantCommandRepository,
    MerchantDocumentCommandRepository,
    MerchantDocumentQueryRepository,
    MerchantQueryRepository,
    UserQueryRepository,
)
from service.merchant.repository.merchant_command_repository import (
    MerchantCommandRepositoryImpl,
)
from service.merchant.repository.merchant_document_command_repository import (
    MerchantDocumentCommandRepositoryImpl,
)
from service.merchant.repository.merchant_document_query_repository import (
    MerchantDocumentQueryRepositoryImpl,
)
from service.merchant.repository.merchant_query_repository import (
    MerchantQueryRepositoryImpl,
)


@dataclass(frozen=True)
class GuardOptions:
    """Dependency guards for the merchant service. Merchant only reaches the user service, so a single guard is enough."""

    user: DependencyGuard | None = None


@dataclass(frozen=True)
class Repositories:
    merchant_query: MerchantQueryRepository
    merchant_command: MerchantCommandRepository
    merchant_document_query: MerchantDocumentQueryRepository
    merchant_document_command: MerchantDocumentCommandRepository
    user_query: UserQueryRepository


def new_repositories(
    db: Database,
    *,
    user_channel: grpc_aio.Channel,
    guards: GuardOptions,
) -> Repositories:
    return Repositories(
        merchant_query=MerchantQueryRepositoryImpl(db),
        merchant_command=MerchantCommandRepositoryImpl(db),
        merchant_document_query=MerchantDocumentQueryRepositoryImpl(db),
        merchant_document_command=MerchantDocumentCommandRepositoryImpl(db),
        user_query=UserQueryAdapter(
            user_channel, guard=guards.user, row_cls=GetUserByIDRow
        ),
    )


__all__ = ["GuardOptions", "Repositories", "new_repositories"]
