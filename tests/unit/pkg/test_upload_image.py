"""Unit tests for the file-upload port (`pkg/upload_image`). Documents accept `.pdf`/`.docx` up to 10 MB; images accept `.jpg`/`.jpeg`/`.png` up to 5 MB. The stored filename is `{unix_nano}{ext}` and the returned value is the relative path. sync API, the methods are async because `UploadFile.read` is a coroutine."""

from __future__ import annotations

import os

import pytest

from pkg.logger.logger import Logger
from pkg.upload_image import ImageUpload, new_image_upload
from shared.errors import AppError


class FakeFile:
    def __init__(self, filename: str, data: bytes = b"hello") -> None:
        self.filename = filename
        self.size = len(data)
        self._data = data

    async def read(self) -> bytes:
        return self._data

    async def seek(self, pos: int) -> int:
        return pos


def _upload() -> ImageUpload:
    return new_image_upload(Logger("test", "error"))


async def test_document_upload_stores_pdf(tmp_path) -> None:
    upload_dir = str(tmp_path / "merchant_document")
    path = await _upload().process_image_upload(
        upload_dir, FakeFile("nib.pdf"), is_document=True
    )
    assert path.startswith(upload_dir)
    assert path.endswith(".pdf")
    assert os.path.isfile(path)


async def test_image_upload_stores_png(tmp_path) -> None:
    upload_dir = str(tmp_path / "images")
    path = await _upload().process_image_upload(
        upload_dir, FakeFile("logo.PNG"), is_document=False
    )
    assert path.endswith(".png")


async def test_document_rejects_image_extension(tmp_path) -> None:
    with pytest.raises(AppError) as excinfo:
        await _upload().process_image_upload(
            str(tmp_path), FakeFile("photo.jpg"), is_document=True
        )
    assert excinfo.value.code == 400
    assert excinfo.value.message == "Only PDF, DOCX are allowed"


async def test_image_rejects_document_extension(tmp_path) -> None:
    with pytest.raises(AppError) as excinfo:
        await _upload().process_image_upload(
            str(tmp_path), FakeFile("doc.pdf"), is_document=False
        )
    assert excinfo.value.code == 400
    assert excinfo.value.message == "Only JPG, JPEG, PNG are allowed"


async def test_document_rejects_oversized_file(tmp_path) -> None:
    file = FakeFile("big.pdf")
    file.size = (10 << 20) + 1
    with pytest.raises(AppError) as excinfo:
        await _upload().process_image_upload(str(tmp_path), file, is_document=True)
    assert excinfo.value.code == 400
    assert excinfo.value.message == "File size must be less than 10MB"


async def test_image_rejects_oversized_file(tmp_path) -> None:
    file = FakeFile("big.png")
    file.size = (5 << 20) + 1
    with pytest.raises(AppError) as excinfo:
        await _upload().process_image_upload(str(tmp_path), file, is_document=False)
    assert excinfo.value.code == 400
    assert excinfo.value.message == "File size must be less than 5MB"


async def test_size_falls_back_to_reading_stream(tmp_path) -> None:
    file = FakeFile("a.pdf", data=b"x" * 10)
    del file.size  # force the read() fallback
    path = await _upload().process_image_upload(
        str(tmp_path), file, is_document=True
    )
    assert os.path.getsize(path) == 10


def test_ensure_upload_directory_is_idempotent(tmp_path) -> None:
    upload = _upload()
    target = str(tmp_path / "nested" / "dir")
    upload.ensure_upload_directory(target)
    upload.ensure_upload_directory(target)
    assert os.path.isdir(target)


def test_cleanup_image_on_failure_removes_file(tmp_path) -> None:
    path = tmp_path / "gone.pdf"
    path.write_bytes(b"x")
    _upload().cleanup_image_on_failure(str(path))
    assert not path.exists()
    # Removing a missing file must not raise.
    _upload().cleanup_image_on_failure(str(path))


async def test_save_uploaded_file_rejects_zero_byte_write(tmp_path) -> None:
    with pytest.raises(AppError) as excinfo:
        await _upload().save_uploaded_file(FakeFile("e.pdf", data=b""), str(tmp_path / "e.pdf"))
    assert excinfo.value.code == 500


__all__ = []
