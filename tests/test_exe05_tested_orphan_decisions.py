"""EXE-05 (unregistered tested orphans): measured value and recorded decisions.

EXE-05 is ``classification_counts/TESTED_ORPHAN`` from
scripts/classify_executable_registration_debt.py over the *unregistered*
inventory. The registered-population ``tested_orphans`` list in
executable_value_report.json is a different measure (EXE-04).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from scripts import classify_executable_registration_debt as debt
from scripts import measure_mycelium_kpis as kpis
from scripts.validate_executable_integration_value import (
    CONTRACT,
    REGISTRY,
    SCHEMA,
    load_yaml,
    validate_registry,
)

ROOT = Path(__file__).resolve().parents[1]
BATCH = "MYCELIUM_EXE05_TESTED_ORPHAN_BATCH_3"
MANIFEST = yaml.safe_load(kpis.MANIFEST.read_text(encoding="utf-8"))
EXE05 = next(k for k in MANIFEST["kpis"] if k["id"] == "EXE-05")

# The 15 assets EXE-05 counted at ae430f01 and the decision taken for each.
DECISIONS = {
    "scripts/missioncontrol_federated_crosswalk.py": "REGISTER",
    "scripts/mip_health_selfheal_probe.py": "REGISTER",
    "scripts/build_incubator_index.py": "LIBRARY_ONLY",
    "scripts/code_purple_census_delta.py": "LIBRARY_ONLY",
    "scripts/code_purple_iteration.py": "LIBRARY_ONLY",
    "scripts/export_incubator_runtime.py": "LIBRARY_ONLY",
    "scripts/extract_themes.py": "LIBRARY_ONLY",
    "scripts/g3a_protocol.py": "LIBRARY_ONLY",
    "scripts/missioncontrol_bounded_apply.py": "LIBRARY_ONLY",
    "scripts/parse_chat_tuple.py": "LIBRARY_ONLY",
    "scripts/qps_sideload_v1.py": "LIBRARY_ONLY",
    "scripts/refresh_model_package_index.py": "LIBRARY_ONLY",
    "scripts/render_portal_tiles.py": "LIBRARY_ONLY",
    "scripts/validate_ssot_style_bridge.py": "LIBRARY_ONLY",
    "scripts/validate_tuple.py": "LIBRARY_ONLY",
}


def _registry_report():
    contract = load_yaml(CONTRACT)
    registry = load_yaml(REGISTRY)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors, report = validate_registry(contract, registry, schema)
    assert errors == []
    return registry, report


def _workflow_runs(path: str, executable_text: str) -> bool:
    return debt._runs_asset(path, executable_text)


def _exe05(payload: dict) -> dict:
    return kpis.evaluate_kpi(EXE05, {"debt": payload}, {})


def test_exe05_measures_zero_live_and_in_committed_report():
    payload = debt.classify()
    assert payload["classification_counts"]["TESTED_ORPHAN"] == 0
    row = _exe05(payload)
    assert row["status"] == "MEASURED"
    assert row["value"] == 0
    assert row["band"] == "GREEN"

    committed = json.loads(kpis.OUTPUT.read_text(encoding="utf-8"))
    (exe05,) = [k for k in committed["kpis"] if k["id"] == "EXE-05"]
    assert exe05["value"] == 0
    assert exe05["band"] == "GREEN"
    assert "EXE-05" not in {r["id"] for r in committed["red_kpis"]}


def test_every_exe05_decision_is_recorded_in_the_registry():
    registry, report = _registry_report()
    by_path = {n["path"]: n for n in registry["nodes"]}
    batch = [n for n in registry["nodes"] if n.get("registration_batch") == BATCH]
    decided = {n["path"]: n["exe05_decision"] for n in batch if n["type"] != "WORKFLOW"}
    assert decided == DECISIONS

    edges = registry["edges"]
    executable_text = debt._executable_workflow_text(debt.WORKFLOWS)
    for path, decision in DECISIONS.items():
        node = by_path[path]
        stem = Path(path).stem
        assert node["tested"] is True, path
        assert node["value_scope"] == "V0_TESTED_ONLY", path
        assert node["value_evidence"] == [], path
        tests = [t for t in node["test_proof_evidence"] if t.startswith("tests/")]
        assert tests, path
        assert any(stem in (ROOT / t).read_text(encoding="utf-8") for t in tests), path
        assert node["id"] not in report["tested_orphans"], path
        touching = [e for e in edges if node["id"] in (e["from"], e["to"])]
        if decision == "REGISTER":
            assert node["current_state"] == "REGISTERED_CONNECTED_VALUE_WITHHELD", path
            assert not node.get("intentional_no_consumer"), path
            (edge,) = touching
            assert edge["to"] == node["id"] and edge["type"] == "TRIGGERED_BY", path
            assert edge["evidence"].startswith("run_"), path
            assert edge["evidence"] in node["test_proof_evidence"], path
            assert node["id"] not in report["library_reference_only"], path
        else:
            assert node["current_state"] == "LIBRARY_REFERENCE_ONLY", path
            assert node["intentional_no_consumer"] is True, path
            assert node["library_only_reason"].strip(), path
            assert touching == [], path
            assert node["id"] in report["library_reference_only"], path
            # Library-only must stay true: no workflow step may run it.
            assert not _workflow_runs(path, executable_text), path


def test_registered_crosswalk_is_run_by_its_registered_workflow():
    registry, _ = _registry_report()
    node_map = {n["id"]: n for n in registry["nodes"]}
    workflow = node_map["reg3_federated_launchpad_qa_workflow"]
    text = (ROOT / workflow["path"]).read_text(encoding="utf-8")
    assert re.search(r"python -m scripts\.missioncontrol_federated_crosswalk\b", text)
    runner = (ROOT / "scripts" / "mip_repo_self_index.py").read_text(encoding="utf-8")
    assert '"scripts/mip_health_selfheal_probe.py"' in runner
    assert "run_health_selfheal_probe" in runner


def test_new_unregistered_tested_module_makes_exe05_non_zero(tmp_path, monkeypatch):
    sentinel = "scripts/exe05_sentinel_new_module.py"
    report = json.loads(debt.REPORT.read_text(encoding="utf-8"))
    assert sentinel not in report["inventory"]["unregistered_assets"]
    report["inventory"]["unregistered_assets"].append(sentinel)
    report_path = tmp_path / "executable_value_report.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")

    real_stems = debt._test_stems

    def stems_with_sentinel(tests_root):
        return real_stems(tests_root) | {"exe05_sentinel_new_module"}

    monkeypatch.setattr(debt, "_test_stems", stems_with_sentinel)
    payload = debt.classify(report_path=report_path)
    orphans = [
        r["asset"]
        for r in payload["candidates"]
        if r["classification"] == "TESTED_ORPHAN"
    ]
    assert orphans == [sentinel]
    row = _exe05(payload)
    assert row["value"] == 1
    assert row["band"] != "GREEN"
