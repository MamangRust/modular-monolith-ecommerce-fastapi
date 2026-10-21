# Distributed Modular Monolith — Ecommerce Platform (Python / FastAPI)

A production-grade, **modular-monolith ecommerce backend** written in **Python 3.12**, organised around domain-driven service boundaries while keeping the operational simplicity of a single deployable unit. Each business domain — Auth, Users, Roles, Categories, Merchants (plus detail/award/business/policy satellites), Products, Carts, Reviews (plus review details), Sliders, Banners, Shipping Addresses, Orders, Order Items, Transactions — is a self-contained package with a clean internal architecture (`handler → service → repository`), and every domain ships as its own container that communicates with the rest over **gRPC** and asynchronous **Kafka** events.

An **API Gateway** built on **FastAPI** exposes a unified **REST API** (`/api/...`) and translates HTTP requests into gRPC calls to the domain services, validating JWTs and roles at the edge (`RoleValidatorGRPC`). Persistence is raw SQL over **SQLAlchemy 2.0 async + asyncpg** (no ORM mapping layer), migrated with **Alembic**, and every domain event is written through a **transactional outbox** so a Kafka outage can never lose a domain event. A dedicated **email worker** drains the outbox email topics with retry/DLQ semantics and Postgres-backed dedup.

The port is a line-by-line parity port of the Go reference (`monolith-ecommerce-grpc`); every deliberate deviation is numbered in [`Planning.md`](Planning.md).

---

## Key Features

| Domain | gRPC | Capabilities |
|--------|------|--------------|
| **Auth** | 50051 | Register, login, JWT access/refresh, password recovery & OTP verification, 3 outbox email topics |
| **Roles** | 50052 | RBAC role management + the legacy Kafka role-validation servicer (gateway uses direct gRPC) |
| **Users** | 50053 | User profiles, avatars, admin listings |
| **Categories** | 50054 | Category CRUD + trash + 3 stats servicers (by-id / by-merchant) |
| **Merchants** | 50055 | Onboarding, status lifecycle, documents (multipart upload), 5 outbox topics, transaction-event consumer |
| **Order Items** | 50056 | Line-item CRUD + `CalculateTotalPrice` (internal RPC used by order) |
| **Orders** | 50057 | Multi-service create/update saga (stock reservation ledger + items + shipping), trash/restore, atomic CTE purge, revenue/order stats |
| **Products** | 50058 | Product CRUD, stock adjustments, merchant/category adapters, image upload |
| **Transactions** | 50059 | Payment derivation (items + shipping + PPN 11%) with a payment state machine, 2 outbox topics in one DB transaction, amount/method stats (global + by-merchant) |
| **Carts** | 50060 | Per-user carts with product snapshot + stock check via adapters |
| **Reviews** | 50061 | Product reviews + review details (photo/video), rating filters |
| **Sliders** | 50062 | Homepage slider CRUD with image upload |
| **Shipping Addresses** | 50063 | Per-order shipping records (REST seed via command RPC) |
| **Banners** | 50064 | Promotional banners with date/time validity windows |
| **Merchant Award / Business / Policy / Detail** | 50065–50068 | Merchant satellites, incl. social links hosted on merchant_detail |
| **Review Details** | 50069 | Review media attachments |
| **Email Worker** | — | Kafka consumer (no gRPC): 8 outbox email topics, retry topic + DLQ, Postgres consumer-inbox dedup, SMTP |
| **REST Gateway** | 5000 | FastAPI + JWT middleware + `RoleValidatorGRPC`, `/health` `/live` `/ready` |

---

## Architecture Overview

The platform follows a **Distributed Modular Monolith** architecture — each module is a self-contained Python package with its own clean-architecture internals, deployed as an independent container. The **FastAPI gateway** is the only HTTP surface; everything behind it is gRPC.

### Core Architecture Principles

- **Single Responsibility**: each service owns its domain logic, data access, and caching layer
- **Clean Architecture**: every service follows `handler → service → repository` with explicit dependency wiring in `apps/server.py`
- **Cross-domain calls go over gRPC**: a service never reads another domain's tables (parity rule #9); it calls that domain's gRPC API through a guarded adapter in `pkg/adapter` (circuit breaker + bulkhead per dependency)
- **Event-Driven Decoupling**: the transactional outbox + Kafka decouple producers from consumers without direct service dependencies
- **Observability-First**: every service is instrumented with OpenTelemetry tracing and structured logging; the email worker additionally exposes five per-event counters
- **Async end to end**: `grpc.aio`, `asyncpg`, `redis` (asyncio), and `aiokafka` — no blocking I/O on the request path (SMTP goes through a worker thread)

### Service dependency graph (adapter edges)

```text
role → user → auth                (auth → role,user; user → role)
category → merchant(+document)    (merchant → user)
merchant_detail(+social) / merchant_award / merchant_business / merchant_policy
                                  (semuanya → merchant)
product → cart, review            (product → category,merchant; cart/review → user,product)
shipping_address → order_item → order → transaction
email worker (Kafka consumer)     (dedup via Postgres consumer inbox)
```

---

## Data & Event Flow

### Synchronous flow (REST → gRPC)

```text
HTTP → gateway (JWT middleware + RoleValidatorGRPC → role service)
     → gRPC client (shared channel per domain + DependencyGuardInterceptor)
     → domain gRPC handler → business service (query/command)
     → repository (raw SQL) / redis cache / guarded gRPC adapters
     → PostgreSQL
```

### Asynchronous flow (transactional outbox → Kafka)

Every email/notify side effect is an **outbox row written in the same database
transaction as the business mutation**. A per-service `OutboxRelay` claims rows
(`FOR UPDATE SKIP LOCKED` + lease fencing) and publishes to Kafka; consumers
dedup through the Postgres **consumer inbox** so at-least-once redelivery never
sends an email twice.

Two round-trip cache topics are ecommerce-specific:

- `transaction` produces `merchant-service-topic-transaction-event` → the
  **merchant** service evicts its cached merchant;
- `merchant` produces `transaction-service-topic-merchant-status-event` → the
  **transaction** service invalidates its `transaction:*` namespace.

### Kafka topics in the port

| Producer | Topics |
|----------|--------|
| auth (outbox, 3) | `email-service-topic-auth-register`, `email-service-topic-auth-forgot-password`, `email-service-topic-auth-verify-code-success` |
| merchant (outbox, 5) | `email-service-topic-merchant-create`, `email-service-topic-merchant-update-status`, `email-service-topic-merchant-document-create`, `email-service-topic-merchant-document-update-status`, `merchant-service-topic-transaction-event` |
| transaction (outbox, 2) | `email-service-topic-transaction-create`, `merchant-service-topic-transaction-event` |
| merchant (direct) | `transaction-service-topic-merchant-status-event` |
| email worker | consumes the 8 `email-service-topic-*` topics; offloads transient SMTP failures to `email-service-topic-email-retry`; dead-letters to `email-service-topic-email-dlq` after 5 attempts |

---

## Observability

Every service initialises OpenTelemetry tracing and structured logging; the email worker additionally exposes per-event counters (sent / failed / duplicated / invalid / retried, plus a dead-letter counter). Prometheus client and OTel instrumentors for FastAPI, gRPC, and aiokafka emit spans and metrics across the REST → gRPC → Kafka hops.

The Grafana / Prometheus / Loki / Jaeger **collector configuration** is provided under `grafana_setup/` (datasources, dashboards, Prometheus rules) — ported from the Go reference. **Pending (parity item):** the collector containers are not yet wired into the local `docker-compose.yml`, so telemetry is emitted only when `OTEL_ENABLED=true` and `OTEL_ENDPOINT` points at an external collector.

| Pillar | Library / Tool | Notes |
|--------|---------------|-------|
| **Metrics** | OpenTelemetry SDK + Prometheus exporter | per-service cache + tracing metrics |
| **Logging** | structlog | structured JSON logs to stdout |
| **Tracing** | OpenTelemetry SDK + OTLP exporter | spans across REST → gRPC → Kafka hops |
| **Dashboards** | Grafana (config in `grafana_setup/`) | ported from Go reference; collector wiring pending |

---

## Technology Stack

- **Python 3.12**, `grpc.aio`, FastAPI, SQLAlchemy 2.0 async + asyncpg (raw SQL, sqlx-style)
- **Alembic** migrations mirroring the Go reference SQL (timestamptz deviation noted)
- **Redis** (asyncio) — one logical DB per domain, keys/TTLs verbatim from Go
- **aiokafka** producer/managed consumers (manual commit where the offset must follow the side effect)
- **OpenTelemetry** (OTLP) tracing + structured logging
- **uv** for dependency management; ruff + mypy strict gates
- **Docker Compose** for local infra + full stack; Kubernetes manifests in `deployments/kubernetes/`

---

## Getting Started

### Prerequisites

- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- Docker (for PostgreSQL 17, Redis 7, Kafka 3.9)

### 1. Configure the environment

```bash
cp .env.example .env   # adjust credentials; secrets must not be committed
```

### 2. Create the virtualenv

```bash
make setup             # uv venv + uv sync
```

### 3. Start infrastructure and run migrations

```bash
make infra-up          # postgres + redis + kafka
make migrate           # alembic upgrade head
make seed              # optional: seed roles/banners/categories/... (idempotent)
```

### 4. Run the services

Every domain has a dev runner (`PYTHONPATH=. python -m service.<domain>.cmd.main`):

```bash
make run-gateway       # REST gateway on :5000
make run-auth          # or run-role run-user run-category run-merchant ...
make run-transaction
make run-email         # email worker (Kafka consumer)
```

Or start the whole stack (builds images, runs the migrate one-shot, then all
19 gRPC domains + gateway + email worker):

```bash
make services-up
```

### 5. Verify

```bash
curl localhost:5000/health
curl localhost:5000/ready      # readiness includes a health check per domain channel
```

### Stopping

```bash
make services-down   # app services + infra
# or: make infra-down  (infra only)
```

---

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make setup` | create `.venv` + install dependencies (uv) |
| `make infra-up` / `infra-down` | start/stop postgres + redis + kafka |
| `make services-up` / `services-down` | full stack incl. migrate one-shot, 19 domains, gateway, email worker |
| `make proto` | regenerate `pb/` from `proto/` (69 protos, 23 packages) |
| `make migrate` / `make revision m="..."` | alembic upgrade / new revision |
| `make seed` | idempotent development seeder |
| `make test` | unit tests (no infrastructure required) |
| `make test-int` | unit + integration + contract (needs the infra up) |
| `make e2e` | end-to-end suite (needs the full stack) |
| `make lint` / `make typecheck` | ruff / mypy |
| `make run-<domain>` | run one service locally (19 domains, gateway, email) |

---

## Testing

The port is gated slice by slice (see `Planning.md`):

- **unit** — handlers/services/mappers with fakes, no infrastructure (`make test`);
- **integration** — real PostgreSQL/Redis per repository + ephemeral `grpc.aio` servers per domain, including the full order and transaction create sagas over real cross-domain adapters (`make test-int`);
- **contract** — the real FastAPI gateway app over HTTPX against the real domain servers (`make test-int`);
- **e2e** — the full REST journey register → login → category → merchant → product → cart → shipping → order → transaction → review through the gateway (`make e2e`).

---

## Project Structure

```
monolith-fastapi-ecommerce/
├── proto/                         # Protobuf definitions (69 files, 23 packages, verbatim Go)
├── pb/                            # Generated Python protobuf modules
├── pkg/                           # Platform libraries
│   ├── adapter/                   #   Cross-domain gRPC clients (guard-wired)
│   ├── auth/                      #   JWT token manager
│   ├── config/                    #   pydantic-settings (Go-parity env names)
│   ├── database/                  #   asyncpg engine + Alembic migrations + schema rows + seeder
│   ├── email/                     #   Email HTML template (Go text/template port)
│   ├── emailretry/                #   Retry/DLQ contract (headers + linear backoff)
│   ├── event/                     #   EmailEnvelope + marshal helpers
│   ├── kafka/                     #   aiokafka producer / managed consumer (headers support)
│   ├── logger/                    #   Structured logger
│   ├── middleware/                #   gRPC method instrumentation decorator
│   ├── otel/                      #   OpenTelemetry initialization
│   ├── outbox/                    #   Transactional outbox relay + Postgres consumer inbox
│   ├── redis/                     #   Redis client helpers
│   ├── resilience/                #   Circuit breaker, bulkhead, dependency guards, interceptors
│   ├── server/                    #   grpc.aio server bootstrap + cleanup hooks
│   └── utils/                     #   random string, api key, trace id, slug helpers
├── shared/                        # Shared domain libraries
│   ├── domain/                    #   Domain models (record/request/response)
│   ├── mapper/                    #   Domain ↔ Protobuf ↔ REST mappers
│   ├── cache/                     #   CacheStore abstraction
│   ├── observability/             #   Cache + tracing metrics
│   ├── convert/                   #   Type conversion helpers
│   ├── errors/                    #   Per-domain error catalogues + FastAPI handlers
│   └── errorhandler/              #   Error handling utilities
├── service/                       # All application services (each with its own Dockerfile)
│   ├── apigateway/                #   FastAPI REST gateway (app/, handler/, middlewares/)
│   ├── auth/ role/ user/          #   Identity stack
│   ├── category/ banner/ slider/  #   Content domains
│   ├── merchant/ merchant_detail/ #   Merchant + satellites (award/business/policy)
│   ├── merchant_award/ merchant_business/ merchant_policy/
│   ├── product/ cart/ review/ review_detail/
│   ├── order/ order_item/ shipping_address/ transaction/
│   └── email/                     #   Email worker (Kafka consumer + SMTP + retry/DLQ)
├── tests/                         # unit / integration / contract / e2e
├── deployments/                   # docker-compose.yml, kubernetes/
├── scripts/                       # Proto generation
├── alembic.ini / pyproject.toml / uv.lock
└── Planning.md                    # Slice-by-slice port plan + numbered parity notes
```

---

## Status & Roadmap

All planned domains are ported and gated (see `Planning.md` for the full plan and the numbered
parity notes):

- **Ported**: banner, category, order_item, shipping_address, slider, review_detail, merchant
  (+ merchant_document, upload_image), merchant_detail (+ social links), merchant_award,
  merchant_business, merchant_policy, product, cart, review, order, **transaction**,
  **email worker** — repositories, cache, services, gRPC handlers, outbox/retry wiring, and the
  FastAPI gateway surface.
- **Pending**: the full **observability collector stack** — Prometheus/Grafana/Loki/Jaeger
  collector *containers* are not wired into the local `docker-compose.yml` (the dashboard and
  datasource configs are ported under `grafana_setup/`). Point `OTEL_ENDPOINT` at an external
  collector to see telemetry.

Behaviour is verified by the test gate: `make lint`, `make typecheck`, `make test`
(unit, no infrastructure), `make test-int` (integration + contract against real
PostgreSQL/Redis), and `make e2e` (full journey through the gateway).

---

## License

This project is open-sourced for educational and development purposes.

---

<p align="center">
  Built with Python, FastAPI, gRPC, and a passion for clean architecture.
</p>
