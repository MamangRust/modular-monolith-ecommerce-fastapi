# Distributed modular monolith — FastAPI gateway + gRPC domain services
PYTHON ?= $(shell [ -d .venv ] && echo .venv/bin/python || echo python3)
VENV := .venv

# gRPC service ports (parity with Go reference, authoritative sources:
# service/*/cmd/main.go + deployments/local/docker.env):
#   auth 50051 | role 50052 | user 50053 | category 50054 | merchant 50055
#   order_item 50056 | order 50057 | product 50058 | transaction 50059
#   cart 50060 | review 50061 | slider 50062 | shipping_address 50063
#   banner 50064 | merchant_award 50065 | merchant_business 50066
#   merchant_detail 50067 | merchant_policy 50068 | review_detail 50069
#   email worker: Kafka consumer, no gRPC port
# REST gateway: 5000

.PHONY: help
help:
	@echo "Targets:"
	@echo "  setup          create .venv + install dependencies (uv)"
	@echo "  infra-up       start postgres/redis/kafka (docker compose, no profile)"
	@echo "  infra-down     stop the stack"
	@echo "  services-up    build + start migrate, gateway, 19 gRPC services and the email worker (--profile services)"
	@echo "  services-down  stop app services + infra"
	@echo "  proto          regenerate pb/ from proto/ (grpcio-tools)"
	@echo "  migrate        alembic upgrade head"
	@echo "  revision       create a new alembic revision"
	@echo "  seed           seed development/test database"
	@echo "  test           unit tests (no infra required)"
	@echo "  test-int       integration tests (needs infra-up: DB+Redis+Kafka)"
	@echo "  e2e            end-to-end tests (needs full services up)"
	@echo "  lint           ruff check"
	@echo "  typecheck      mypy"
	@echo "  run-ROLE       run a service: run-role, run-user, run-gateway, ..."

.PHONY: setup
setup:
	uv venv $(VENV)
	uv sync --group dev
	@echo "Virtualenv ready. Use: source $(VENV)/bin/activate"

.PHONY: infra-up
infra-up:
	docker compose -f deployments/docker-compose.yml up -d

.PHONY: infra-down
infra-down:
	docker compose -f deployments/docker-compose.yml down

.PHONY: services-up
services-up:
	docker compose -f deployments/docker-compose.yml --profile services up -d --build

.PHONY: services-down
services-down:
	docker compose -f deployments/docker-compose.yml --profile services down

.PHONY: proto
proto:
	$(PYTHON) -m scripts.gen_grpc

.PHONY: migrate
migrate:
	$(PYTHON) -m alembic -c alembic.ini upgrade head

.PHONY: revision
revision:
	$(PYTHON) -m alembic -c alembic.ini revision -m "$(m)"

.PHONY: seed
seed:
	$(PYTHON) -m pkg.database.seeder

.PHONY: test
test:
	$(PYTHON) -m pytest -m "not integration and not e2e"

.PHONY: test-int
test-int:
	$(PYTHON) -m pytest -m "not e2e"

.PHONY: e2e
e2e:
	$(PYTHON) -m pytest -m e2e

.PHONY: lint
lint:
	$(PYTHON) -m ruff check pkg shared service tests scripts

.PHONY: typecheck
typecheck:
	$(PYTHON) -m mypy

# ---- service runners (dev) ----
.PHONY: run-role
run-role:
	PYTHONPATH=. $(PYTHON) -m service.role.cmd.main

.PHONY: run-user
run-user:
	PYTHONPATH=. $(PYTHON) -m service.user.cmd.main

.PHONY: run-banner
run-banner:
	PYTHONPATH=. $(PYTHON) -m service.banner.cmd.main

.PHONY: run-category
run-category:
	PYTHONPATH=. $(PYTHON) -m service.category.cmd.main

.PHONY: run-order-item
run-order-item:
	PYTHONPATH=. $(PYTHON) -m service.order_item.cmd.main

.PHONY: run-shipping-address
run-shipping-address:
	PYTHONPATH=. $(PYTHON) -m service.shipping_address.cmd.main

.PHONY: run-slider
run-slider:
	PYTHONPATH=. $(PYTHON) -m service.slider.cmd.main

.PHONY: run-gateway
run-gateway:
	PYTHONPATH=. $(PYTHON) -m service.apigateway.cmd.main

.PHONY: run-auth
run-auth:
	PYTHONPATH=. $(PYTHON) -m service.auth.cmd.main

.PHONY: run-transaction
run-transaction:
	PYTHONPATH=. $(PYTHON) -m service.transaction.cmd.main

.PHONY: run-merchant
run-merchant:
	PYTHONPATH=. $(PYTHON) -m service.merchant.cmd.main

.PHONY: run-merchant-detail
run-merchant-detail:
	PYTHONPATH=. $(PYTHON) -m service.merchant_detail.cmd.main

.PHONY: run-merchant-award
run-merchant-award:
	PYTHONPATH=. $(PYTHON) -m service.merchant_award.cmd.main

.PHONY: run-merchant-business
run-merchant-business:
	PYTHONPATH=. $(PYTHON) -m service.merchant_business.cmd.main

.PHONY: run-merchant-policy
run-merchant-policy:
	PYTHONPATH=. $(PYTHON) -m service.merchant_policy.cmd.main

.PHONY: run-product
run-product:
	PYTHONPATH=. $(PYTHON) -m service.product.cmd.main

.PHONY: run-cart
run-cart:
	PYTHONPATH=. $(PYTHON) -m service.cart.cmd.main

.PHONY: run-review
run-review:
	PYTHONPATH=. $(PYTHON) -m service.review.cmd.main

.PHONY: run-order
run-order:
	PYTHONPATH=. $(PYTHON) -m service.order.cmd.main

.PHONY: run-email
run-email:
	PYTHONPATH=. $(PYTHON) -m service.email.cmd.main
