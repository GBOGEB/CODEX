import copy
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("project_recursive_control", ROOT / "scripts" / "project_recursive_control.py")
prc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prc)

INPUT_PATHS = (prc.KPI_REPORT, prc.VALUE_OBSERVATION, prc.CONTROL_EVENTS, prc.APPLY_POLICY, prc.FEDERATED_INPUTS)


@pytest.fixture
def root(tmp_path):
    """A private copy of every input, so tampering never touches the repository."""
    pins = yaml.safe_load((ROOT / prc.FEDERATED_INPUTS).read_text(encoding="utf-8"))
    for rel in INPUT_PATHS + tuple(Path(p["local_path"]) for p in pins["inputs"]):
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, target)
    return tmp_path


def _fed_path(root):
    pins = yaml.safe_load((root / prc.FEDERATED_INPUTS).read_text(encoding="utf-8"))
    return root / pins["inputs"][0]["local_path"]


def _resolve(document, pointer):
    node = document
    for part in pointer.strip("/").split("/"):
        node = node[int(part)] if isinstance(node, list) else node[part]
    return node


def _data(**overrides):
    base = {
        "hub_convergence": {"crosschecks": [], "repos": {}},
        "kpi_report": {"checks": [], "kpis": [], "red_kpis": []},
        "value_observation": {"next_control_action": "PRESERVE_CONTROL",
                              "unregistered_asset_count": 0, "tested_orphan_count": 0},
    }
    base.update(overrides)
    return base


def _kpi(kpi_id, band, unlock=None):
    return {"id": kpi_id, "dimension": "execution", "name": kpi_id, "value": 1, "target": 2,
            "band": band, "unlock": unlock}


# --------------------------------------------------------------------------- committed projection

def test_committed_projection_is_fresh():
    assert prc.main(["--check"]) == 0


def test_projection_is_deterministic(root):
    assert prc.render(prc.build(root)) == prc.render(prc.build(root))


def test_projection_never_mutates_or_transfers_authority():
    projection = prc.build()
    assert projection["mutation"] is False
    assert projection["control_events_written"] is False
    assert projection["authority_transfer"] is False
    assert projection["formal_credit_delta"] == 0 and projection["engineering_credit_delta"] == 0


def test_every_source_pointer_resolves_into_its_input():
    data, _ = prc.load_inputs()
    projection = prc.build()
    for horizon in prc.HORIZONS:
        for item in projection["horizons"][horizon]:
            assert item["sources"], item["id"]
            for source in item["sources"]:
                _resolve(data[source["input"]], source["pointer"])


def test_ranks_are_contiguous_per_horizon():
    projection = prc.build()
    for horizon in prc.HORIZONS:
        assert [i["rank"] for i in projection["horizons"][horizon]] == list(
            range(1, len(projection["horizons"][horizon]) + 1))


def test_federated_input_is_recorded_with_its_pin():
    projection = prc.build()
    fed = [m for m in projection["inputs"] if m["origin"] == "FEDERATED"]
    assert [m["repository"] for m in fed] == ["GBOGEB/pipeline-automation-hub"]
    assert len(fed[0]["revision"]) == 40


def test_proof_receipt_binds_the_registered_nodes():
    receipt = json.loads((ROOT / "mission_control/mycelium/receipts/RECURSIVE_CONTROL_RCH04_PR1163_PROOF.json")
                         .read_text(encoding="utf-8"))
    registry = yaml.safe_load((ROOT / "mission_control/mycelium/executable_integration_registry.yaml")
                              .read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in registry["nodes"]}
    run = receipt["proof_runs"]["missioncontrol_mycelium_exact_head"]
    assert run["conclusion"] == "success" and run["checkout"] == "pull_request.head.sha"
    evidence = f"run_{run['run']}_job_{run['job']}"
    for node_id in receipt["proven_nodes"]:
        node = nodes[node_id]
        assert "PENDING" not in node["current_state"], node_id
        assert node["exact_revision"] == receipt["node_revision_sha"], node_id
        assert evidence in node["test_proof_evidence"], node_id
    path = next(p for p in registry["integration_paths"] if p["id"] == "missioncontrol_recursive_control_rch04")
    assert path["executed"] and receipt["receipt_id"] in path["evidence"] and evidence in path["evidence"]
    assert receipt["mutation_enabled"] is False and receipt["projection_mutates_control_events"] is False


def test_control_manifest_declares_the_projection():
    manifest = yaml.safe_load((ROOT / "mission_control/mycelium/control_manifest.yaml").read_text(encoding="utf-8"))
    rc = manifest["recursive_control"]
    assert rc["projection"] == prc.OUTPUT.as_posix()
    assert rc["builder"] == "scripts/project_recursive_control.py"
    assert rc["mutation_enabled"] is False


# --------------------------------------------------------------------------- fail closed

def test_does_not_write_control_events(root):
    before = hashlib.sha256((root / prc.CONTROL_EVENTS).read_bytes()).hexdigest()
    prc.build(root)
    assert hashlib.sha256((root / prc.CONTROL_EVENTS).read_bytes()).hexdigest() == before


def test_tampered_federated_input_fails_closed(root):
    fed = _fed_path(root)
    fed.write_bytes(fed.read_bytes().replace(b'"HOLD"', b'"ADMITTED"', 1))
    with pytest.raises(prc.ProjectionError, match="does not match pin"):
        prc.build(root)


def test_missing_federated_input_fails_closed(root):
    _fed_path(root).unlink()
    with pytest.raises(prc.ProjectionError, match="missing input"):
        prc.build(root)


def test_missing_local_input_fails_closed(root):
    (root / prc.KPI_REPORT).unlink()
    with pytest.raises(prc.ProjectionError, match="missing input"):
        prc.build(root)


def test_unexpected_federated_schema_fails_closed(root):
    pins_path = root / prc.FEDERATED_INPUTS
    pins = yaml.safe_load(pins_path.read_text(encoding="utf-8"))
    pins["inputs"][0]["expected_schema_version"] = "9.9"
    pins_path.write_text(yaml.safe_dump(pins), encoding="utf-8")
    with pytest.raises(prc.ProjectionError, match="schema_version"):
        prc.build(root)


def test_crlf_copy_matches_pin(root):
    fed = _fed_path(root)
    fed.write_bytes(fed.read_bytes().replace(b"\n", b"\r\n"))
    prc.build(root)


def test_enabled_apply_is_reported_but_still_not_used(root):
    policy_path = root / prc.APPLY_POLICY
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    policy["mutation_enabled"] = True
    policy_path.write_text(yaml.safe_dump(policy), encoding="utf-8")
    projection = prc.build(root)
    assert projection["apply_state"] == "ENABLED_NOT_USED"
    assert projection["mutation"] is False


def test_check_reports_stale_projection(root, monkeypatch, capsys):
    monkeypatch.setattr(prc, "ROOT", root)
    assert prc.main([]) == 0
    out = root / prc.OUTPUT
    out.write_text(out.read_text(encoding="utf-8").replace('"current"', '"now"', 1), encoding="utf-8")
    assert prc.main(["--check"]) == 1
    assert "STALE" in capsys.readouterr().err


# --------------------------------------------------------------------------- ranking rules

def test_rc01_failed_federated_check_is_current():
    data = _data(hub_convergence={"crosschecks": [{"id": "C18_x", "result": "FAIL", "detail": "d"},
                                                  {"id": "C19_y", "result": "WARN", "detail": "w"}],
                                  "repos": {}})
    items = prc.derive_items(data)
    assert [(i["id"], i["rule"]) for i in items] == [("FEDERATED_C18_X", "RC-01")]


def test_rc02_failed_kpi_check_is_current():
    data = _data(kpi_report={"checks": [{"id": "CHK-01", "status": "FAIL", "name": "n"}], "kpis": [], "red_kpis": []})
    assert [i["rule"] for i in prc.derive_items(data)] == ["RC-02"]


def test_rc03_only_starved_repos_that_notify():
    repos = {
        "A": {"plateau": {"state": "STARVED"}, "notify": True},
        "B": {"plateau": {"state": "STARVED"}, "notify": False},
        "C": {"plateau": {"state": "STABLE_HOLD"}, "notify": True},
    }
    items = prc.derive_items(_data(hub_convergence={"crosschecks": [], "repos": repos}))
    assert len(items) == 1 and items[0]["rule"] == "RC-03"
    assert [s["pointer"] for s in items[0]["sources"]] == ["/repos/A/plateau"]


def test_rc04_preserve_control_adds_nothing():
    assert prc.derive_items(_data()) == []
    data = _data(value_observation={"next_control_action": "CLASSIFY_TESTED_ORPHANS",
                                    "unregistered_asset_count": 0, "tested_orphan_count": 2})
    assert [i["id"] for i in prc.derive_items(data)] == ["CLASSIFY_TESTED_ORPHANS"]


def test_kpi_rules_split_by_band_and_unlock():
    kpis = [_kpi("K-1", "RED", "do x"), _kpi("K-2", "RED"), _kpi("K-3", "AMBER", "do y"),
            _kpi("K-4", "AMBER"), _kpi("K-5", "GREEN", "done")]
    red = [{"id": k["id"], "unlock": k["unlock"]} for k in kpis if k["band"] == "RED"]
    items = prc.derive_items(_data(kpi_report={"checks": [], "kpis": kpis, "red_kpis": red}))
    assert [(i["id"], i["rule"]) for i in items] == [("KPI_K-1", "RC-05"), ("KPI_K-2", "RC-06"), ("KPI_K-3", "RC-07")]
    assert items[0]["unlock"] == "do x" and "unlock" not in items[1]


def test_rank_places_rules_in_their_horizons():
    items = [{"id": "a", "rule": "RC-06"}, {"id": "b", "rule": "RC-01"}, {"id": "c", "rule": "RC-05"}]
    horizons = prc.rank(copy.deepcopy(items))
    assert [i["id"] for i in horizons["current"]] == ["b"]
    assert [i["id"] for i in horizons["mid"]] == ["c"]
    assert [i["id"] for i in horizons["long"]] == ["a"]


def test_manual_horizon_items_are_retained_not_dropped():
    derived = {"current": [{"id": "X"}], "mid": [{"id": "SHARED"}], "long": []}
    events = {"snapshot_at": "t", "horizons": {"current": [{"id": "SHARED"}], "mid": [], "long": [{"id": "STEER"}]}}
    delta = prc.horizon_delta(derived, events)
    assert delta == {"control_events_snapshot_at": "t", "derived_only": ["X"],
                     "shared": ["SHARED"], "manual_only_retained": ["STEER"]}


def test_pages_copy_matches_canonical_projection():
    canonical = (ROOT / prc.OUTPUT).read_text(encoding="utf-8")
    pages = (ROOT / prc.PAGES_OUTPUT).read_text(encoding="utf-8")
    assert json.loads(canonical) == json.loads(pages)
