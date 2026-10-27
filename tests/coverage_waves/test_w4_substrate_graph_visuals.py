"""Coverage wave 4 (L3): semantic_substrate engines, topology graph, thermo, visuals.

The Plotly visual builders are exercised against a recording fake ``plotly``
injected into ``sys.modules``, so they run identically whether or not Plotly
is installed (CI does not install it).
"""
from __future__ import annotations

import functools
import json
import sys
import types

import pytest
import yaml

from tests.coverage_waves._loader import load, run_main

DELTA = "semantic_substrate/engines/delta_extractor.py"
TUPLES = "semantic_substrate/engines/tuple_registry_engine.py"
DRIFT = "semantic_substrate/analytics/drift_engine.py"
HOOK = "semantic_substrate/hooks/semantic_commit_hook.py"
GRAPH = "src/topology/engineering_graph_runtime_v1.py"
THERMO = "src/thermo/backend_compare.py"


# ---------------------------------------------------------------- fake plotly
class _Rec:
    def __init__(self, kind, *args, **kwargs):
        self.kind, self.args, self.kwargs = kind, args, kwargs


class _Figure:
    def __init__(self, data=None, layout=None, **kwargs):
        self.data = list(data) if isinstance(data, (list, tuple)) else ([data] if data else [])
        self.layout_obj = layout
        self.layout = {}
        self.yaxes = []

    def add_trace(self, trace, row=None, col=None):
        self.data.append((trace, row, col))

    def update_layout(self, **kwargs):
        self.layout.update(kwargs)

    def update_yaxes(self, **kwargs):
        self.yaxes.append(kwargs)

    def write_html(self, path):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("<html>fake</html>")


@pytest.fixture
def fake_plotly(monkeypatch):
    go = types.ModuleType("plotly.graph_objects")
    go.Figure = _Figure
    for name in ("Bar", "Heatmap", "Scatter", "Scatter3d", "Mesh3d", "Layout"):
        setattr(go, name, functools.partial(_Rec, name))
    subplots = types.ModuleType("plotly.subplots")
    subplots.make_subplots = lambda **kwargs: _Figure()
    pkg = types.ModuleType("plotly")
    pkg.graph_objects, pkg.subplots = go, subplots
    monkeypatch.setitem(sys.modules, "plotly", pkg)
    monkeypatch.setitem(sys.modules, "plotly.graph_objects", go)
    monkeypatch.setitem(sys.modules, "plotly.subplots", subplots)
    return go


@pytest.fixture
def no_plotly(monkeypatch):
    monkeypatch.setitem(sys.modules, "plotly", None)
    monkeypatch.setitem(sys.modules, "plotly.graph_objects", None)
    monkeypatch.setitem(sys.modules, "plotly.subplots", None)


# ---------------------------------------------------------------- delta extractor
@pytest.mark.parametrize(
    ("path", "kind"),
    [("a.yaml", "semantic-config"), ("b.md", "documentation"), ("c.py", "runtime"), ("d.json", "unknown")],
)
def test_classify_change(path, kind):
    assert load(DELTA).classify_change(path) == kind


def test_delta_entry_shape():
    m = load(DELTA)
    entry = m.generate_delta_entry(["x.py", "y.md"], date="2026-10-27")
    assert entry["id"] is None and entry["date"] == "2026-10-27"
    assert entry["added"] == ["x.py", "y.md"]
    assert [f["classification"] for f in entry["files"]] == ["runtime", "documentation"]
    assert m.generate_delta_entry([])["date"]


def test_next_delta_id_rules():
    m = load(DELTA)
    assert m._next_delta_id([]) == "DELTA-0001"
    assert m._next_delta_id([{"id": "DELTA-0007"}, {"id": "DELTA-x"}, {"id": "OTHER"}, {}]) == "DELTA-0008"
    assert m._next_delta_id([{"id": "nope"}]) == "DELTA-0001"


def test_append_delta_to_ledger_roundtrip(tmp_path):
    m = load(DELTA)
    ledger = tmp_path / "ledger.yaml"
    first = m.append_delta_to_ledger(m.generate_delta_entry(["a.py"], date="d"), path=ledger)
    assert first["id"] == "DELTA-0001"
    second = m.append_delta_to_ledger(dict(m.generate_delta_entry(["b.py"]), id="DELTA-0042"), path=ledger)
    assert second["id"] == "DELTA-0042"
    third = m.append_delta_to_ledger(m.generate_delta_entry(["c.py"]), path=ledger)
    assert third["id"] == "DELTA-0043"
    data = yaml.safe_load(ledger.read_text(encoding="utf-8"))
    assert [d["id"] for d in data["deltas"]] == ["DELTA-0001", "DELTA-0042", "DELTA-0043"]


def test_load_ledger_empty_file(tmp_path):
    m = load(DELTA)
    empty = tmp_path / "e.yaml"
    empty.write_text("", encoding="utf-8")
    assert m._load_ledger(empty) == {"version": "0.1.0", "deltas": []}


def test_delta_main_prints_stub(capsys):
    run_main(DELTA)
    assert "semantic-config" in capsys.readouterr().out


# ---------------------------------------------------------------- tuple registry
def _registry(tmp_path, monkeypatch, text):
    m = load(TUPLES)
    reg = tmp_path / "tuple_registry.yaml"
    if text is not None:
        reg.write_text(text, encoding="utf-8")
    monkeypatch.setattr(m, "REGISTRY", reg)
    return m.TupleRegistryEngine()


def test_tuple_lineage_walks_parents(tmp_path, monkeypatch):
    eng = _registry(tmp_path, monkeypatch, """tuples:
  - {tuple_id: T3, parent_id: T2}
  - {tuple_id: T2, parent_id: T1}
  - {tuple_id: T1}
  - {tuple_id: T9, parent_id: GONE}
""")
    assert eng.lineage("T3") == ["T3", "T2", "T1"]
    assert eng.lineage("T9") == ["T9"]
    assert eng.lineage("NOPE") == []
    assert eng.get_tuple("T1") == {"tuple_id": "T1"}


def test_tuple_registry_missing_or_empty(tmp_path, monkeypatch):
    assert _registry(tmp_path, monkeypatch, None).registry == {"tuples": []}
    assert _registry(tmp_path, monkeypatch, "").registry == {"tuples": []}


def test_tuple_registry_main_uses_repo_registry(capsys):
    run_main(TUPLES)
    assert capsys.readouterr().out.strip().startswith("[")


# ---------------------------------------------------------------- drift engine
def test_drift_flags_unknown_files(tmp_path):
    m = load(DRIFT)
    dag = tmp_path / "dag.yaml"
    dag.write_text("branches: []\n", encoding="utf-8")
    res = m.evaluate_semantic_drift({"files": [{"path": "x.bin", "classification": "unknown"},
                                               {"path": "y.py", "classification": "runtime"}]}, dag)
    assert res["finding_count"] == 1 and res["findings"][0]["rule_id"] == "DRIFT-002"
    assert res["drift_score"] == 1 and res["debt_status"] == "healthy"
    assert res["rules_version"] == "0.1.0"


def test_drift_stale_active_branches(tmp_path):
    m = load(DRIFT)
    dag = tmp_path / "dag.yaml"
    dag.write_text("branches:\n  - {id: ROOT, status: active}\n  - {id: B1, status: active}\n", encoding="utf-8")
    res = m.evaluate_semantic_drift({}, dag)
    assert [f["rule_id"] for f in res["findings"]] == ["DRIFT-003"]
    only_root = tmp_path / "root.yaml"
    only_root.write_text("branches:\n  - {id: ROOT, status: active}\n", encoding="utf-8")
    assert m.evaluate_semantic_drift({}, only_root)["finding_count"] == 0


@pytest.mark.parametrize(("unknowns", "status"), [(2, "warning"), (3, "critical")])
def test_drift_status_thresholds(tmp_path, monkeypatch, unknowns, status):
    m = load(DRIFT)
    model = tmp_path / "debt.yaml"
    model.write_text("semantic_debt:\n  thresholds:\n    warning: {min_score: 2}\n    critical: {min_score: 3}\n",
                     encoding="utf-8")
    monkeypatch.setattr(m, "DEBT_MODEL", model)
    dag = tmp_path / "dag.yaml"
    dag.write_text("", encoding="utf-8")
    files = [{"path": f"f{i}", "classification": "unknown"} for i in range(unknowns)]
    assert m.evaluate_semantic_drift({"files": files}, dag)["debt_status"] == status


# ---------------------------------------------------------------- commit hook
@pytest.mark.parametrize(
    ("msg", "ok"),
    [("fix INV-001", True), ("see DELTA-0002", True), ("TUP-0003 lineage", True), ("INV-1 short", False), ("", False)],
)
def test_validate_commit_message(msg, ok):
    assert load(HOOK).validate_commit_message(msg) is ok


@pytest.mark.parametrize(("argv", "code", "needle"), [(["INV-123"], 0, "passed"), ([], 1, "failed")])
def test_hook_main_exit_codes(argv, code, needle, capsys):
    with pytest.raises(SystemExit) as exc:
        run_main(HOOK, argv)
    assert exc.value.code == code
    assert needle in capsys.readouterr().out


# ---------------------------------------------------------------- engineering graph
@pytest.mark.parametrize(
    ("label", "edge"),
    [("MIT link", "signal"), ("mis trip", "interlock"), ("OPC UA", "network"), ("MCS bus", "network"),
     ("PCW loop", "flow"), ("hvac duct", "flow"), ("cable", "topology")],
)
def test_classify_interface(label, edge):
    m = load(GRAPH)
    assert m.EngineeringTopologyRuntime().classify_interface(label).value == edge


def test_graph_neighbors_and_export():
    m = load(GRAPH)
    rt = m.EngineeringTopologyRuntime()
    rt.register_graph(m.EngineeringGraph("g", "G"))
    for nid in ("A", "B", "C"):
        rt.add_node("g", m.SemanticNode(nid, nid, m.NodeType.SUBSYSTEM))
    rt.add_edge("g", m.SemanticEdge("A", "B", m.EdgeType.FLOW, "PCW"))
    rt.add_edge("g", m.SemanticEdge("C", "A", m.EdgeType.SIGNAL, "MIT"))
    assert [n.node_id for n in rt.neighbors("g", "A")] == ["B"]
    assert rt.neighbors("g", "B") == []
    data = json.loads(rt.export_graph_json("g"))
    assert data["title"] == "G" and len(data["edges"]) == 2
    assert data["edges"][0]["confidence"] == 1.0
    with pytest.raises(KeyError):
        rt.neighbors("missing", "A")


def test_graph_main_demo(capsys):
    run_main(GRAPH)
    data = json.loads(capsys.readouterr().out)
    assert data["edges"][0]["edge_type"] == "flow"


# ---------------------------------------------------------------- thermo
def test_backend_compare_scaffold():
    m = load(THERMO)
    (res,) = m.BackendComparisonEngine().compare()
    assert (res.backend_a, res.backend_b) == ("fallback", "nist_reference")
    assert 0 <= res.scientific_confidence <= 100
    assert min(res.delta_h, res.delta_s, res.delta_rho, res.delta_cp) >= 0


# ---------------------------------------------------------------- metric_display
@pytest.mark.parametrize(
    ("key", "name"),
    [("ci_cd", "CI/CD"), ("publication_readiness", "Publication"), ("thermo_dynamics", "Thermo Dynamics")],
)
def test_normalize_metric_name(key, name):
    from visuals import metric_display
    assert metric_display.normalize_metric_name(key) == name


@pytest.mark.parametrize(("name", "abbr"), [("Governance", "Gov"), ("Publication", "Pub"), ("Federation", "Federa")])
def test_abbreviate_metric_name(name, abbr):
    from visuals import metric_display
    assert metric_display.abbreviate_metric_name(name) == abbr


# ---------------------------------------------------------------- plotly visuals
SIMPLE_VISUALS = [
    ("visuals.backend_residual_heatmap", "build_backend_residual_heatmap", "backend_residual_heatmap.html"),
    ("visuals.thermo_kpi_overlay", "build_thermo_kpi_overlay", "thermo_kpi_overlay.html"),
]


@pytest.mark.parametrize(("mod", "fn", "html"), SIMPLE_VISUALS)
def test_simple_visual_builds_and_writes(mod, fn, html, fake_plotly, tmp_path, monkeypatch, capsys):
    module = __import__(mod, fromlist=[fn])
    fig = getattr(module, fn)()
    assert fig.layout["title"]
    assert fig.data[0].kind in ("Heatmap", "Bar")
    monkeypatch.chdir(tmp_path)
    module.main()
    assert (tmp_path / "outputs" / html).read_text(encoding="utf-8") == "<html>fake</html>"
    assert "generated" in capsys.readouterr().out


@pytest.mark.parametrize(("mod", "fn"), [(m, f) for m, f, _ in SIMPLE_VISUALS])
def test_simple_visual_without_plotly_exits(mod, fn, no_plotly):
    module = __import__(mod, fromlist=[fn])
    with pytest.raises(SystemExit, match="Plotly is required"):
        getattr(module, fn)()


def test_agent_telemetry_timeline(fake_plotly, tmp_path, capsys):
    from visuals import agent_telemetry_timeline as atl
    metrics = {"agents": {"a": 50, "b": 70}, "runtime_targets": {"t": 90}, "wave": "W7",
               "architecture_score_before": 60, "architecture_score_target": 80, "completion_percent": 42}
    fig = atl.build_telemetry_figure(metrics)
    (bar1, r1, c1), (bar2, r2, c2) = fig.data
    assert bar1.kwargs["x"] == ["a", "b"] and bar1.kwargs["y"] == [50, 70] and (r1, c1) == (1, 1)
    assert bar2.kwargs["y"] == [90] and (r2, c2) == (1, 2)
    assert "W7" in fig.layout["title"] and "42%" in fig.layout["title"]
    mfile = tmp_path / "m.json"
    mfile.write_text(json.dumps(metrics), encoding="utf-8")
    out = tmp_path / "o" / "t.html"
    assert atl.main(["--metrics", str(mfile), "--output", str(out)]) == 0
    assert out.is_file()
    assert atl.main(["--metrics", str(tmp_path / "none.json")]) == 1
    assert "FAIL: metrics file not found" in capsys.readouterr().out


def test_agent_telemetry_defaults_and_no_plotly(fake_plotly, no_plotly):
    from visuals import agent_telemetry_timeline as atl
    with pytest.raises(SystemExit):
        atl.build_telemetry_figure({})


def test_orchestration_dependency_graph(fake_plotly, tmp_path, capsys):
    from visuals import orchestration_dependency_graph as odg
    topo = {"root": "R", "agents": [{"id": "a1", "role": "integrity"}, {"id": "a2", "role": "mystery"}]}
    fig = odg.build_dependency_graph(topo)
    edges, nodes = fig.data
    assert edges.kwargs["x"][:3] == [0.0, 1.0, None]
    assert nodes.kwargs["text"][0] == "R" and "(integrity)" in nodes.kwargs["text"][1]
    assert nodes.kwargs["marker"]["color"] == ["#fbbf24", "#34d399", odg.DEFAULT_COLOUR]
    assert nodes.kwargs["marker"]["size"] == [20, 14, 14]
    tfile = tmp_path / "t.json"
    tfile.write_text(json.dumps(topo), encoding="utf-8")
    out = tmp_path / "o" / "g.html"
    assert odg.main(["--topology", str(tfile), "--output", str(out)]) == 0 and out.is_file()
    assert odg.main(["--topology", str(tmp_path / "missing.json")]) == 1
    assert "FAIL: topology file not found" in capsys.readouterr().out


def test_orchestration_graph_empty_and_no_plotly(fake_plotly, no_plotly):
    from visuals import orchestration_dependency_graph as odg
    with pytest.raises(SystemExit):
        odg.build_dependency_graph({})


def test_orchestration_graph_root_only(fake_plotly):
    from visuals import orchestration_dependency_graph as odg
    edges, nodes = odg.build_dependency_graph({}).data
    assert edges.kwargs["x"] == [] and nodes.kwargs["text"] == ["ROOT"]


# ---------------------------------------------------------------- convergence surface
WAVES_YAML = """waves:
  - {wave: W1}
  - {wave: W2}
wave_metrics:
  renderer_governance_progress: {W1: 10, W2: 20}
  thermodynamic_progress: {W1: 1, W2: 2.5}
  publication_progress: {W1: 5, W2: 6}
"""


def _manifest(tmp_path, text):
    p = tmp_path / "w.yaml"
    p.write_text(text, encoding="utf-8")
    return p


def test_convergence_load_metrics(tmp_path):
    from visuals import convergence_surface_3d as cs
    waves, gov, pub, thermo = cs.load_convergence_metrics(_manifest(tmp_path, WAVES_YAML))
    assert waves == ["W1", "W2"] and gov == [10.0, 20.0] and pub == [5.0, 6.0] and thermo == [1.0, 2.5]


@pytest.mark.parametrize(
    ("text", "match"),
    [
        ("- 1\n", "must be a mapping"),
        ("waves: 3\n", '"waves" must be a list'),
        ("waves: [{x: 1}]\n", r"waves\[0\] must include wave"),
        ("waves: [{wave: W1}]\nwave_metrics: []\n", '"wave_metrics" must be a mapping'),
        ("waves: [{wave: W1}]\nwave_metrics: {renderer_governance_progress: 3}\n", "must be a mapping"),
        ("waves: [{wave: W1}]\nwave_metrics: {renderer_governance_progress: {W1: true}}\n", "must be numeric"),
        ("waves: [{wave: W1}]\nwave_metrics: {renderer_governance_progress: {}}\n", "must be numeric"),
    ],
)
def test_convergence_manifest_validation(tmp_path, text, match):
    from visuals import convergence_surface_3d as cs
    with pytest.raises(ValueError, match=match):
        cs.load_convergence_metrics(_manifest(tmp_path, text))


def test_convergence_missing_manifest(tmp_path):
    from visuals import convergence_surface_3d as cs
    with pytest.raises(FileNotFoundError):
        cs.load_convergence_metrics(tmp_path / "none.yaml")


def test_convergence_figure_and_main(fake_plotly, tmp_path, monkeypatch, capsys):
    from visuals import convergence_surface_3d as cs
    manifest = _manifest(tmp_path, WAVES_YAML)
    fig = cs.build_convergence_surface_figure(manifest)
    (path, _, _), (mesh, _, _) = fig.data
    assert path.kind == "Scatter3d" and path.kwargs["text"] == ["W1", "W2"]
    assert mesh.kind == "Mesh3d" and mesh.kwargs["z"] == [1.0, 2.5]
    out = tmp_path / "html" / "c.html"
    monkeypatch.setattr(cs, "DEFAULT_MANIFEST_PATH", manifest)
    monkeypatch.setattr(cs, "DEFAULT_OUTPUT_PATH", out)
    monkeypatch.setattr(cs.build_convergence_surface_figure, "__defaults__", (manifest,))
    cs.main()
    assert out.is_file() and "generated" in capsys.readouterr().out


def test_convergence_no_plotly(no_plotly, tmp_path):
    from visuals import convergence_surface_3d as cs
    with pytest.raises(SystemExit):
        cs.build_convergence_surface_figure(_manifest(tmp_path, WAVES_YAML))


# ---------------------------------------------------------------- incubator dashboard
PHASE_MAP = {
    "dmaic_phases": {
        "DEFINE": {"incubator_categories": ["INCUBATOR"], "incubator_themes": ["scope"]},
        "MEASURE": {"incubator_categories": ["ANALYSIS"], "incubator_themes": ["metrics"]},
        "CONTROL": {"incubator_categories": ["CONTROL_OPS"], "incubator_themes": ["ops"]},
    },
    "routing_rules": [{"condition": "unmatched", "default_phase": "IMPROVE"}],
}


@pytest.mark.parametrize(
    ("tuple_", "phase"),
    [
        ({"category": "ANALYSIS", "theme": "metrics"}, "MEASURE"),
        ({"category": "CONTROL_OPS", "theme": "other"}, "CONTROL"),
        ({"category": "ZZZ", "theme": "scope"}, "DEFINE"),
        ({"category": "ZZZ", "theme": "zzz"}, "IMPROVE"),
    ],
)
def test_resolve_phase_priorities(tuple_, phase):
    from visuals import incubator_dmaic_dashboard as idd
    assert idd._resolve_phase(tuple_, PHASE_MAP) == phase


def test_resolve_phase_hard_default():
    from visuals import incubator_dmaic_dashboard as idd
    assert idd._resolve_phase({}, {"routing_rules": [{"condition": "other"}]}) == "DEFINE"


def test_load_tuples_skips_schema_and_non_tuples(tmp_path):
    from visuals import incubator_dmaic_dashboard as idd
    (tmp_path / "a.yml").write_text("id: A\ncategory: ANALYSIS\n", encoding="utf-8")
    (tmp_path / "b.yaml").write_text("id: B\n", encoding="utf-8")
    (tmp_path / "session_tuple_schema.yml").write_text("id: SCHEMA\n", encoding="utf-8")
    (tmp_path / "c.yml").write_text("- not a dict\n", encoding="utf-8")
    assert [t["id"] for t in idd._load_tuples(tmp_path)] == ["A", "B"]


def test_build_dmaic_dashboard(fake_plotly):
    from visuals import incubator_dmaic_dashboard as idd
    tuples = [
        {"id": "A", "category": "ANALYSIS", "theme": "metrics", "date": "2026-01-01", "title": "t"},
        {"id": "B", "category": "WEIRD", "theme": "x"},
        {"id": "C", "theme": "scope"},
    ]
    fig = idd.build_dmaic_dashboard(tuples, PHASE_MAP)
    bar = fig.data[0][0]
    assert bar.kwargs["y"] == [1, 1, 0, 1, 0]
    scatter_names = [t.kwargs["name"] for t, _, _ in fig.data[1:]]
    assert scatter_names == ["ANALYSIS", "INCUBATOR", "WEIRD"]
    assert "3 tuple(s)" in fig.layout["title"] and "MEASURE: 1" in fig.layout["title"]
    assert fig.yaxes[0]["categoryarray"] == idd.DMAIC_ORDER


def test_dmaic_dashboard_no_plotly(no_plotly):
    from visuals import incubator_dmaic_dashboard as idd
    with pytest.raises(SystemExit):
        idd.build_dmaic_dashboard([], PHASE_MAP)


def test_dmaic_dashboard_main(fake_plotly, tmp_path, monkeypatch, capsys):
    from visuals import incubator_dmaic_dashboard as idd
    inc = tmp_path / "inc"
    inc.mkdir()
    (inc / "a.yml").write_text("id: A\ncategory: ANALYSIS\ntheme: metrics\n", encoding="utf-8")
    pmap = tmp_path / "map.yml"
    pmap.write_text(yaml.safe_dump(PHASE_MAP), encoding="utf-8")
    out = tmp_path / "o" / "d.html"
    monkeypatch.setattr(sys, "argv", ["x", "--incubator", str(inc), "--map", str(pmap), "--output", str(out)])
    assert idd.main() == 0
    assert out.is_file() and "generated" in capsys.readouterr().out
