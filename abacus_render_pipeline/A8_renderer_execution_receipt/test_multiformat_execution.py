from __future__ import annotations

import json
import tempfile
from pathlib import Path

from multiformat_execution import (
    MULTIFORMAT_RECEIPT,
    PDF_OUTPUT,
    PPTX_OUTPUT,
    execute_multiformat,
)
from multiformat_promotion import PROMOTION_RECEIPT, promote_multiformat
from multiformat_validation import load_and_validate_multiformat_receipt


def test_multiformat_receipt_is_deterministic_and_content_addressed():
    first = execute_multiformat()
    first_pptx = first["artifacts"]["pptx"]["artifact_sha256"]
    first_pdf = first["artifacts"]["pdf"]["artifact_sha256"]

    second = execute_multiformat()
    assert first["decision"] == "accept"
    assert second["decision"] == "accept"
    assert second["artifacts"]["pptx"]["artifact_sha256"] == first_pptx
    assert second["artifacts"]["pdf"]["artifact_sha256"] == first_pdf
    assert second["cross_format_parity"]["pass"] is True
    assert second["artifacts"]["pptx"]["checks"]["layout"]["pass"] is True
    assert second["artifacts"]["pptx"]["checks"]["overflow"]["pass"] is True
    assert second["artifacts"]["pptx"]["checks"]["content"]["pass"] is True
    assert second["artifacts"]["pdf"]["checks"]["layout"]["pass"] is True
    assert second["artifacts"]["pdf"]["checks"]["overflow"]["pass"] is True
    assert second["artifacts"]["pdf"]["checks"]["content"]["pass"] is True
    assert PPTX_OUTPUT.exists()
    assert PDF_OUTPUT.exists()

    validated = load_and_validate_multiformat_receipt(MULTIFORMAT_RECEIPT)
    assert validated["decision"] == "accept"


def test_one_bundle_promotion_receipt_covers_both_formats():
    execute_multiformat()
    result = promote_multiformat()
    assert result["decision"] == "PROMOTE"
    assert result["checks"]["pptx_accepted"] is True
    assert result["checks"]["pdf_accepted"] is True
    assert result["checks"]["cross_format_parity"] is True
    assert set(result["artifact_sha256"]) == {"pptx", "pdf"}
    assert PROMOTION_RECEIPT.exists()


def test_tampered_multiformat_receipt_is_rejected():
    execute_multiformat()
    source = json.loads(MULTIFORMAT_RECEIPT.read_text(encoding="utf-8"))
    source["artifacts"]["pptx"]["artifact_sha256"] = "0" * 64
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "tampered_multiformat_receipt.json"
        path.write_text(json.dumps(source), encoding="utf-8")
        try:
            load_and_validate_multiformat_receipt(path)
        except ValueError as exc:
            assert "content-address validation failed" in str(exc)
        else:
            raise AssertionError("tampered multiformat receipt should have been rejected")


def test_cross_format_parity_cannot_be_self_asserted():
    execute_multiformat()
    source = json.loads(MULTIFORMAT_RECEIPT.read_text(encoding="utf-8"))
    source["cross_format_parity"]["pass"] = False
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "false_parity_receipt.json"
        path.write_text(json.dumps(source), encoding="utf-8")
        try:
            load_and_validate_multiformat_receipt(path)
        except ValueError as exc:
            assert "cross-format parity mismatch" in str(exc)
        else:
            raise AssertionError("self-asserted parity state should not bypass revalidation")


if __name__ == "__main__":
    test_multiformat_receipt_is_deterministic_and_content_addressed()
    test_one_bundle_promotion_receipt_covers_both_formats()
    test_tampered_multiformat_receipt_is_rejected()
    test_cross_format_parity_cannot_be_self_asserted()
    print("A8.2 multiformat receipt tests: PASS")
