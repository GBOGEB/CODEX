"""Coverage wave 9 (L3): the ``src/**/*_runtime_v1`` semantic runtime family
(adaptive mesh, interactive knowledge, ecosystem, governance mesh, autonomous
orchestrator, copilot, semantic reasoning, continuity fabric).
"""
from __future__ import annotations

import json

import pytest

from tests.coverage_waves._loader import load, run_main

ADAPT = "src/adaptive/adaptive_engineering_intelligence_mesh_runtime_v1.py"
KNOW = "src/runtime/interactive_knowledge_runtime_v1.py"
ECO = "src/ecosystem/distributed_semantic_ecosystem_runtime_v1.py"
GOV = "src/governance/semantic_governance_mesh_runtime_v1.py"
ORCH = "src/orchestration/autonomous_engineering_orchestrator_v1.py"
COPILOT = "src/copilot/recursive_engineering_copilot_runtime_v1.py"
REASON = "src/ai/engineering_semantic_reasoning_runtime_v1.py"
CONT = "src/continuity/semantic_continuity_fabric_runtime_v1.py"
ALL = [ADAPT, KNOW, ECO, GOV, ORCH, COPILOT, REASON, CONT]


# ---------------------------------------------------------------- adaptive mesh
@pytest.mark.parametrize(
    ("interfaces", "res", "sync", "topo", "align"),
    [
        ([], 0.88, 0.86, 0.91, 0.89),
        (["MIS", "MIT"], 0.88, 0.89, 0.91, 0.93),
        (["HVAC", "PCW"], 0.93, 0.86, 0.94, 0.89),
    ],
)
def test_adaptive_resilience(interfaces, res, sync, topo, align):
    m = load(ADAPT)
    p = m.AdaptiveEngineeringIntelligenceMeshRuntime().analyze_resilience({"label": "S", "i": interfaces})
    assert p.subsystem == "S"
    assert (p.resilience_score, p.synchronization_health, p.topology_integrity, p.semantic_alignment) == \
        pytest.approx((res, sync, topo, align))


def test_adaptive_optimize_and_signals():
    m = load(ADAPT)
    rt = m.AdaptiveEngineeringIntelligenceMeshRuntime()
    rt.register_signal(m.AdaptiveSignal("s1", "S", m.AdaptationMode.RECOVER, "r", 0.9))
    assert list(rt.active_signals) == ["s1"]
    ev = rt.optimize_runtime({"label": "S", "i": ["HVAC", "MIS", "PCW"]})
    assert ev.event_id == "opt::S" and len(ev.optimization_actions) == 3
    assert ev.expected_convergence_gain == pytest.approx(0.12)
    bare = rt.optimize_runtime({})
    assert bare.event_id == "opt::unknown" and bare.optimization_actions == []
    assert bare.expected_convergence_gain == pytest.approx(0.04)
    assert json.loads(rt.export_json(bare))["affected_domains"] == ["thermal", "controls", "runtime"]
    assert rt.analyze_resilience({}).subsystem == "unknown"


# ---------------------------------------------------------------- interactive knowledge
def test_knowledge_search_scores_and_order():
    m = load(KNOW)
    rt = m.InteractiveKnowledgeRuntime()
    rt.register_node("A", {"label": "Alpha", "i": ["pcw", "hvac"]})
    rt.register_node("B", {"i": ["pcw"]})
    rt.register_node("C", {"label": "none"})
    res = rt.semantic_search("PCW HVAC")
    assert [(r.node_id, r.score, r.matched_terms) for r in res] == [("A", 1.0, ["pcw", "hvac"]),
                                                                    ("B", 0.5, ["pcw"])]
    assert res[1].label == "B"
    assert rt.semantic_search("") == []


def test_knowledge_runtime_view():
    m = load(KNOW)
    rt = m.InteractiveKnowledgeRuntime()
    rt.register_edge("A", "B")
    rt.register_edge("A", "C")
    ev = m.EvidenceReference("e1", "T", "p.png", "EvidenceCard", 0.9)
    rt.link_evidence("A", ev)
    view = rt.generate_runtime_view("A")
    assert view.visible_nodes == ["A", "B", "C"] and view.visible_edges == ["A->B", "A->C"]
    assert view.evidence_refs == [ev] and view.view_id == "runtime::A" and view.title.endswith("A")
    lonely = json.loads(rt.export_runtime_view("Z"))
    assert lonely["visible_nodes"] == ["Z"] and lonely["evidence_refs"] == []


# ---------------------------------------------------------------- ecosystem
def test_ecosystem_sync_and_cluster():
    m = load(ECO)
    rt = m.DistributedSemanticEcosystemRuntime()
    a = m.FederatedSemanticNode("a", m.EcosystemDomain.THERMAL, "S", ["PCW", "HVAC", "x"])
    b = m.FederatedSemanticNode("b", m.EcosystemDomain.CONTROLS, "T", ["HVAC", "x", "MIS"])
    rt.register_node(a)
    rt.register_node(b)
    ev = rt.synchronize_domains(a, b)
    assert sorted(ev.propagated_context) == ["HVAC", "x"] and ev.confidence == pytest.approx(0.8)
    assert rt.sync_events[ev.event_id] is ev and ev.event_id == "sync::a::b"
    big = m.FederatedSemanticNode("c", m.EcosystemDomain.HVAC, "U", [str(i) for i in range(20)])
    assert rt.synchronize_domains(big, big).confidence == 0.99
    cl = rt.create_cluster("k", list(m.EcosystemDomain), ["S"])
    assert cl.recursive_alignment_score == pytest.approx(0.93)
    assert rt.create_cluster("z", list(m.EcosystemDomain) * 3, []).recursive_alignment_score == 0.99
    assert json.loads(rt.export_json(cl))["participating_domains"][0] == "thermal"


# ---------------------------------------------------------------- governance mesh
def test_governance_findings_and_trust():
    m = load(GOV)
    rt = m.SemanticGovernanceMeshRuntime()
    rt.register_policy(m.SemanticPolicy("p", "c", "r", m.GovernanceSeverity.ERROR))
    assert list(rt.policies) == ["p"]
    f = rt.validate_subsystem({"label": "S", "i": ["MIS", "HVAC"]})
    assert [(x.finding_id, x.severity.value) for x in f] == [("gov-mis-mit", "warning"), ("gov-hvac-cooling", "info")]
    assert rt.validate_subsystem({"i": ["MIS", "MIT", "HVAC", "PCW"]}) == []
    t = rt.calculate_trust_score({"label": "S", "i": ["MIS", "MIT", "HVAC", "PCW"]})
    assert (t.topology_score, t.synchronization_score, t.governance_score) == pytest.approx((0.92, 0.88, 0.93))
    plain = rt.calculate_trust_score({})
    assert plain.subsystem == "unknown" and plain.evidence_score == 0.92
    assert json.loads(rt.export_json(t))["subsystem"] == "S"


@pytest.mark.xfail(
    strict=True,
    reason=(
        "production_defect: semantic_governance_mesh_runtime_v1 (and engineering_semantic_reasoning_runtime_v1) "
        "match interface tokens as raw substrings of the JSON payload, so words like 'TRANSMISSION' trigger "
        "MIS findings for subsystems that have no MIS interface"
    ),
)
def test_governance_ignores_mis_inside_other_words():
    m = load(GOV)
    assert m.SemanticGovernanceMeshRuntime().validate_subsystem({"label": "Transmission line"}) == []


# ---------------------------------------------------------------- autonomous orchestrator
def test_orchestrator_tasks_agents_recommendations():
    m = load(ORCH)
    rt = m.AutonomousEngineeringOrchestrator()
    rt.register_agent(m.RuntimeAgent("ag", "thermal"))
    task = m.SemanticTask("t1", "T", m.TaskPriority.HIGH, m.WorkflowState.PENDING, ["HVAC loop", "PCW", "MIS"])
    rt.create_task(task)
    rt.assign_task("t1", "ag")
    rt.transition_task("t1", m.WorkflowState.ESCALATED)
    assert rt.agents["ag"].active_tasks == ["t1"] and rt.tasks["t1"].workflow_state == m.WorkflowState.ESCALATED
    rec = rt.generate_recommendation(task)
    assert rec.category == "thermal_dependency_review" and rec.confidence == pytest.approx(0.94)
    assert len(rec.rationale) == 2 and rec.recommendation_id == "rec::t1"
    generic = rt.generate_recommendation(m.SemanticTask("t2", "T", m.TaskPriority.LOW, m.WorkflowState.PENDING))
    assert (generic.category, generic.confidence, generic.rationale) == ("general_review", 0.72, [])
    mis_only = rt.generate_recommendation(m.SemanticTask("t3", "T", m.TaskPriority.LOW, m.WorkflowState.PENDING,
                                                         ["mis"]))
    assert mis_only.category == "general_review" and mis_only.confidence == pytest.approx(0.75)
    assert json.loads(rt.export_json(rec))["category"] == "thermal_dependency_review"
    with pytest.raises(KeyError):
        rt.assign_task("t1", "nobody")


# ---------------------------------------------------------------- copilot
def test_copilot_review_with_and_without_memory():
    m = load(COPILOT)
    rt = m.RecursiveEngineeringCopilotRuntime()
    empty = rt.recursive_review("S")
    assert empty.findings == [] and empty.convergence_score == pytest.approx(0.82)
    rt.store_memory(m.SemanticMemory("m", "S", inferred_risks=["HVAC dependency", "MIS integrity"],
                                     recommendations=["r1"]))
    loop = rt.recursive_review("S")
    assert loop.findings[0] == "r1" and len(loop.findings) == 3
    assert loop.unresolved_items == ["HVAC dependency", "MIS integrity"]
    assert loop.convergence_score == pytest.approx(0.92)
    resp = rt.generate_copilot_response("S", m.CopilotMode.REVIEW)
    assert resp.confidence == pytest.approx(0.92) and resp.actions == loop.findings
    cold = rt.generate_copilot_response("X", m.CopilotMode.PLANNING)
    assert cold.confidence == 0.78 and cold.actions == [] and cold.copilot_id == "copilot::X"
    assert json.loads(rt.export_json(cold))["mode"] == "planning"


def test_copilot_partial_risks():
    m = load(COPILOT)
    rt = m.RecursiveEngineeringCopilotRuntime()
    rt.store_memory(m.SemanticMemory("m", "S", inferred_risks=["MIS integrity"]))
    assert rt.recursive_review("S").convergence_score == pytest.approx(0.86)


# ---------------------------------------------------------------- semantic reasoning
def test_reasoning_intent():
    m = load(REASON)
    rt = m.EngineeringSemanticReasoningRuntime()
    plain = rt.infer_intent({})
    assert (plain.intent_id, plain.category, plain.confidence, plain.reasoning) == ("unknown", "general_system", 0.65, [])
    it = rt.infer_intent({"label": "N", "i": ["PCW", "HVAC"]})
    assert it.category == "environmental_control" and it.confidence == pytest.approx(0.83)
    assert it.reasoning[-1].startswith("Combined HVAC and PCW")
    capped = rt.infer_intent({"i": list(rt.UTILITY_KEYWORDS) * 2})
    assert capped.confidence == pytest.approx(0.99) or capped.confidence < 0.99


def test_reasoning_anomalies_and_dependencies():
    m = load(REASON)
    rt = m.EngineeringSemanticReasoningRuntime()
    an = rt.detect_anomalies([{"label": "A", "i": ["MIS"]}, {"label": "B", "i": ["MIS", "MIT"]}, {"i": []}])
    assert [a.anomaly_id for a in an] == ["anomaly::A"] and an[0].affected_nodes == ["A"]
    d = rt.infer_dependencies({"label": "S", "i": ["PCW"]}, {"label": "T", "i": ["HVAC"]})
    assert (d.dependency_type, d.confidence) == ("thermal_support", 0.91)
    d = rt.infer_dependencies({"i": ["MCS", "PCW"]}, {"i": ["MIT", "HVAC"]})
    assert (d.source, d.target, d.dependency_type) == ("unknown", "unknown", "control_signal")
    g = rt.infer_dependencies({}, {})
    assert (g.dependency_type, g.confidence) == ("topology", 0.72)
    assert json.loads(rt.export_json(g))["explanation"].startswith("Generic")


# ---------------------------------------------------------------- continuity fabric
def test_continuity_fabric_lifecycle(monkeypatch):
    m = load(CONT)
    clock = iter([100.0, 100.5, 200.0, 200.2])
    monkeypatch.setattr(m.time, "time", lambda: next(clock))
    rt = m.SemanticContinuityFabricRuntime()
    fab = rt.register_fabric("f", "S")
    assert fab.continuity_score == 0.75 and rt.restore_latest_snapshot("f") is None
    s1 = rt.create_snapshot("S", ["n"], ["e"], ["g"], ["m"])
    s2 = rt.create_snapshot("S", [], [], [], [])
    assert (s1.snapshot_id, s1.timestamp, s2.snapshot_id) == ("snap::S::100", 100.5, "snap::S::200")
    rt.attach_snapshot_to_fabric("f", s1.snapshot_id)
    rt.attach_snapshot_to_fabric("f", s1.snapshot_id)
    rt.attach_snapshot_to_fabric("f", s2.snapshot_id)
    assert fab.snapshots == [s1.snapshot_id, s2.snapshot_id] and fab.continuity_score == pytest.approx(0.82)
    ev = rt.create_lineage_event("S", s1.snapshot_id, s2.snapshot_id, "evolve", ["why"])
    assert ev.event_id == "lineage::S::1"
    rt.attach_lineage_to_fabric("f", ev.event_id)
    rt.attach_lineage_to_fabric("f", ev.event_id)
    assert fab.lineage_events == [ev.event_id] and fab.continuity_score == pytest.approx(0.86)
    restored = rt.restore_latest_snapshot("f")
    assert restored is s2 and restored.continuity_state == m.ContinuityState.RESTORED
    assert json.loads(rt.export_json(ev))["source_snapshot"] == s1.snapshot_id


def test_continuity_score_caps():
    m = load(CONT)
    rt = m.SemanticContinuityFabricRuntime()
    rec = m.ContinuityFabricRecord("f", "S", snapshots=list("abcdefgh"), lineage_events=list("abcdefgh"))
    assert rt.calculate_continuity_score(rec) == pytest.approx(0.99)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "production_defect: semantic_continuity_fabric_runtime_v1 builds snapshot ids from int(time.time()), "
        "so two snapshots of one subsystem within the same second share an id and the first is overwritten"
    ),
)
def test_continuity_snapshots_in_same_second_are_kept(monkeypatch):
    m = load(CONT)
    monkeypatch.setattr(m.time, "time", lambda: 1234.0)
    rt = m.SemanticContinuityFabricRuntime()
    rt.create_snapshot("S", ["a"], [], [], [])
    rt.create_snapshot("S", ["b"], [], [], [])
    assert len(rt.snapshots) == 2


# ---------------------------------------------------------------- demos
@pytest.mark.parametrize("path", ALL)
def test_main_demos_print_json(path, capsys):
    run_main(path)
    out = capsys.readouterr().out
    assert "{" in out and '"' in out
