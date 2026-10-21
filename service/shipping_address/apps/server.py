"""Shipping address service composition root.

No Kafka producer or consumer: repositories -> cache -> service -> handler ->
two servicers (query, command)."""

from __future__ import annotations

from pb.shipping_address import (
    shipping_address_command_pb2_grpc,
    shipping_address_query_pb2_grpc,
)
from pkg.config.settings import Settings, get_settings
from pkg.redis.redis import new_redis_client
from pkg.server import GRPCServer
from pkg.server import new_server as new_grpc_server
from pkg.server.config import ServerConfig
from service.shipping_address.handler import new_handler
from service.shipping_address.repository import new_repositories
from service.shipping_address.service import new_service
from shared.cache import CacheStore

SERVICE_NAME = "shipping_address-service"
SERVICE_PORT = 50063
SHIPPING_ADDRESS_SERVICE_NAMES = [
    "pb.shipping_address.ShippingQueryService",
    "pb.shipping_address.ShippingCommandService",
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

    repos = new_repositories(srv.db)
    service = new_service(repos, cache_store, srv.logger)
    handler = new_handler(service, srv.logger)

    def register(server) -> None:
        shipping_address_query_pb2_grpc.add_ShippingQueryServiceServicer_to_server(
            handler.shipping_address_query, server
        )
        shipping_address_command_pb2_grpc.add_ShippingCommandServiceServicer_to_server(
            handler.shipping_address_command, server
        )

    srv.register_services = register
    srv.reflection_services = list(SHIPPING_ADDRESS_SERVICE_NAMES)
    return srv


__all__ = [
    "SERVICE_NAME",
    "SERVICE_PORT",
    "SHIPPING_ADDRESS_SERVICE_NAMES",
    "new_server",
]
