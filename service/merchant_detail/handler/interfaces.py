"""merchant_detail handler"""

from __future__ import annotations

from typing import Protocol


class MerchantDetailQueryHandlerPort(Protocol):
    pass


class MerchantDetailCommandHandlerPort(Protocol):
    pass


class MerchantSocialLinkCommandHandlerPort(Protocol):
    pass


__all__ = [
    "MerchantDetailCommandHandlerPort",
    "MerchantDetailQueryHandlerPort",
    "MerchantSocialLinkCommandHandlerPort",
]
