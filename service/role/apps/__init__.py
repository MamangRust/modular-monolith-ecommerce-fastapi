"""Role service composition root."""

from service.role.apps.server import (
    ROLE_SERVICE_NAMES,
    SERVICE_NAME,
    SERVICE_PORT,
    new_server,
)

__all__ = ["ROLE_SERVICE_NAMES", "SERVICE_NAME", "SERVICE_PORT", "new_server"]
