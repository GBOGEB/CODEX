"""Fail-closed checkout identity tests for the UBI runtime receipt."""

import json
import hashlib

import pytest
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/ubi_runtime_receipt.py"
EVALUATED = "a" * 40
REVIEWED = "b" * 40


def run_receipt(tmp_path, *, mode="PR_MERGE_TEST", evaluated=EVALUATED,
                requested=REVIEWED):
    output = tmp_path / "outputs/ubi9"
    output.mkdir(parents=True, exist_ok=True)
    (output / "authority.log").write_text("OK\n", encoding="utf-8")
    env = {
        **os.environ,
        "IMAGE_REF": "registry.example/ubi9@sha256:" + "c" * 64,
        "GITHUB_SHA": EVALUATED,
        "EVALUATED_SHA": evaluated,
        "REQUESTED_HEAD_SHA": requested,
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


def test_genuine_exact_head_receipt(tmp_path):
    result = run_receipt(tmp_path, mode="EXACT_HEAD", requested=EVALUATED)
    assert result.returncode == 0, result.stderr
    receipt = json.loads(
        (tmp_path / "outputs/ubi9/receipt.json").read_text(encoding="utf-8")
    )
    assert receipt["checkout_identity"]["exact_head"] is True
    assert receipt["checkout_identity"]["mode"] == "EXACT_HEAD"


@pytest.mark.parametrize("filename", [
    "rex-rollup.json", "rex-rollup.exitcode", "rex-rollup.duration_ms",
])
def test_partial_pipeline_receipt_rejected(tmp_path, filename):
    output = tmp_path / "outputs/ubi9"
    output.mkdir(parents=True)
    (output / filename).write_text("{}", encoding="utf-8")
    result = run_receipt(tmp_path)
    assert result.returncode != 0
    assert "partial REX pipeline receipt" in result.stderr
    assert not (output / "receipt.json").exists()


@pytest.mark.parametrize(("exit_code", "duration", "payload"), [
    ("1", "25", "{}"),
    ("0", "-1", "{}"),
    ("0", "25", "[]"),
])
def test_nonpassing_rex_pipeline_evidence_rejected(
    tmp_path, exit_code, duration, payload
):
    output = tmp_path / "outputs/ubi9"
    output.mkdir(parents=True)
    (output / "rex-rollup.json").write_text(payload, encoding="utf-8")
    (output / "rex-rollup.exitcode").write_text(exit_code, encoding="utf-8")
    (output / "rex-rollup.duration_ms").write_text(duration, encoding="utf-8")
    result = run_receipt(tmp_path)
    assert result.returncode != 0
    assert "invalid REX output pipeline execution" in result.stderr
    assert not (output / "receipt.json").exists()


def test_successful_rex_pipeline_output_is_content_bound(tmp_path):
    output = tmp_path / "outputs/ubi9"
    output.mkdir(parents=True)
    payload = '{"advisory": true}'
    (output / "rex-rollup.json").write_text(payload, encoding="utf-8")
    (output / "rex-rollup.exitcode").write_text("0", encoding="utf-8")
    (output / "rex-rollup.duration_ms").write_text("27", encoding="utf-8")
    result = run_receipt(tmp_path)
    assert result.returncode == 0, result.stderr
    receipt = json.loads((output / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["output_pipeline"]["sha256"] == hashlib.sha256(
        payload.encode("utf-8")
    ).hexdigest()
    assert receipt["output_pipeline"]["duration_ms"] == 27
    assert receipt["output_pipeline"]["exit_code"] == 0
    assert receipt["checkout_identity"]["exact_head"] is False


@pytest.mark.parametrize("invalid_sha", ["bad", "A" * 40, "f" * 39])
def test_invalid_requested_sha_rejected(tmp_path, invalid_sha):
    result = run_receipt(tmp_path, requested=invalid_sha)
    assert result.returncode != 0
    assert "Invalid 40-character checkout SHA" in result.stderr
