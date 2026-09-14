from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from semantic_acceptance_gate import DEFAULT_RECEIPT, evaluate
from semantic_delta_replay import run as run_replay

ROOT = Path(__file__).resolve().parents[2]
A8 = ROOT / "abacus_render_pipeline" / "A8_renderer_execution_receipt"
sys.path.insert(0, str(A8))

from renderer_execution import execute


def test_replay_exact_sequence():
    result = run_replay()
    assert result["status"] == "PASS"
    assert result["final_state"]["exact_TUP_0001_to_TUP_0008"] is True
    assert result["final_state"]["visited_count"] >= 8


def test_renderer_acceptance_requires_verified_receipt():
    execute()
    result = evaluate()
    assert result["status"] == "PASS"
    assert result["semantic_promotions_allowed"] is True
    assert all(result["checks"].values())
    assert result["receipt_summary"]["decision"] == "accept"


def test_tampered_renderer_receipt_blocks_promotion():
    execute()
    receipt = json.loads(DEFAULT_RECEIPT.read_text(encoding="utf-8"))
    receipt["artifact_sha256"] = "0" * 64
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "tampered_receipt.json"
        path.write_text(json.dumps(receipt), encoding="utf-8")
        result = evaluate(path)
    assert result["status"] == "FAIL"
    assert result["semantic_promotions_allowed"] is False
    assert result["checks"]["renderer_execution_receipt_valid"] is False


if __name__ == "__main__":
    test_replay_exact_sequence()
    test_renderer_acceptance_requires_verified_receipt()
    test_tampered_renderer_receipt_blocks_promotion()
    print("A8 semantic replay and receipt acceptance tests: PASS")
