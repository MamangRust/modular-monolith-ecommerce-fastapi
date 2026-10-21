"""transaction request DTOs. - **service/cache records** (plain dataclasses): `FindAllTransaction`, `FindAllTransactionByMerchant`, the stats request records; - **command DTOs** (pydantic): `CreateTransactionRequest` / `UpdateTransactionRequest`. `validator` tags on the command DTOs require `order_id`/`merchant_id`/ `payment_method`/`amount` (`user_id` and `payment_status` are untagged), but the transaction gRPC handlers never call `Validate` and the catalogue's `ErrGrpcValidateCreate/UpdateTransaction` sentinels are unreferenced (dead catalog entries).: the pydantic models carry the constraints, nothing enforces them on the wire — the service derives the final amount/status itself."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class FindAllTransaction:
    """Service/cache request (`requests.FindAllTransaction`)."""

    search: str
    page: int
    page_size: int


@dataclass
class FindAllTransactionByMerchant:
    """Service/cache request (`requests.FindAllTransactionByMerchant`)."""

    merchant_id: int
    search: str
    page: int
    page_size: int


@dataclass
class MonthAmountTransaction:
    year: int
    month: int


@dataclass
class MonthAmountTransactionMerchant:
    merchant_id: int
    year: int
    month: int


@dataclass
class YearAmountTransactionMerchant:
    merchant_id: int
    year: int


@dataclass
class MonthMethodTransaction:
    year: int
    month: int


@dataclass
class MonthMethodTransactionMerchant:
    merchant_id: int
    year: int
    month: int


@dataclass
class YearMethodTransactionMerchant:
    merchant_id: int
    year: int


class CreateTransactionRequest(BaseModel):
    """Gateway/body request (`requests.CreateTransactionRequest`). `user_id` may be 0 — the service then resolves the owner from the order."""

    user_id: int = 0
    order_id: int
    merchant_id: int
    payment_method: str
    amount: int
    payment_status: str = ""


class CreateTransactionRecordRequest(BaseModel):
    """Repository/service record (reuses `CreateTransactionRequest`)."""

    user_id: int
    order_id: int
    merchant_id: int
    payment_method: str
    amount: int
    payment_status: str


class UpdateTransactionRequest(BaseModel):
    """Gateway/body request (`requests.UpdateTransactionRequest`). `transaction_id` is set by the gRPC handler from the proto field (`*int`). `order_id`/`merchant_id` of 0 fall back to the existing row inside the service; `payment_status` empty means "unchanged"."""

    transaction_id: int = 0
    order_id: int
    merchant_id: int
    payment_method: str
    amount: int
    payment_status: str = ""


class UpdateTransactionRecordRequest(BaseModel):
    """Repository record (reuses `UpdateTransactionRequest`)."""

    transaction_id: int
    order_id: int
    merchant_id: int
    payment_method: str
    amount: int
    payment_status: str


__all__ = [
    "CreateTransactionRecordRequest",
    "CreateTransactionRequest",
    "FindAllTransaction",
    "FindAllTransactionByMerchant",
    "MonthAmountTransaction",
    "MonthAmountTransactionMerchant",
    "MonthMethodTransaction",
    "MonthMethodTransactionMerchant",
    "UpdateTransactionRecordRequest",
    "UpdateTransactionRequest",
    "YearAmountTransactionMerchant",
    "YearMethodTransactionMerchant",
]
