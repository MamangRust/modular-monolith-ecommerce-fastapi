"""Gateway order handler: REST <-> order gRPC. Only transport concerns live here: build the proto request, call the domain over gRPC, convert a gRPC failure back to its original AppError, and map the proto response to the shared response envelope. No SQL, no business rules. Like the other domains, deliberately does not cache in the gateway. gateway order handler caches under its own `order:` namespace and invalidates on every mutation; drops that layer, so every request goes straight to the order service, which serves/invalidates its own cache. `Create` reads `merchant_id`/`user_id` from the **body** (binds the whole `requests.CreateOrderRequest`; the order gateway never reads the JWT subject, unlike review). `Update` uses the path id and ignores the body's `order_id`; the nested shipping DTO is attached only when the body carries one, and a non-positive `shipping_id` is sent as 0 (`pointerValue`). registers a single `OrderStatsService` carrying all eight stats RPCs; the Python proto splits the by-merchant RPCs into `OrderStatsByMerchantService`, so the handler holds two stubs (proto-layout normalisation)."""

from __future__ import annotations

import grpc
from google.protobuf import empty_pb2

from pb.order import (
    order_command_pb2,
    order_command_pb2_grpc,
    order_common_pb2,
    order_query_pb2,
    order_query_pb2_grpc,
)
from pb.order.stats import (
    order_stats_pb2,
    order_stats_pb2_grpc,
    order_statsbymerchant_pb2,
    order_statsbymerchant_pb2_grpc,
)
from pb.shipping_address import shipping_address_command_pb2
from service.apigateway.app.client import ServiceConnections
from shared.domain.requests.order import (
    CreateOrderRequest,
    UpdateOrderRequest,
)
from shared.domain.response.order import (
    OrderMonthlyApi,
    OrderMonthlyTotalRevenueApi,
    OrderResponseAll,
    OrderResponseApi,
    OrderResponseDelete,
    OrderResponseDeleteAtApi,
    OrderResponsePagination,
    OrderResponsePaginationDeleteAt,
    OrderYearlyApi,
    OrderYearlyTotalRevenueApi,
)
from shared.errors import parse_grpc_error
from shared.mapper.order import (
    to_api_response_monthly_order,
    to_api_response_monthly_total_revenue,
    to_api_response_order,
    to_api_response_order_all,
    to_api_response_order_delete,
    to_api_response_order_delete_at,
    to_api_response_pagination_order,
    to_api_response_pagination_order_delete_at,
    to_api_response_yearly_order,
    to_api_response_yearly_total_revenue,
)

RPC_TIMEOUT = 30.0


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Gateway-side clamping."""
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


class OrderHandler:
    def __init__(self, connections: ServiceConnections) -> None:
        channel = connections.channel("order")
        self._query = order_query_pb2_grpc.OrderQueryServiceStub(channel)
        self._command = order_command_pb2_grpc.OrderCommandServiceStub(channel)
        self._stats = order_stats_pb2_grpc.OrderStatsServiceStub(channel)
        self._stats_by_merchant = order_statsbymerchant_pb2_grpc.OrderStatsByMerchantServiceStub(channel)

    # ---- query ----

    async def find_all(self, page: int, page_size: int, search: str) -> OrderResponsePagination:
        page, page_size = normalize_pagination(page, page_size)
        request = order_query_pb2.FindAllOrderRequest(page=page, page_size=page_size, search=search or "")
        try:
            response = await self._query.FindAll(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_order(response)

    async def find_by_id(self, order_id: int) -> OrderResponseApi:
        request = order_common_pb2.FindByIdOrderRequest(id=order_id)
        try:
            response = await self._query.FindById(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_order(response)

    async def find_by_active(self, page: int, page_size: int, search: str) -> OrderResponsePaginationDeleteAt:
        page, page_size = normalize_pagination(page, page_size)
        request = order_query_pb2.FindAllOrderRequest(page=page, page_size=page_size, search=search or "")
        try:
            response = await self._query.FindByActive(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_order_delete_at(response)

    async def find_by_trashed(
        self, page: int, page_size: int, search: str
    ) -> OrderResponsePaginationDeleteAt:
        page, page_size = normalize_pagination(page, page_size)
        request = order_query_pb2.FindAllOrderRequest(page=page, page_size=page_size, search=search or "")
        try:
            response = await self._query.FindByTrashed(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_order_delete_at(response)

    # ---- command ----

    async def create(self, body: CreateOrderRequest) -> OrderResponseApi:
        items = [
            order_command_pb2.CreateOrderItemRequest(
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
            )
            for item in body.items
        ]
        request = order_command_pb2.CreateOrderRequest(
            merchant_id=body.merchant_id,
            user_id=body.user_id,
            total_price=body.total_price,
            items=items,
            shipping=shipping_address_command_pb2.CreateShippingAddressRequest(
                alamat=body.shipping_address.alamat,
                provinsi=body.shipping_address.provinsi,
                kota=body.shipping_address.kota,
                courier=body.shipping_address.courier,
                shipping_method=body.shipping_address.shipping_method,
                shipping_cost=body.shipping_address.shipping_cost,
                negara=body.shipping_address.negara,
            ),
        )
        try:
            response = await self._command.Create(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_order(response)

    async def update(self, order_id: int, body: UpdateOrderRequest) -> OrderResponseApi:
        items = [
            order_command_pb2.UpdateOrderItemRequest(
                order_item_id=item.order_item_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
            )
            for item in body.items
        ]
        request = order_command_pb2.UpdateOrderRequest(
            order_id=order_id,
            user_id=body.user_id,
            total_price=body.total_price,
            items=items,
        )
        if body.shipping_address is not None:
            shipping = body.shipping_address
            request.shipping.CopyFrom(
                shipping_address_command_pb2.UpdateShippingAddressRequest(
                    shipping_id=shipping.shipping_id or 0,
                    alamat=shipping.alamat,
                    provinsi=shipping.provinsi,
                    kota=shipping.kota,
                    courier=shipping.courier,
                    shipping_method=shipping.shipping_method,
                    shipping_cost=shipping.shipping_cost,
                    negara=shipping.negara,
                )
            )
        try:
            response = await self._command.Update(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_order(response)

    async def trash(self, order_id: int) -> OrderResponseDeleteAtApi:
        request = order_common_pb2.FindByIdOrderRequest(id=order_id)
        try:
            response = await self._command.TrashedOrder(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_order_delete_at(response)

    async def restore(self, order_id: int) -> OrderResponseDeleteAtApi:
        request = order_common_pb2.FindByIdOrderRequest(id=order_id)
        try:
            response = await self._command.RestoreOrder(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_order_delete_at(response)

    async def delete_permanent(self, order_id: int) -> OrderResponseDelete:
        request = order_common_pb2.FindByIdOrderRequest(id=order_id)
        try:
            response = await self._command.DeleteOrderPermanent(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_order_delete(response)

    async def restore_all(self) -> OrderResponseAll:
        try:
            response = await self._command.RestoreAllOrder(empty_pb2.Empty(), timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_order_all(response)

    async def delete_all_permanent(self) -> OrderResponseAll:
        try:
            response = await self._command.DeleteAllOrderPermanent(empty_pb2.Empty(), timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_order_all(response)

    # ---- stats ----

    async def find_monthly_total_revenue(self, year: int, month: int) -> OrderMonthlyTotalRevenueApi:
        request = order_stats_pb2.FindYearMonthTotalRevenue(year=year, month=month)
        try:
            response = await self._stats.FindMonthlyTotalRevenue(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_monthly_total_revenue(response)

    async def find_yearly_total_revenue(self, year: int) -> OrderYearlyTotalRevenueApi:
        request = order_stats_pb2.FindYearTotalRevenue(year=year)
        try:
            response = await self._stats.FindYearlyTotalRevenue(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_yearly_total_revenue(response)

    async def find_monthly_total_revenue_by_merchant(
        self, year: int, month: int, merchant_id: int
    ) -> OrderMonthlyTotalRevenueApi:
        request = order_statsbymerchant_pb2.FindYearMonthTotalRevenueByMerchant(
            year=year, month=month, merchant_id=merchant_id
        )
        try:
            response = await self._stats_by_merchant.FindMonthlyTotalRevenueByMerchant(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_monthly_total_revenue(response)

    async def find_yearly_total_revenue_by_merchant(
        self, year: int, merchant_id: int
    ) -> OrderYearlyTotalRevenueApi:
        request = order_statsbymerchant_pb2.FindYearTotalRevenueByMerchant(year=year, merchant_id=merchant_id)
        try:
            response = await self._stats_by_merchant.FindYearlyTotalRevenueByMerchant(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_yearly_total_revenue(response)

    async def find_monthly_revenue(self, year: int) -> OrderMonthlyApi:
        request = order_stats_pb2.FindYearOrder(year=year)
        try:
            response = await self._stats.FindMonthlyRevenue(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_monthly_order(response)

    async def find_yearly_revenue(self, year: int) -> OrderYearlyApi:
        request = order_stats_pb2.FindYearOrder(year=year)
        try:
            response = await self._stats.FindYearlyRevenue(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_yearly_order(response)

    async def find_monthly_revenue_by_merchant(self, year: int, merchant_id: int) -> OrderMonthlyApi:
        request = order_statsbymerchant_pb2.FindYearOrderByMerchant(year=year, merchant_id=merchant_id)
        try:
            response = await self._stats_by_merchant.FindMonthlyRevenueByMerchant(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_monthly_order(response)

    async def find_yearly_revenue_by_merchant(self, year: int, merchant_id: int) -> OrderYearlyApi:
        request = order_statsbymerchant_pb2.FindYearOrderByMerchant(year=year, merchant_id=merchant_id)
        try:
            response = await self._stats_by_merchant.FindYearlyRevenueByMerchant(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_yearly_order(response)


__all__ = ["OrderHandler", "normalize_pagination"]
