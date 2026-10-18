"""The L1 results page is a faithful, current rendering of the gate manifest and the committed CI record."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def _module(name):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_committed_page_is_current():
    page = (REPO_ROOT / "docs/gistau-ch15/l1_validation.html").read_text(encoding="utf-8")
    assert page == _module("render_l1_validation").render(), "regenerate: python tools/render_l1_validation.py"


def test_record_matches_gate_coverage():
    gate = yaml.safe_load((REPO_ROOT / "governance/physics/CH15_CANONICAL_VALIDATION.yaml").read_text(encoding="utf-8"))
    record = json.loads((REPO_ROOT / "docs/gistau-ch15/data/l1_validation_results.json").read_text(encoding="utf-8"))["record"]
    assert record["examples_checked"] == len(gate["checked"])
    assert record["examples_source_check_required"] == sorted(gate.get("source_check_required", {}))
    assert record["examples_excluded"] == len(gate["excluded"])
    ids = {r["example_id"] for r in record["rows"]}
    assert set(gate["checked"]) <= ids
    assert not ids & set(gate["excluded"])


def test_page_never_shows_open_or_excluded_examples_as_passing():
    page = (REPO_ROOT / "docs/gistau-ch15/l1_validation.html").read_text(encoding="utf-8")
    gate = yaml.safe_load((REPO_ROOT / "governance/physics/CH15_CANONICAL_VALIDATION.yaml").read_text(encoding="utf-8"))
    for eid in list(gate.get("source_check_required", {})) + list(gate["excluded"]):
        card = page.split(f'id="{eid}"', 1)[1].split("</article>", 1)[0]
        assert 'class="badge pass"' not in card


def test_compare_record_detects_drift():
    tool = _module("ch15_canonical_validation")
    recorded = json.loads((REPO_ROOT / "docs/gistau-ch15/data/l1_validation_results.json").read_text(encoding="utf-8"))
    fresh = json.loads(json.dumps(recorded["record"]))
    assert tool.compare_record(fresh, recorded) == []
    fresh["rows"][0]["computed"] *= 1.001
    assert any(p.startswith("RECORD_DRIFT") for p in tool.compare_record(fresh, recorded))
    assert tool.compare_record(fresh, {"record": "PENDING_FIRST_CI_RECORD"})[0].startswith("RECORD_PENDING")
