from __future__ import annotations

import errno
import os
from pathlib import Path

import pytest

from scripts.bounded_filesystem_scout import scan_roots


def test_complete_bounded_scan_is_deterministic(tmp_path: Path) -> None:
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    nested = tmp_path / "a"
    nested.mkdir()
    (nested / "x.txt").write_text("x", encoding="utf-8")

    first = scan_roots([tmp_path])
    second = scan_roots([tmp_path])

    assert first == second
    assert first["status"] == "COMPLETE"
    assert first["complete"] is True
    assert first["skipped_count"] == 0
    assert first["file_count"] == 2
    assert first["authority"] == "DISCOVERY_RECEIPT_ONLY"
    assert first["formal_credit_delta"] == 0


def test_permission_failure_makes_receipt_partial(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    denied = tmp_path / "denied"
    denied.mkdir()
    (denied / "secret.txt").write_text("secret", encoding="utf-8")
    (tmp_path / "visible.txt").write_text("visible", encoding="utf-8")

    real_scandir = os.scandir

    def guarded_scandir(path):
        if Path(str(path)).name == "denied":
            raise PermissionError(errno.EACCES, "permission denied", str(path))
        return real_scandir(path)

    monkeypatch.setattr(os, "scandir", guarded_scandir)
    receipt = scan_roots([tmp_path])

    assert receipt["status"] == "PARTIAL"
    assert receipt["complete"] is False
    assert receipt["skipped_count"] == 1
    assert receipt["skipped"][0]["error_type"] == "PERMISSION_DENIED"
    assert receipt["file_count"] == 1


def test_path_too_long_failure_is_recorded_not_silenced(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    deep = tmp_path / "deep"
    deep.mkdir()
    (tmp_path / "visible.txt").write_text("visible", encoding="utf-8")

    real_scandir = os.scandir

    def length_guard(path):
        if Path(str(path)).name == "deep":
            raise OSError(errno.ENAMETOOLONG, "file name too long", str(path))
        return real_scandir(path)

    monkeypatch.setattr(os, "scandir", length_guard)
    receipt = scan_roots([tmp_path])

    assert receipt["status"] == "PARTIAL"
    assert receipt["complete"] is False
    assert receipt["skipped_count"] == 1
    assert receipt["skipped"][0]["error_type"] == "PATH_TOO_LONG"
    assert receipt["file_count"] == 1


def test_missing_root_is_explicit_partial(tmp_path: Path) -> None:
    receipt = scan_roots([tmp_path / "missing"])
    assert receipt["status"] == "PARTIAL"
    assert receipt["complete"] is False
    assert receipt["skipped"][0]["error_type"] == "ROOT_NOT_FOUND"
