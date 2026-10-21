"""Process-level configuration. Variable names keep reference implementation (viper keys): DB_*, REDIS_*, KAFKA_BROKERS, SECRET_KEY, OTEL_*, GRPC_<DOMAIN>_ADDR, SMTP_*. SMTP settings are only required by the email worker; every other process must be able to boot without them."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load `.env` (gitignored) into os.environ once at import. This must happen
# before any settings class is instantiated so that both pydantic's own
# env parsing and the raw os.environ lookups in
# `RedisSettings.resolve_for_service` see the same values.
load_dotenv()


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    db_driver: Literal["pgx", "postgres"] = Field("pgx", alias="DB_DRIVER")
    db_host: str = Field("", alias="DB_HOST")
    db_port: str = Field("5432", alias="DB_PORT")
    db_username: str = Field("", alias="DB_USERNAME")
    db_name: str = Field("payment_gateway", alias="DB_NAME")
    db_password: str = Field("", alias="DB_PASSWORD")
    db_max_open_conns: int = Field(100, alias="DB_MAX_OPEN_CONNS")
    db_min_idle_conns: int = Field(50, alias="DB_MIN_IDLE_CONNS")
    # used viper durations (1h / 30m); Python keeps plain seconds.
    db_conn_max_lifetime: int = Field(3600, alias="DB_CONN_MAX_LIFETIME")
    db_conn_max_idle_time: int = Field(1800, alias="DB_CONN_MAX_IDLE_TIME")

    @property
    def async_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_username}"
            f":{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    def pool_size(self) -> int:
        return self.db_max_open_conns


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    redis_host: str = Field("", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")
    redis_password: str = Field("", alias="REDIS_PASSWORD")
    redis_db: int = Field(0, alias="REDIS_DB")

    # Domain services may override the generic keys with a suffixed
    # REDIS_HOST_<SUFFIX>). Suffix is the upper-cased service name
    # without the "-service" suffix.
    def resolve_for_service(self, service_name: str) -> RedisSettings:
        suffix = service_name.removesuffix("-service").upper()
        env = os.environ

        def pick(suffixed: str, generic: str, fallback: str = "") -> str:
            return env.get(suffixed) or env.get(generic) or fallback

        return RedisSettings(
            redis_host=pick(f"REDIS_HOST_{suffix}", "REDIS_HOST"),
            redis_port=int(pick(f"REDIS_PORT_{suffix}", "REDIS_PORT", "6379") or 0) or 6379,
            redis_password=pick(f"REDIS_PASSWORD_{suffix}", "REDIS_PASSWORD"),
            redis_db=int(env.get(f"REDIS_DB_{suffix}") or env.get("REDIS_DB") or 0),
        )


class KafkaSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    kafka_brokers: str = Field("localhost:9092", alias="KAFKA_BROKERS")

    @property
    def broker_list(self) -> list[str]:
        return [b.strip() for b in self.kafka_brokers.split(",") if b.strip()]


class GrpcSettings(BaseSettings):
    """gRPC service addresses, consumed by the gateway and cross-domain adapters. Each service also has a default port."""

    model_config = SettingsConfigDict(extra="ignore")

    # + deployments/local/local.env (see Planning.md section 0).
    grpc_auth_addr: str = Field("localhost:50051", alias="GRPC_AUTH_ADDR")
    grpc_role_addr: str = Field("localhost:50052", alias="GRPC_ROLE_ADDR")
    grpc_user_addr: str = Field("localhost:50053", alias="GRPC_USER_ADDR")
    grpc_category_addr: str = Field("localhost:50054", alias="GRPC_CATEGORY_ADDR")
    grpc_merchant_addr: str = Field("localhost:50055", alias="GRPC_MERCHANT_ADDR")
    grpc_order_item_addr: str = Field("localhost:50056", alias="GRPC_ORDER_ITEM_ADDR")
    grpc_order_addr: str = Field("localhost:50057", alias="GRPC_ORDER_ADDR")
    grpc_product_addr: str = Field("localhost:50058", alias="GRPC_PRODUCT_ADDR")
    grpc_transaction_addr: str = Field("localhost:50059", alias="GRPC_TRANSACTION_ADDR")
    grpc_cart_addr: str = Field("localhost:50060", alias="GRPC_CART_ADDR")
    grpc_review_addr: str = Field("localhost:50061", alias="GRPC_REVIEW_ADDR")
    grpc_slider_addr: str = Field("localhost:50062", alias="GRPC_SLIDER_ADDR")
    grpc_shipping_address_addr: str = Field("localhost:50063", alias="GRPC_SHIPPING_ADDRESS_ADDR")
    grpc_banner_addr: str = Field("localhost:50064", alias="GRPC_BANNER_ADDR")
    grpc_merchant_award_addr: str = Field("localhost:50065", alias="GRPC_MERCHANT_AWARD_ADDR")
    grpc_merchant_business_addr: str = Field("localhost:50066", alias="GRPC_MERCHANT_BUSINESS_ADDR")
    grpc_merchant_detail_addr: str = Field("localhost:50067", alias="GRPC_MERCHANT_DETAIL_ADDR")
    grpc_merchant_policy_addr: str = Field("localhost:50068", alias="GRPC_MERCHANT_POLICY_ADDR")
    grpc_review_detail_addr: str = Field("localhost:50069", alias="GRPC_REVIEW_DETAIL_ADDR")


class SmtpSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    smtp_host: str = Field("", alias="SMTP_HOST")
    smtp_port: int = Field(587, alias="SMTP_PORT")
    smtp_user: str = Field("", alias="SMTP_USER")
    smtp_password: str = Field("", alias="SMTP_PASSWORD")
    # reads EMAIL_MAX_RETRIES / EMAIL_RETRY_BACKOFF (a duration) in
    # service/email; both fall back to the emailretry defaults when unset or
    # non-positive.
    max_retries: int = Field(0, alias="EMAIL_MAX_RETRIES")
    retry_backoff_seconds: float = Field(0.0, alias="EMAIL_RETRY_BACKOFF")

    def require(self) -> SmtpSettings:
        if not self.smtp_host:
            raise RuntimeError("SMTP_HOST is required for the email worker")
        return self


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    env: str = Field("development", alias="ENV")
    secret_key: str = Field("", alias="SECRET_KEY")
    otel_endpoint: str = Field("localhost:4317", alias="OTEL_ENDPOINT")
    otel_enabled: bool = Field(True, alias="OTEL_ENABLED")
    enable_reflection: bool = Field(False, alias="ENABLE_REFLECTION")
    gateway_port: int = Field(5000, alias="GATEWAY_PORT")

    def require_secret_key(self, service_name: str) -> str:
        if not self.secret_key:
            raise RuntimeError(f"SECRET_KEY is required for {service_name}")
        return self.secret_key


class Settings:
    """Facade bundling every settings group for one process."""

    def __init__(self) -> None:
        self.database = DatabaseSettings()
        self.redis = RedisSettings()
        self.kafka = KafkaSettings()
        self.grpc = GrpcSettings()
        self.smtp = SmtpSettings()
        self.app = AppSettings()


@lru_cache
def get_settings() -> Settings:
    return Settings()
