from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import office_com  # noqa: E402


def test_require_windows_raises_off_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(office_com.sys, "platform", "linux")

    with pytest.raises(office_com.OfficeComError, match="requires Windows"):
        office_com._require_windows()


def test_convert_document_to_pdf_raises_off_windows(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(office_com.sys, "platform", "linux")

    with pytest.raises(office_com.OfficeComError, match="requires Windows"):
        office_com.convert_document_to_pdf(tmp_path / "in.docx", tmp_path / "out.pdf")


@pytest.mark.skipif(
    sys.platform != "win32", reason="Office COM automation requires Windows"
)
def test_convert_document_to_pdf_on_windows_with_word() -> None:
    pytest.importorskip("win32com.client")

    from docx import Document

    # Deliberately neither pytest's tmp_path fixture NOR tempfile.mkdtemp():
    # both create a directory with an owner-only ACL (tempfile.mkdtemp()'s is
    # documented Python security hardening; pytest's tmp_path uses the same
    # mechanism). On at least one real Windows machine that ACL is scoped
    # tighter than "same Windows user account" -- confirmed via icacls that
    # even an interactive PowerShell session in the same account gets "Access
    # is denied" listing such a directory -- so a freshly launched Word.exe
    # process (nominally the same user, but a different process/logon
    # context) can't read it either, surfacing as a confusing "couldn't find
    # your file" COM error that has nothing to do with office_com.py itself
    # (verified separately: office_com.convert_document_to_pdf works
    # correctly against a plain, non-owner-restricted directory). A directory
    # created with a plain Path.mkdir() inherits normal, non-restrictive
    # permissions from its parent and carries no such issue.
    work_dir = Path(tempfile.gettempdir()) / "office-com-test-scratch"
    work_dir.mkdir(exist_ok=True)
    try:
        source = work_dir / "sample.docx"
        Document().save(source)
        destination = work_dir / "sample.pdf"

        try:
            result = office_com.convert_document_to_pdf(source, destination)
        except office_com.OfficeComError as exc:
            pytest.skip(f"Word is not available via COM automation on this machine: {exc}")

        assert result == destination.resolve()
        assert destination.exists()
        assert destination.stat().st_size > 0
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
