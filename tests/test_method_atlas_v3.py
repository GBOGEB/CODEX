"""Method Atlas v3: seed contract, derivation rules and projection parity."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/method_atlas"))
import build_method_atlas as atlas  # noqa: E402

SEED = ROOT / "tools/method_atlas/method_atlas_seed.yaml"
OUT = ROOT / "docs/method_atlas"
LANES = {"GOGREEN", "MAROON", "JADE", "EVERRED", "CPURPLE"}


def seed():
    return yaml.safe_load(SEED.read_text(encoding="utf-8"))


def test_seed_declares_the_five_canonical_lanes_and_valid_stages():
    s = seed()
    assert s["schema"] == "codex.method_atlas.seed.v3"
    assert {l["id"] for l in s["lanes"]} == LANES
    assert len({l["tag"] for l in s["lanes"]}) == 5
    stages = {x["id"] for x in s["spine"]}
    ids = [b["id"] for b in s["blocks"]]
    assert len(ids) == len(set(ids))
    for b in s["blocks"]:
        assert b["stage"] in stages
        assert set(b.get("lanes") or []) <= LANES
        assert b["need"] and b["customer"] and b["supplier"]
    for lane in s["lanes"]:
        rx = re.compile(lane["pattern"], re.I)
        assert all(rx.fullmatch(sp) for sp in lane["canonical_spellings"]), lane["id"]


def test_seed_has_no_flow_mapping_comma_splits():
    # An unquoted comma inside `{key: a, b}` silently turns `b` into a null key.
    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                assert v is not None or k == "max_ratio", f"null key {path}/{k}"
                walk(v, f"{path}/{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
    walk(seed(), "")


def test_broker_modes_are_ordered_and_terminate():
    modes = seed()["broker"]["modes"]
    bounds = [m["max_ratio"] for m in modes]
    assert bounds[-1] is None and bounds[:-1] == sorted(bounds[:-1])


@pytest.mark.parametrize("expr,expected", [
    ("0 2 * * *", {2: 1}),
    ("*/15 6 * * 1-5", {6: 4}),
    ("30 */6 * * *", {0: 1, 6: 1, 12: 1, 18: 1}),
    ("0 8,20 * * *", {8: 1, 20: 1}),
    ("bad", {}),
])
def test_cron_runs_by_hour(expr, expected):
    assert atlas.cron_runs_by_hour(expr) == expected


def test_matrix_size_and_max_parallel():
    assert atlas.matrix_size({"matrix": {"py": ["3.11", "3.12"], "os": ["a", "b", "c"]}}) == (6, False)
    assert atlas.matrix_size({"matrix": {"include": [{"a": 1}, {"a": 2}]}}) == (2, False)
    assert atlas.matrix_size({"matrix": "${{ fromJSON(needs.x.outputs.m) }}"}) == (1, True)
    wf = atlas.parse_workflow("R", ".github/workflows/x.yml", """
name: X
on:
  pull_request: {paths: ['src/**']}
  schedule: [{cron: '0 3 * * *'}]
concurrency: {group: 'x-${{ github.ref }}', cancel-in-progress: true}
jobs:
  a: {runs-on: ubuntu-latest, strategy: {max-parallel: 2, matrix: {n: [1, 2, 3, 4]}}}
  b: {runs-on: ubuntu-latest, needs: a, timeout-minutes: 10}
""")
    assert wf["job_slots"] == 3 and wf["needs_depth"] == 2
    assert wf["path_filtered"] == {"pull_request": True}
    assert wf["concurrency_group"] and wf["cancel_in_progress"]
    assert wf["crons"] == ["0 3 * * *"] and wf["max_timeout_min"] == 360


def test_topological_order_rejects_cycles():
    assert atlas.topo_order(["a", "b"], [{"source": "a", "target": "b"}]) == ["a", "b"]
    with pytest.raises(ValueError):
        atlas.topo_order(["a", "b"], [{"source": "a", "target": "b"}, {"source": "b", "target": "a"}])


def _repo(path: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        (path / rel).parent.mkdir(parents=True, exist_ok=True)
        (path / rel).write_text(text, encoding="utf-8")


def test_build_on_synthetic_federation(tmp_path, monkeypatch):
    host = tmp_path / "HOST"
    tracked = {
        "make.py": "OUT='out/report.json'\n",
        "use.py": "IN='out/report.json'\n",
        "out/report.json": json.dumps({"summary": {"open": 3, "closed": 7}}),
        "ops/bd_queue_burndown.json": json.dumps({"total": 4}),
        "notes.md": "GoGREEN and go_green and Code Purple and EVERRED together.\n",
        ".github/workflows/ci.yml": "name: CI\non: [push, pull_request]\njobs:\n  t: {runs-on: ubuntu-latest}\n",
    }
    _repo(host, tracked)
    # Stand-ins for git: the tracked set is exactly `tracked`; the seed written below stays untracked.
    monkeypatch.setattr(atlas, "tracked_files", lambda path: sorted(tracked))
    monkeypatch.setattr(atlas, "repo_identity", lambda spec, path: {
        "id": spec["id"], "remote": spec["remote"], "role": spec["role"], "path": spec["path"],
        "present": True, "head": "0" * 40, "branch": "main", "dirty_tracked": 0})
    s = seed()
    s["repos"] = [{"id": "HOST", "path": ".", "remote": "x/host", "role": "test"}]
    s["host_repo"] = "HOST"
    for lane in s["lanes"]:
        lane["source"] = {"repo": "HOST", "path": "notes.md"}
    s["monikers"] = {}
    s["orchestrators"] = []
    s["blocks"] = [
        {"id": "MAKE", "name": "make", "repo": "HOST", "stage": "S5_EXECUTE", "lanes": [], "entry": "make.py",
         "need": "n", "inputs": [], "outputs": [{"path": "out/report.json"}], "supplier": "s", "customer": "c"},
        {"id": "USE", "name": "use", "repo": "HOST", "stage": "S7_PUBLISH", "lanes": ["GOGREEN"], "entry": "use.py",
         "need": "n", "inputs": [{"path": "out/report.json"}, {"path": "missing.json"}],
         "outputs": [{"path": "x.json", "kind": "runtime"}], "supplier": "s", "customer": "c"},
    ]
    seed_path = host / "tools/method_atlas/method_atlas_seed.yaml"  # untracked, so not scanned
    seed_path.parent.mkdir(parents=True)
    seed_path.write_text(yaml.safe_dump(s, sort_keys=False), encoding="utf-8")

    a, _ = atlas.build(seed_path)
    lanes = {l["id"]: l for l in a["taxonomy"]["lanes"]}
    gg = {v["spelling"]: v for v in lanes["GOGREEN"]["variants"]}
    assert gg["GoGREEN"]["canonical"] and gg["go_green"]["normalize_to"] == "GoGREEN"
    assert {v["spelling"] for v in lanes["CPURPLE"]["variants"]} == {"Code Purple"}
    assert any(c["pair"] == "GOGREEN+EVERRED" for c in a["taxonomy"]["combinations"])

    blocks = {b["id"]: b for b in a["dag"]["blocks"]}
    assert blocks["MAKE"]["verdict"] == "IO_OK"
    assert blocks["USE"]["verdict"] == "INPUT_MISSING"
    assert blocks["MAKE"]["outputs"][0]["referenced_by_entry"] is True
    assert {"source": "MAKE", "target": "USE", "via": "out/report.json", "derived": "io_match"} in a["dag"]["edges"]
    assert a["dag"]["topological_order"].index("MAKE") < a["dag"]["topological_order"].index("USE")

    repo = a["orchestration"]["per_repo"]["HOST"]
    assert repo["workflows"] == 1 and repo["pr_jobs_min"] == 1 and repo["flood_risk_workflows"] == [".github/workflows/ci.yml"]
    ledger = {e["path"]: e for e in a["ledger"]["entries"]}
    assert ledger["ops/bd_queue_burndown.json"]["theme"] == "ISSUES"
    assert ledger["ops/bd_queue_burndown.json"]["counts"] == {"total": 4}
    assert "head" not in a["repos"][0]

    files = atlas.outputs(a, s, tmp_path / "out")
    page = files[tmp_path / "out" / "index.html"]
    m = re.search(r'<script id="atlas-data" type="application/json">([\s\S]*?)</script>', page)
    assert json.loads(m.group(1)) == a and a["digest"] in page
    assert "fetch(" not in page


@pytest.mark.skipif(not (OUT / "method_atlas.json").exists(), reason="atlas not generated")
def test_committed_projection_matches_committed_json():
    data = json.loads((OUT / "method_atlas.json").read_text(encoding="utf-8"))
    page = (OUT / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<script id="atlas-data" type="application/json">([\s\S]*?)</script>', page)
    assert json.loads(m.group(1)) == data
    assert {l["id"] for l in data["taxonomy"]["lanes"]} == LANES
    assert data["authority"]["network"] is False and data["authority"]["dispatch"] is False
    mmd = (OUT / "method_atlas.mmd").read_text(encoding="utf-8")
    assert mmd.startswith("flowchart LR\n")
    for e in data["dag"]["edges"]:
        assert atlas.mid(e["source"]) in mmd and atlas.mid(e["target"]) in mmd
