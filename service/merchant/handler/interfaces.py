"""Merchant handler"""

from __future__ import annotations

from typing import Protocol


class MerchantQueryHandlerPort(Protocol):
    pass


class MerchantCommandHandlerPort(Protocol):
    pass


class MerchantDocumentQueryHandlerPort(Protocol):
    pass


class MerchantDocumentCommandHandlerPort(Protocol):
    pass


__all__ = [
    "MerchantCommandHandlerPort",
    "MerchantDocumentCommandHandlerPort",
    "MerchantDocumentQueryHandlerPort",
    "MerchantQueryHandlerPort",
]
