"""merchant_policy query cache.

Every list cache written here is also read. Reads/writes never raise:
`CacheStore` swallows Redis errors so a cache outage degrades to a DB read."""

from __future__ import annotations

from pkg.database.schema.merchant_policy import (
    GetMerchantPoliciesActiveRow,
    GetMerchantPoliciesRow,
    GetMerchantPoliciesTrashedRow,
    GetMerchantPolicyRow,
)
from pkg.logger.logger import Logger
from service.merchant_policy.redis.cache import (
    decode_page,
    encode_page,
    policy_active_row_from_dict,
    policy_active_row_to_dict,
    policy_by_id_from_dict,
    policy_by_id_to_dict,
    policy_row_from_dict,
    policy_row_to_dict,
)
from service.merchant_policy.redis.common import (
    TTL_DEFAULT,
    merchant_policy_active_key,
    merchant_policy_all_key,
    merchant_policy_by_id_key,
    merchant_policy_trashed_key,
)
from shared.cache import CacheStore


class MerchantPolicyQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_merchant_policies(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantPoliciesRow], int] | None:
        payload = await self._store.get_json(
            merchant_policy_all_key(page, page_size, search)
        )
        return decode_page(payload, policy_row_from_dict)

    async def set_merchant_policies(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantPoliciesRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            merchant_policy_all_key(page, page_size, search),
            encode_page(rows, total, policy_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_merchant_policies_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantPoliciesActiveRow], int] | None:
        payload = await self._store.get_json(
            merchant_policy_active_key(page, page_size, search)
        )
        return decode_page(payload, policy_active_row_from_dict)

    async def set_merchant_policies_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantPoliciesActiveRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            merchant_policy_active_key(page, page_size, search),
            encode_page(rows, total, policy_active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_merchant_policies_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantPoliciesTrashedRow], int] | None:
        payload = await self._store.get_json(
            merchant_policy_trashed_key(page, page_size, search)
        )
        return decode_page(payload, policy_active_row_from_dict)

    async def set_merchant_policies_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantPoliciesTrashedRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            merchant_policy_trashed_key(page, page_size, search),
            encode_page(rows, total, policy_active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_merchant_policy(
        self, merchant_policy_id: int
    ) -> GetMerchantPolicyRow | None:
        payload = await self._store.get_json(
            merchant_policy_by_id_key(merchant_policy_id)
        )
        if not isinstance(payload, dict):
            return None
        return policy_by_id_from_dict(payload)

    async def set_merchant_policy(self, row: GetMerchantPolicyRow) -> None:
        await self._store.set_json(
            merchant_policy_by_id_key(row.merchant_policy_id),
            policy_by_id_to_dict(row),
            TTL_DEFAULT,
        )


__all__ = ["MerchantPolicyQueryCacheImpl"]
