from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "analytics" / "qps_thermo_dashboard" / "build_qps_thermo_dashboard.py"
spec = importlib.util.spec_from_file_location("qps_builder", MODULE)
qps_builder = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = qps_builder
spec.loader.exec_module(qps_builder)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_builder_outputs_renderable_dashboard_artifacts() -> None:
    qps_builder.build()

    slideshow = qps_builder.SLIDES_HTML.read_text(encoding="utf-8")
    warm = qps_builder.WARM_HTML.read_text(encoding="utf-8")
    b_line = qps_builder.B_LINE_HTML.read_text(encoding="utf-8")

    assert "Plotly.react" in slideshow
    assert "data-slide=\"7\"" in slideshow
    assert "Controls Engineering" in slideshow
    assert "source_requirement" in slideshow
    assert "traceBadge" in slideshow
    assert "Export SVG" in slideshow
    assert "U / W / S Recovery Analytics" in warm
    assert "200 g/s vacuum-break" in warm
    assert "QCELL → QRB Transport Model" in b_line
    assert "31 mbar @ 2 K to 26 mbar @ 3.9 K" in b_line


def test_dataset_traceability_and_extended_controls_columns() -> None:
    qps_builder.build()
    controls = read_csv(qps_builder.CONTROLS_CSV)
    metrics = read_csv(qps_builder.METRICS_CSV)

    required_controls = {
        "line",
        "scenario",
        "density",
        "velocity",
        "travel_time_60m_min",
        "travel_time_60m_expected",
        "travel_time_60m_max",
        "travel_time_91_5m_min",
        "travel_time_91_5m_expected",
        "travel_time_91_5m_max",
        "travel_time_151_5m_min",
        "travel_time_151_5m_expected",
        "travel_time_151_5m_max",
        "reynolds_number",
        "volumetric_flow_m3_s",
        "residence_time_s",
        "transport_delay_s",
        "effective_deadtime_s",
        "recommended_controller_bandwidth_hz",
        "recommended_scan_period_s",
        "recommended_pid_update_period_s",
    }
    assert required_controls.issubset(controls[0])
    assert {row["source_document"] for row in controls} == {"CONTRACT"}
    assert {row["source_document"] for row in metrics} == {"CONTRACT"}
    assert all(row["source_requirement"] for row in controls)
    assert len(controls) == 14
    for row in controls:
        assert float(row["travel_time_151_5m_min"]) <= float(row["travel_time_151_5m_expected"]) <= float(row["travel_time_151_5m_max"])
        assert float(row["effective_deadtime_s"]) >= float(row["transport_delay_s"])


def test_warm_dataset_is_u_w_s_only_with_expanded_scenarios() -> None:
    qps_builder.build()
    warm = read_csv(qps_builder.WARM_CSV)

    assert {row["line"] for row in warm} == {"U", "W", "S"}
    assert {"RTM-289", "RTM-292", "RTM-296"}.issubset({row["rtm_calculation"] for row in warm})
    scenarios = {row["scenario"] for row in warm}
    assert {"conditioning", "purge", "guard replenishment", "0-3 g/s envelope", "200 g/s vacuum-break"}.issubset(scenarios)
    assert all(row["transport_delay_s"] for row in warm)


def test_b_line_deep_dive_dataset() -> None:
    qps_builder.build()
    b_line = read_csv(qps_builder.B_LINE_CSV)

    assert {row["station"] for row in b_line} == {"QCELL outlet", "intermediate route", "QRB interface"}
    assert any(row["pressure_mbar"] == "31.0" and row["temperature_k"] == "2.0" for row in b_line)
    assert any(row["pressure_mbar"] == "26.0" and row["temperature_k"] == "3.9" for row in b_line)
    assert {row["source_document"] for row in b_line} == {"CONTRACT"}
