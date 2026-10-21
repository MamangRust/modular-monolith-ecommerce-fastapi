"""Email worker process entrypoint."""

from __future__ import annotations

import asyncio
import signal

from service.email.apps.worker import new_worker


async def run() -> None:
    worker = await new_worker()
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:  # pragma: no cover - non-POSIX
            pass
    try:
        await stop.wait()
    finally:
        await worker.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
