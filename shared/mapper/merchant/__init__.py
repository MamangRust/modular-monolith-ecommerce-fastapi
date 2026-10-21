"""Merchant response mapper. Two mapper packages (`merchant` + `merchant_documents`) are merged here because both are served by the same merchant service; the bundle exposes the four query/command groups and factory functions the `NewMerchantResponseMapper` / `NewMerchantDocumentResponseMapper`."""

from __future__ import annotations

from shared.mapper.merchant.command import (
    to_api_response_merchant_all,
    to_api_response_merchant_delete,
    to_api_response_merchant_delete_at,
)
from shared.mapper.merchant.document_command import (
    to_api_response_merchant_document_all,
    to_api_response_merchant_document_delete,
)
from shared.mapper.merchant.document_query import (
    to_api_response_merchant_document,
    to_api_response_pagination_merchant_document,
    to_api_response_pagination_merchant_document_delete_at,
    to_api_responses_merchant_document,
)
from shared.mapper.merchant.mapper import (
    map_merchant_document_response,
    map_merchant_document_response_delete_at,
    map_merchant_response,
    map_merchant_response_delete_at,
    map_pagination_meta,
    to_merchant_document_response,
    to_merchant_document_response_delete_at,
    to_merchant_response,
    to_merchant_response_delete_at,
)
from shared.mapper.merchant.query import (
    to_api_response_merchant,
    to_api_response_pagination_merchant,
    to_api_response_pagination_merchant_delete_at,
    to_api_responses_merchant,
)


class MerchantQueryMapper:
    """Query-side mapper bundle (`MerchantQueryResponseMapper`)."""

    to_api_response_merchant = staticmethod(to_api_response_merchant)
    to_api_responses_merchant = staticmethod(to_api_responses_merchant)
    to_api_response_pagination_merchant = staticmethod(
        to_api_response_pagination_merchant
    )
    to_api_response_pagination_merchant_delete_at = staticmethod(
        to_api_response_pagination_merchant_delete_at
    )


class MerchantCommandMapper:
    """Command-side mapper bundle (`MerchantCommandResponseMapper`)."""

    to_api_response_merchant = staticmethod(to_api_response_merchant)
    to_api_response_merchant_delete_at = staticmethod(to_api_response_merchant_delete_at)
    to_api_response_merchant_delete = staticmethod(to_api_response_merchant_delete)
    to_api_response_merchant_all = staticmethod(to_api_response_merchant_all)


class MerchantDocumentQueryMapper:
    """Document query bundle (`MerchantDocumentQueryResponseMapper`)."""

    to_api_response_merchant_document = staticmethod(to_api_response_merchant_document)
    to_api_responses_merchant_document = staticmethod(
        to_api_responses_merchant_document
    )
    to_api_response_pagination_merchant_document = staticmethod(
        to_api_response_pagination_merchant_document
    )
    to_api_response_pagination_merchant_document_delete_at = staticmethod(
        to_api_response_pagination_merchant_document_delete_at
    )


class MerchantDocumentCommandMapper:
    """Document command bundle (`MerchantDocumentCommandResponseMapper`)."""

    to_api_response_merchant_document = staticmethod(to_api_response_merchant_document)
    to_api_response_merchant_document_delete = staticmethod(
        to_api_response_merchant_document_delete
    )
    to_api_response_merchant_document_all = staticmethod(
        to_api_response_merchant_document_all
    )


class MerchantResponseMapper:
    """Factory `NewMerchantResponseMapper`."""

    def __init__(self) -> None:
        self._query = MerchantQueryMapper()
        self._command = MerchantCommandMapper()

    def query_mapper(self) -> MerchantQueryMapper:
        return self._query

    def command_mapper(self) -> MerchantCommandMapper:
        return self._command


class MerchantDocumentResponseMapper:
    """Factory `NewMerchantDocumentResponseMapper`."""

    def __init__(self) -> None:
        self._query = MerchantDocumentQueryMapper()
        self._command = MerchantDocumentCommandMapper()

    def query_mapper(self) -> MerchantDocumentQueryMapper:
        return self._query

    def command_mapper(self) -> MerchantDocumentCommandMapper:
        return self._command


def new_merchant_response_mapper() -> MerchantResponseMapper:
    return MerchantResponseMapper()


def new_merchant_document_response_mapper() -> MerchantDocumentResponseMapper:
    return MerchantDocumentResponseMapper()


__all__ = [
    "MerchantCommandMapper",
    "MerchantDocumentCommandMapper",
    "MerchantDocumentQueryMapper",
    "MerchantDocumentResponseMapper",
    "MerchantQueryMapper",
    "MerchantResponseMapper",
    "map_merchant_document_response",
    "map_merchant_document_response_delete_at",
    "map_merchant_response",
    "map_merchant_response_delete_at",
    "map_pagination_meta",
    "new_merchant_document_response_mapper",
    "new_merchant_response_mapper",
    "to_api_response_merchant",
    "to_api_response_merchant_all",
    "to_api_response_merchant_delete",
    "to_api_response_merchant_delete_at",
    "to_api_response_merchant_document",
    "to_api_response_merchant_document_all",
    "to_api_response_merchant_document_delete",
    "to_api_response_pagination_merchant",
    "to_api_response_pagination_merchant_delete_at",
    "to_api_response_pagination_merchant_document",
    "to_api_response_pagination_merchant_document_delete_at",
    "to_api_responses_merchant",
    "to_api_responses_merchant_document",
    "to_merchant_document_response",
    "to_merchant_document_response_delete_at",
    "to_merchant_response",
    "to_merchant_response_delete_at",
]
