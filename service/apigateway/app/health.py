"""Health/readiness endpoints (gateway: /health /live /ready)."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])


def register_health(app) -> None:
    app.include_router(router)

    @router.get("/health")
    @router.get("/live")
    async def health() -> dict:
        return {"status": "ok"}

    @app.get("/ready", include_in_schema=True)
    async def ready(request: Request) -> JSONResponse:
        connections = getattr(request.app.state, "connections", None)
        if connections is None:
            return JSONResponse(
                status_code=503,
                content={"status": "unavailable", "grpc": "not initialized"},
            )
        results = await connections.check_readiness()
        down = [domain for domain, ok in results.items() if not ok]
        if down:
            return JSONResponse(
                status_code=503,
                content={"status": "unavailable", "domains": down},
            )
        return JSONResponse(content={"status": "ready"})
