"""Role membership validation over Kafka. The gateway cannot read the role database, so it asks the role service: publish `{user_id, correlation_id, reply_topic}` to `request-role`, wait for the reply on `response-role`, cache the result for 5 minutes. A timeout is a 408, an invalid/empty role set is a 401, and a send failure is a 500 — exactly the failure modes."""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any

from pkg.kafka.kafka import Kafka
from pkg.logger.logger import Logger
from service.apigateway.redis.role import RoleCache
from shared.errors import (
    AppError,
    ErrorType,
    err_unauthorized,
    new_internal_error,
)

REQUEST_TOPIC = "request-role"
REPLY_TOPIC = "response-role"
CONSUMER_GROUP = "role-validator-gateway"
DEFAULT_TIMEOUT = 5.0

err_role_validation_timeout = AppError(
    ErrorType.TIMEOUT.value, 408, "Timeout waiting for role validation"
)


class RoleValidator:
    def __init__(
        self,
        kafka: Kafka,
        cache: RoleCache,
        logger: Logger,
        timeout: float = DEFAULT_TIMEOUT,
        request_topic: str = REQUEST_TOPIC,
        reply_topic: str = REPLY_TOPIC,
        group_id: str = CONSUMER_GROUP,
    ) -> None:
        self._kafka = kafka
        self._cache = cache
        self._logger = logger
        self._timeout = timeout
        self._request_topic = request_topic
        self._reply_topic = reply_topic
        self._group_id = group_id
        self._pending: dict[str, asyncio.Future[dict[str, Any]]] = {}
        self._consumer: Any = None

    @property
    def pending_count(self) -> int:
        return len(self._pending)

    async def start(self) -> None:
        self._consumer = await self._kafka.start_consumers(
            [self._reply_topic],
            self._group_id,
            self._handle_response,
            manual_commit=False,
        )
        self._logger.info(
            "role validator consumer started",
            topic=self._reply_topic,
            group_id=self._group_id,
        )

    async def close(self) -> None:
        for future in self._pending.values():
            if not future.done():
                future.cancel()
        self._pending.clear()

    async def _handle_response(self, msg: Any, commit: Any) -> None:
        try:
            payload = json.loads(msg.value)
        except (TypeError, ValueError) as exc:
            self._logger.error("invalid role response payload", error=str(exc))
            return
        correlation_id = str(payload.get("correlation_id", ""))
        future = self._pending.pop(correlation_id, None)
        if future is None:
            self._logger.debug(
                "no waiting channel for role response", correlation_id=correlation_id
            )
            return
        if not future.done():
            future.set_result(payload)

    async def validate(self, user_id: int) -> list[str]:
        cached = await self._cache.get_user_roles(user_id)
        if cached:
            return cached

        correlation_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future: asyncio.Future[dict[str, Any]] = loop.create_future()
        self._pending[correlation_id] = future

        payload = {
            "user_id": int(user_id),
            "correlation_id": correlation_id,
            "reply_topic": self._reply_topic,
        }
        try:
            await self._kafka.send_message(
                self._request_topic, correlation_id, json.dumps(payload)
            )
        except Exception as exc:
            self._pending.pop(correlation_id, None)
            self._logger.error("failed to publish role request", error=str(exc))
            raise new_internal_error(exc).with_message(
                "Failed to send role validation request"
            ) from exc

        try:
            response = await asyncio.wait_for(future, timeout=self._timeout)
        except TimeoutError as exc:
            self._logger.error(
                "timeout waiting for role validation", correlation_id=correlation_id
            )
            raise err_role_validation_timeout from exc
        finally:
            self._pending.pop(correlation_id, None)

        roles = [str(role) for role in (response.get("role_names") or [])]
        if not response.get("valid") or not roles:
            raise err_unauthorized.with_message("Unauthorized")

        await self._cache.set_user_roles(user_id, roles)
        return roles


__all__ = [
    "CONSUMER_GROUP",
    "DEFAULT_TIMEOUT",
    "REPLY_TOPIC",
    "REQUEST_TOPIC",
    "RoleValidator",
    "err_role_validation_timeout",
]
