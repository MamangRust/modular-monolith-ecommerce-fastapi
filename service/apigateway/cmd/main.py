"""Gateway entrypoint: uvicorn on GATEWAY_PORT (default 5000)."""

from __future__ import annotations

import uvicorn

from service.apigateway.app.app import create_app


def main() -> None:
    from pkg.config.settings import get_settings

    port = get_settings().app.gateway_port
    uvicorn.run(create_app(), host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
