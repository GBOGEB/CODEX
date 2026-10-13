"""Unit evidence tests for advisory diagnostic rollup."""
import json
import subprocess
import sys

SCRIPT = "scripts/diagnostic_coverage_rollup.py"
SHA = "a" * 40
OTHER = "b" * 40


def run(tmp_path, *args):
    out = tmp_path / "out.json"
    result = subprocess.run([sys.executable, SCRIPT, "--source-sha", SHA,
                             "--out", str(out), *args], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return json.loads(out.read_text())


def test_unknown_not_promoted(tmp_path):
    receipt = run(tmp_path)
    assert receipt["metrics"]["verified_surfaces"] == 0
    assert all(v["status"] == "UNKNOWN" for v in receipt["coverage"].values())
    assert receipt["metrics"]["mean_queue_wait_seconds"] is None


def test_stale_runtime_is_historical(tmp_path):
    path = tmp_path / "runtime.json"
    path.write_text(json.dumps({"source_sha": OTHER, "outcomes": {"a": "PASS"},
                                "image_digest": "sha256:abc"}))
    receipt = run(tmp_path, "--runtime", str(path))
    assert receipt["coverage"]["runtime"]["status"] == "HISTORICAL"


def test_current_quality_counts_only_observed(tmp_path):
    path = tmp_path / "quality.json"
    path.write_text(json.dumps({"source_sha": SHA, "current": {"total": 2},
        "diagnostics": [{"tool": "ruff"}, {"tool": "pyright"}]}))
    receipt = run(tmp_path, "--quality", str(path))
    q = receipt["coverage"]["quality"]
    assert (q["ruff_findings"], q["pyright_findings"]) == (1, 1)
    assert q["eligible_files"] is None
    assert receipt["metrics"]["verified_surfaces"] == 1


def test_runtime_failure_not_pass(tmp_path):
    path = tmp_path / "runtime.json"
    path.write_text(json.dumps({"source_sha": SHA, "outcomes": {"entry": "FAIL"},
                                "image_digest": "sha256:abc"}))
    receipt = run(tmp_path, "--runtime", str(path))
    assert receipt["coverage"]["runtime"]["status"] == "FAILED"
