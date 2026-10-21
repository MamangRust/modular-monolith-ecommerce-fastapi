"""Random generators and identifier helpers."""

from __future__ import annotations

import secrets

_ALPHANUM = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


def generate_random_string(length: int) -> str:
    return "".join(secrets.choice(_ALPHANUM) for _ in range(length))


def generate_api_key() -> str:
    """64-char hex API key. reads 32 random bytes and hex-encodes them; matches exactly. (The earlier `pk_live_...` shape was unused until the merchant domain — the first caller — so it is corrected here.)"""
    return secrets.token_hex(32)


def generate_trace_id(prefix: str) -> str:
    return f"{prefix}-{secrets.token_hex(8)}"


def format_rupiah(digit: int) -> str:
    """Format an integer amount as Rupiah: 1500000 -> 'Rp 1.500.000'."""
    negative = digit < 0
    sign = "-" if negative else ""
    body = f"{abs(digit):,}".replace(",", ".")
    return f"Rp {sign}{body}"


def random_card_number() -> str:
    """16-digit Visa-like number with Luhn check digit."""
    prefix = "4"
    body = "".join(secrets.choice("0123456789") for _ in range(14))
    partial = prefix + body
    double = [int(d) for d in partial[::-1]]
    checksum = 0
    for i, d in enumerate(double):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    check_digit = (10 - checksum % 10) % 10
    return partial + str(check_digit)
