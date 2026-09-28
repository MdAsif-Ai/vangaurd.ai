"""Local storage backend tests."""

from pathlib import Path

import pytest

from app.integrations.storage import LocalStorageBackend, StorageError


async def test_save_read_delete_roundtrip(tmp_path: Path) -> None:
    backend = LocalStorageBackend(tmp_path)
    await backend.save("org-1/doc-1/report.txt", b"financial data")
    assert await backend.exists("org-1/doc-1/report.txt") is True
    content = await backend.read("org-1/doc-1/report.txt")
    assert content == b"financial data"
    await backend.delete("org-1/doc-1/report.txt")
    assert await backend.exists("org-1/doc-1/report.txt") is False


async def test_read_missing_object_raises(tmp_path: Path) -> None:
    backend = LocalStorageBackend(tmp_path)
    with pytest.raises(StorageError):
        await backend.read("missing.txt")


async def test_path_traversal_is_rejected(tmp_path: Path) -> None:
    backend = LocalStorageBackend(tmp_path)
    with pytest.raises(StorageError):
        await backend.save("../outside.txt", b"forbidden")


async def test_health_check(tmp_path: Path) -> None:
    backend = LocalStorageBackend(tmp_path)
    assert await backend.health_check() is True