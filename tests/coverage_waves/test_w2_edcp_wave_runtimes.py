"""Coverage wave 2 (L3): EDCP ``waveNN`` runtime modules under ``src/``.

Each module is a small in-memory engine plus a ``__main__`` demo; both the
engine behaviour and the demo output are asserted.
"""
from __future__ import annotations

import pytest

from tests.coverage_waves._loader import load, run_main

W11 = "src/governance/runtime_validation/wave11_recursive_runtime_audit.py"
W12 = "src/runtime/orchestration/wave12_multi_deck_runtime_orchestrator.py"
W13 = "src/runtime/interactive/wave13_interactive_runtime_layer.py"
W14 = "src/runtime/layout/wave14_adaptive_semantic_layout_engine.py"
W15 = "src/intelligence/graph/wave15_engineering_graph_intelligence.py"
W16 = "src/intelligence/query/wave16_semantic_runtime_query_engine.py"
W17 = "src/orchestration/autonomous/wave17_autonomous_semantic_orchestrator.py"
W18 = "src/intelligence/inference/wave18_ai_semantic_inference_layer.py"
W19 = "src/autonomy/self_healing/wave19_recursive_semantic_self_healing.py"
W20 = "src/agents/semantic/wave20_autonomous_engineering_agents.py"
W30 = "src/visual_runtime/html/wave30_html_runtime_core.py"


def test_w11_audit_scores_and_report():
    m = load(W11)
    audit = m.RecursiveRuntimeAudit()
    assert audit.calculate_category_score("missing") == 0
    audit.add_metric("A", m.MetricSnapshot("a1", 1, 80, 100, 0.5))
    audit.add_metric("A", m.MetricSnapshot("a2", 1, 10, 100, 0.1))
    audit.add_metric("B", m.MetricSnapshot("b1", 1, 50, 100, 0.2))
    assert audit.calculate_category_score("A") == 41.0
    assert audit.calculate_total_score() == 51.0
    report = audit.generate_audit_report()
    assert report["total_score"] == 51.0
    assert [x["name"] for x in report["categories"]["A"]["metrics"]] == ["a1", "a2"]
    assert report["categories"]["B"]["metrics"][0]["weighted_score"] == 10.0


def test_w12_orchestrator_resolves_templates_by_domain():
    m = load(W12)
    orch = m.MultiDeckRuntimeOrchestrator()
    orch.register_deck(m.DeckManifest("d1", "cryo", "pptx", 3, "p"))
    orch.register_deck(m.DeckManifest("d2", "cryo", "pdf", 1, "p"))
    orch.register_template(m.RuntimeTemplate("t1", ["cryo"], [], "x"))
    orch.register_template(m.RuntimeTemplate("t2", ["mfg"], [], "x"))
    assert [t.template_id for t in orch.resolve_template("cryo")] == ["t1"]
    assert orch.resolve_template("none") == []
    s = orch.build_runtime_summary()
    assert s == {"registered_decks": 2, "registered_templates": 2, "domains": ["cryo"], "deck_ids": ["d1", "d2"]}


def test_w13_navigation_graph_skips_regions_without_target():
    m = load(W13)
    rt = m.InteractiveEngineeringRuntime()
    rt.register_overlay(m.InteractiveOverlay("o1", "T", [
        m.InteractiveRegion("r1", "L", "evidence", target_slide="s2"),
        m.InteractiveRegion("r2", "L", "note"),
    ]))
    assert rt.build_navigation_graph() == {"o1": ["s2"]}
    manifest = rt.build_overlay_manifest()
    assert manifest["o1"]["region_count"] == 2
    assert manifest["o1"]["regions"][1]["target_slide"] is None


def test_w14_layout_density_and_order():
    m = load(W14)
    eng = m.AdaptiveSemanticLayoutEngine()
    eng.register_zone(m.LayoutZone("z", [
        m.LayoutCard("a", "table", 1, 1000, 500),
        m.LayoutCard("b", "svg", 5, 1000, 500),
        m.LayoutCard("c", "evidence", 5, 200, 100),
    ]))
    assert eng.calculate_zone_density("z") == 1.02
    assert [c.card_id for c in eng.optimize_card_order("z")] == ["c", "b", "a"]
    assert eng.build_layout_manifest()["z"] == {"card_count": 3, "density": 1.02, "optimized_order": ["c", "b", "a"]}
    with pytest.raises(KeyError):
        eng.calculate_zone_density("nope")


def test_w15_graph_neighbors_lineage_query():
    m = load(W15)
    g = m.EngineeringSemanticGraph()
    for n in ("a", "b", "c"):
        g.add_node(m.EngineeringNode(n, "t", n.upper()))
    g.add_edge(m.EngineeringEdge("a", "b", "feeds"))
    g.add_edge(m.EngineeringEdge("c", "a", "cites"))
    assert g.get_neighbors("a") == {"b", "c"}
    assert g.get_neighbors("b") == {"a"}
    assert g.build_lineage_graph()["c"] == {"label": "C", "neighbors": ["a"]}
    assert g.semantic_query("feeds") == [{"source": "a", "target": "b", "relation": "feeds"}]
    assert g.semantic_query("none") == []


def test_w16_query_scores_and_sorts():
    m = load(W16)
    eng = m.SemanticRuntimeQueryEngine()
    eng.register_document(m.SemanticDocument("d1", "T1", "cryo", semantic_tags=["x"]))
    eng.register_document(m.SemanticDocument("d2", "T2", "cryo", semantic_tags=["x", "y"]))
    eng.register_document(m.SemanticDocument("d3", "T3", "cryo", semantic_tags=["z"]))
    res = eng.semantic_query(["x", "y"])
    assert [(r.document_id, r.score, r.matched_tags) for r in res] == [("d2", 1.0, ["x", "y"]), ("d1", 0.5, ["x"])]
    assert eng.semantic_query([]) == []
    assert eng.build_semantic_index()["d3"] == {"title": "T3", "domain": "cryo", "semantic_tags": ["z"]}


def test_w17_health_penalty_and_actions():
    m = load(W17)
    orch = m.AutonomousSemanticOrchestrator()
    orch.register_signal(m.RuntimeSignal("s1", "layout_drift", 0.5))
    orch.register_signal(m.RuntimeSignal("s2", "ocr_intrusion", 0.9))
    orch.register_signal(m.RuntimeSignal("s3", "other", 0.1))
    assert orch.evaluate_runtime_health() == {"signal_count": 3, "runtime_health_score": 90}
    actions = orch.generate_optimization_actions()
    assert [(a.action_id, a.priority) for a in actions] == [("opt_s1", 8), ("opt_s2", 10)]
    loop = orch.build_runtime_feedback_loop()
    assert len(loop["optimization_actions"]) == 2


def test_w17_health_floor_is_zero():
    m = load(W17)
    orch = m.AutonomousSemanticOrchestrator()
    for i in range(30):
        orch.register_signal(m.RuntimeSignal(f"s{i}", "x", 0.0))
    assert orch.evaluate_runtime_health()["runtime_health_score"] == 0


def test_w18_inference_confidence_and_drift():
    m = load(W18)
    layer = m.AISemanticInferenceLayer()
    assert layer.calculate_semantic_confidence() == 0.0
    layer.register_inference(m.SemanticInference("i1", "t", 0.9))
    layer.register_inference(m.SemanticInference("i2", "t", 0.6))
    layer.register_drift_signal(m.SemanticDriftSignal("d1", 0.7, ["r2", "r1"]))
    layer.register_drift_signal(m.SemanticDriftSignal("d2", 0.65, ["r9"]))
    layer.register_drift_signal(m.SemanticDriftSignal("d3", 0.9, ["r1"]))
    assert layer.build_inference_summary() == {
        "semantic_confidence": 0.75,
        "high_drift_regions": ["r1", "r2"],
        "inference_count": 2,
        "drift_signal_count": 3,
    }


@pytest.mark.parametrize(
    ("drift", "strategy"),
    [
        ("layout_drift", "adaptive_layout_rebalance"),
        ("ocr_intrusion", "increase_ocr_suppression"),
        ("semantic_mismatch", "semantic_region_reclassification"),
        ("weird", "generic_runtime_stabilization"),
    ],
)
def test_w19_strategy_per_drift_type(drift, strategy):
    m = load(W19)
    sh = m.RecursiveSemanticSelfHealing()
    sh.register_drift_condition(m.DriftCondition("c", "r", drift, 0.4))
    (action,) = sh.generate_healing_actions()
    assert action.strategy == strategy
    assert action.confidence == 0.9


def test_w19_stability_and_confidence_floor():
    m = load(W19)
    sh = m.RecursiveSemanticSelfHealing()
    assert sh.calculate_runtime_stability() == 100.0
    sh.register_drift_condition(m.DriftCondition("c1", "r1", "x", 10.0))
    sh.register_drift_condition(m.DriftCondition("c2", "r2", "x", 0.0))
    actions = sh.generate_healing_actions()
    assert [a.confidence for a in actions] == [0.1, 1.0]
    summary = sh.build_self_healing_summary()
    assert summary["runtime_stability"] == 55.0
    assert summary["healing_action_count"] == 2


def test_w20_agent_confidence_capped_and_coordination():
    m = load(W20)
    agent = m.AutonomousEngineeringAgent("a")
    assert agent.build_agent_summary()["avg_confidence"] == 0
    assert agent.evaluate_task(m.SemanticTask("t", "obj", 5)).confidence == 0.75
    assert agent.evaluate_task(m.SemanticTask("t", "obj", 50)).confidence == 0.99
    coord = m.SemanticAgentCoordinator()
    coord.register_agent(m.AutonomousEngineeringAgent("x"))
    coord.register_agent(m.AutonomousEngineeringAgent("y"))
    coord.distribute_task(m.SemanticTask("t1", "o", 1))
    s = coord.build_coordination_summary()
    assert s["x"] == {"agent_id": "x", "task_count": 1, "decision_count": 1, "avg_confidence": 0.59}
    assert set(s) == {"x", "y"}


def test_w30_html_escapes_and_assembles():
    m = load(W30)
    core = m.HTMLRuntimeCore()
    card = m.RuntimeCard("c<1>", "T&C", "evidence", "<b>x</b>", tags=["a\"b"])
    html = core.render_document([m.RuntimeSlide("s1", "Title <x>", "Sub", [card])])
    assert html.startswith("<!doctype html>")
    assert "&lt;b&gt;x&lt;/b&gt;" in html and "<b>x</b>" not in html
    assert "T&amp;C" in html and 'data-card-id="c&lt;1&gt;"' in html
    assert "a&quot;b" in html and "Title &lt;x&gt;" in html
    assert core.render_document([]).count("runtime-slide") == 0


@pytest.mark.parametrize("path", [W11, W12, W13, W14, W15, W16, W17, W18, W19, W20])
def test_main_demo_prints_summary(path, capsys):
    run_main(path)
    out = capsys.readouterr().out
    assert out.strip()[0] in "{["


def test_w30_main_demo(capsys):
    run_main(W30)
    out = capsys.readouterr().out
    assert out.startswith("<!doctype html>")
    assert 'data-slide-id="QRB_AUB_001"' in out
