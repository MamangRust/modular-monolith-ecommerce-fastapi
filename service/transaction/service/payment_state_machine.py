"""Payment status state machine.

The set is deliberately small and canonical; any status outside it is rejected
by validation instead of being persisted silently. The legacy `'completed'`
value (the column default) is normalised to `'success'` on both sides so rows
created before the state machine keep working."""

from __future__ import annotations

PAYMENT_STATUS_PENDING = "pending"
PAYMENT_STATUS_SUCCESS = "success"
PAYMENT_STATUS_FAILED = "failed"
PAYMENT_STATUS_REFUNDED = "refunded"

_ALLOWED_PAYMENT_TRANSITIONS: dict[str, set[str]] = {
    PAYMENT_STATUS_PENDING: {PAYMENT_STATUS_SUCCESS, PAYMENT_STATUS_FAILED},
    PAYMENT_STATUS_SUCCESS: {PAYMENT_STATUS_REFUNDED},
    PAYMENT_STATUS_FAILED: set(),
    PAYMENT_STATUS_REFUNDED: set(),
}


def normalize_payment_status(status: str) -> str:
    if status == "completed":
        return PAYMENT_STATUS_SUCCESS
    return status


def is_valid_payment_status(status: str) -> bool:
    return normalize_payment_status(status) in _ALLOWED_PAYMENT_TRANSITIONS


def can_transition_payment_status(from_status: str, to_status: str) -> bool:
    """A transition to the same status is always allowed so idempotent updates
 and partial updates (where the caller echoes the current status) do not
 fail."""
    source = normalize_payment_status(from_status)
    target = normalize_payment_status(to_status)
    if source == target:
        return True
    transitions = _ALLOWED_PAYMENT_TRANSITIONS.get(source)
    if transitions is None:
        return False
    return target in transitions


__all__ = [
    "PAYMENT_STATUS_FAILED",
    "PAYMENT_STATUS_PENDING",
    "PAYMENT_STATUS_REFUNDED",
    "PAYMENT_STATUS_SUCCESS",
    "can_transition_payment_status",
    "is_valid_payment_status",
    "normalize_payment_status",
]
