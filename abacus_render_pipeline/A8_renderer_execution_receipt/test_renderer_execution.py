from __future__ import annotations

import json
import tempfile
from pathlib import Path

from promotion_receipt import promote
from renderer_execution import RECEIPT_DIR, execute
from receipt_validation import load_and_validate_receipt


def test_execution_receipt_is_content_addressed_and_deterministic():
    first = execute()
    second = execute()
    assert first["decision"] == "accept"
    assert second["decision"] == "accept"
    assert first["artifact_sha256"] == second["artifact_sha256"]
    assert first["ssot_sha256"] == second["ssot_sha256"]
    assert first["tuple_ledger_sha256"] == second["tuple_ledger_sha256"]
    assert first["checks"]["contrast"]["pass"] is True
    assert first["checks"]["layout"]["pass"] is True
    assert first["checks"]["overflow"]["pass"] is True
    assert first["checks"]["semantic_replay"]["pass"] is True

    validated = load_and_validate_receipt(RECEIPT_DIR / "renderer_execution_receipt.json")
    assert validated["artifact_sha256"] == first["artifact_sha256"]


def test_governed_promotion_receipt_is_persisted():
    execution = execute()
    result = promote()
    assert result["decision"] == "PROMOTE"
    assert result["semantic_promotions_allowed"] is True
    assert result["artifact_sha256"] == execution["artifact_sha256"]
    assert (RECEIPT_DIR / "promotion_receipt.json").exists()


def test_tampered_receipt_is_rejected():
    execute()
    source = json.loads((RECEIPT_DIR / "renderer_execution_receipt.json").read_text(encoding="utf-8"))
    source["artifact_sha256"] = "0" * 64
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "tampered.json"
        path.write_text(json.dumps(source), encoding="utf-8")
        try:
            load_and_validate_receipt(path)
        except ValueError as exc:
            assert "content-address validation failed" in str(exc)
        else:
            raise AssertionError("tampered receipt should have been rejected")


if __name__ == "__main__":
    test_execution_receipt_is_content_addressed_and_deterministic()
    test_governed_promotion_receipt_is_persisted()
    test_tampered_receipt_is_rejected()
    print("A8 renderer execution receipt tests: PASS")
