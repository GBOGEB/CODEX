from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
A7 = ROOT / "abacus_render_pipeline" / "A7_executable_semantic_runtime"
sys.path.insert(0, str(ROOT))

from codex.contract_governance.builder import workbook_payload
from codex.contract_governance.io import content_hash, load_ssot

SCHEMA = HERE / "receipt_schema.json"
TUPLE_LEDGER = A7 / "data" / "semantic_tuple_ledger.json"
REQUIRED_FORMATS = ("html", "pptx", "pdf", "markdown", "github_pages")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_path(relpath: str) -> Path:
    candidate = (HERE / relpath).resolve()
    root = HERE.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"artifact path escapes A9 boundary: {relpath}")
    return candidate


def load_and_validate_receipt(receipt_path: Path) -> dict[str, Any]:
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema).iter_errors(receipt), key=lambda error: list(error.path)
    )
    if errors:
        raise ValueError(
            "receipt schema validation failed: "
            + "; ".join(error.message for error in errors)
        )

    ssot_path = ROOT / receipt["ssot_relpath"]
    if not ssot_path.exists():
        raise ValueError(f"SSOT path does not exist: {ssot_path}")
    ssot = load_ssot(ssot_path)
    canonical = content_hash(workbook_payload(ssot, receipt["render_mode"]))

    expected_top = {
        "ssot_sha256": sha256_path(ssot_path),
        "canonical_content_sha256": canonical,
        "tuple_ledger_sha256": sha256_path(TUPLE_LEDGER),
    }
    top_mismatches = [
        f"{field}: receipt={receipt.get(field)} actual={actual}"
        for field, actual in expected_top.items()
        if receipt.get(field) != actual
    ]
    if top_mismatches:
        raise ValueError(
            "receipt top-level content-address validation failed: "
            + "; ".join(top_mismatches)
        )

    env_source = os.environ.get("ABACUS_SOURCE_SHA")
    if env_source and receipt.get("source_commit") != env_source:
        raise ValueError(
            f"receipt source_commit mismatch: receipt={receipt.get('source_commit')} env={env_source}"
        )

    format_errors: list[str] = []
    for name in REQUIRED_FORMATS:
        item = receipt["formats"][name]
        artifact = _artifact_path(item["artifact_relpath"])
        if not artifact.exists():
            format_errors.append(f"{name}: artifact missing at {artifact}")
            continue
        actual_sha = sha256_path(artifact)
        if item["artifact_sha256"] != actual_sha:
            format_errors.append(
                f"{name}: artifact sha mismatch receipt={item['artifact_sha256']} actual={actual_sha}"
            )
        actual_bytes = artifact.stat().st_size
        if item["artifact_bytes"] != actual_bytes:
            format_errors.append(
                f"{name}: artifact byte-size mismatch receipt={item['artifact_bytes']} actual={actual_bytes}"
            )
        telemetry = item["telemetry"]
        layout_pass = bool(telemetry.get("layout_pass"))
        overflow_pass = bool(telemetry.get("overflow_pass"))
        parity_pass = bool(item["semantic_parity"].get("pass"))
        expected_decision = (
            "accept" if layout_pass and overflow_pass and parity_pass else "reject"
        )
        if item["decision"] != expected_decision:
            format_errors.append(
                f"{name}: decision={item['decision']} expected={expected_decision}"
            )

    if format_errors:
        raise ValueError("format receipt validation failed: " + "; ".join(format_errors))

    html_sha = receipt["formats"]["html"]["artifact_sha256"]
    pages_sha = receipt["formats"]["github_pages"]["artifact_sha256"]
    parity_expected = (
        all(receipt["formats"][name]["semantic_parity"]["pass"] for name in REQUIRED_FORMATS)
        and html_sha == pages_sha
    )
    if receipt["cross_format_parity"]["pass"] != parity_expected:
        raise ValueError(
            "cross-format parity decision inconsistent with validated format evidence"
        )
    if receipt["cross_format_parity"]["canonical_content_sha256"] != canonical:
        raise ValueError("cross-format parity canonical content hash mismatch")

    expected_decision = (
        "accept"
        if all(receipt["formats"][name]["decision"] == "accept" for name in REQUIRED_FORMATS)
        and parity_expected
        and bool(receipt["semantic_replay"]["pass"])
        else "reject"
    )
    if receipt["decision"] != expected_decision:
        raise ValueError(
            f"receipt decision inconsistent with evidence: receipt={receipt['decision']} expected={expected_decision}"
        )
    return receipt


if __name__ == "__main__":
    receipt_path = HERE / "receipts" / "multiformat_execution_receipt.json"
    validated = load_and_validate_receipt(receipt_path)
    print(
        json.dumps(
            {
                "status": "PASS",
                "decision": validated["decision"],
                "formats": list(validated["formats"]),
                "cross_format_parity": validated["cross_format_parity"]["pass"],
            },
            indent=2,
        )
    )
