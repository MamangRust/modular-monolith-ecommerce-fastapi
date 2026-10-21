"""File upload validation and storage. operates on `*multipart.FileHeader`; operates on FastAPI's `UploadFile`. The validation rules are identical: - document uploads accept `.pdf`/`.docx` up to 10 MB; - image uploads accept `.jpg`/`.jpeg`/`.png` up to 5 MB; - the stored filename is `{unix_nano}{ext}` under the requested directory; - the returned path is the relative path (e.g. `uploads/merchant_document/1234567890.pdf`), which is what the document row stores. Because `UploadFile.read` is async, `process_image_upload` / `save_uploaded_file` are async (versions are sync). Size validation prefers `UploadFile.size` (set by Starlette's multipart parser) and falls back to reading the stream when it is unavailable (e.g. hand-built test files)."""

from __future__ import annotations

import os
import time
from typing import Any

from pkg.logger.logger import Logger
from shared.errors import new_bad_request_error, new_internal_error

_DOCUMENT_TYPES = {".pdf": True, ".docx": True}
_IMAGE_TYPES = {".jpg": True, ".jpeg": True, ".png": True}
_DOCUMENT_ALLOWED = "PDF, DOCX"
_IMAGE_ALLOWED = "JPG, JPEG, PNG"
_DOCUMENT_MAX_SIZE = 10 << 20  # 10 MB
_IMAGE_MAX_SIZE = 5 << 20  # 5 MB


def _allowed_list(allowed: dict[str, bool]) -> str:
    return _DOCUMENT_ALLOWED if allowed is _DOCUMENT_TYPES else _IMAGE_ALLOWED


class ImageUpload:
    def __init__(self, logger: Logger) -> None:
        self._logger = logger

    def ensure_upload_directory(self, upload_dir: str) -> None:
        if os.path.isdir(upload_dir):
            return
        try:
            os.makedirs(upload_dir, mode=0o755, exist_ok=True)
        except OSError as exc:
            self._logger.error(
                "failed to create upload directory", directory=upload_dir, error=str(exc)
            )
            raise new_internal_error(exc) from exc

    async def process_image_upload(
        self, upload_dir: str, file: Any, is_document: bool
    ) -> str:
        allowed = _DOCUMENT_TYPES if is_document else _IMAGE_TYPES
        max_size = _DOCUMENT_MAX_SIZE if is_document else _IMAGE_MAX_SIZE

        filename = getattr(file, "filename", "") or ""
        ext = os.path.splitext(filename)[1].lower()
        if not allowed.get(ext):
            raise new_bad_request_error(
                f"Only {_allowed_list(allowed)} are allowed"
            )

        size = getattr(file, "size", None)
        if size is None:
            data = await file.read()
            size = len(data)
            await file.seek(0)

        if size > max_size:
            size_mb = float(max_size) / (1 << 20)
            raise new_bad_request_error(
                f"File size must be less than {size_mb:.0f}MB"
            )

        try:
            self.ensure_upload_directory(upload_dir)
        except Exception as exc:
            raise new_internal_error(exc) from exc

        stored_name = f"{time.time_ns()}{ext}"
        image_path = os.path.join(upload_dir, stored_name)

        try:
            await self.save_uploaded_file(file, image_path)
        except Exception as exc:
            self._logger.error(
                "failed to save uploaded file", path=image_path, error=str(exc)
            )
            raise new_internal_error(exc) from exc

        self._logger.debug(
            "successfully saved uploaded file",
            path=image_path,
            size=size,
            is_document=is_document,
        )
        return image_path

    def cleanup_image_on_failure(self, image_path: str) -> None:
        try:
            os.remove(image_path)
        except OSError as exc:
            self._logger.debug(
                "failed to clean up uploaded file after failure",
                path=image_path,
                error=str(exc),
            )

    async def save_uploaded_file(self, file: Any, dst: str) -> None:
        try:
            data = await file.read()
        except Exception as exc:
            raise new_internal_error(exc) from exc

        try:
            with open(dst, "wb") as out:
                out.write(data)
        except OSError as exc:
            raise new_internal_error(exc) from exc

        # verifies the write: a zero-byte destination is a failure.
        try:
            if os.path.getsize(dst) == 0:
                raise new_internal_error(RuntimeError("failed to verify file write"))
        except OSError as exc:
            raise new_internal_error(exc) from exc


def new_image_upload(logger: Logger) -> ImageUpload:
    return ImageUpload(logger)


__all__ = ["ImageUpload", "new_image_upload"]
