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


def test_cron_day_fraction_minutes_and_movability():
    assert atlas.cron_day_fraction("0 2 * * *") == 1.0
    assert atlas.cron_day_fraction("0 2 * * 1") == round(1 / 7, 4)
    assert atlas.cron_day_fraction("0 2 * * 1-5") == round(5 / 7, 4)
    assert atlas.cron_day_fraction("0 0 1 * *") == round(1 / 30.44, 4)
    assert atlas.cron_day_fraction("0 0 * * 0,7") == round(1 / 7, 4)  # 0 and 7 are both Sunday
    assert atlas.cron_minutes("15 3,9 * * *") == [(3, 15), (9, 15)]
    assert atlas.movable_cron("0 2 * * *") and atlas.movable_cron("30 1,13 * * 1")
    assert not atlas.movable_cron("*/5 * * * *") and not atlas.movable_cron("0 */6 * * *")


def test_stagger_moves_biggest_movable_first_and_respects_fixed_crons():
    entries = [
        {"repo": "R", "file": "a.yml", "name": "a", "cron": "0 2 * * *", "job_slots": 20},
        {"repo": "R", "file": "b.yml", "name": "b", "cron": "0 2 * * *", "job_slots": 13},
        {"repo": "R", "file": "c.yml", "name": "c", "cron": "*/5 * * * *", "job_slots": 3},
    ]
    plan = atlas.stagger_plan(entries, slots=20)
    assert plan["peak_minute_slots_before"] == 36
    assert [m["file"] for m in plan["moves"]][:1] == ["a.yml"]  # a fixed */5 cron anchors 02:00
    assert plan["peak_minute_slots_after"] < 36
    assert all(atlas.movable_cron(m["to"]) and m["to"].split()[1:] == m["from"].split()[1:] for m in plan["moves"])


def test_parse_check_and_stale_verdict(tmp_path):
    (tmp_path / "ok.json").write_text('{"a": 1}', encoding="utf-8")
    (tmp_path / "bad.json").write_text("{nope", encoding="utf-8")
    (tmp_path / "x.md").write_text("# x", encoding="utf-8")
    assert atlas.parse_check(tmp_path / "ok.json") == "OK"
    assert atlas.parse_check(tmp_path / "bad.json") == "FAIL"
    assert atlas.parse_check(tmp_path / "x.md") == "NA"
    ins = [{"status": "OK", "changed_ts": 200}]
    outs = [{"status": "OK", "changed_ts": 100}]
    assert atlas.block_verdict(True, True, ins, outs, freshness=True) == "STALE_OUTPUT"
    assert atlas.block_verdict(True, True, ins, outs, freshness=False) == "IO_OK"
    assert atlas.block_verdict(True, True, ins, [{"status": "OK", "parse": "FAIL"}], True) == "OUTPUT_UNPARSEABLE"


def test_git_blob_oid_matches_git():
    assert atlas.git_blob_oid(b"") == "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"


def test_build_on_synthetic_federation(tmp_path, monkeypatch):
    host = tmp_path / "HOST"
    trees = {
        "HOST": {
            "notes.md": "GoGREEN and go_green and Code Purple and EVERRED together.\n",
            "ops/bd_queue_burndown.json": json.dumps({"total": 4}),
            ".github/workflows/ci.yml": "name: CI\non: [push, pull_request]\njobs:\n  t: {runs-on: ubuntu-latest}\n",
            ".github/workflows/nightly.yml": ("name: Nightly GoGREEN\non:\n  schedule: [{cron: '0 2 * * *'}, {cron: '0 2 * * 1'}]\n"
                                              "jobs:\n  a: {runs-on: ubuntu-latest}\n  b: {runs-on: ubuntu-latest}\n"),
        },
        "SIB": {
            "make.py": "OUT='out/report.json'\n",
            "use.py": "IN='out/report.json'\n",
            "stale.py": "src.json out/stale.json\n",
            "src.json": "{}",
            "out/report.json": json.dumps({"summary": {"open": 3, "closed": 7}}),
            "out/stale.json": "{}",
        },
    }
    trees["MIRROR"] = {**trees["SIB"], "use.py": "changed\n"}
    for name, files in trees.items():
        _repo(tmp_path / name, files)

    def oid(name, rel):
        return atlas.git_blob_oid(trees[name][rel].encode())

    times = {"src.json": 200, "out/stale.json": 100, "out/report.json": 150}
    # Stand-ins for git: each tracked set is exactly its tree; the seed written below stays untracked.
    monkeypatch.setattr(atlas, "blob_index", lambda path: {rel: oid(path.name, rel) for rel in trees[path.name]})
    monkeypatch.setattr(atlas, "worktree_modified", lambda path: {"out/report.json"} if path.name == "SIB" else set())
    monkeypatch.setattr(atlas, "last_change", lambda path, rel: {"commit": "c" * 40, "ts": times.get(rel, 50)})
    monkeypatch.setattr(atlas, "repo_identity", lambda spec, path: {
        "id": spec["id"], "remote": spec.get("remote"), "role": spec.get("role"), "path": spec["path"],
        "present": True, "head": path.name.lower() * 4, "tree": "t" * 40, "branch": "main", "dirty_tracked": 0})
    s = seed()
    s["repos"] = [{"id": "HOST", "path": ".", "remote": "x/host", "role": "test"},
                  {"id": "SIB", "path": "../SIB", "remote": "x/sib", "role": "test"}]
    s["host_repo"] = "HOST"
    s["mirrors"] = [{"id": "SIB_MIRROR", "of": "SIB", "path": "../MIRROR"}]
    for lane in s["lanes"]:
        lane["source"] = {"repo": "HOST", "path": "notes.md"}
    s["monikers"] = {}
    s["orchestrators"] = []

    def blk(i, entry, ins, outs, lanes=()):
        return {"id": i, "name": i, "repo": "SIB", "stage": "S5_EXECUTE", "lanes": list(lanes), "entry": entry,
                "need": "n", "inputs": ins, "outputs": outs, "supplier": "s", "customer": "c"}

    s["blocks"] = [
        blk("MAKE", "make.py", [], [{"path": "out/report.json"}]),
        blk("USE", "use.py", [{"path": "out/report.json"}, {"path": "missing.json"}],
            [{"path": "x.json", "kind": "runtime"}], ["GOGREEN"]),
        blk("STALE", "stale.py", [{"path": "src.json"}], [{"path": "out/stale.json"}]),
    ]
    seed_path = host / "tools/method_atlas/method_atlas_seed.yaml"
    seed_path.parent.mkdir(parents=True)
    seed_path.write_text(yaml.safe_dump(s, sort_keys=False), encoding="utf-8")

    a, _, _ = atlas.build(seed_path)
    lanes = {l["id"]: l for l in a["taxonomy"]["lanes"]}
    gg = {v["spelling"]: v for v in lanes["GOGREEN"]["variants"]}
    assert gg["GoGREEN"]["canonical"] and gg["go_green"]["normalize_to"] == "GoGREEN"
    assert {v["spelling"] for v in lanes["CPURPLE"]["variants"]} == {"Code Purple"}
    assert any(c["pair"] == "GOGREEN+EVERRED" for c in a["taxonomy"]["combinations"])

    blocks = {b["id"]: b for b in a["dag"]["blocks"]}
    assert blocks["MAKE"]["verdict"] == "IO_OK"
    assert blocks["USE"]["verdict"] == "INPUT_MISSING"
    assert blocks["STALE"]["verdict"] == "STALE_OUTPUT"
    out = blocks["MAKE"]["outputs"][0]
    assert out["referenced_by_entry"] is True and out["parse"] == "OK"
    assert out["oid"] == oid("SIB", "out/report.json") and out["worktree"] == "MODIFIED"
    assert blocks["MAKE"]["worktree_modified"] == ["out/report.json"] and out["changed_ts"] == 150
    assert {"source": "MAKE", "target": "USE", "via": "out/report.json", "derived": "io_match"} in a["dag"]["edges"]
    assert a["dag"]["topological_order"].index("MAKE") < a["dag"]["topological_order"].index("USE")

    host_repo, sib_repo = a["repos"]
    assert "head" not in host_repo and "tree" not in host_repo and sib_repo["tree"] == "t" * 40
    (mirror,) = a["mirrors"]
    assert mirror["files_differing"] == 1 and mirror["differing_sample"] == ["use.py"] and not mirror["same_commit"]

    o = a["orchestration"]
    assert o["per_repo"]["HOST"]["flood_risk_workflows"] == [".github/workflows/ci.yml"]
    assert [w["lanes"] for w in o["workflows"] if w["file"].endswith("nightly.yml")] == [["GOGREEN"]]
    c = o["cron"]
    assert c["slots_by_hour_worst_day"]["2"] == 4 and c["slots_by_hour_every_day"]["2"] == 2
    assert (c["peak_minutes"][0]["time"], c["peak_minutes"][0]["job_slots"]) == ("02:00", 4)
    assert {e["cron"] for e in c["contributors_by_hour"]["2"]} == {"0 2 * * *", "0 2 * * 1"}
    ledger = {e["path"]: e for e in a["ledger"]["entries"]}
    assert ledger["ops/bd_queue_burndown.json"]["theme"] == "ISSUES"
    assert ledger["ops/bd_queue_burndown.json"]["counts"] == {"total": 4}
    assert ledger["ops/bd_queue_burndown.json"]["oid"] == oid("HOST", "ops/bd_queue_burndown.json")

    files = atlas.outputs(a, s, tmp_path / "out")
    page = files[tmp_path / "out" / "index.html"]
    m = re.search(r'<script id="atlas-data" type="application/json">([\s\S]*?)</script>', page)
    assert json.loads(m.group(1)) == a and a["digest"] in page
    assert "fetch(" not in page


def test_run_checks_records_status_per_block(tmp_path):
    fake = {"digest": "d", "dag": {"blocks": [
        {"id": "P", "repo": "R", "verdict": "IO_OK", "check": "python -c \"print('ok')\""},
        {"id": "F", "repo": "R", "verdict": "IO_OK", "check": "python -c \"raise SystemExit(3)\""},
        {"id": "N", "repo": "R", "verdict": "IO_OK", "check": None}]}}
    receipt = atlas.run_checks(fake, {"R": tmp_path})
    got = {r["block"]: (r["status"], r["exit_code"]) for r in receipt["results"]}
    assert got == {"P": ("PASS", 0), "F": ("FAIL", 3)} and receipt["summary"] == {"FAIL": 1, "PASS": 1}


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
