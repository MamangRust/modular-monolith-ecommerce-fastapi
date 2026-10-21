"""Role request/response consumer.

The gateway publishes `{user_id, correlation_id, reply_topic}` to
`request-role`; this consumer resolves the user's roles and replies on
the caller-supplied topic, keyed by correlation id.

Delivery contract:
- malformed payload -> log, commit (it can never succeed);
- role lookup failure -> leave uncommitted so Kafka redelivers;
- reply send failure -> leave uncommitted;
- success -> reply then commit."""

from __future__ import annotations

import json
from typing import Any

from pkg.kafka.kafka import Kafka
from pkg.logger.logger import Logger
from service.role.service.interfaces import RoleQueryService
from shared.domain.response.role import RoleResponsePayload

REQUEST_TOPIC = "request-role"
CONSUMER_GROUP = "role-service-group"
REPLY_ATTEMPTS = 3


class RoleKafkaHandler:
    def __init__(
        self,
        service: RoleQueryService,
        kafka: Kafka,
        logger: Logger,
    ) -> None:
        self._service = service
        self._kafka = kafka
        self._logger = logger

    async def handle(self, msg: Any, commit: Any) -> None:
        try:
            payload = json.loads(msg.value)
        except (TypeError, ValueError) as exc:
            self._logger.error("invalid role request payload", error=str(exc))
            await commit(msg)
            return

        correlation_id = str(payload.get("correlation_id", ""))
        reply_topic = str(payload.get("reply_topic", ""))
        if not correlation_id or not reply_topic:
            self._logger.error(
                "role request missing correlation_id or reply_topic",
                topic=getattr(msg, "topic", ""),
            )
            await commit(msg)
            return

        user_id = int(payload.get("user_id", 0) or 0)

        role_names: list[str] = []
        try:
            roles = await self._service.find_by_user_id(user_id)
            role_names = [role.role_name for role in roles]
        except Exception as exc:
            # Leave the offset uncommitted: redelivery is the retry.
            self._logger.error(
                "role lookup failed; leaving message uncommitted",
                user_id=user_id,
                error=str(exc),
            )
            raise

        response = RoleResponsePayload(
            correlation_id=correlation_id,
            valid=bool(role_names),
            role_names=role_names,
        )
        await self._kafka.send_message_with_retry(
            reply_topic, correlation_id, json.dumps(response.to_dict()), REPLY_ATTEMPTS
        )
        await commit(msg)
        self._logger.debug(
            "role validation replied",
            correlation_id=correlation_id,
            valid=response.valid,
        )


__all__ = ["CONSUMER_GROUP", "REQUEST_TOPIC", "RoleKafkaHandler"]
