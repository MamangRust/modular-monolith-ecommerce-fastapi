"""SMTP mailer. Bodies are HTML (`Content-Type: text/html; charset="UTF-8"`), sender and envelope-from are the SMTP user. `net/smtp.SendMail` performs an opportunistic STARTTLS handshake; uses stdlib `smtplib` with `starttls` when the server advertises it, run in a worker thread so the asyncio loop is never blocked."""

from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage


class Mailer:
    def __init__(self, server: str, port: int, user: str, password: str) -> None:
        self._server = server
        self._port = port
        self._user = user
        self._password = password

    async def send(self, to: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = self._user
        message["To"] = to
        message["Subject"] = subject
        message["MIME-Version"] = "1.0"
        message.set_content(body, subtype="html", charset="utf-8")

        await asyncio.to_thread(self._send_sync, to, message)

    def _send_sync(self, to: str, message: EmailMessage) -> None:
        with smtplib.SMTP(self._server, self._port, timeout=30) as client:
            client.ehlo()
            if client.has_extn("starttls"):
                client.starttls()
                client.ehlo()
            if self._password:
                client.login(self._user, self._password)
            client.sendmail(self._user, [to], message.as_string())


__all__ = ["Mailer"]
