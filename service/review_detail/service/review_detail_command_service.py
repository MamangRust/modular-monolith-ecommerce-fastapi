"""Review detail command service. Every *single* mutation invalidates the entire `review_detail:*` cache *after* the repository has committed., `RestoreAll`/`DeleteAll` do **not** flush the cache — review_detail service omits the invalidation for those two bulk ops, and exactly (see). `delete_permanent` first resolves the trashed row (to obtain its `url`) via the read repository, then removes the backing file, then hard-deletes. A repository error (e.g. a 404 `review detail not found`) is propagated unchanged to the gRPC handler, which maps it through `ToGrpcError`, so a missing row surfaces as `NOT_FOUND` on the wire."""

from __future__ import annotations

import os

from pkg.database.schema.review_detail import (
    CreateReviewDetailRow,
    ReviewDetail,
    UpdateReviewDetailRow,
)
from pkg.logger.logger import Logger
from service.review_detail.redis.interfaces import ReviewDetailCommandCache
from service.review_detail.repository.interfaces import (
    ReviewDetailCommandRepository,
    ReviewDetailQueryRepository,
)
from shared.domain.requests.review_detail import (
    CreateReviewDetailRequest,
    UpdateReviewDetailRequest,
)
from shared.observability import Observability

# Uploaded review detail media are stored under this path prefix; only local
# paths are removed on permanent delete (remote URLs are left untouched).
_UPLOAD_PREFIXES = ("uploads/", "./uploads/", "/uploads/")


class ReviewDetailCommandServiceImpl:
    def __init__(
        self,
        repo: ReviewDetailCommandRepository,
        query_repo: ReviewDetailQueryRepository,
        cache: ReviewDetailCommandCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._query_repo = query_repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def create(self, request: CreateReviewDetailRequest) -> CreateReviewDetailRow:
        with self._obs.span("review_detail.command.create"):
            review_detail = await self._repo.create(request)
            await self._cache.invalidate_review_detail_cache()
            self._logger.info(
                "review detail created", review_detail_id=review_detail.review_detail_id
            )
            return review_detail

    async def update(self, request: UpdateReviewDetailRequest) -> UpdateReviewDetailRow:
        review_detail_id = request.review_detail_id or 0
        with self._obs.span("review_detail.command.update", review_detail_id=review_detail_id):
            review_detail = await self._repo.update(request)
            await self._cache.invalidate_review_detail_cache()
            self._logger.info(
                "review detail updated", review_detail_id=review_detail_id
            )
            return review_detail

    async def trash(self, review_detail_id: int) -> ReviewDetail:
        with self._obs.span("review_detail.command.trash", review_detail_id=review_detail_id):
            review_detail = await self._repo.trash(review_detail_id)
            await self._cache.invalidate_review_detail_cache()
            self._logger.info(
                "review detail trashed", review_detail_id=review_detail_id
            )
            return review_detail

    async def restore(self, review_detail_id: int) -> ReviewDetail:
        with self._obs.span("review_detail.command.restore", review_detail_id=review_detail_id):
            review_detail = await self._repo.restore(review_detail_id)
            await self._cache.invalidate_review_detail_cache()
            self._logger.info(
                "review detail restored", review_detail_id=review_detail_id
            )
            return review_detail

    async def delete_permanent(self, review_detail_id: int) -> bool:
        with self._obs.span(
            "review_detail.command.delete_permanent", review_detail_id=review_detail_id
        ):
            # Resolve the trashed row first (raises 404 NOT_FOUND if absent),
            # matching the `FindByIDTrashed` lookup.
            trashed = await self._query_repo.find_by_id_trashed(review_detail_id)
            self._remove_media(trashed.url)
            await self._repo.delete_permanent(review_detail_id)
            await self._cache.invalidate_review_detail_cache()
            self._logger.info(
                "review detail deleted permanently", review_detail_id=review_detail_id
            )
            return True

    async def restore_all(self) -> bool:
        # review_detail command service intentionally does NOT invalidate
        # the cache here. Keep (see).
        with self._obs.span("review_detail.command.restore_all"):
            await self._repo.restore_all()
            self._logger.info("all review details restored")
            return True

    async def delete_all_permanent(self) -> bool:
        # review_detail command service intentionally does NOT invalidate
        # the cache here. Keep (see).
        with self._obs.span("review_detail.command.delete_all_permanent"):
            await self._repo.delete_all_permanent()
            self._logger.info("all review details deleted permanently")
            return True

    def _remove_media(self, url: str | None) -> None:
        """Best-effort local file removal, matching the `os.Remove(url)` guard. ignores only `os.IsNotExist`; a missing local file is hence ignored, while a remote URL is never passed to `os.remove`. Only a local upload path is attempted, and a missing file (`FileNotFoundError`, the Python equivalent of `IsNotExist`) is swallowed."""
        if not url:
            return
        if url.startswith(("http://", "https://", "ftp://")):
            return
        is_local = url.startswith(_UPLOAD_PREFIXES) or ("/" in url and "://" not in url)
        if not is_local:
            return
        try:
            os.remove(url)
        except FileNotFoundError:
            pass
        except OSError as exc:  # pragma: no cover - environment-specific
            self._logger.warn("failed to remove review detail media", path=url, error=str(exc))


__all__ = ["ReviewDetailCommandServiceImpl"]
