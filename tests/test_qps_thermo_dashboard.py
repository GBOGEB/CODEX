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

    assert "Plotly.newPlot" in slideshow or "Plotly.react" in slideshow
    assert "data-slide=\"6\"" in slideshow
    assert "traceBadge" in slideshow
    assert "Export SVG" in slideshow
    assert "U / W / S Recovery Analytics" in warm
    assert "A/B/D/E" in slideshow


def test_dataset_traceability_and_controls_columns() -> None:
    qps_builder.build()
    controls = read_csv(qps_builder.CONTROLS_CSV)
    metrics = read_csv(qps_builder.METRICS_CSV)

    required_controls = {
        "line",
        "scenario",
        "density",
        "velocity",
        "travel_time_60m",
        "travel_time_91_5m",
        "travel_time_151_5m",
        "recommended_deadtime",
        "recommended_sample_period",
        "recommended_filter_constant",
    }
    assert required_controls.issubset(controls[0])
    assert {row["source_document"] for row in controls} == {"CONTRACT"}
    assert {row["source_document"] for row in metrics} == {"CONTRACT"}
    assert all(row["source_table"] for row in metrics)
    assert len(controls) == 14


def test_warm_dataset_is_u_w_s_only_with_rtm_references() -> None:
    qps_builder.build()
    warm = read_csv(qps_builder.WARM_CSV)

    assert {row["line"] for row in warm} == {"U", "W", "S"}
    assert {row["rtm_calculation"] for row in warm} == {"RTM-289", "RTM-292", "RTM-296"}
    assert all(float(row["emergency_recovery_expected"]) > float(row["expected_value"]) for row in warm)
