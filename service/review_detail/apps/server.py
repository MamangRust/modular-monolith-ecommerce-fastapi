"""Review detail service composition root.

The review detail domain has no Kafka consumer or producer, so the composition
is just repositories -> cache -> service -> handler -> servicers."""

from __future__ import annotations

from pb.review_detail import (
    review_detail_command_pb2_grpc,
    review_detail_query_pb2_grpc,
)
from pkg.config.settings import Settings, get_settings
from pkg.redis.redis import new_redis_client
from pkg.server import GRPCServer
from pkg.server import new_server as new_grpc_server
from pkg.server.config import ServerConfig
from service.review_detail.handler import new_handler
from service.review_detail.repository import new_repositories
from service.review_detail.service import new_service
from shared.cache import CacheStore

SERVICE_NAME = "review_detail-service"
SERVICE_PORT = 50069
REVIEW_DETAIL_SERVICE_NAMES = [
    "pb.review_detail.ReviewDetailQueryService",
    "pb.review_detail.ReviewDetailCommandService",
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
        review_detail_query_pb2_grpc.add_ReviewDetailQueryServiceServicer_to_server(
            handler.review_detail_query, server
        )
        review_detail_command_pb2_grpc.add_ReviewDetailCommandServiceServicer_to_server(
            handler.review_detail_command, server
        )

    srv.register_services = register
    srv.reflection_services = list(REVIEW_DETAIL_SERVICE_NAMES)
    return srv


__all__ = [
    "SERVICE_NAME",
    "SERVICE_PORT",
    "REVIEW_DETAIL_SERVICE_NAMES",
    "new_server",
]
