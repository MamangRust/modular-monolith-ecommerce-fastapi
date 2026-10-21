# Runtime image for the transaction service (gRPC).
#
# Build context is the repository root (compose passes `context: ..`):
#
#   docker build -f service/transaction/Dockerfile -t transaction-service .
#
# Dependencies come from the committed `uv.lock` with `--frozen`, so a build
# fails loudly when the lockfile is stale instead of silently resolving newer
# versions.

FROM python:3.12-slim AS deps

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /usr/local/bin/uv

WORKDIR /app

# `[tool.uv] package = false` — the project itself is never installed, so only
# the dependency layer needs the manifests. This keeps source changes from
# invalidating the dependency cache.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.12-slim

# Non-root runtime user (Go reference runs every service as uid 1000).
RUN useradd --create-home --uid 1000 app

WORKDIR /app

COPY --from=deps /app/.venv /app/.venv
COPY --chown=app:app pkg/ pkg/
COPY --chown=app:app shared/ shared/
COPY --chown=app:app pb/ pb/
COPY --chown=app:app service/__init__.py service/__init__.py
COPY --chown=app:app service/transaction/ service/transaction/
# Lets any image run `python -m alembic -c alembic.ini upgrade head` (the
# compose `migrate` one-shot reuses this image with a command override).
COPY --chown=app:app alembic.ini alembic.ini

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_MODULE=service.transaction.cmd.main

USER app

# Go's transaction Dockerfile says EXPOSE 50058 (a copy-paste bug); the
# authoritative port comes from cmd/main.go — 50059.
EXPOSE 50059

CMD ["sh", "-c", "exec python -m \"${APP_MODULE}\""]
