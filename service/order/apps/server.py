"""Order service composition root. wires the shipping query adapter on the same channel as the command adapter, implementing the intended `Update` flow. registers a single `OrderStatsService` carrying all eight stats RPCs; the Python proto splits the by-merchant RPCs into `OrderStatsByMerchantService`, so the one handler is registered on both services (proto-layout normalisation)."""

from __future__ import annotations

import grpc.aio as grpc_aio

from pb.order import order_command_pb2_grpc, order_query_pb2_grpc
from pb.order.stats import (
    order_stats_pb2_grpc,
    order_statsbymerchant_pb2_grpc,
)
from pkg.adapter.guard import default_guard
from pkg.config.settings import Settings, get_settings
from pkg.redis.redis import new_redis_client
from pkg.server import GRPCServer
from pkg.server import new_server as new_grpc_server
from pkg.server.config import ServerConfig
from service.order.handler import new_handler
from service.order.redis import new_mencache
from service.order.repository import GuardOptions, new_repositories
from service.order.service import new_service
from shared.cache import CacheStore

SERVICE_NAME = "order-service"
SERVICE_PORT = 50057
ORDER_SERVICE_NAMES = [
    "pb.order.OrderQueryService",
    "pb.order.OrderCommandService",
    "pb.order.stats.OrderStatsService",
    "pb.order.stats.OrderStatsByMerchantService",
]


async def new_server(settings: Settings | None = None) -> GRPCServer:
    resolved = settings or get_settings()
    config = ServerConfig(
        service_name=SERVICE_NAME,
        port=SERVICE_PORT,
        environment=resolved.app.env,
        otel_endpoint=resolved.app.otel_endpoint,
        enable_telemetry=resolved.app.otel_enabled,
        enable_reflection=resolved.app.enable_reflection,
    )

    srv = await new_grpc_server(config, resolved.database)
    assert srv.db is not None

    redis = await new_redis_client(resolved.redis, SERVICE_NAME, srv.logger)
    srv.redis = redis
    cache_store = CacheStore(redis, srv.logger)
    mencache = new_mencache(cache_store, srv.logger)

    channel_user = grpc_aio.insecure_channel(resolved.grpc.grpc_user_addr)
    channel_product = grpc_aio.insecure_channel(resolved.grpc.grpc_product_addr)
    channel_merchant = grpc_aio.insecure_channel(resolved.grpc.grpc_merchant_addr)
    channel_order_item = grpc_aio.insecure_channel(
        resolved.grpc.grpc_order_item_addr
    )
    channel_shipping = grpc_aio.insecure_channel(
        resolved.grpc.grpc_shipping_address_addr
    )
    channel_transaction = grpc_aio.insecure_channel(
        resolved.grpc.grpc_transaction_addr
    )
    for channel in (
        channel_user,
        channel_product,
        channel_merchant,
        channel_order_item,
        channel_shipping,
        channel_transaction,
    ):
        srv.add_cleanup_hook(channel.close)

    guards = GuardOptions(
        user=default_guard("user", srv.logger),
        merchant=default_guard("merchant", srv.logger),
        product=default_guard("product", srv.logger),
        order_item=default_guard("order_item", srv.logger),
        shipping=default_guard("shipping", srv.logger),
        transaction=default_guard("transaction", srv.logger),
    )

    repos = new_repositories(
        srv.db,
        user_channel=channel_user,
        merchant_channel=channel_merchant,
        product_channel=channel_product,
        order_item_channel=channel_order_item,
        shipping_channel=channel_shipping,
        transaction_channel=channel_transaction,
        guards=guards,
    )
    service = new_service(repos, mencache, srv.logger)
    handler = new_handler(service, srv.logger)

    def register(server) -> None:
        order_query_pb2_grpc.add_OrderQueryServiceServicer_to_server(
            handler.order_query, server
        )
        order_stats_pb2_grpc.add_OrderStatsServiceServicer_to_server(
            handler.order_stats, server
        )
        order_statsbymerchant_pb2_grpc.add_OrderStatsByMerchantServiceServicer_to_server(
            handler.order_stats, server
        )
        order_command_pb2_grpc.add_OrderCommandServiceServicer_to_server(
            handler.order_command, server
        )

    srv.register_services = register
    srv.reflection_services = list(ORDER_SERVICE_NAMES)
    return srv


__all__ = [
    "ORDER_SERVICE_NAMES",
    "SERVICE_NAME",
    "SERVICE_PORT",
    "new_server",
]
