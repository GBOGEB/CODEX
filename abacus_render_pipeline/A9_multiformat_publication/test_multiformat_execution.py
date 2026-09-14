from __future__ import annotations

import json
import tempfile
from pathlib import Path

from multiformat_execution import REQUIRED_FORMATS, execute
from publication_promotion import evaluate
from receipt_validation import (
    load_and_validate_hosted_pages_receipt,
    load_and_validate_receipt,
)

HERE = Path(__file__).resolve().parent
RECEIPT = HERE / "receipts" / "multiformat_execution_receipt.json"


def _synthetic_hosted_receipt(result: dict) -> dict:
    pages = result["formats"]["github_pages"]
    return {
        "receipt_version": "A9.3-PAGES",
        "publication_id": result["publication_id"],
        "source_commit": result["source_commit"],
        "page_url": "https://example.invalid/CODEX/",
        "fetched_url": "https://example.invalid/CODEX/",
        "http_status": 200,
        "deployment_run_id": "test-run",
        "local_artifact_relpath": pages["artifact_relpath"],
        "local_artifact_sha256": pages["artifact_sha256"],
        "hosted_sha256": pages["artifact_sha256"],
        "hosted_bytes": pages["artifact_bytes"],
        "semantic_parity": pages["semantic_parity"],
        "network_fetch_count": 2,
        "fetch_method": "synthetic_test_fixture_no_network",
        "required_consecutive_matches": 2,
        "propagation_observations": [
            {"attempt": 1, "hash_match": True, "semantic_pass": True, "consecutive_governed_matches": 1},
            {"attempt": 2, "hash_match": True, "semantic_pass": True, "consecutive_governed_matches": 2},
        ],
        "fetched_at_utc": "2026-09-14T00:00:00+00:00",
        "decision": "accept",
    }


def test_multiformat_execution_accepts_all_required_format_candidates() -> None:
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
    assert result["formats"]["github_pages"]["telemetry"]["hosted_deployment_required"] is True
    assert result["formats"]["github_pages"]["telemetry"]["hosted_deployment_proven"] is False
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


def test_atomic_promotion_withholds_without_hosted_pages_evidence() -> None:
    execute()
    with tempfile.TemporaryDirectory() as temp_dir:
        missing = Path(temp_dir) / "not-created.json"
        promotion = evaluate(hosted_pages_receipt=missing, refetch_hosted=False)
    assert promotion["decision"] == "WITHHOLD"
    assert promotion["checks"]["github_pages_hosted_receipt_present"] is False
    assert promotion["checks"]["github_pages_hosted_receipt_valid"] is False


def test_hosted_pages_receipt_unlocks_one_atomic_promotion() -> None:
    result = execute()
    with tempfile.TemporaryDirectory() as temp_dir:
        hosted_path = Path(temp_dir) / "hosted.json"
        hosted_path.write_text(
            json.dumps(_synthetic_hosted_receipt(result)), encoding="utf-8"
        )
        hosted = load_and_validate_hosted_pages_receipt(
            hosted_path,
            RECEIPT,
            refetch=False,
        )
        assert hosted["decision"] == "accept"
        assert hosted["required_consecutive_matches"] == 2
        promotion = evaluate(
            hosted_pages_receipt=hosted_path,
            refetch_hosted=False,
        )
    assert promotion["decision"] == "PROMOTE"
    assert set(promotion["artifact_sha256"]) == set(REQUIRED_FORMATS)
    assert promotion["checks"]["github_pages_hosted_receipt_valid"] is True
    assert promotion["hosted_pages"]["hosted_sha256"] == result["formats"]["github_pages"]["artifact_sha256"]


def test_single_observation_hosted_receipt_is_rejected() -> None:
    result = execute()
    hosted = _synthetic_hosted_receipt(result)
    hosted["required_consecutive_matches"] = 1
    with tempfile.TemporaryDirectory() as temp_dir:
        hosted_path = Path(temp_dir) / "hosted-single-observation.json"
        hosted_path.write_text(json.dumps(hosted), encoding="utf-8")
        promotion = evaluate(
            hosted_pages_receipt=hosted_path,
            refetch_hosted=False,
        )
    assert promotion["decision"] == "REJECT"
    assert promotion["checks"]["github_pages_hosted_receipt_valid"] is False
    assert "stable consecutive convergence" in str(promotion["hosted_pages_receipt_error"])


def test_tampered_hosted_pages_hash_rejects_promotion() -> None:
    result = execute()
    hosted = _synthetic_hosted_receipt(result)
    hosted["hosted_sha256"] = "0" * 64
    with tempfile.TemporaryDirectory() as temp_dir:
        hosted_path = Path(temp_dir) / "hosted-tampered.json"
        hosted_path.write_text(json.dumps(hosted), encoding="utf-8")
        promotion = evaluate(
            hosted_pages_receipt=hosted_path,
            refetch_hosted=False,
        )
    assert promotion["decision"] == "REJECT"
    assert promotion["checks"]["github_pages_hosted_receipt_valid"] is False
    assert "do not match governed deployment candidate" in str(
        promotion["hosted_pages_receipt_error"]
    )


if __name__ == "__main__":
    test_multiformat_execution_accepts_all_required_format_candidates()
    test_receipt_revalidates_artifact_ssot_and_tuple_hashes()
    test_tampered_format_hash_is_rejected()
    test_atomic_promotion_withholds_without_hosted_pages_evidence()
    test_hosted_pages_receipt_unlocks_one_atomic_promotion()
    test_single_observation_hosted_receipt_is_rejected()
    test_tampered_hosted_pages_hash_rejects_promotion()
    print("A9.3 multi-format + stable hosted Pages receipt tests: PASS")
