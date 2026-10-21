"""merchant_business handler"""

from __future__ import annotations

from typing import Protocol


class MerchantBusinessQueryHandlerPort(Protocol):
    pass


class MerchantBusinessCommandHandlerPort(Protocol):
    pass


__all__ = [
    "MerchantBusinessCommandHandlerPort",
    "MerchantBusinessQueryHandlerPort",
]
