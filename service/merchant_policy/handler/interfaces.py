"""merchant_policy handler"""

from __future__ import annotations

from typing import Protocol


class MerchantPolicyQueryHandlerPort(Protocol):
    pass


class MerchantPolicyCommandHandlerPort(Protocol):
    pass


__all__ = [
    "MerchantPolicyCommandHandlerPort",
    "MerchantPolicyQueryHandlerPort",
]
