"""Transaction stats REST routes."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.transaction.handler import TransactionHandler
from shared.domain.response.transaction import (
    TransactionMonthlyAmountFailedApi,
    TransactionMonthlyAmountSuccessApi,
    TransactionMonthlyMethodApi,
    TransactionYearlyAmountFailedApi,
    TransactionYearlyAmountSuccessApi,
    TransactionYearlyMethodApi,
)

router = APIRouter(prefix="/api/transaction-stats", tags=["transaction-stats"])


def get_transaction_handler(request: Request) -> TransactionHandler:
    return TransactionHandler(request.app.state.connections)


def _merchant_id(request: Request) -> int:
    raw = request.query_params.get("merchant_id", "")
    try:
        return int(raw)
    except ValueError:
        return 0


@router.get("/monthly-success")
async def find_month_amount_success(
    request: Request, year: int = 0, month: int = 0
) -> TransactionMonthlyAmountSuccessApi:
    return await get_transaction_handler(request).find_monthly_amount_success(
        year, month
    )


@router.get("/yearly-success")
async def find_year_amount_success(
    request: Request, year: int = 0
) -> TransactionYearlyAmountSuccessApi:
    return await get_transaction_handler(request).find_yearly_amount_success(year)


@router.get("/monthly-failed")
async def find_month_amount_failed(
    request: Request, year: int = 0, month: int = 0
) -> TransactionMonthlyAmountFailedApi:
    return await get_transaction_handler(request).find_monthly_amount_failed(
        year, month
    )


@router.get("/yearly-failed")
async def find_year_amount_failed(
    request: Request, year: int = 0
) -> TransactionYearlyAmountFailedApi:
    return await get_transaction_handler(request).find_yearly_amount_failed(year)


@router.get("/monthly-method-success")
async def find_month_method_success(
    request: Request, year: int = 0, month: int = 0
) -> TransactionMonthlyMethodApi:
    return await get_transaction_handler(request).find_monthly_method_success(
        year, month
    )


@router.get("/yearly-method-success")
async def find_year_method_success(
    request: Request, year: int = 0
) -> TransactionYearlyMethodApi:
    return await get_transaction_handler(request).find_yearly_method_success(year)


@router.get("/monthly-method-failed")
async def find_month_method_failed(
    request: Request, year: int = 0, month: int = 0
) -> TransactionMonthlyMethodApi:
    return await get_transaction_handler(request).find_monthly_method_failed(
        year, month
    )


@router.get("/yearly-method-failed")
async def find_year_method_failed(
    request: Request, year: int = 0
) -> TransactionYearlyMethodApi:
    return await get_transaction_handler(request).find_yearly_method_failed(year)


@router.get("/merchant/monthly-success")
async def find_month_amount_success_by_merchant(
    request: Request, year: int = 0, month: int = 0
) -> TransactionMonthlyAmountSuccessApi:
    return await get_transaction_handler(
        request
    ).find_monthly_amount_success_by_merchant(
        _merchant_id(request), year, month
    )


@router.get("/merchant/yearly-success")
async def find_year_amount_success_by_merchant(
    request: Request, year: int = 0
) -> TransactionYearlyAmountSuccessApi:
    return await get_transaction_handler(
        request
    ).find_yearly_amount_success_by_merchant(_merchant_id(request), year)


@router.get("/merchant/monthly-failed")
async def find_month_amount_failed_by_merchant(
    request: Request, year: int = 0, month: int = 0
) -> TransactionMonthlyAmountFailedApi:
    return await get_transaction_handler(
        request
    ).find_monthly_amount_failed_by_merchant(_merchant_id(request), year, month)


@router.get("/merchant/yearly-failed")
async def find_year_amount_failed_by_merchant(
    request: Request, year: int = 0
) -> TransactionYearlyAmountFailedApi:
    return await get_transaction_handler(
        request
    ).find_yearly_amount_failed_by_merchant(_merchant_id(request), year)


@router.get("/merchant/monthly-method-success")
async def find_month_method_success_by_merchant(
    request: Request, year: int = 0, month: int = 0
) -> TransactionMonthlyMethodApi:
    return await get_transaction_handler(
        request
    ).find_monthly_method_success_by_merchant(_merchant_id(request), year, month)


@router.get("/merchant/yearly-method-success")
async def find_year_method_success_by_merchant(
    request: Request, year: int = 0
) -> TransactionYearlyMethodApi:
    return await get_transaction_handler(
        request
    ).find_yearly_method_success_by_merchant(_merchant_id(request), year)


@router.get("/merchant/monthly-method-failed")
async def find_month_method_failed_by_merchant(
    request: Request, year: int = 0, month: int = 0
) -> TransactionMonthlyMethodApi:
    return await get_transaction_handler(
        request
    ).find_monthly_method_failed_by_merchant(_merchant_id(request), year, month)


@router.get("/merchant/yearly-method-failed")
async def find_year_method_failed_by_merchant(
    request: Request, year: int = 0
) -> TransactionYearlyMethodApi:
    return await get_transaction_handler(
        request
    ).find_yearly_method_failed_by_merchant(_merchant_id(request), year)


__all__ = ["router"]
