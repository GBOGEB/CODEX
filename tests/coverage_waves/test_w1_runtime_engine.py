"""Coverage wave 1 (L3): behaviour tests for ``runtime_engine``.

Tests only; production modules are untouched. Every writer is redirected to
``tmp_path`` so the repo tree stays clean.
"""
from __future__ import annotations

import json
from subprocess import CalledProcessError

import pytest

from runtime_engine import dmaic_runtime_tracker as tracker
from runtime_engine import orchestration_bridge as bridge
from runtime_engine import pca_convergence_analysis as pca
from runtime_engine import pipeline_config
from runtime_engine import plotly_wave_dashboard as dash
from runtime_engine import runtime_control_center as rcc
from runtime_engine import telemetry_pipeline as tele


def test_dmaic_summary_current_average_delta():
    summary = tracker.build_dmaic_summary()
    assert set(summary) == set(tracker.DMAIC)
    assert summary["define"] == {"current": 78, "average": 74.0, "delta": 8}
    assert summary["control"]["delta"] == 24
    for phase, values in tracker.DMAIC.items():
        assert summary[phase]["current"] == values[-1]


def test_pca_summary_normalises_to_one_and_picks_dominant():
    summary = pca.compute_pca_summary()
    assert summary["dominant_factor"] == "governance"
    assert summary["total_variance"] == pytest.approx(3.36)
    assert sum(summary["normalized_factors"].values()) == pytest.approx(1.0, abs=0.01)
    assert summary["convergence_state"] == "STABILIZING"


def test_pipeline_steps_exist_on_disk():
    root = tracker.ROOT / "runtime_engine"
    for step in pipeline_config.PIPELINE_STEPS:
        assert (root / step).is_file(), step


def test_wave_velocity_and_kpi_score():
    assert tele.compute_wave_velocity() == [14, 12, 8, 5, 3, 2]
    assert tele.compute_kpi_score() == pytest.approx(57.85)


def test_build_payload_shape():
    payload = tele.build_payload()
    t = payload["telemetry"]
    assert payload["waves"] is tele.WAVES
    assert t["velocity_average"] == pytest.approx(7.33)
    assert t["average_score"] == pytest.approx(76.43)
    assert t["dmaic"] == tele.DMAIC
    assert set(payload["claimed_vs_actual"]) == {"claimed", "actual", "missing_execution"}


def test_telemetry_main_writes_json(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(tele, "OUTPUT", tmp_path / "out")
    tele.main()
    data = json.loads((tmp_path / "out" / "telemetry.json").read_text(encoding="utf-8"))
    assert data["waves"][0]["wave"] == "W1"
    assert "Telemetry pipeline executed." in capsys.readouterr().out


def test_render_dashboard_missing_telemetry_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(dash, "TELEMETRY", tmp_path / "nope.json")
    with pytest.raises(FileNotFoundError, match="telemetry_pipeline.py"):
        dash.render_dashboard()


def test_render_dashboard_substitutes_placeholders(tmp_path, monkeypatch):
    tel = tmp_path / "telemetry.json"
    tel.write_text(json.dumps(tele.build_payload()), encoding="utf-8")
    html = tmp_path / "o" / "dash.html"
    monkeypatch.setattr(dash, "TELEMETRY", tel)
    monkeypatch.setattr(dash, "HTML", html)
    monkeypatch.setattr(dash, "OUTPUT", tmp_path / "o")
    dash.render_dashboard()
    text = html.read_text(encoding="utf-8")
    assert "__WAVES__" not in text and "__SCORES__" not in text
    assert '["W1", "W2"' in text
    assert "[48, 62, 74" in text


@pytest.mark.xfail(
    strict=True,
    reason=(
        "production_defect: telemetry_pipeline writes ROOT/runtime_output/telemetry.json "
        "but plotly_wave_dashboard reads ROOT/outputs/runtime_engine/telemetry.json, so the "
        "pipeline's step 4 can never find step 1's output"
    ),
)
def test_telemetry_output_is_where_dashboard_reads_it():
    assert tele.OUTPUT / "telemetry.json" == dash.TELEMETRY


def test_orchestration_bridge_runs_each_step(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(bridge, "run", lambda cmd, check: calls.append((cmd, check)))
    bridge.execute_pipeline()
    assert [c[0][1].rsplit("runtime_engine", 1)[1][1:] for c in calls] == pipeline_config.PIPELINE_STEPS
    assert all(check for _, check in calls)
    assert capsys.readouterr().out.count("Executed:") == len(pipeline_config.PIPELINE_STEPS)


@pytest.fixture
def fresh_status(monkeypatch):
    status = {"SUCCESS": [], "FAILED": []}
    monkeypatch.setattr(rcc, "STATUS", status)
    return status


def test_control_center_success_path(monkeypatch, fresh_status):
    monkeypatch.setattr(rcc, "run", lambda *a, **k: None)
    assert rcc.execute_pipeline("x.py") is True
    assert fresh_status["SUCCESS"] == ["x.py"]


def test_control_center_called_process_error(monkeypatch, fresh_status):
    def boom(*a, **k):
        raise CalledProcessError(2, "cmd", output="o", stderr="e")

    monkeypatch.setattr(rcc, "run", boom)
    assert rcc.execute_pipeline("bad.py") is False
    failed = fresh_status["FAILED"][0]
    assert failed["script"] == "bad.py" and failed["stdout"] == "o" and failed["stderr"] == "e"


def test_control_center_os_error_has_empty_streams(monkeypatch, fresh_status):
    def boom(*a, **k):
        raise OSError("no exe")

    monkeypatch.setattr(rcc, "run", boom)
    assert rcc.execute_pipeline("bad.py") is False
    assert fresh_status["FAILED"][0]["stdout"] == ""


@pytest.mark.parametrize(
    ("ok", "state", "rate"),
    [(4, "FULLY_OPERATIONAL", 1.0), (0, "FAILED", 0.0), (2, "PARTIAL_OPERATIONAL", 0.5)],
)
def test_execution_summary_states(fresh_status, ok, state, rate):
    fresh_status["SUCCESS"].extend(f"s{i}" for i in range(ok))
    summary = rcc.build_execution_summary()
    assert summary["runtime_state"] == state
    assert summary["success_rate"] == rate


def test_execution_summary_no_pipelines(monkeypatch, fresh_status):
    monkeypatch.setattr(rcc, "PIPELINE_STEPS", [])
    summary = rcc.build_execution_summary()
    assert summary["runtime_state"] == "NO_PIPELINES"
    assert summary["success_rate"] == 0.0
