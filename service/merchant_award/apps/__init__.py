"""Merchant award service composition root."""

from __future__ import annotations

from service.merchant_award.apps.server import (
    MERCHANT_AWARD_SERVICE_NAMES,
    SERVICE_NAME,
    SERVICE_PORT,
    new_server,
)

__all__ = [
    "MERCHANT_AWARD_SERVICE_NAMES",
    "SERVICE_NAME",
    "SERVICE_PORT",
    "new_server",
]
