"""Cart service composition root. cart has no outbox/Kafka surface (the service produces no events). Both adapters are consumed by the command service's `Create`: the product adapter supplies the snapshot fields (name/price/image/weight) and the stock check, and the user adapter validates the owner exists."""

from __future__ import annotations

import grpc.aio as grpc_aio

from pb.cart import cart_command_pb2_grpc, cart_query_pb2_grpc
from pkg.adapter.guard import default_guard
from pkg.config.settings import Settings, get_settings
from pkg.redis.redis import new_redis_client
from pkg.server import GRPCServer
from pkg.server import new_server as new_grpc_server
from pkg.server.config import ServerConfig
from service.cart.handler import new_handler
from service.cart.redis import new_mencache
from service.cart.repository import GuardOptions, new_repositories
from service.cart.service import new_service
from shared.cache import CacheStore

SERVICE_NAME = "cart-service"
SERVICE_PORT = 50060
CART_SERVICE_NAMES = [
    "pb.cart.CartQueryService",
    "pb.cart.CartCommandService",
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
    srv.add_cleanup_hook(channel_user.close)
    srv.add_cleanup_hook(channel_product.close)
    guards = GuardOptions(
        user=default_guard("user", srv.logger),
        product=default_guard("product", srv.logger),
    )

    repos = new_repositories(
        srv.db,
        user_channel=channel_user,
        product_channel=channel_product,
        guards=guards,
    )
    service = new_service(repos, mencache, srv.logger)
    handler = new_handler(service, srv.logger)

    def register(server) -> None:
        cart_query_pb2_grpc.add_CartQueryServiceServicer_to_server(handler.cart_query, server)
        cart_command_pb2_grpc.add_CartCommandServiceServicer_to_server(handler.cart_command, server)

    srv.register_services = register
    srv.reflection_services = list(CART_SERVICE_NAMES)
    return srv


__all__ = [
    "CART_SERVICE_NAMES",
    "SERVICE_NAME",
    "SERVICE_PORT",
    "new_server",
]
