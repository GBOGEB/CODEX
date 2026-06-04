from __future__ import annotations

import json
from pathlib import Path

import pytest

SSOT = Path("contract_governance/ssot/abacus_contract_governance.yaml")


def test_bootstrap_ssot_declares_bidder_and_internal_tiers() -> None:
    text = SSOT.read_text(encoding="utf-8")

    assert "ABACUS-CGW-W000-W001" in text
    assert "name: Requirements" in text
    assert "name: Extraction Audit" in text
    assert "audience: internal" in text


def test_builds_and_validates_both_tiers(tmp_path: Path) -> None:
    pytest.importorskip("pydantic")
    pytest.importorskip("ruamel.yaml")
    pytest.importorskip("jinja2")
    pytest.importorskip("openpyxl")
    from openpyxl import load_workbook

    from codex.contract_governance.builder import build_artifacts
    from codex.contract_governance.io import load_ssot
    from codex.contract_governance.validator import validate_generated

    ssot = load_ssot(SSOT)
    internal = build_artifacts(ssot, tmp_path, "internal")
    bidder = build_artifacts(ssot, tmp_path, "bidder")

    validate_generated(ssot, tmp_path, "internal")
    validate_generated(ssot, tmp_path, "bidder")

    assert internal["content_hash"] != bidder["content_hash"]
    bidder_wb = load_workbook(bidder["xlsx"], read_only=True)
    assert "Extraction Audit" not in bidder_wb.sheetnames
    assert "Evaluation Notes" not in bidder_wb.sheetnames
    assert bidder_wb.sheetnames == ["Requirements", "Traceability Matrix"]


def test_content_hash_is_manifested_from_canonical_payload(tmp_path: Path) -> None:
    pytest.importorskip("pydantic")
    pytest.importorskip("ruamel.yaml")
    pytest.importorskip("jinja2")
    pytest.importorskip("openpyxl")
    from codex.contract_governance.builder import build_artifacts
    from codex.contract_governance.io import load_ssot

    ssot = load_ssot(SSOT)
    result = build_artifacts(ssot, tmp_path, "bidder")
    manifest = json.loads(Path(result["manifest"]).read_text(encoding="utf-8"))

    assert manifest["content_hash_algorithm"] == "sha256"
    assert manifest["content_hash"] == result["content_hash"]
    assert len(manifest["content_hash"]) == 64
