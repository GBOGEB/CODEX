"""Coverage wave 3 (L3): ``delta1_bridge``, ``core_bridge`` and ``src/reliability``.

All filesystem work happens under ``tmp_path``; no repo file is written.
"""
from __future__ import annotations

import json

import pytest

from core_bridge import absorb, render
from delta1_bridge import __main__ as d1cli
from delta1_bridge import adapter, ranking, schema
from tests.coverage_waves._loader import load, run_main

GOOD_METRICS = {
    "timestamp": "t", "sha": "s", "quality_score": 80, "total_commits": 1,
    "python_files": 2, "test_files": 3, "total_loc": 4, "workflows": 5,
    "phase_scores": {"define": {"files": 1, "score": 2, "weight": 3}},
}


# ---------------------------------------------------------------- schema
def test_validate_metrics_accepts_complete_payload():
    assert schema.validate_metrics(GOOD_METRICS) == []


def test_validate_metrics_reports_every_issue_kind():
    bad = dict(GOOD_METRICS, quality_score=101, workflows="x",
               phase_scores={"a": 1, "b": {"files": 1}})
    del bad["sha"]
    issues = schema.validate_metrics(bad)
    assert "missing required key: sha" in issues
    assert "key 'workflows' must be numeric, got str" in issues
    assert "quality_score must be within [0, 100]" in issues
    assert "phase_scores['a'] must be a mapping" in issues
    assert "phase_scores['b'] missing 'score'" in issues


def test_validate_metrics_non_mapping_inputs():
    assert schema.validate_metrics([1]) == ["metrics payload must be a mapping, got list"]
    assert "phase_scores must be a mapping" in schema.validate_metrics(dict(GOOD_METRICS, phase_scores=[1]))


def test_load_and_validate_metrics_paths(tmp_path):
    missing = schema.load_and_validate_metrics(tmp_path / "none.json")
    assert missing["found"] is False and missing["valid"] is False
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    res = schema.load_and_validate_metrics(broken)
    assert res["found"] is True and res["issues"][0].startswith("could not parse JSON")
    good = tmp_path / "good.json"
    good.write_text(json.dumps(GOOD_METRICS), encoding="utf-8")
    res = schema.load_and_validate_metrics(good)
    assert res["valid"] is True and res["data"]["sha"] == "s"


# ---------------------------------------------------------------- ranking
DEMO_IDS = ["a", "b", "c"]
DEMO_CMP = [
    {"a": "a", "b": "b", "a_score": 2, "b_score": 1},
    {"a": "a", "b": "c", "a_score": 3, "b_score": 1},
    {"a": "b", "b": "c", "a_score": 2, "b_score": 1},
]


@pytest.mark.parametrize(
    ("ids", "cmp"),
    [(["a"], []), (["a", "a"], []), (["a", "b"], [{"a": "a", "b": "a"}]), (["a", "b"], [{"a": "a", "b": "z"}])],
)
def test_validate_rejects_bad_input(ids, cmp):
    with pytest.raises(ValueError):
        ranking._validate(ids, cmp)


def test_wins_matrix_counts_ties_as_half():
    wins = ranking._wins_matrix(["a", "b"], [
        {"a": "a", "b": "b", "a_score": 1, "b_score": 1},
        {"a": "a", "b": "b", "a_score": 0, "b_score": 1},
    ])
    assert wins == [[0.0, 0.5], [1.5, 0.0]]


def test_fallback_fit_orders_by_wins(monkeypatch):
    monkeypatch.setattr(ranking, "CANONICAL_BT_AVAILABLE", False)
    res = ranking.fit_bradley_terry(DEMO_IDS, DEMO_CMP, iterations=200)
    assert res["engine"] == "fallback"
    assert res["ranking"] == ["a", "b", "c"]
    assert sum(res["strengths"].values()) == pytest.approx(1.0)
    assert 1 <= res["iterations"] <= 200
    assert ranking.rank_pairwise(DEMO_IDS, DEMO_CMP, iterations=50) == ["a", "b", "c"]


def test_fallback_fit_converges_early_on_symmetric_ties():
    res = ranking._fallback_fit(["a", "b"], [{"a": "a", "b": "b", "a_score": 1, "b_score": 1}])
    assert res["iterations"] == 1
    assert res["strengths"] == {"a": 0.5, "b": 0.5}


def test_fallback_item_without_games_keeps_strength():
    res = ranking._fallback_fit(["a", "b", "c"], [{"a": "a", "b": "b", "a_score": 1, "b_score": 1}], iterations=3)
    assert set(res["strengths"]) == {"a", "b", "c"}


def test_normalize_for_canonical():
    out = ranking._normalize_for_canonical([
        {"a": "x", "b": "y", "a_score": 3, "b_score": 1},
        {"a": "x", "b": "y", "a_score": 0, "b_score": 0},
    ])
    assert out[0]["a_score"] == 0.75 and out[0]["b_score"] == 0.25
    assert out[1]["a_score"] == out[1]["b_score"] == 0.5


def test_canonical_path_adds_ranking_and_engine(monkeypatch):
    seen = {}

    def fake(ids, comparisons, iterations, tolerance):
        seen["cmp"] = comparisons
        return {"strengths": {"a": 0.2, "b": 0.8}}

    monkeypatch.setattr(ranking, "CANONICAL_BT_AVAILABLE", True)
    monkeypatch.setattr(ranking, "_canonical_fit", fake)
    res = ranking.fit_bradley_terry(["a", "b"], [{"a": "a", "b": "b", "a_score": 1, "b_score": 3}])
    assert res == {"strengths": {"a": 0.2, "b": 0.8}, "engine": "canonical", "ranking": ["b", "a"]}
    assert seen["cmp"][0]["b_score"] == 0.75


def test_canonical_path_wraps_non_dict(monkeypatch):
    monkeypatch.setattr(ranking, "CANONICAL_BT_AVAILABLE", True)
    monkeypatch.setattr(ranking, "_canonical_fit", lambda *a, **k: [0.1, 0.9])
    assert ranking.fit_bradley_terry(["a", "b"], []) == {"strengths": [0.1, 0.9], "engine": "canonical"}


# ---------------------------------------------------------------- adapter
def _codex_like(root, metrics=GOOD_METRICS, manifest=True):
    (root / "src").mkdir(parents=True)
    (root / "src" / "bridge_adapter.py").write_text("", encoding="utf-8")
    if metrics is not None:
        (root / "docs" / "api").mkdir(parents=True)
        (root / "docs" / "api" / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
    if manifest:
        (root / "federation").mkdir()
        (root / "federation" / "manifest.yaml").write_text("x: 1\n", encoding="utf-8")
    return root


def test_detect_repo_by_markers(tmp_path):
    assert adapter.detect_repo(tmp_path) is None
    (tmp_path / "ocd-adr").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "federation.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "bridge_adapter.py").write_text("", encoding="utf-8")
    assert adapter.detect_repo(tmp_path).repo == "GBOGEB/cryoplant-project"


def test_status_unknown(tmp_path):
    res = adapter.federation_status(tmp_path)
    assert res["status"] == "unknown" and res["repo"] is None


def test_status_ok(tmp_path):
    res = adapter.federation_status(_codex_like(tmp_path))
    assert res["status"] == "ok" and res["repo"] == "GBOGEB/CODEX"
    assert res["manifest_path"].replace("\\", "/") == "federation/manifest.yaml"
    assert any(d.startswith("metrics OK") for d in res["details"])


def test_status_degraded_invalid_metrics(tmp_path):
    res = adapter.federation_status(_codex_like(tmp_path, metrics={"sha": 1}, manifest=False))
    assert res["status"] == "degraded"
    assert any(d.startswith("metrics INVALID") for d in res["details"])
    # CODEX lists src/bridge_adapter.py as both marker and manifest candidate.
    assert res["manifest_path"].replace("\\", "/") == "src/bridge_adapter.py"


def test_status_error_and_explicit_descriptor(tmp_path):
    res = adapter.federation_status(tmp_path, descriptor=adapter.KNOWN_REPOS[1])
    assert res["status"] == "error" and res["plane"] == "runtime"
    assert res["details"] == ["metrics MISSING", "manifest MISSING"]


def test_assimilate_carries_context(tmp_path):
    res = adapter.assimilate({"k": 1}, repo_root=_codex_like(tmp_path))
    assert res["context"] == {"k": 1} and res["status"] == "ok"
    assert adapter.assimilate(repo_root=tmp_path)["context"] == {}
    assert adapter.GREEK_TRACE_SEQUENCE[0] == "alpha"


# ---------------------------------------------------------------- CLI
def test_cli_status_text_and_json(tmp_path, capsys):
    root = _codex_like(tmp_path)
    assert d1cli.main(["status", "--repo-root", str(root)]) == 0
    assert "plane   : governance" in capsys.readouterr().out
    assert d1cli.main(["status", "--repo-root", str(tmp_path / "x"), "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "unknown"


def test_cli_validate_metrics(tmp_path, capsys):
    good = tmp_path / "m.json"
    good.write_text(json.dumps(GOOD_METRICS), encoding="utf-8")
    assert d1cli.main(["validate-metrics", str(good)]) == 0
    capsys.readouterr()
    assert d1cli.main(["validate-metrics", str(tmp_path / "no.json")]) == 1


def test_cli_rank_demo(capsys):
    assert d1cli.main(["rank-demo"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["ranking"][0] == "artifact_a"
    assert "canonical_engine_available" in out


def test_cli_requires_command():
    with pytest.raises(SystemExit):
        d1cli.main([])


# ---------------------------------------------------------------- core_bridge
DASH = """<html><body>
<h3>Implementation Gaps (Current Stub)</h3>
  <ul><li>gap</li></ul>
  <p class="muted">muted</p>
  <p>tail</p>
</body></html>"""


def _workspace(tmp_path, dashboard=DASH, glossary='terms:\n  - tag: "A"\n  - tag: B\n'):
    (tmp_path / "docs").mkdir()
    if dashboard is not None:
        (tmp_path / "docs" / "federation_bridge_dashboard.html").write_text(dashboard, encoding="utf-8")
    if glossary is not None:
        (tmp_path / "GLOSSARY.yaml").write_text(glossary, encoding="utf-8")
    for name in ("a.docx", "b.pptx", "c.txt", "d.py", "visio_e.svg", "plain.svg"):
        (tmp_path / name).write_text("x", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "f.docx").write_text("x", encoding="utf-8")
    return absorb.FederationBridgeEngine(tmp_path)


def test_engine_creates_ingress_and_loads_glossary(tmp_path):
    eng = _workspace(tmp_path)
    assert (tmp_path / "core_bridge" / "ingress").is_dir()
    assert len(eng.glossary["terms"]) == 2


def test_glossary_fallback_parser_without_yaml(tmp_path, monkeypatch):
    monkeypatch.setattr(absorb, "HAS_YAML", False)
    eng = _workspace(tmp_path)
    assert eng.glossary == {"terms": [{"tag": "A"}, {"tag": "B"}]}


def test_missing_glossary_and_empty_yaml(tmp_path):
    assert _workspace(tmp_path, glossary=None).glossary == {"terms": []}


def test_scan_workspace_counts_by_kind(tmp_path):
    stats = _workspace(tmp_path).scan_workspace()
    assert stats == {"docx": 1, "pptx": 1, "py_loose": 1, "txt": 1, "visio_svg": 1}


def test_execute_patch_rewrites_then_is_idempotent(tmp_path, capsys):
    eng = _workspace(tmp_path)
    assert eng.execute_patch() is True
    html = eng.dashboard_path.read_text(encoding="utf-8")
    assert "Implementation Status (Active Pipeline Connected)" in html
    assert "2 verified terms" in html and "Processed N=5 files" in html
    assert "Implementation Gaps" not in html
    assert eng.execute_patch() is True
    assert "idempotent" in capsys.readouterr().out


def test_execute_patch_fallback_header_replace(tmp_path):
    eng = _workspace(tmp_path, dashboard="<h3>Implementation Gaps (Current Stub)</h3><div>x</div>")
    assert eng.execute_patch() is True
    assert "<h3>Implementation Status</h3>" in eng.dashboard_path.read_text(encoding="utf-8")


def test_execute_patch_refuses_unknown_layout_and_missing_file(tmp_path, capsys):
    eng = _workspace(tmp_path, dashboard="<html>nothing</html>")
    assert eng.execute_patch() is False
    eng.dashboard_path.unlink()
    assert eng.execute_patch() is False
    assert "not found" in capsys.readouterr().out


def test_absorb_main_exit_code(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert absorb.main() == 1


@pytest.mark.parametrize(
    ("fmt", "suffix", "needle"),
    [("html", ".html", "<html><body>a---b</body></html>"), ("PDF ", ".pdf", "Source File: s.md"),
     ("slides", ".slides", "Total Segments: 2"), ("csv", ".csv", "Header1,Header2")],
)
def test_render_formats(tmp_path, fmt, suffix, needle):
    src = tmp_path / "s.md"
    src.write_text("a---b", encoding="utf-8")
    pipe = render.SlugRenderPipeline(tmp_path / "out")
    msg = pipe.process_transform(src, fmt)
    assert msg.startswith("[+]")
    assert needle in (tmp_path / "out" / f"s_export{suffix}").read_text(encoding="utf-8")


def test_render_errors(tmp_path):
    pipe = render.SlugRenderPipeline(tmp_path / "out")
    assert pipe.process_transform(tmp_path / "nope", "html").startswith("[-] Error: Source asset missing")
    src = tmp_path / "s.md"
    src.write_text("x", encoding="utf-8")
    assert "Unsupported format token: docx" in pipe.process_transform(src, "docx")


@pytest.mark.xfail(
    strict=True,
    reason=(
        "production_defect: core_bridge/render.py reports '<stem>_export.xlsx' for the sheet/xlsx "
        "formats but only writes '<stem>_export.csv', so the reported output path never exists"
    ),
)
def test_render_sheet_reported_path_exists(tmp_path):
    src = tmp_path / "s.md"
    src.write_text("x", encoding="utf-8")
    msg = render.SlugRenderPipeline(tmp_path / "out").process_transform(src, "sheet")
    reported = msg.split("at: ", 1)[1]
    assert (tmp_path / "out" / "s_export.xlsx").exists() and reported.endswith("s_export.xlsx")


def test_render_main_usage_and_run(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["render.py"])
    assert render.main() == 1
    (tmp_path / "s.md").write_text("x", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["render.py", "s.md", "html"])
    assert render.main() == 0
    assert (tmp_path / "docs" / "rendered_outputs" / "s_export.html").is_file()
    monkeypatch.setattr("sys.argv", ["render.py", "s.md", "bogus"])
    assert render.main() == 1


# ---------------------------------------------------------------- reliability
CAR = "src/reliability/convergence_assurance_runtime_v1.py"
RCO = "src/reliability/release_certification_orchestrator_v1.py"
SCE = "src/reliability/semantic_chaos_engineering_runtime_v1.py"
SCS = "src/reliability/statistical_convergence_synthesis_runtime_v1.py"
TFI = "src/reliability/topology_fault_injection_matrix_v1.py"


def test_convergence_metrics_monotone_and_bounded():
    m = load(CAR)
    rt = m.ConvergenceAssuranceRuntime()
    metrics = rt.generate_wave_metrics(1, 40)
    assert metrics[0].convergence_percent == 55.0 and metrics[0].sigma_equivalent == 4.0
    values = [x.convergence_percent for x in metrics]
    assert values == sorted(values) and max(values) <= 99.999
    assert all(4.0 <= x.sigma_equivalent <= 6.0 for x in metrics)
    assert json.loads(rt.export_json(metrics[0]))["wave"] == 1


@pytest.mark.parametrize(
    ("start", "end", "state"),
    [(1, 3, "active-hardening"), (1, 25, "advanced-asymptotic-convergence"), (1, 40, "near-deterministic-convergence")],
)
def test_convergence_assessment_states(start, end, state):
    m = load(CAR)
    rt = m.ConvergenceAssuranceRuntime()
    a = rt.assess_convergence(rt.generate_wave_metrics(start, end))
    assert a.convergence_state == state
    assert a.current_wave == end
    assert a.projected_next_wave >= a.current_convergence


@pytest.mark.parametrize(
    ("evidence", "status", "passed"),
    [
        ({"esrc": 99.996, "pca": 99.5, "anova": 99.5, "residual": 0.001}, "PASS", 4),
        ({"esrc": 99.996, "pca": 98.0, "anova": 99.5, "residual": 0.001}, "HOLD", 3),
        ({}, "FAIL", 0),
    ],
)
def test_release_certification_status(evidence, status, passed):
    m = load(RCO)
    res = m.ReleaseCertificationOrchestrator().evaluate_release("rc", evidence)
    assert res.overall_status == status
    assert res.passed_gates == passed and res.failed_gates == 4 - passed
    assert 4.0 <= res.sigma_equivalent <= 6.0


def test_release_certification_sigma_and_export():
    m = load(RCO)
    orch = m.ReleaseCertificationOrchestrator()
    res = orch.evaluate_release("rc", {"esrc": 99.996, "pca": 99.0, "anova": 99.0, "residual": 0.0})
    assert res.sigma_equivalent == 6.0
    assert res.convergence_confidence == pytest.approx(99.332)
    assert json.loads(orch.export_json(res))["gates"][0]["gate_id"] == "G1"


def test_chaos_recovery_scoring():
    m = load(SCE)
    rt = m.SemanticChaosEngineeringRuntime()
    fault = m.ChaosFault("f", m.FaultType.TOPOLOGY_DRIFT, "S", 1.0)
    rt.inject_fault(fault)
    assert rt.injected_faults == {"f": fault}
    none = rt.verify_recovery(fault, {})
    assert none.recovered is False and none.findings == []
    assert none.residual_instability == pytest.approx(0.12)
    full = rt.verify_recovery(fault, {"continuity_restored": True, "governance_restored": True,
                                      "evidence_links_restored": True})
    assert full.recovered is True and len(full.findings) == 3
    assert full.recovery_score == pytest.approx(0.98)
    target = rt.evaluate_target([none, full])
    assert target.residual_defect_rate == pytest.approx(0.07)
    assert target.gap == pytest.approx(99.995 - 99.93)
    assert json.loads(rt.export_json(full))["fault_id"] == "f"


def test_chaos_empty_target_and_zero_gap():
    m = load(SCE)
    rt = m.SemanticChaosEngineeringRuntime()
    empty = rt.evaluate_target([])
    assert empty.current_reliability == 0.0 and empty.residual_defect_rate == 100.0
    assert m.SixSigmaConvergenceTarget(current_reliability=100.0).gap == 0.0


def test_statistical_synthesis_bounds():
    m = load(SCS)
    rt = m.StatisticalConvergenceSynthesisRuntime()
    high = rt.synthesize(m.ConvergenceEvidence(1, 1, 1, 1, 1, 1))
    assert high.sigma_equivalent == 6.0 and high.convergence_confidence == 99.999
    low = rt.synthesize(m.ConvergenceEvidence(0.5, 0.5, 0.5, 0.5, 0.5, 0.5))
    assert low.sigma_equivalent == 4.0 and low.evidence_strength == 0.5
    assert len(low.supporting_signals) == 5
    assert json.loads(rt.export_json(low))["convergence_confidence"] == 50.0


@pytest.mark.parametrize(
    ("severities", "sigma"),
    [([0.1], "6σ"), ([0.4], "5σ"), ([2.0], "4.5σ"), ([5.0], "4σ")],
)
def test_fault_matrix_sigma_bands(severities, sigma):
    m = load(TFI)
    mx = m.TopologyFaultInjectionMatrix()
    for i, s in enumerate(severities):
        mx.register_scenario(m.FaultInjectionScenario(f"s{i}", "x", "f", "e", s))
        mx.execute_scenario(f"s{i}")
    assert mx.summarize_matrix()["sigma_equivalent"] == sigma


def test_fault_matrix_result_fields_and_empty_summary():
    m = load(TFI)
    mx = m.TopologyFaultInjectionMatrix()
    assert mx.summarize_matrix()["sigma_equivalent"] == "undefined"
    mx.register_scenario(m.FaultInjectionScenario("s", "x", "f", "e", 5.0))
    r = mx.execute_scenario("s")
    assert r.recovery_latency_ms == 600 and r.recovered is False
    assert json.loads(mx.export_json(r))["scenario_id"] == "s"
    with pytest.raises(KeyError):
        mx.execute_scenario("missing")


@pytest.mark.parametrize("path", [CAR, RCO, SCE, SCS, TFI])
def test_reliability_main_demos_emit_json(path, capsys):
    run_main(path)
    out = capsys.readouterr().out
    assert out.lstrip().startswith("{")
    assert '"' in out
