from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from codex.contract_governance.builder import build_artifacts
from codex.contract_governance.io import load_ssot
from codex.contract_governance.validator import validate_generated

SSOT = Path("contract_governance/ssot/abacus_contract_governance.yaml")
FORBIDDEN_BIDDER_STRINGS = {
    "Extraction Audit",
    "Evaluation Notes",
    "REQ-W001-001",
    "Generated tier stripping",
    "Internal evaluation placeholder",
}


def _pdf_full_text(path: Path) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def test_build_artifacts_generates_a_pdf_report(tmp_path: Path) -> None:
    ssot = load_ssot(SSOT)
    result = build_artifacts(ssot, tmp_path, "internal")

    assert "pdf" in result
    pdf_path = Path(result["pdf"])
    assert pdf_path.exists()

    report_text = _pdf_full_text(pdf_path)
    assert "Requirements" in report_text
    assert "Extraction Audit" in report_text
    assert "REQ-W001-001" in report_text


def test_pdf_text_content_is_deterministic_across_builds(tmp_path: Path) -> None:
    ssot = load_ssot(SSOT)
    first = build_artifacts(ssot, tmp_path / "first", "internal")
    second = build_artifacts(ssot, tmp_path / "second", "internal")

    assert _pdf_full_text(Path(first["pdf"])) == _pdf_full_text(Path(second["pdf"]))


def test_bidder_pdf_strips_internal_only_content(tmp_path: Path) -> None:
    ssot = load_ssot(SSOT)
    result = build_artifacts(ssot, tmp_path, "bidder")
    validate_generated(ssot, tmp_path, "bidder")

    pdf_text = _pdf_full_text(Path(result["pdf"]))
    for forbidden in FORBIDDEN_BIDDER_STRINGS:
        assert forbidden not in pdf_text
