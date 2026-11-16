from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("federation_pr_dag", ROOT / "scripts/ci/federation_pr_dag.py")
dag = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dag)


def pr(repo, num, verdict, files=(), body="", title="feat", **kw):
    return {"id": dag.node_id(repo, num), "repo": repo, "number": num, "kind": "pr",
            "title": title, "verdict": verdict, "files": list(files), "body": body, **kw}


def census(*nodes):
    return {"repos": ["O/CODEX", "O/ABACUS"], "observed_at": "T", "nodes": list(nodes)}


def test_kahn_orders_dependencies_and_reports_cycles():
    nodes = {v: {"priority": p, "effort": 1.0} for v, p in (("a", 0.1), ("b", 0.9), ("c", 0.5))}
    order, stuck = dag.kahn(nodes, [{"from": "a", "to": "c", "soft": False, "kind": "x"}])
    assert order == ["b", "a", "c"] and stuck == []
    cyc = [{"from": "a", "to": "c", "soft": True, "kind": "x"}, {"from": "c", "to": "a", "soft": False, "kind": "x"}]
    order, stuck = dag.kahn(nodes, cyc)
    assert stuck == ["a", "c"] and order == ["b"]
    kept, dropped = dag.break_cycles(nodes, cyc)
    assert dropped[0]["soft"] and len(kept) == 1


def test_cpm_finds_zero_slack_chain():
    nodes = {"a": {"effort": 2.0, "priority": 0}, "b": {"effort": 1.0, "priority": 0},
             "c": {"effort": 3.0, "priority": 0}, "d": {"effort": 1.0, "priority": 0}}
    edges = [{"from": "a", "to": "c"}, {"from": "b", "to": "d"}]
    order, _ = dag.kahn(nodes, edges)
    res = dag.cpm(nodes, edges, order)
    assert res["makespan"] == 5.0
    assert res["critical_path"] == ["a", "c"]
    assert res["slack"]["b"] == 3.0 and res["slack"]["c"] == 0


def test_reverse_pressure_flows_to_blockers():
    nodes = {"blocker": {"priority": 0.1, "effort": 1.0}, "urgent": {"priority": 1.0, "effort": 1.0}}
    edges = [{"from": "blocker", "to": "urgent"}]
    order, _ = dag.kahn(nodes, edges)
    rp = dag.reverse_pressure(nodes, edges, order, lam=0.5)
    assert rp["blocker"]["pressure"] == 0.6 and rp["blocker"]["leverage"] == 2
    assert rp["blocker"]["pressure"] > nodes["blocker"]["priority"]


def test_graph_edges_kit_pin_depends_on_gates_and_shared_files():
    c = census(
        pr("O/CODEX", 1, "THREADS", [dag.KIT_PRODUCER], title="mip kit 1.4", unresolved=2),
        pr("O/ABACUS", 2, "REQ_PENDING", [dag.KIT_CONSUMER]),
        pr("O/ABACUS", 3, "READY", ["docs/data/x.json"], body="Depends-on: O/ABACUS#2"),
        pr("O/ABACUS", 4, "CONFLICT", ["docs/data/x.json"]),
        pr("O/CODEX", 5, "NEEDS_APPROVAL", held_runs=6, title="chore: metrics refresh"),
    )
    nodes, edges = dag.build_graph(c)
    kinds = {(e["from"], e["to"]): e["kind"] for e in edges}
    assert kinds[("CODEX#1", "ABACUS#2")] == "kit_pin"
    assert kinds[("ABACUS#2", "ABACUS#3")] == "depends_on"
    assert kinds[("ABACUS#3", "ABACUS#4")] == "shared_generated"
    assert kinds[("GATE:CODEX#5:approve-runs", "CODEX#5")] == "human_gate"
    assert nodes["CODEX#1"]["effort"] == 1.0  # 0.5 + 2 threads * 0.25


def test_analyze_and_pilot_detect_vector_effects():
    c = census(
        pr("O/CODEX", 1, "THREADS", [dag.KIT_PRODUCER], unresolved=4),
        pr("O/ABACUS", 2, "REQ_PENDING", [dag.KIT_CONSUMER]),
        pr("O/ABACUS", 3, "CONFLICT", ["docs/data/x.json"]),
        pr("O/ABACUS", 4, "READY", ["docs/data/x.json"]),
        pr("O/CODEX", 5, "NEEDS_APPROVAL", held_runs=3),
    )
    rep = dag.analyze(c)
    assert rep["deadlock_nodes"] == []
    assert rep["critical_path"][0] == "GATE:CODEX#5:approve-runs"
    assert rep["nodes"]["CODEX#5"]["waits_on"] == ["GATE:CODEX#5:approve-runs"]
    single = rep["pilot"]["single"]
    assert single["approve_bot_runs"]["makespan_saved"] > 0
    assert single["regen_on_main"]["ready_gained"] >= 0
    assert all(p["effect"] in ("multiplying", "additive", "overlapping") for p in rep["pilot"]["pairs"])
    assert len(rep["payload_sha256"]) == 64
    md = dag.to_markdown(rep)
    assert "## Critical path" in md and "Pilot" in md


def test_bd_queue_rows_become_ranked_issue_nodes():
    text = "| 1 | #500 TRIAGE gate | EXTERNAL_GATE | x | y |\n| 2 | #753 QPS lane | EXTERNAL_GATE | x | y |\n"
    rows = dag.parse_bd_queue(text, "O/CODEX")
    assert [r["id"] for r in rows] == ["CODEX!500", "CODEX!753"]
    assert rows[0]["priority"] == 1.0 and rows[1]["priority"] == 0.5
    assert rows[0]["effort"] == dag.HUMAN_WAIT
    c = census(pr("O/CODEX", 9, "READY", body="Fixes #500"), *rows)
    _, edges = dag.build_graph(c)
    assert {"from": "CODEX#9", "to": "CODEX!500", "kind": "closes_bd", "soft": False} in edges


def test_parent_control_issues_are_not_ranked():
    text = "| 1 | #319 DMAIC control | PARENT_CONTROL | x | y |\n"
    rep = dag.analyze(census(*dag.parse_bd_queue(text, "O/CODEX")))
    assert "CODEX!319" in rep["nodes"] and "CODEX!319" not in rep["ranking"]
