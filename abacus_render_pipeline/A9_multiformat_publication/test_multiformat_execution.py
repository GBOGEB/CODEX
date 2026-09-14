from __future__ import annotations

import json
import tempfile
from pathlib import Path

from multiformat_execution import REQUIRED_FORMATS, execute
from publication_promotion import evaluate
from receipt_validation import load_and_validate_receipt

HERE = Path(__file__).resolve().parent
RECEIPT = HERE / "receipts" / "multiformat_execution_receipt.json"


def test_multiformat_execution_accepts_all_required_formats() -> None:
    result = execute()
    assert result["decision"] == "accept"
    assert result["cross_format_parity"]["pass"] is True
    assert result["semantic_replay"]["pass"] is True
    assert tuple(result["formats"].keys()) == REQUIRED_FORMATS

    for name in REQUIRED_FORMATS:
        item = result["formats"][name]
        assert item["decision"] == "accept"
        assert item["semantic_parity"]["coverage"] == 1.0
        assert item["telemetry"]["layout_pass"] is True
        assert item["telemetry"]["overflow_pass"] is True

    assert result["formats"]["pptx"]["telemetry"]["geometry_overflow_count"] == 0
    assert result["formats"]["pdf"]["telemetry"]["empty_page_count"] == 0
    assert (
        result["formats"]["html"]["artifact_sha256"]
        == result["formats"]["github_pages"]["artifact_sha256"]
    )


def test_receipt_revalidates_artifact_ssot_and_tuple_hashes() -> None:
    execute()
    validated = load_and_validate_receipt(RECEIPT)
    assert validated["decision"] == "accept"
    assert validated["cross_format_parity"]["pass"] is True


def test_tampered_format_hash_is_rejected() -> None:
    execute()
    source = json.loads(RECEIPT.read_text(encoding="utf-8"))
    source["formats"]["pptx"]["artifact_sha256"] = "0" * 64
    with tempfile.TemporaryDirectory() as temp_dir:
        tampered = Path(temp_dir) / "tampered.json"
        tampered.write_text(json.dumps(source), encoding="utf-8")
        try:
            load_and_validate_receipt(tampered)
        except ValueError as exc:
            assert "artifact sha mismatch" in str(exc)
        else:
            raise AssertionError("tampered multi-format receipt must be rejected")


def test_one_promotion_receipt_binds_all_formats() -> None:
    execute()
    promotion = evaluate()
    assert promotion["decision"] == "PROMOTE"
    assert set(promotion["artifact_sha256"]) == set(REQUIRED_FORMATS)
    assert all(promotion["checks"].values())


if __name__ == "__main__":
    test_multiformat_execution_accepts_all_required_formats()
    test_receipt_revalidates_artifact_ssot_and_tuple_hashes()
    test_tampered_format_hash_is_rejected()
    test_one_promotion_receipt_binds_all_formats()
    print("A9 multi-format execution receipt tests: PASS")
