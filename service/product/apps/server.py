"""Product service composition root. product has no outbox/Kafka surface (the service produces no events). Unlike the merchant_* leaf domains, both adapters are consumed: the command service validates the parent category and merchant on `Create`/`Update`."""

from __future__ import annotations

import grpc.aio as grpc_aio

from pb.product import (
    product_command_pb2_grpc,
    product_query_pb2_grpc,
)
from pkg.adapter.guard import default_guard
from pkg.config.settings import Settings, get_settings
from pkg.redis.redis import new_redis_client
from pkg.server import GRPCServer
from pkg.server import new_server as new_grpc_server
from pkg.server.config import ServerConfig
from service.product.handler import new_handler
from service.product.redis import new_mencache
from service.product.repository import GuardOptions, new_repositories
from service.product.service import new_service
from shared.cache import CacheStore

SERVICE_NAME = "product-service"
SERVICE_PORT = 50058
PRODUCT_SERVICE_NAMES = [
    "pb.product.ProductQueryService",
    "pb.product.ProductCommandService",
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

    channel_category = grpc_aio.insecure_channel(resolved.grpc.grpc_category_addr)
    channel_merchant = grpc_aio.insecure_channel(resolved.grpc.grpc_merchant_addr)
    srv.add_cleanup_hook(channel_category.close)
    srv.add_cleanup_hook(channel_merchant.close)
    guards = GuardOptions(
        category=default_guard("category", srv.logger),
        merchant=default_guard("merchant", srv.logger),
    )

    repos = new_repositories(
        srv.db,
        category_channel=channel_category,
        merchant_channel=channel_merchant,
        guards=guards,
    )
    service = new_service(repos, mencache, srv.logger)
    handler = new_handler(service, srv.logger)

    def register(server) -> None:
        product_query_pb2_grpc.add_ProductQueryServiceServicer_to_server(handler.product_query, server)
        product_command_pb2_grpc.add_ProductCommandServiceServicer_to_server(handler.product_command, server)

    srv.register_services = register
    srv.reflection_services = list(PRODUCT_SERVICE_NAMES)
    return srv


__all__ = [
    "PRODUCT_SERVICE_NAMES",
    "SERVICE_NAME",
    "SERVICE_PORT",
    "new_server",
]
