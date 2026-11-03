"""Coverage wave 6 (L3): ID pulse/scheduler scripts, CReq resolver, lineage
reports, slide-id enforcer, SVG abstraction, self-healing, renderer lint.
"""
from __future__ import annotations

import hashlib
import json
import xml.etree.ElementTree as ET

import pytest

from tests.coverage_waves._loader import load, run_main
from tools.traceability import lineage_report

SLIDE = "governance/SLIDE_ID_ENFORCER.py"
TRACE = "generators/traceability_engine.py"
SCALE = "scripts/id_pulse_scale_controller.py"
POOL = "scripts/id_pulse_local_pool.py"
SCHED = "scripts/id_work_conserving_scheduler.py"
CREQ = "triage/requirements/creq_resolver.py"
SVG10 = "src/reconstruction/svg_engine/wave10_svg_abstraction_engine.py"
HEAL = "src/self_healing/recursive_self_healing_runtime_v1.py"
RLINT = "semantic_substrate/renderer/renderer_lint_engine.py"


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# ---------------------------------------------------------------- slide id enforcer
@pytest.mark.parametrize(
    ("raw", "value"),
    [(" 'MSLIDE_A_01' # c", "MSLIDE_A_01"), (' "x" ', "x"), (" y ", "y"), (" ' ", "'")],
)
def test_slide_normalize_value(raw, value):
    assert load(SLIDE)._normalize_value(raw) == value


def test_slide_validate_pass_fail_empty(tmp_path, capsys):
    m = load(SLIDE)
    good = _write(tmp_path / "g.yaml", "a:\n  slide_id: MSLIDE_QPS_01\nb:\n  slide_id: \"MSLIDE_X_2_99\"\n")
    assert m.validate(str(good)) == 0
    bad = _write(tmp_path / "b.yaml", "slide_id: mslide_x_01\nslide_id: MSLIDE_X_1\n")
    assert m.validate(str(bad)) == 1
    empty = _write(tmp_path / "e.yaml", "title: none\n")
    assert m.validate(str(empty)) == 1
    out = capsys.readouterr().out
    assert "PASS: slide_id format valid" in out and "(2 entries)" in out
    assert out.count("invalid slide_id") == 2 and "no slide_id entries found" in out


@pytest.mark.xfail(
    strict=True,
    reason=(
        "production_defect: governance/SLIDE_ID_ENFORCER.py only matches lines starting with 'slide_id:', so "
        "YAML list items ('- slide_id: X', the form MANIFEST/MASTER_SLIDE_REGISTRY.yaml uses) are never checked"
    ),
)
def test_slide_list_item_ids_are_validated(tmp_path, capsys):
    m = load(SLIDE)
    bad = _write(tmp_path / "list.yaml", "slides:\n  - slide_id: not-valid\n")
    m.validate(str(bad))
    assert "invalid slide_id 'not-valid'" in capsys.readouterr().out


def test_slide_main_usage_and_run(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        run_main(SLIDE)
    assert exc.value.code == 2
    good = _write(tmp_path / "g.yaml", "slide_id: MSLIDE_A_01\n")
    with pytest.raises(SystemExit) as exc:
        run_main(SLIDE, [str(good)])
    assert exc.value.code == 0
    assert "Usage:" in capsys.readouterr().out


# ---------------------------------------------------------------- traceability placeholder
def test_traceability_engine_is_explicit_placeholder():
    m = load(TRACE)
    assert m.REQUIRED_LINEAGE_CHAIN[0] == "source_document"
    assert m.REQUIRED_LINEAGE_CHAIN[-1] == "execution_deliverable"
    with pytest.raises(NotImplementedError, match="W004"):
        m.main()
    with pytest.raises(NotImplementedError):
        run_main(TRACE)


# ---------------------------------------------------------------- scale controller
def test_scale_rejects_non_power_of_two():
    with pytest.raises(ValueError):
        load(SCALE).decide(3, 10, 3, 0, 0)


@pytest.mark.parametrize(
    ("kwargs", "action", "nxt", "reason"),
    [
        ({"current": 8, "queue": 100, "active_workers": 8, "rework_rate": 0, "collisions": 1}, "RAMP_DOWN", 4,
         "correctness_or_efficiency_guard"),
        ({"current": 8, "queue": 100, "active_workers": 8, "rework_rate": 0.2, "collisions": 0}, "RAMP_DOWN", 4,
         "correctness_or_efficiency_guard"),
        ({"current": 8, "queue": 100, "active_workers": 8, "rework_rate": 0, "collisions": 0, "speed_per_sue": 0.5,
          "baseline_speed_per_sue": 1.0}, "RAMP_DOWN", 4, "correctness_or_efficiency_guard"),
        ({"current": 8, "queue": 100, "active_workers": 2, "rework_rate": 0, "collisions": 0}, "RAMP_DOWN", 4,
         "capacity_starved"),
        ({"current": 1, "queue": 100, "active_workers": 0, "rework_rate": 0, "collisions": 0}, "HOLD", 1,
         "capacity_starved"),
        ({"current": 8, "queue": 10, "active_workers": 8, "rework_rate": 0, "collisions": 0}, "RAMP_DOWN", 4,
         "queue_shallow"),
        ({"current": 8, "queue": 100, "active_workers": 8, "rework_rate": 0, "collisions": 0}, "RAMP_UP", 16,
         "promotion_gate_pass"),
        ({"current": 64, "queue": 1000, "active_workers": 64, "rework_rate": 0, "collisions": 0}, "HOLD", 64,
         "promotion_gate_pass"),
        ({"current": 32, "queue": 1000, "active_workers": 32, "rework_rate": 0, "collisions": 0}, "HOLD", 32,
         "hold_32_for_second_sample"),
        ({"current": 32, "queue": 1000, "active_workers": 32, "rework_rate": 0, "collisions": 0, "sample_count": 2,
          "previous_wall_ms": 100, "wall_ms": 200}, "HOLD", 32, "hold_32_for_second_sample"),
        ({"current": 32, "queue": 1000, "active_workers": 32, "rework_rate": 0, "collisions": 0, "sample_count": 2,
          "previous_wall_ms": 100, "wall_ms": 150}, "RAMP_UP", 64, "promotion_gate_pass"),
        ({"current": 8, "queue": 30, "active_workers": 6, "rework_rate": 0, "collisions": 0}, "HOLD", 8, "hold_band"),
    ],
)
def test_scale_decisions(kwargs, action, nxt, reason):
    res = load(SCALE).decide(**kwargs)
    assert (res["action"], res["next_workers"], res["reasons"]) == (action, nxt, [reason])
    assert res["next_sue_depth"] == nxt * 3


def test_scale_telemetry_fields():
    res = load(SCALE).decide(4, 20, 4, 0, 0, speed_per_sue=0.9, baseline_speed_per_sue=1.0, previous_queue=25,
                             previous_wall_ms=0, wall_ms=10)
    assert res["d_queue"] == -5 and res["wall_ratio"] is None
    assert res["speed_degradation"] == pytest.approx(0.1)
    assert res["queue_per_effective_sue"] == pytest.approx(1.6667)


def test_scale_main_cli(capsys):
    run_main(SCALE, ["--current", "2", "--queue", "20", "--active-workers", "2"])
    assert json.loads(capsys.readouterr().out)["action"] == "RAMP_UP"


# ---------------------------------------------------------------- local pool
def test_pool_spread_and_percentile():
    m = load(POOL)
    assert m.spread([]) == 0.0 and m.spread([0, 0]) == 0.0
    assert m.spread([5, 10]) == 0.5
    assert m.percentile([], 0.5) == 0
    assert m.percentile([3, 1, 2], 0.5) == 2 and m.percentile([1, 2, 3, 4], 0.95) == 4


def _plan(tmp_path, workers, bins, queue=6):
    return _write(tmp_path / "plan.json", json.dumps({"workers": workers, "bins": bins, "queue": queue,
                                                     "plan_created_epoch_ns": 1}))


def test_pool_main_writes_receipts_and_stats(tmp_path, capsys):
    bins = [{"shard": 0, "items": ["a", "b"], "weight": 2}, {"shard": 1, "items": ["c"], "weight": 1}]
    plan = _plan(tmp_path, 2, bins, queue=3)
    out = tmp_path / "receipts"
    with pytest.raises(SystemExit) as exc:
        run_main(POOL, ["--plan", str(plan), "--out-dir", str(out), "--local-threads", "1"])
    assert exc.value.code == 0
    r0 = json.loads((out / "receipt-00.json").read_text())
    assert r0["assigned_count"] == 2 and r0["queue"] == 3 and r0["authority_mutation"] == "FORBIDDEN"
    stats = json.loads((out / "pool_stats.json").read_text())
    assert stats["logical_workers"] == 2 and stats["local_threads"] == 1
    assert stats["count_skew"] == 0.5 and stats["weight_skew"] == 0.5
    assert stats["external_runner_admission_wait_ns"] > 0
    assert capsys.readouterr().out.startswith("ID_LOCAL_POOL_PASS ")


@pytest.mark.parametrize(("workers", "nbins"), [(3, 3), (2, 1)])
def test_pool_rejects_invalid_plan(tmp_path, workers, nbins):
    bins = [{"shard": i, "items": [], "weight": 0} for i in range(nbins)]
    plan = _plan(tmp_path, workers, bins)
    with pytest.raises(SystemExit, match="invalid logical worker plan"):
        run_main(POOL, ["--plan", str(plan), "--out-dir", str(tmp_path / "o")])


# ---------------------------------------------------------------- work-conserving scheduler
def test_item_urgency_and_density():
    m = load(SCHED)
    assert m.Item("a", max_queue_s=0).urgency() == 1.0
    assert m.Item("a", age_s=150, max_queue_s=300).urgency() == 2.0
    assert m.Item("a", age_s=3000, max_queue_s=300).urgency() == 8.0
    it = m.Item("a", est_remaining_s=2, convergence_gain=1, stability_gain=2, unblock_gain=4)
    assert it.value_density() == pytest.approx(2.5)
    assert it.value_density(0.1) == pytest.approx(2.75)


def test_choose_prioritises_overdue_then_density():
    m = load(SCHED)
    items = [
        m.Item("cheap", est_remaining_s=0.1),
        m.Item("overdue", est_remaining_s=100, age_s=500, max_queue_s=300),
        m.Item("running", state="RUNNING", est_remaining_s=0.01),
        m.Item("affine", est_remaining_s=0.1, setup_affinity="gpu"),
        m.Item("nodeadline", est_remaining_s=50, max_queue_s=0),
    ]
    assert [x.id for x in m.choose(items, 3, {"gpu"})] == ["overdue", "affine", "cheap"]
    assert m.choose(items, -1) == []


def test_squeeze_and_preemption():
    m = load(SCHED)
    queued = [m.Item("long", est_remaining_s=50), m.Item("short", est_remaining_s=2)]
    assert m.squeeze_candidate(queued, 5).id == "short"
    assert m.squeeze_candidate(queued, 1) is None
    running = [m.Item("slow", state="RUNNING", est_remaining_s=100), m.Item("pinned", state="RUNNING",
                                                                            resumable=False, est_remaining_s=1000)]
    target, incoming = m.preemption_candidate(running, [m.Item("hot", est_remaining_s=0.5)])
    assert (target.id, incoming.id) == ("slow", "hot")
    assert m.preemption_candidate(running, []) is None
    assert m.preemption_candidate(running, [m.Item("x", state="RUNNING")]) is None
    assert m.preemption_candidate([running[1]], [m.Item("hot")]) is None
    assert m.preemption_candidate([m.Item("fast", state="RUNNING", est_remaining_s=1)],
                                  [m.Item("same", est_remaining_s=1)]) is None


def test_summarize_queue_statistics():
    m = load(SCHED)
    items = [m.Item(str(i), age_s=float(a), max_queue_s=3) for i, a in enumerate([1, 2, 3, 4])]
    items.append(m.Item("r", state="RUNNING"))
    s = m.summarize(items, pool_size=5)
    assert s["queue_depth"] == 4 and s["running_depth"] == 1
    assert s["p50_queue_age_s"] == 2.5 and s["p95_queue_age_s"] == 4.0
    assert s["overdue_count"] == 2 and s["pool"]["execution_slots"] == 4
    empty = m.summarize([], pool_size=0)
    assert empty["p95_queue_age_s"] is None and empty["max_queue_age_s"] == 0.0
    assert empty["pool"]["execution_slots"] == 0


def test_scheduler_main_cli(tmp_path, capsys):
    q = _write(tmp_path / "q.json", json.dumps({"items": [{"id": "a", "est_remaining_s": 1},
                                                          {"id": "b", "est_remaining_s": 9}]}))
    with pytest.raises(SystemExit) as exc:
        run_main(SCHED, ["--queue-json", str(q), "--free-slots", "1", "--squeeze-window-s", "0.5"])
    assert exc.value.code == 0
    out = json.loads(capsys.readouterr().out)
    assert [d["id"] for d in out["dispatch"]] == ["a"] and out["squeeze"] is None


# ---------------------------------------------------------------- CReq resolver
GLOBAL = {"requirements": [{"id": "CReq_001", "title": "G1"}, {"id": "CReq_002", "title": "G2"},
                           {"id": "CReq_003", "title": "G3"}]}
FULL_CHAIN = [{"role": r, "state": "APPROVED"} for r in
              ("local_repo_owner", "parent_cADR_or_cOCD_authority", "global_CReq_authority")]


def test_creq_resolve_overrides_and_fallbacks():
    m = load(CREQ)
    raw = json.dumps(GLOBAL).encode()
    overlay = {"repo": "CODEX", "requirements": [
        {"id": "CReq_CODEX_001", "mode": "override", "overrides": "CReq_001", "title": "L1",
         "approval_state": "APPROVED", "approval_chain": FULL_CHAIN},
        {"id": "CReq_CODEX_002", "mode": "override", "overrides": "CReq_002", "title": "L2",
         "approval_state": "APPROVED", "approval_chain": FULL_CHAIN[:2]},
        {"id": "CReq_CODEX_009", "title": "Add", "parent_global_requirement": "CReq_003"},
    ]}
    r = m.resolve(GLOBAL, raw, overlay)
    rows = {row["effective_id"]: row["source"] for row in r["effective_requirements"]}
    assert rows == {"CReq_CODEX_001": "approved_local_override", "CReq_002": "global_fallback",
                    "CReq_CODEX_009": "local_addition", "CReq_003": "global"}
    assert r["warnings"] == ["CReq_CODEX_002 override blocked: approval chain incomplete"]
    assert r["global_registry_sha256"] == hashlib.sha256(raw).hexdigest()
    assert r["effective_requirement_count"] == 4 and len(r["receipt_sha256"]) == 64
    assert [row["effective_id"] for row in r["effective_requirements"]] == sorted(rows)


@pytest.mark.parametrize(
    ("glob", "overlay", "match"),
    [
        ({"requirements": [{"id": "BAD", "title": "x"}]}, {"repo": "R"}, "invalid global id"),
        ({"requirements": [{"id": "CReq_001", "title": "a"}, {"id": "CReq_001", "title": "b"}]}, {"repo": "R"},
         "duplicate global id"),
        (GLOBAL, {"repo": "R", "requirements": [{"id": "CReq_1", "title": "x"}]}, "invalid local id"),
        (GLOBAL, {"repo": "R", "requirements": [{"id": "CReq_R_001", "title": "x"}, {"id": "CReq_R_001",
                                                                                    "title": "y"}]},
         "duplicate local id"),
        (GLOBAL, {"repo": "R", "requirements": [{"id": "CReq_R_001", "title": "x", "overrides": "CReq_999"}]},
         "unknown global parent"),
    ],
)
def test_creq_resolve_rejects(glob, overlay, match):
    with pytest.raises(ValueError, match=match):
        load(CREQ).resolve(glob, b"{}", overlay)


def test_creq_main(tmp_path, capsys):
    g = _write(tmp_path / "g.json", json.dumps(GLOBAL))
    o = _write(tmp_path / "o.json", json.dumps({"repo": "R", "requirements": [
        {"id": "CReq_R_001", "mode": "override", "overrides": "CReq_001", "title": "L"}]}))
    out = tmp_path / "r.json"
    run_main(CREQ, ["--global-registry", str(g), "--overlay", str(o), "--out", str(out)])
    text = capsys.readouterr().out
    assert "CReq resolution: PASS" in text and "WARN: CReq_R_001 override blocked" in text
    assert json.loads(out.read_text(encoding="utf-8"))["repo"] == "R"


# ---------------------------------------------------------------- lineage report
def _lineage(errors, traversal):
    return {"status": "fail" if errors else "pass", "checked_at": "t", "node_count": 2,
            "error_count": len(errors), "errors": errors, "traversal": traversal,
            "nodes": [{"id": "I1", "title": "ITT", "stage": "ITT", "parent": None, "status": "ok",
                       "created": "c", "updated": "u"},
                      {"id": "A1", "title": "Pkg", "stage": "Applicant", "parent": "I1", "status": "ok",
                       "created": "c", "updated": "u"}]}


def test_lineage_reports_pass(tmp_path):
    paths = lineage_report.generate_reports(_lineage([], ["I1", "A1"]), tmp_path / "a" / "l.json",
                                            tmp_path / "b" / "l.md", tmp_path / "c" / "g.json")
    md = paths["markdown"].read_text(encoding="utf-8")
    assert "**PASS**" in md and "2. **Applicant**" in md and "No lineage validation errors" in md
    graph = json.loads(paths["graph"].read_text(encoding="utf-8"))
    assert graph["edges"] == [{"source": "I1", "target": "A1"}] and len(graph["nodes"]) == 2


def test_lineage_reports_fail_without_traversal(tmp_path):
    rep = _lineage([{"code": "L1", "message": "gap", "node_id": "A1"}, {"code": "L2", "message": "m"}], [])
    paths = lineage_report.generate_reports(rep, tmp_path / "l.json", tmp_path / "l.md", tmp_path / "g.json")
    md = paths["markdown"].read_text(encoding="utf-8")
    assert "**FAIL**" in md and "No complete lineage traversal" in md
    assert "- `L1` (`A1`): gap" in md and "- `L2`: m" in md


# ---------------------------------------------------------------- wave10 SVG abstraction
def test_svg10_generates_parseable_svg():
    m = load(SVG10)
    eng = m.SVGAbstractionEngine()
    model = m.SlideSemanticModel("s", "CAD", [m.SemanticRegion("r", "EvidenceCard", 0.9, {"x": 10, "y": 20}),
                                              m.SemanticRegion("q", "Table", 0.9, {})])
    svg = eng.generate_slide_svg(model, "Plain title")
    root = ET.fromstring(svg)
    rects = root.findall(".//{http://www.w3.org/2000/svg}rect")
    assert len(rects) == 3
    assert rects[1].get("x") == "10" and rects[1].get("width") == "100"
    assert eng.build_svg_canvas(10, 20).startswith('<svg width="10" height="20"')


def test_svg10_rejects_unknown_slide_type():
    m = load(SVG10)
    with pytest.raises(ValueError, match="Unsupported slide type"):
        m.SVGAbstractionEngine().generate_slide_svg(m.SlideSemanticModel("s", "VIDEO"), "t")


@pytest.mark.xfail(
    strict=True,
    reason=(
        "production_defect: wave10_svg_abstraction_engine interpolates title/region_type into SVG without "
        "XML escaping (wave30 escapes), so a title such as 'R&D <draft>' yields malformed SVG"
    ),
)
def test_svg10_escapes_title():
    m = load(SVG10)
    svg = m.SVGAbstractionEngine().generate_slide_svg(m.SlideSemanticModel("s", "PID"), "R&D <draft>")
    ET.fromstring(svg)


def test_svg10_main(capsys):
    run_main(SVG10)
    assert capsys.readouterr().out.count('class="semantic-region"') == 2


# ---------------------------------------------------------------- recursive self-healing
@pytest.mark.parametrize(
    ("context", "actions", "score"),
    [
        ([], ["repair_topology"], 0.84),
        (["mis trip"], ["repair_topology", "recover_governance"], 0.88),
        (["PCW", "alignment"], ["repair_topology", "restore_synchronization", "rebuild_semantic_alignment"], 0.92),
        (["HVAC", "MIS", "Alignment"], ["repair_topology", "recover_governance", "restore_synchronization",
                                        "rebuild_semantic_alignment"], 0.96),
    ],
)
def test_healing_plan_actions(context, actions, score):
    m = load(HEAL)
    rt = m.RecursiveSelfHealingRuntime()
    anomaly = m.RuntimeAnomaly("a", "WCS", "t", 0.5, context)
    rt.register_anomaly(anomaly)
    plan = rt.generate_healing_plan(anomaly)
    assert [a.value for a in plan.healing_actions] == actions
    assert plan.expected_recovery_score == pytest.approx(score)
    state = rt.execute_recovery(plan)
    assert state.continuity_score == pytest.approx(min(0.90 + 0.02 * len(actions), 0.99))
    assert state.governance_restored is ("recover_governance" in actions)
    assert json.loads(rt.export_json(state))["subsystem"] == "WCS"


def test_healing_main(capsys):
    run_main(HEAL)
    assert '"plan_id": "heal::WCS.HCC"' in capsys.readouterr().out


# ---------------------------------------------------------------- renderer lint engine
def test_renderer_lint_missing_manifest(tmp_path, monkeypatch):
    m = load(RLINT)
    monkeypatch.setattr(m, "MANIFEST", tmp_path)
    report = m.RendererLintEngine().lint()
    assert report["status"] == "warning" and report["issue_count"] == 2
    assert {i["rule"] for i in report["issues"]} == {"manifest-required-file"}


def test_renderer_lint_tokens_and_sections(tmp_path, monkeypatch):
    m = load(RLINT)
    monkeypatch.setattr(m, "MANIFEST", tmp_path)
    _write(tmp_path / "STYLE_GUIDE.md", "semantic colors must transform by theme #4A3110")
    _write(tmp_path / "RENDER_RULES.md", "Typography Engine\nLayout Engine\n")
    report = m.RendererLintEngine().lint()
    msgs = [i["message"] for i in report["issues"]]
    assert msgs == ["Missing governance token: #FFE9A3", "Missing renderer governance section: Navigation Engine",
                    "Missing renderer governance section: Contrast Engine"]


def test_renderer_lint_pass_and_export(tmp_path, monkeypatch):
    m = load(RLINT)
    monkeypatch.setattr(m, "MANIFEST", tmp_path)
    _write(tmp_path / "STYLE_GUIDE.md", "semantic colors must transform by theme #4A3110 #FFE9A3")
    _write(tmp_path / "RENDER_RULES.md", "Typography Engine Layout Engine Navigation Engine Contrast Engine")
    report = m.RendererLintEngine().lint()
    assert report == {"issue_count": 0, "issues": [], "status": "pass"}
    out = tmp_path / "r" / "lint.json"
    m.export_lint_report(out, report)
    assert json.loads(out.read_text(encoding="utf-8"))["status"] == "pass"
