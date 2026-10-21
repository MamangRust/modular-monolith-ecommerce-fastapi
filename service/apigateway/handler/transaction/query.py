"""Transaction query REST routes. (chi) registers `/{id}` between the other routes but chi prioritises static segments, so `/active` and `/trashed` still match. Starlette matches routes in registration order, so registers the static `/active` and `/trashed` first and the `/{transaction_id}` route last (otherwise `/active` would be captured as an id). The gateway does not cache. Path guards reproduce verbatim: `FindById` → 400 "Invalid Transaction ID", `FindByMerchant` → 400 "Invalid Merchant ID" (`id <= 0` or a failed parse)."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.transaction.handler import TransactionHandler
from shared.domain.response.transaction import (
    TransactionResponseApi,
    TransactionResponsePagination,
    TransactionResponsePaginationDeleteAt,
)
from shared.errors.core import new_bad_request_error

router = APIRouter(prefix="/api/transaction-query", tags=["transaction-query"])


def get_transaction_handler(request: Request) -> TransactionHandler:
    return TransactionHandler(request.app.state.connections)


@router.get("")
async def find_all_transactions(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> TransactionResponsePagination:
    return await get_transaction_handler(request).find_all(page, page_size, search)


@router.get("/active")
async def find_by_active(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> TransactionResponsePagination:
    return await get_transaction_handler(request).find_by_active(
        page, page_size, search
    )


@router.get("/trashed")
async def find_by_trashed(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> TransactionResponsePaginationDeleteAt:
    return await get_transaction_handler(request).find_by_trashed(
        page, page_size, search
    )


@router.get("/merchant/{merchant_id}")
async def find_by_merchant(
    request: Request,
    merchant_id: int,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> TransactionResponsePagination:
    if merchant_id <= 0:
        raise new_bad_request_error("Invalid Merchant ID")
    return await get_transaction_handler(request).find_by_merchant(
        merchant_id, page, page_size, search
    )


# Registered last: Starlette matches in order, so a literal `/active` or
# `/trashed` must be reachable before this capture-all id route.
@router.get("/{transaction_id}")
async def find_by_id(
    request: Request,
    transaction_id: int,
) -> TransactionResponseApi:
    if transaction_id <= 0:
        raise new_bad_request_error("Invalid Transaction ID")
    return await get_transaction_handler(request).find_by_id(transaction_id)


__all__ = ["router"]
