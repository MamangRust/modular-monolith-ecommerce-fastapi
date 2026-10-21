"""Auth service apps package."""

from service.auth.apps.server import (
    AUTH_SERVICE_NAMES,
    SERVICE_NAME,
    SERVICE_PORT,
    new_server,
)

__all__ = ["AUTH_SERVICE_NAMES", "SERVICE_NAME", "SERVICE_PORT", "new_server"]
