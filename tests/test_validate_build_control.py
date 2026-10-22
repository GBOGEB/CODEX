from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "validate_build_control.py"
spec = importlib.util.spec_from_file_location("validate_build_control", SCRIPT)
bc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bc)


@pytest.fixture()
def pack(tmp_path: Path) -> Path:
    """Copy the handover pack, its manifest and downstream docs into a scratch root."""
    manifest = bc._manifest(REPO_ROOT)
    rels = set(bc._pack_paths(manifest)) | set(bc.REQUIRED) | {bc.BASELINE}
    rels |= set(bc.EXTERNAL_ANCHORS.values())
    rels |= {p.relative_to(REPO_ROOT) for g in bc.DOWNSTREAM_GLOBS for p in REPO_ROOT.glob(g)}
    for rel in rels:
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / rel, dst)
    return tmp_path


def _edit(root: Path, rel: Path, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert old in text, f"fixture drift: {old!r} not in {rel}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _report(root: Path) -> tuple[int, dict]:
    out = root / "out" / "report.json"
    rc = bc.validate(root, out)
    return rc, json.loads(out.read_text(encoding="utf-8"))


def _check(report: dict, name: str) -> dict:
    return next(c for c in report["checks"] if c["name"] == name)


# --- positive -----------------------------------------------------------------


def test_committed_repo_passes_and_reports_kpis(tmp_path: Path) -> None:
    out = tmp_path / "report.json"
    assert bc.validate(REPO_ROOT, out) == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["status"] == "passed"
    assert {c["name"] for c in report["checks"]} == {f.__name__.removeprefix("check_") for f in bc.CHECKS}
    assert _check(report, "diff_decisions")["kpis"]["changes_total"] >= 12
    assert _check(report, "rtm_consistency")["kpis"]["coverage_pct"] == 100.0


def test_report_is_idempotent(pack: Path) -> None:
    _, first = _report(pack)
    _, second = _report(pack)
    assert first == second


def test_downstream_drop_below_ratchet_still_passes(pack: Path) -> None:
    _edit(pack, Path("Book_Master.md"), "WCS-HP", "WCS.HP")
    rc, report = _report(pack)
    assert rc == 0
    down = _check(report, "rename_downstream")["kpis"]
    assert down["legacy_hits"] < down["ratchet_baseline"]


# --- negative (blocking) ------------------------------------------------------


def test_missing_decision_fails(pack: Path) -> None:
    _edit(pack, bc.MASTER_DIFF, "WCS.R) +] | ✅ |", "WCS.R) +] |  |")
    rc, report = _report(pack)
    assert rc == 1
    assert "diff_decisions" in report["blocking_failed"]
    assert any(e.startswith("C01:") for e in _check(report, "diff_decisions")["errors"])


def test_pending_decision_is_valid_but_lowers_approval(pack: Path) -> None:
    _edit(pack, bc.MASTER_DIFF, "WCS.R) +] | ✅ |", "WCS.R) +] | ⏳ |")
    rc, report = _report(pack)
    kpis = _check(report, "diff_decisions")["kpis"]
    assert rc == 0
    assert kpis["pending"] == 1 and kpis["approved_pct"] < 100.0


def test_rtm_id_drift_fails(pack: Path) -> None:
    _edit(pack, bc.RTM_CSV, "RTM.009,", "RTM.099,")
    rc, report = _report(pack)
    errors = _check(report, "rtm_consistency")["errors"]
    assert rc == 1
    assert any("RTM.009" in e for e in errors) and any("RTM.099" in e for e in errors)


def test_rtm_shall_text_drift_fails(pack: Path) -> None:
    _edit(pack, bc.REQUIREMENTS_JSON, "no PTFE or elastomer", "PTFE allowed")
    rc, report = _report(pack)
    assert rc == 1
    assert any("RTM.001" in e for e in _check(report, "rtm_consistency")["errors"])


def test_unresolved_itp_reference_fails(pack: Path) -> None:
    _edit(pack, bc.ITP_CSV, "PROC_DBBA_Purge,", "PROC_DOES_NOT_EXIST,")
    rc, report = _report(pack)
    assert rc == 1
    assert "trace_references" in report["blocking_failed"]


def test_manifest_listing_missing_file_fails(pack: Path) -> None:
    (pack / "07_ops" / "OCD" / "OCD.md").unlink()
    rc, report = _report(pack)
    assert rc == 1
    assert "07_ops/OCD/OCD.md: listed in manifest but missing" in _check(report, "glob_manifest")["errors"]


def test_baseline_version_mismatch_fails(pack: Path) -> None:
    _edit(pack, bc.REQUIREMENTS_JSON, '"baseline": "1.3.0"', '"baseline": "1.4.0"')
    rc, report = _report(pack)
    assert rc == 1
    assert "baseline_meta" in report["blocking_failed"]


def test_legacy_name_in_pack_fails(pack: Path) -> None:
    _edit(pack, Path("07_ops/OCD/OCD.md"), "\n", "\nRelief to WCS-LP.\n")
    rc, report = _report(pack)
    assert rc == 1
    assert _check(report, "rename_pack")["kpis"]["legacy_hits"] == 1


def test_ledger_files_are_exempt_from_rename_check(pack: Path) -> None:
    rc, report = _report(pack)
    assert rc == 0
    assert all(p.as_posix() not in str(_check(report, "rename_pack")) for p in bc.RENAME_LEDGER)


def test_missing_required_file_fails(pack: Path) -> None:
    (pack / bc.RTM_CSV).unlink()
    assert bc.validate(pack, None) == 1


# --- ratchet (report-only) ----------------------------------------------------


def test_downstream_regression_is_reported_but_not_blocking(pack: Path) -> None:
    _edit(pack, Path("Book_Master.md"), "\n", "\nQRB-A and QRB-B.\n")
    rc, report = _report(pack)
    down = _check(report, "rename_downstream")
    assert rc == 0
    assert down["status"] == "failed" and down["blocking"] is False
    assert "rename_downstream" not in report["blocking_failed"]


def test_word_boundaries_do_not_overcount() -> None:
    pattern = bc._legacy_pattern(REPO_ROOT)
    assert pattern.findall("WCS-LP, QRB-A/B, WCS-LPX, XQRB-A, QRB.A") == ["WCS-LP", "QRB-A"]
