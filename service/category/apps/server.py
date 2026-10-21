"""Category service composition root.

No Kafka producer or consumer: repositories -> cache -> service -> handler ->
five servicers (query, command, and the three stats services)."""

from __future__ import annotations

from pb.category import category_command_pb2_grpc, category_query_pb2_grpc
from pb.category.stats import (
    category_stats_byid_pb2_grpc,
    category_stats_bymerchant_pb2_grpc,
    category_stats_pb2_grpc,
)
from pkg.config.settings import Settings, get_settings
from pkg.redis.redis import new_redis_client
from pkg.server import GRPCServer
from pkg.server import new_server as new_grpc_server
from pkg.server.config import ServerConfig
from service.category.handler import new_handler
from service.category.repository import new_repositories
from service.category.service import new_service
from shared.cache import CacheStore

SERVICE_NAME = "category-service"
SERVICE_PORT = 50054
CATEGORY_SERVICE_NAMES = [
    "pb.category.CategoryQueryService",
    "pb.category.CategoryCommandService",
    "pb.category.stats.CategoryStatsService",
    "pb.category.stats.CategoryStatsByIdService",
    "pb.category.stats.CategoryStatsByMerchantService",
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
        category_query_pb2_grpc.add_CategoryQueryServiceServicer_to_server(
            handler.category_query, server
        )
        category_command_pb2_grpc.add_CategoryCommandServiceServicer_to_server(
            handler.category_command, server
        )
        category_stats_pb2_grpc.add_CategoryStatsServiceServicer_to_server(
            handler.category_stats, server
        )
        category_stats_byid_pb2_grpc.add_CategoryStatsByIdServiceServicer_to_server(
            handler.category_stats_by_id, server
        )
        category_stats_bymerchant_pb2_grpc.add_CategoryStatsByMerchantServiceServicer_to_server(
            handler.category_stats_by_merchant, server
        )

    srv.register_services = register
    srv.reflection_services = list(CATEGORY_SERVICE_NAMES)
    return srv


__all__ = ["CATEGORY_SERVICE_NAMES", "SERVICE_NAME", "SERVICE_PORT", "new_server"]
