"""Transaction command REST routes. `Create` decodes the JSON body and returns **201** (`http.StatusCreated`). `Update` sends only the path id + `payment_status`, read from `FormValue("status")`: the URL query first, then an urlencoded/multipart form field. Path-id guards (`id <= 0 → 400 "Invalid ID"`) reproduce verbatim; the gateway does not cache. registers `/restore/all` and `/permanent/all` after their `{id}` variants but chi prioritises static segments; Starlette matches in registration order, so registers the static paths first."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from service.apigateway.handler.transaction.handler import TransactionHandler
from shared.domain.requests.transaction import CreateTransactionRequest
from shared.domain.response.transaction import (
    TransactionResponseAll,
    TransactionResponseApi,
    TransactionResponseDelete,
    TransactionResponseDeleteAtApi,
)
from shared.errors.core import new_bad_request_error

router = APIRouter(prefix="/api/transaction-command", tags=["transaction-command"])


def get_transaction_handler(request: Request) -> TransactionHandler:
    return TransactionHandler(request.app.state.connections)


async def _form_value(request: Request, key: str) -> str:
    """query params first, then the form body."""
    value = request.query_params.get(key, "")
    if value:
        return value
    if "form" in request.headers.get("content-type", ""):
        form = await request.form()
        raw = form.get(key)
        if isinstance(raw, str):
            return raw
    return ""


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    request: Request,
    body: CreateTransactionRequest,
) -> TransactionResponseApi:
    return await get_transaction_handler(request).create(body)


# Static paths first — `/restore/all` must not be captured as id="all".
@router.post("/restore/all")
async def restore_all_transactions(request: Request) -> TransactionResponseAll:
    return await get_transaction_handler(request).restore_all()


@router.post("/permanent/all")
async def delete_all_transactions_permanent(
    request: Request,
) -> TransactionResponseAll:
    return await get_transaction_handler(request).delete_all_permanent()


@router.post("/update/{transaction_id}")
async def update_transaction(
    request: Request,
    transaction_id: int,
) -> TransactionResponseApi:
    if transaction_id <= 0:
        raise new_bad_request_error("Invalid ID")
    payment_status = await _form_value(request, "status")
    return await get_transaction_handler(request).update(
        transaction_id, payment_status
    )


@router.post("/trashed/{transaction_id}")
async def trash_transaction(
    request: Request,
    transaction_id: int,
) -> TransactionResponseDeleteAtApi:
    if transaction_id <= 0:
        raise new_bad_request_error("Invalid ID")
    return await get_transaction_handler(request).trash(transaction_id)


@router.post("/restore/{transaction_id}")
async def restore_transaction(
    request: Request,
    transaction_id: int,
) -> TransactionResponseDeleteAtApi:
    if transaction_id <= 0:
        raise new_bad_request_error("Invalid ID")
    return await get_transaction_handler(request).restore(transaction_id)


@router.delete("/permanent/{transaction_id}")
async def delete_transaction_permanent(
    request: Request,
    transaction_id: int,
) -> TransactionResponseDelete:
    if transaction_id <= 0:
        raise new_bad_request_error("Invalid ID")
    return await get_transaction_handler(request).delete_permanent(transaction_id)


__all__ = ["router"]
