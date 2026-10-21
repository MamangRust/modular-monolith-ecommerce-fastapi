"""Review service composition root. review has no outbox/Kafka surface (the service produces no events). Both adapters are consumed by the command service's `Create`: the user adapter validates the author exists and the product adapter validates the reviewed product exists."""

from __future__ import annotations

import grpc.aio as grpc_aio

from pb.review import review_command_pb2_grpc, review_query_pb2_grpc
from pkg.adapter.guard import default_guard
from pkg.config.settings import Settings, get_settings
from pkg.redis.redis import new_redis_client
from pkg.server import GRPCServer
from pkg.server import new_server as new_grpc_server
from pkg.server.config import ServerConfig
from service.review.handler import new_handler
from service.review.redis import new_mencache
from service.review.repository import GuardOptions, new_repositories
from service.review.service import new_service
from shared.cache import CacheStore

SERVICE_NAME = "review-service"
SERVICE_PORT = 50061
REVIEW_SERVICE_NAMES = [
    "pb.review.ReviewQueryService",
    "pb.review.ReviewCommandService",
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
        review_query_pb2_grpc.add_ReviewQueryServiceServicer_to_server(handler.review_query, server)
        review_command_pb2_grpc.add_ReviewCommandServiceServicer_to_server(handler.review_command, server)

    srv.register_services = register
    srv.reflection_services = list(REVIEW_SERVICE_NAMES)
    return srv


__all__ = [
    "REVIEW_SERVICE_NAMES",
    "SERVICE_NAME",
    "SERVICE_PORT",
    "new_server",
]
