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


def test_export_cpath_loads_in_issue_critical_path_and_merges_base():
    spec = importlib.util.spec_from_file_location("issue_critical_path", ROOT / "scripts/issue_critical_path.py")
    cp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cp)
    c = census(
        pr("O/CODEX", 1, "THREADS", [dag.KIT_PRODUCER], unresolved=2, body="Fixes #500"),
        pr("O/ABACUS", 2, "REQ_PENDING", [dag.KIT_CONSUMER]),
        pr("O/CODEX", 5, "NEEDS_APPROVAL", held_runs=3),
        *dag.parse_bd_queue("| 1 | #500 TRIAGE gate | EXTERNAL_GATE | x | y |\n", "O/CODEX"),
    )
    g = dag.to_cpath(c)
    nodes, edges = cp.load_graph(g)
    assert nodes["CODEX#500"]["kind"] == "issue" and nodes["CODEX#500"]["closure"] == "external"
    assert nodes["CODEX#1"]["effort_days"] == 0.125  # 1.0 h / 8
    assert ("CODEX#1", "CODEX#500") in edges and ("CODEX#1", "ABACUS#2") in edges
    assert nodes["GATE:CODEX#5:approve-runs"]["kind"] == "gate"
    base = {"schema": dag.CPATH_SCHEMA, "as_of": "B", "goals": ["CODEX#500"],
            "nodes": [{"id": "CODEX#500", "kind": "issue", "closure": "external", "title": "curated"}],
            "edges": []}
    merged = dag.to_cpath(c, base)
    assert next(n for n in merged["nodes"] if n["id"] == "CODEX#500")["title"] == "curated"
    assert merged["goals"] == ["CODEX#500"]
    cp.load_graph(merged)


def _cpath_graph(nodes, edges=(), goals=()):
    return {"schema": dag.CPATH_SCHEMA, "as_of": "B", "goals": list(goals), "nodes": list(nodes), "edges": list(edges)}


def test_export_cpath_base_refreshes_census_owned_records():
    # #1333 review P1: a --base snapshot must not pin an earlier PR verdict or keep closed PRs.
    base = _cpath_graph(
        [{"id": "CODEX#1", "kind": "pr", "verdict": "REQ_RED", "effort_days": 0.375},
         {"id": "CODEX#9", "kind": "pr", "verdict": "THREADS", "effort_days": 0.1},  # closed since
         {"id": "OTHER#4", "kind": "pr", "title": "curated, repo not censused"},
         {"id": "GATE:CODEX#9:owner-checklist", "kind": "gate", "closure": "owner-decision"},
         {"id": "GATE:BD-17", "kind": "gate", "closure": "owner-decision", "title": "curated gate"},
         {"id": "CODEX#500", "kind": "issue", "closure": "external", "title": "curated"}],
        [{"from": "GATE:CODEX#9:owner-checklist", "to": "CODEX#9", "source": "federation_pr_dag:human_gate"},
         {"from": "CODEX#9", "to": "CODEX#500", "source": "#2752 ledger"},
         {"from": "GATE:BD-17", "to": "CODEX#500", "source": "#2752 ledger"}],
        goals=["CODEX#500"])
    c = census(pr("O/CODEX", 1, "READY"), *dag.parse_bd_queue("| 1 | #500 gate | EXTERNAL_GATE | x | y |\n", "O/CODEX"))
    merged = dag.to_cpath(c, base)
    ids = {n["id"]: n for n in merged["nodes"]}
    assert ids["CODEX#1"]["verdict"] == "READY"
    assert "CODEX#9" not in ids and "GATE:CODEX#9:owner-checklist" not in ids
    assert ids["OTHER#4"]["title"] == "curated, repo not censused" and "GATE:BD-17" in ids
    assert ids["CODEX#500"]["title"] == "curated"
    assert [(e["from"], e["to"]) for e in merged["edges"]] == [("GATE:BD-17", "CODEX#500")]
    spec = importlib.util.spec_from_file_location("issue_critical_path", ROOT / "scripts/issue_critical_path.py")
    cp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cp)
    cp.load_graph(merged)


def test_export_cpath_parent_control_is_not_work():
    # #1333 review P2: PARENT_CONTROL stays non-actionable in the C-path graph.
    c = census(*dag.parse_bd_queue("| 1 | #879 DMAIC control | PARENT_CONTROL | x | y |\n", "O/CODEX"))
    rec = next(n for n in dag.to_cpath(c)["nodes"] if n["id"] == "CODEX#879")
    assert rec["actionable"] is False and rec["goal_weight"] == 0.0
    assert rec["effort_days"] == 0.0 and rec["latency_days"] == 0.0


def test_actions_unavailable_gate_is_the_kahn_root():
    c = census(pr("O/CODEX", 1, "REQ_RED"), pr("O/CODEX", 2, "BEHIND"), pr("O/CODEX", 3, "THREADS"),
               pr("O/ABACUS", 4, "REQ_RED"))
    c["actions_blocked"] = {"O/CODEX": "account is locked due to a billing issue"}
    rep = dag.analyze(c)
    g = "GATE:O:actions-unavailable"
    assert rep["kahn_order"][0] == g
    succ = {e["to"] for e in rep["edges"] if e["from"] == g}
    assert succ == {"CODEX#1", "CODEX#2"}  # THREADS needs no CI; ABACUS not blocked
    assert g in rep["critical_path"]
    assert "Actions cannot start" in dag.to_markdown(rep)


def test_actions_block_reason_and_unreadable_rules():
    assert dag.actions_block_reason(["x", "The job was not started because your account is locked due to a billing issue."])
    assert dag.actions_block_reason(["Process completed with exit code 1."]) is None
    assert dag.required_contexts(None) == (None, False)
    latest = {"a": {"status": "completed", "conclusion": "failure"},
              "b": {"status": "in_progress", "conclusion": None},
              "c": {"status": "completed", "conclusion": "success"}}
    assert dag.classify_checks(None, latest) == (["a"], ["b"])
    assert dag.classify_checks(["c"], latest) == ([], [])
    assert dag.classify_checks(None, {}) == ([], ["<no check runs; required set unreadable>"])
