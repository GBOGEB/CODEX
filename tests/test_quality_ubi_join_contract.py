"""Regression guard for multi-producer artifact join location and source binding."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/quality-ubi-testflight.yml"


def _join_workflow() -> str:
    content = WORKFLOW.read_text(encoding="utf-8")
    return content.split("\n  evidence-join:\n", 1)[1]


def test_quality_artifact_download_preserves_nested_quality_archive():
    join = _join_workflow()
    assert (
        "name: codex-quality-census\n"
        "          # The producer archive preserves outputs/quality/ within its root.\n"
        "          path: ."
    ) in join
    assert 'Path("outputs/quality/burndown.json").read_text()' in join


def test_runtime_artifact_download_preserves_nested_archive_path():
    join = _join_workflow()
    assert "name: codex-ubi9-runtime\n          path: ." in join
    assert 'Path("outputs/ubi9/receipt.json").read_text()' in join


def test_join_remains_fail_closed_on_source_identity_and_evidence_hashes():
    join = _join_workflow()
    assert "needs.quality-census.result == 'success'" in join
    assert "needs.ubi9-runtime.result == 'success'" in join
    assert 'quality.get("source_sha") != sha' in join
    assert 'runtime.get("source_sha") != sha' in join
    assert 'quality.get("input_sha256")' in join
    assert 'runtime.get("sha256")' in join
    assert 'raise SystemExit("Refusing mismatched exact-head evidence")' in join
    assert 'raise SystemExit("Refusing unbound quality or runtime evidence")' in join
