"""Redis client factory.

Domain services may override the generic REDIS_* keys with a suffixed
variant (REDIS_HOST_ROLE,...) — see RedisSettings.resolve_for_service."""

from __future__ import annotations

import redis.asyncio as aioredis

from pkg.config.settings import RedisSettings
from pkg.logger.logger import Logger

DIAL_TIMEOUT = 5.0
READ_WRITE_TIMEOUT = 3.0
POOL_SIZE = 10
MIN_IDLE = 3


async def new_redis_client(settings: RedisSettings, service_name: str, logger: Logger) -> aioredis.Redis:
    s = settings.resolve_for_service(service_name)
    if not s.redis_host:
        raise RuntimeError(f"Redis host is not configured for {service_name}")
    client = aioredis.from_url(
        "redis://" + (f":{s.redis_password}@" if s.redis_password else ""),
        host=s.redis_host,
        port=s.redis_port,
        db=s.redis_db,
        socket_timeout=READ_WRITE_TIMEOUT,
        socket_connect_timeout=DIAL_TIMEOUT,
        max_connections=POOL_SIZE,
        decode_responses=True,
    )
    await client.ping()
    logger.info("redis connection established", host=s.redis_host, port=s.redis_port, db=s.redis_db)
    return client


async def close_redis(client: aioredis.Redis | None, logger: Logger) -> None:
    if client is None:
        return
    await client.aclose()
    logger.info("redis connection closed")
