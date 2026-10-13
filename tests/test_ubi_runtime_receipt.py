"""Fail-closed checkout identity tests for the UBI runtime receipt."""

import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/ubi_runtime_receipt.py"
EVALUATED = "a" * 40
REVIEWED = "b" * 40


def run_receipt(tmp_path, *, mode="PR_MERGE_TEST", evaluated=EVALUATED):
    output = tmp_path / "outputs/ubi9"
    output.mkdir(parents=True, exist_ok=True)
    (output / "authority.log").write_text("OK\n", encoding="utf-8")
    env = {
        **os.environ,
        "IMAGE_REF": "registry.example/ubi9@sha256:" + "c" * 64,
        "GITHUB_SHA": EVALUATED,
        "EVALUATED_SHA": evaluated,
        "REQUESTED_HEAD_SHA": REVIEWED,
        "CHECKOUT_IDENTITY": mode,
    }
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_synthetic_merge_identity_is_not_exact_head(tmp_path):
    result = run_receipt(tmp_path)
    assert result.returncode == 0, result.stderr
    receipt = json.loads(
        (tmp_path / "outputs/ubi9/receipt.json").read_text(encoding="utf-8")
    )
    identity = receipt["checkout_identity"]
    assert identity["mode"] == "PR_MERGE_TEST"
    assert identity["evaluated_sha"] == EVALUATED
    assert identity["requested_head_sha"] == REVIEWED
    assert identity["exact_head"] is False
    assert receipt["source_sha"] == EVALUATED


def test_inconsistent_exact_head_claim_fails_closed(tmp_path):
    result = run_receipt(tmp_path, mode="EXACT_HEAD")
    assert result.returncode != 0
    assert "Inconsistent checkout identity" in result.stderr


def test_checkout_mismatch_fails_closed(tmp_path):
    result = run_receipt(tmp_path, evaluated="d" * 40)
    assert result.returncode != 0
    assert "Evaluated checkout and GitHub SHA mismatch" in result.stderr
