"""Order service process entrypoint."""

from __future__ import annotations

import asyncio
import signal

from pkg.server import cleanup, serve
from service.order.apps.server import new_server


async def run() -> None:
    srv = await new_server()
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:  # pragma: no cover - non-POSIX
            pass
    try:
        await serve(srv, stop)
    finally:
        await cleanup(srv)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
