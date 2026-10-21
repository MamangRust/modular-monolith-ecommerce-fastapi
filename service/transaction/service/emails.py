"""transaction email body rendering. renders the transaction-created email with `email.GenerateEmailHTML` (an HTML template carrying `Title`/`Message`/`Button`/`Link`)."""

from __future__ import annotations


def email_body(message: str, button: str, link: str) -> str:
    return f"{message}\n\n{button}: {link}"


__all__ = ["email_body"]
