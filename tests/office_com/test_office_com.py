from __future__ import annotations

import sys
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
def test_convert_document_to_pdf_on_windows_with_word(tmp_path: Path) -> None:
    pytest.importorskip("win32com.client")

    from docx import Document

    source = tmp_path / "sample.docx"
    Document().save(source)
    destination = tmp_path / "sample.pdf"

    try:
        result = office_com.convert_document_to_pdf(source, destination)
    except office_com.OfficeComError as exc:
        pytest.skip(f"Word is not available via COM automation on this machine: {exc}")

    assert result == destination.resolve()
    assert destination.exists()
    assert destination.stat().st_size > 0
