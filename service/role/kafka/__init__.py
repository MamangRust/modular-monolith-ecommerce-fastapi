"""Role Kafka consumers."""

from service.role.kafka.role_consumer import (
    CONSUMER_GROUP,
    REQUEST_TOPIC,
    RoleKafkaHandler,
)

__all__ = ["CONSUMER_GROUP", "REQUEST_TOPIC", "RoleKafkaHandler"]
