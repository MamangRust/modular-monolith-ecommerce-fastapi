# Runtime image for the email worker (Kafka consumer, no gRPC).
#
# Build context is the repository root (compose passes `context: ..`):
#
#   docker build -f service/email/Dockerfile -t email-service .
#
# Dependencies come from the committed `uv.lock` with `--frozen`, so a build
# fails loudly when the lockfile is stale instead of silently resolving newer
# versions.

FROM python:3.12-slim AS deps

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.12-slim

RUN useradd --create-home --uid 1000 app

WORKDIR /app

COPY --from=deps /app/.venv /app/.venv
COPY --chown=app:app pkg/ pkg/
COPY --chown=app:app shared/ shared/
COPY --chown=app:app service/__init__.py service/__init__.py
COPY --chown=app:app service/email/ service/email/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_MODULE=service.email.cmd.main

USER app

CMD ["sh", "-c", "exec python -m \"${APP_MODULE}\""]
