"""Merchant detail service composition root."""

from __future__ import annotations

from service.merchant_detail.apps.server import (
    MERCHANT_DETAIL_SERVICE_NAMES,
    SERVICE_NAME,
    SERVICE_PORT,
    new_server,
)

__all__ = [
    "MERCHANT_DETAIL_SERVICE_NAMES",
    "SERVICE_NAME",
    "SERVICE_PORT",
    "new_server",
]
