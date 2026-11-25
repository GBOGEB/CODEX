import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import issue_critical_path as cp


def graph(nodes, edges):
    return {"schema": cp.GRAPH_SCHEMA,
            "nodes": [{"kind": "issue", **n} for n in nodes],
            "edges": [{"from": a, "to": b} for a, b in edges]}


def n(id_, **kw):
    return {"id": id_, "effort_days": kw.pop("e", 1.0), "latency_days": kw.pop("lat", 0.0), **kw}


def test_kahn_waves_and_cycle_detection():
    nodes, edges = cp.load_graph(graph([n("a"), n("b"), n("c"), n("x"), n("y")],
                                       [("a", "b"), ("b", "c"), ("x", "y"), ("y", "x")]))
    waves, cycle = cp.kahn(nodes, edges)
    assert waves == [["a"], ["b"], ["c"]]
    assert cycle == ["x", "y"]


def test_cpm_critical_path_and_slack():
    # a(1) -> b(3) -> d(1); a -> c(1) -> d. Critical a-b-d = 5 days; c has 2 days slack.
    nodes, edges = cp.load_graph(graph([n("a"), n("b", e=3), n("c"), n("d")],
                                       [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]))
    waves, _ = cp.kahn(nodes, edges)
    res = cp.cpm(nodes, edges, [x for w in waves for x in w])
    assert res["path"] == ["a", "b", "d"]
    assert res["duration_days"] == 5
    assert res["slack"]["c"] == 2 and res["slack"]["b"] == 0


def test_class_defaults_fill_missing_durations():
    nodes, _ = cp.load_graph({"schema": cp.GRAPH_SCHEMA, "edges": [],
                              "nodes": [{"id": "g", "kind": "gate"}, {"id": "i", "kind": "issue", "closure": "external"}]})
    assert (nodes["g"]["effort_days"], nodes["g"]["latency_days"]) == cp.CLASS_DEFAULTS["gate"]
    assert nodes["i"]["latency_days"] == cp.CLASS_DEFAULTS["external"][1]


def test_cones_and_betweenness_find_chokepoint():
    nodes, edges = cp.load_graph(graph([n("a"), n("hub"), n("c"), n("d")],
                                       [("a", "hub"), ("hub", "c"), ("hub", "d")]))
    cone = cp.cones(nodes, edges)
    assert cone["a"] == {"hub", "c", "d"} and cone["c"] == set()
    bc = cp.betweenness(nodes, edges)
    assert max(bc, key=bc.get) == "hub"


def test_reverse_pressure_flows_to_enablers_only_through_goals():
    data = graph([n("bd", kind="bd"), n("gate", kind="gate"), n("goal"), n("orphan_bd", kind="bd")],
                 [("bd", "gate"), ("gate", "goal")])
    nodes, edges = cp.load_graph(data)
    p = cp.reverse_pressure(nodes, edges, alpha=0.5)
    assert p["goal"] == 1.0
    assert p["gate"] == pytest.approx(0.5) and p["bd"] == pytest.approx(0.25)
    assert p["orphan_bd"] == 0.0


def test_levers_multiplier_and_and_join_synergy():
    # j needs both owner and agent levers: neither alone unlocks it -> synergy 1.
    data = graph([n("o", levers=["owner"], e=0.5), n("g", levers=["agent"], e=1.0),
                  n("j"), n("k")], [("o", "j"), ("g", "j"), ("o", "k")])
    nodes, edges = cp.load_graph(data)
    res = cp.levers(nodes, edges)
    assert res["levers"]["owner"]["unlocks"] == ["k"]
    assert res["levers"]["owner"]["multiplier"] == 2.0
    assert res["levers"]["agent"]["unlocks"] == []
    assert res["synergy"] == [{"levers": ["agent", "owner"], "extra_unlocks": ["j"], "synergy": 1}]


def test_pca_first_component_tracks_correlated_features():
    rows = [[i, 2 * i + 0.01 * (i % 3), 5.0] for i in range(10)]
    out = cp.pca(rows, ["x", "y", "const"], k=2)
    first = out["components"][0]
    assert first["explained"] > 0.6
    assert set(list(first["loadings"])[:2]) == {"x", "y"}
    assert "no inference" in out["note"]


def test_bradley_terry_orders_dominant_item_first():
    s = cp.bradley_terry(["a", "b", "c"], {"a": [3, 3], "b": [2, 2], "c": [1, 1]})
    assert s["a"] > s["b"] > s["c"]


def test_edges_from_text_directions():
    e = cp.edges_from_text("ABACUS#10", "Blocked by #7. Closes #12 and fixes CODEX #3.", "ABACUS")
    pairs = {(x["from"], x["to"]) for x in e}
    assert pairs == {("ABACUS#7", "ABACUS#10"), ("ABACUS#10", "ABACUS#12"), ("ABACUS#10", "CODEX#3")}


def test_validation_rejects_bad_graphs():
    with pytest.raises(ValueError, match="schema"):
        cp.load_graph({"schema": "x", "nodes": [], "edges": []})
    with pytest.raises(ValueError, match="unknown node"):
        cp.load_graph(graph([n("a")], [("a", "zz")]))
    with pytest.raises(ValueError, match="duplicate"):
        cp.load_graph(graph([n("a"), n("a")], []))
    with pytest.raises(ValueError, match="self edge"):
        cp.load_graph(graph([n("a")], [("a", "a")]))


def test_main_writes_report(tmp_path, capsys):
    g = tmp_path / "g.json"
    g.write_text(json.dumps(graph([n("a"), n("b")], [("a", "b")])))
    out = tmp_path / "out" / "r.json"
    assert cp.main(["--graph", str(g), "--out", str(out)]) == 0
    rep = json.loads(out.read_text())
    assert rep["schema"] == cp.REPORT_SCHEMA and rep["critical_path"] == ["a", "b"]
    assert "critical path: a -> b" in capsys.readouterr().out


def test_done_nodes_take_no_time_and_goal_paths_are_reported():
    data = graph([n("done", e=9, done=True), n("a"), n("goal"), n("side", e=4), n("end2")],
                 [("done", "goal"), ("a", "goal"), ("side", "end2")])
    data["goals"] = ["goal"]
    rep = cp.analyse(data)
    assert rep["goal_paths"] == [{"target": "goal", "days": 2.0, "path": ["a", "goal"]}]
    assert rep["critical_path"] == ["side", "end2"]


def test_and_mode_gives_every_required_blocker_full_pressure():
    data = graph([n("b1", kind="bd"), n("b2", kind="bd"), n("b3", kind="bd", done=True), n("goal")],
                 [("b1", "goal"), ("b2", "goal"), ("b3", "goal")])
    nodes, edges = cp.load_graph(data)
    and_p = cp.reverse_pressure(nodes, edges, alpha=0.5)
    share_p = cp.reverse_pressure(nodes, edges, alpha=0.5, mode="share")
    assert and_p["b1"] == and_p["b2"] == pytest.approx(0.5)
    assert share_p["b1"] == pytest.approx(0.5 / 3)
    with pytest.raises(ValueError, match="mode"):
        cp.reverse_pressure(nodes, edges, mode="max")


def test_lever_cover_finds_k_way_set_and_hidden_blockers():
    data = graph([n("a1", levers=["A"], e=0.5), n("a2", levers=["A"], e=0.5), n("b1", levers=["B"], e=2),
                  n("loose", e=1), n("gate", levers=["A"], e=1, done=True), n("goal")],
                 [("a1", "goal"), ("a2", "goal"), ("b1", "goal"), ("loose", "goal"), ("gate", "a1")])
    nodes, edges = cp.load_graph(data)
    res = cp.lever_cover(nodes, edges, "goal")
    assert [s["lever"] for s in res["steps"]] == ["A", "B"]
    assert res["steps"][0]["completes"] == 2 and res["steps"][0]["share"] == 0.5
    assert res["residual"] == ["loose"] and res["ready_after_cover"] is False


@pytest.mark.parametrize("canary", ["ABACUS#2470", "abacus!2470", "GBOGEB/ABACUS#2470"])
def test_protected_control_is_not_generic_lever_completion(canary):
    data = graph([n("policy", levers=["admin"]), n(canary, kind="pr", levers=["merge"], done=True),
                  n("ABACUS#2471", levers=["merge"], done=True), n("child"), n("ordinary", levers=["merge"]),
                  n("ordinary_child")],
                 [("policy", canary), (canary, "ABACUS#2471"), ("policy", "ABACUS#2471"),
                  ("ABACUS#2471", "child"), ("ordinary", "ordinary_child")])
    nodes, edges = cp.load_graph(data)
    res = cp.levers(nodes, edges)
    assert res["levers"]["merge"]["members"] == ["ordinary"]
    assert res["levers"]["merge"]["unlocks"] == ["ordinary_child"]
    assert all("ABACUS#2471" not in row["extra_unlocks"] for row in res["synergy"])
    cover = cp.lever_cover(nodes, edges, "child")
    assert canary in cover["residual"]
    assert "ABACUS#2471" in cover["residual"]
    assert cover["ready_after_cover"] is False
    report = cp.analyse(data)
    assert (report["nodes"], report["edges"]) == (6, 5)
    assert report["execution_classification"] == "ADVISORY_ONLY"
    assert report["authority_transfer"] is False
    assert report["protected_control"]["merge_eligible"] is False
    assert report["protected_control"]["completion_verified"] is False
    assert report["protected_control"]["present"] is True
    assert next(r for r in report["ranking"] if r["id"] == canary)["advisory_action_class"] == (
        "PROTECTED_NEVER_MERGE"
    )


def test_absent_canary_does_not_clear_refusal_obligation():
    data = graph([n("policy", levers=["admin"]), n("ABACUS#2471"), n("child")],
                 [("policy", "ABACUS#2471"), ("ABACUS#2471", "child")])
    nodes, edges = cp.load_graph(data)
    assert "ABACUS#2471" not in cp.levers(nodes, edges)["levers"]["admin"]["unlocks"]
    assert "ABACUS#2470" in cp.lever_cover(nodes, edges, "ABACUS#2471")["residual"]
    assert "ABACUS#2470" in cp.lever_cover(nodes, edges, "child")["residual"]
    report = cp.analyse(data)
    assert report["protected_control"]["present"] is False
    assert report["protected_control"]["completion_verified"] is False
    assert report["operational_readiness"] == "NOT_QUALIFIED"
