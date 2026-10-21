"""merchant_award handler"""

from __future__ import annotations

from typing import Protocol


class MerchantAwardQueryHandlerPort(Protocol):
    pass


class MerchantAwardCommandHandlerPort(Protocol):
    pass


__all__ = [
    "MerchantAwardCommandHandlerPort",
    "MerchantAwardQueryHandlerPort",
]
