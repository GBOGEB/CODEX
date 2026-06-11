#!/usr/bin/env python3
"""Build the QPS User Interface Thermo Dashboard analytics module.

The CONTRACT remains the single source of truth. This builder emits governed
SSOT_DERIVATIVE CSV and HTML artifacts for controls, inventory, pressure-drop,
and future digital-twin studies.
"""
from __future__ import annotations

import csv
import html
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

MODULE_DIR = Path(__file__).resolve().parent
DATA_DIR = MODULE_DIR / "data"
DOCS_DIR = MODULE_DIR / "docs"
SLIDES_HTML = MODULE_DIR / "qps_thermo_slideshow_dashboard.html"
WARM_HTML = MODULE_DIR / "warm_piping_dashboard.html"
B_LINE_HTML = MODULE_DIR / "b_line_dashboard.html"
CONTROLS_CSV = DATA_DIR / "qps_controls_response_dataset.csv"
METRICS_CSV = DATA_DIR / "qps_density_velocity_dataset.csv"
WARM_CSV = DATA_DIR / "qps_warm_piping_dataset.csv"
B_LINE_CSV = DATA_DIR / "qps_b_line_response_dataset.csv"

TRACE = {
    "source_document": "CONTRACT",
    "source_section": "3 Technical Requirements / QPS User Interfaces",
    "source_table": "Table 7 Helium Inventory; Table 9 QRB Measuring Points",
    "source_figure": "Figure 3 QPS interface mapping",
    "source_requirement": "RTM-289 / RTM-292 / RTM-296 / QPS controls response model",
}

# SSOT-derived engineering envelope. Values are explicit in derivative datasets
# so downstream controls/digital-twin studies do not scrape HTML. Density is
# kg/m^3, velocity is m/s, flow basis is g/s, and DN is interpreted in mm.
LINE_BASIS = [
    {"line": "A", "family": "cold", "interface": "A", "dn": "DN25", "diameter_m": 0.025, "route_length_m": 151.5, "flow_basis_g_s": 6.0, "notes": "QPS supply interface A"},
    {"line": "B", "family": "cold", "interface": "B", "dn": "DN40", "diameter_m": 0.040, "route_length_m": 151.5, "flow_basis_g_s": 12.0, "notes": "QPS return interface B; highest density variability"},
    {"line": "D", "family": "cold", "interface": "D", "dn": "DN32", "diameter_m": 0.032, "route_length_m": 151.5, "flow_basis_g_s": 9.0, "notes": "QPS distribution interface D"},
    {"line": "E", "family": "cold", "interface": "E", "dn": "DN20", "diameter_m": 0.020, "route_length_m": 151.5, "flow_basis_g_s": 4.0, "notes": "QPS trim/interface E; density-sensitive"},
    {"line": "W", "family": "warm", "interface": "W", "dn": "DN80", "diameter_m": 0.080, "route_length_m": 151.5, "flow_basis_g_s": 28.0, "notes": "Warm recovery W; high velocity watch item"},
    {"line": "U", "family": "warm", "interface": "U", "dn": "DN65", "diameter_m": 0.065, "route_length_m": 91.5, "flow_basis_g_s": 20.0, "notes": "Warm utility U, RTM-289 calculation basis"},
    {"line": "S", "family": "warm", "interface": "S", "dn": "DN150", "diameter_m": 0.150, "route_length_m": 60.0, "flow_basis_g_s": 45.0, "notes": "Warm safety/header S, RTM-296 calculation basis"},
]

SCENARIOS = {
    "2K-SB": {"density_factor": 1.18, "velocity_factor": 0.82, "description": "2 K standby / low-flow stabilization"},
    "2K-OP": {"density_factor": 0.82, "velocity_factor": 1.22, "description": "2 K operation / process-flow basis"},
}

BASE_DENSITY = {"A": 6.8, "B": 8.6, "D": 7.4, "E": 5.2, "W": 1.65, "U": 1.45, "S": 1.20}
BASE_VELOCITY = {"A": 3.8, "B": 4.6, "D": 4.2, "E": 3.3, "W": 8.8, "U": 6.4, "S": 4.9}
VARIABILITY = {"A": 0.10, "B": 0.24, "D": 0.13, "E": 0.20, "W": 0.18, "U": 0.14, "S": 0.12}
DISTANCES = [("60m", 60.0), ("91_5m", 91.5), ("151_5m", 151.5)]

WARM_OPERATING_SCENARIOS = [
    {"line": "U", "scenario": "conditioning", "flow_g_s": 5.0, "density_factor": 1.05, "velocity_factor": 0.45, "basis": "U conditioning"},
    {"line": "U", "scenario": "purge", "flow_g_s": 12.0, "density_factor": 0.95, "velocity_factor": 0.75, "basis": "U purge"},
    {"line": "U", "scenario": "guard replenishment", "flow_g_s": 20.0, "density_factor": 1.00, "velocity_factor": 1.00, "basis": "U guard replenishment"},
    {"line": "W", "scenario": "2K-SB", "flow_g_s": 1.0, "density_factor": 1.18, "velocity_factor": 0.82, "basis": "W 2K-SB"},
    {"line": "W", "scenario": "2K-OP", "flow_g_s": 3.0, "density_factor": 0.82, "velocity_factor": 1.22, "basis": "W 2K-OP"},
    {"line": "W", "scenario": "0-3 g/s envelope", "flow_g_s": 3.0, "density_factor": 1.00, "velocity_factor": 1.00, "basis": "W 0–3 g/s envelope"},
    {"line": "S", "scenario": "residual", "flow_g_s": 10.0, "density_factor": 1.10, "velocity_factor": 0.30, "basis": "S residual"},
    {"line": "S", "scenario": "100 g/s nominal", "flow_g_s": 100.0, "density_factor": 1.00, "velocity_factor": 1.00, "basis": "S 100 g/s nominal"},
    {"line": "S", "scenario": "150 g/s spike", "flow_g_s": 150.0, "density_factor": 0.92, "velocity_factor": 1.50, "basis": "S 150 g/s spike"},
    {"line": "S", "scenario": "200 g/s vacuum-break", "flow_g_s": 200.0, "density_factor": 0.85, "velocity_factor": 2.00, "basis": "S 200 g/s vacuum-break"},
]


@dataclass(frozen=True)
class MetricRow:
    line: str
    family: str
    interface: str
    scenario: str
    dn: str
    diameter_m: float
    route_length_m: float
    flow_basis_g_s: float
    metric: str
    min_value: float
    expected_value: float
    max_value: float
    unit: str
    source_document: str
    source_section: str
    source_table: str
    source_figure: str
    source_requirement: str


def round3(value: float) -> float:
    return round(value, 3)


def round6(value: float) -> float:
    return round(value, 6)


def envelope(expected: float, variability: float) -> tuple[float, float, float]:
    return (round3(expected * (1.0 - variability)), round3(expected), round3(expected * (1.0 + variability)))


def line_by_name(name: str) -> dict[str, object]:
    return next(line for line in LINE_BASIS if line["line"] == name)


def metric_rows() -> list[MetricRow]:
    rows: list[MetricRow] = []
    for line in LINE_BASIS:
        for scenario, factors in SCENARIOS.items():
            density_expected = BASE_DENSITY[line["line"]] * factors["density_factor"]
            velocity_expected = BASE_VELOCITY[line["line"]] * factors["velocity_factor"]
            for metric, values, unit in (
                ("Density", envelope(density_expected, VARIABILITY[line["line"]]), "kg/m^3"),
                ("Velocity", envelope(velocity_expected, VARIABILITY[line["line"]]), "m/s"),
            ):
                rows.append(
                    MetricRow(
                        line=line["line"],
                        family=line["family"],
                        interface=line["interface"],
                        scenario=scenario,
                        dn=line["dn"],
                        diameter_m=line["diameter_m"],
                        route_length_m=line["route_length_m"],
                        flow_basis_g_s=line["flow_basis_g_s"],
                        metric=metric,
                        min_value=values[0],
                        expected_value=values[1],
                        max_value=values[2],
                        unit=unit,
                        **TRACE,
                    )
                )
    return rows


def travel_time_envelope(velocity_row: MetricRow, distance: float) -> dict[str, float]:
    return {
        "min": round3(distance / velocity_row.max_value),
        "expected": round3(distance / velocity_row.expected_value),
        "max": round3(distance / velocity_row.min_value),
    }


def controls_rows(rows: Iterable[MetricRow]) -> list[dict[str, object]]:
    lookup: dict[tuple[str, str, str], MetricRow] = {(r.line, r.scenario, r.metric): r for r in rows}
    controls: list[dict[str, object]] = []
    for line in LINE_BASIS:
        area_m2 = math.pi * (line["diameter_m"] / 2.0) ** 2
        viscosity_pa_s = 3.0e-6 if line["family"] == "cold" else 2.0e-5
        for scenario in SCENARIOS:
            density_row = lookup[(line["line"], scenario, "Density")]
            velocity_row = lookup[(line["line"], scenario, "Velocity")]
            distance_times = {label: travel_time_envelope(velocity_row, distance) for label, distance in DISTANCES}
            transport_delay = distance_times["151_5m"]["expected"]
            residence_time = line["route_length_m"] / velocity_row.expected_value
            effective_deadtime = transport_delay + 0.5 * residence_time
            density = density_row.expected_value
            velocity = velocity_row.expected_value
            row = {
                "line": line["line"],
                "scenario": scenario,
                "density": density,
                "velocity": velocity,
                "travel_time_60m": distance_times["60m"]["expected"],
                "travel_time_91_5m": distance_times["91_5m"]["expected"],
                "travel_time_151_5m": distance_times["151_5m"]["expected"],
            }
            for label, _distance in DISTANCES:
                for key in ("min", "expected", "max"):
                    row[f"travel_time_{label}_{key}"] = distance_times[label][key]
            row.update(
                {
                    "reynolds_number": round3(density * velocity * line["diameter_m"] / viscosity_pa_s),
                    "volumetric_flow_m3_s": round6(velocity * area_m2),
                    "residence_time_s": round3(residence_time),
                    "transport_delay_s": round3(transport_delay),
                    "effective_deadtime_s": round3(effective_deadtime),
                    "recommended_controller_bandwidth_hz": round6(1.0 / (2.0 * math.pi * max(effective_deadtime, 0.001))),
                    "recommended_scan_period_s": round3(max(0.05, effective_deadtime / 20.0)),
                    "recommended_pid_update_period_s": round3(max(0.1, effective_deadtime / 10.0)),
                    "recommended_deadtime": round3(effective_deadtime),
                    "recommended_sample_period": round3(max(0.05, effective_deadtime / 20.0)),
                    "recommended_filter_constant": round3(effective_deadtime / 3.0),
                    **TRACE,
                }
            )
            controls.append(row)
    return controls


def warm_rows(rows: Iterable[MetricRow]) -> list[dict[str, object]]:
    metric_lookup: dict[tuple[str, str, str], MetricRow] = {(r.line, r.scenario, r.metric): r for r in rows}
    out: list[dict[str, object]] = []
    for row in rows:
        if row.family != "warm":
            continue
        calc_ref = {"U": "RTM-289", "W": "RTM-292", "S": "RTM-296"}[row.line]
        emergency_multiplier = 1.35 if row.line == "W" else 1.20
        out.append(
            {
                **asdict(row),
                "operating_basis": SCENARIOS[row.scenario]["description"],
                "rtm_calculation": calc_ref,
                "travel_time_60m_expected": travel_time_envelope(metric_lookup[(row.line, row.scenario, "Velocity")], 60.0)["expected"],
                "transport_delay_s": travel_time_envelope(metric_lookup[(row.line, row.scenario, "Velocity")], 151.5)["expected"],
                "emergency_recovery_min": round3(row.min_value * emergency_multiplier),
                "emergency_recovery_expected": round3(row.expected_value * emergency_multiplier),
                "emergency_recovery_max": round3(row.max_value * emergency_multiplier),
            }
        )
    for scenario in WARM_OPERATING_SCENARIOS:
        line = line_by_name(scenario["line"])
        calc_ref = {"U": "RTM-289", "W": "RTM-292", "S": "RTM-296"}[scenario["line"]]
        density = round3(BASE_DENSITY[scenario["line"]] * scenario["density_factor"])
        velocity = round3(BASE_VELOCITY[scenario["line"]] * scenario["velocity_factor"])
        variability = VARIABILITY[scenario["line"]]
        for metric, expected, unit in (("Density", density, "kg/m^3"), ("Velocity", velocity, "m/s")):
            lo, mid, hi = envelope(expected, variability)
            out.append(
                {
                    "line": scenario["line"],
                    "family": "warm",
                    "interface": scenario["line"],
                    "scenario": scenario["scenario"],
                    "dn": line["dn"],
                    "diameter_m": line["diameter_m"],
                    "route_length_m": line["route_length_m"],
                    "flow_basis_g_s": scenario["flow_g_s"],
                    "metric": metric,
                    "min_value": lo,
                    "expected_value": mid,
                    "max_value": hi,
                    "unit": unit,
                    **TRACE,
                    "operating_basis": scenario["basis"],
                    "rtm_calculation": calc_ref,
                    "travel_time_60m_expected": round3(60.0 / velocity),
                    "transport_delay_s": round3(151.5 / velocity),
                    "emergency_recovery_min": lo,
                    "emergency_recovery_expected": mid,
                    "emergency_recovery_max": hi,
                }
            )
    return out


def b_line_rows() -> list[dict[str, object]]:
    stations = [
        {"station": "QCELL outlet", "route_position_m": 0.0, "fraction": 0.0},
        {"station": "intermediate route", "route_position_m": 75.75, "fraction": 0.5},
        {"station": "QRB interface", "route_position_m": 151.5, "fraction": 1.0},
    ]
    out: list[dict[str, object]] = []
    for scenario, factors in SCENARIOS.items():
        velocity_expected = BASE_VELOCITY["B"] * factors["velocity_factor"]
        density_start = BASE_DENSITY["B"] * factors["density_factor"]
        for station in stations:
            f = station["fraction"]
            pressure_mbar = 31.0 + (26.0 - 31.0) * f
            temperature_k = 2.0 + (3.9 - 2.0) * f
            density = density_start * (pressure_mbar / 31.0) * (2.0 / temperature_k)
            velocity = velocity_expected * (31.0 / pressure_mbar) * (temperature_k / 2.0)
            out.append(
                {
                    "line": "B",
                    "scenario": scenario,
                    "station": station["station"],
                    "route_position_m": station["route_position_m"],
                    "pressure_mbar": round3(pressure_mbar),
                    "temperature_k": round3(temperature_k),
                    "density": round3(density),
                    "velocity": round3(velocity),
                    "transport_lag_s": round3(station["route_position_m"] / velocity),
                    "basis": "31 mbar @ 2 K to 26 mbar @ 3.9 K from QCELL outlet to QRB interface",
                    **TRACE,
                }
            )
    return out


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows for {path}")
    fieldnames = list(rows[0].keys())
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def embedded_payload(metric_dicts: list[dict[str, object]], controls: list[dict[str, object]], warm: list[dict[str, object]], b_line: list[dict[str, object]]) -> str:
    payload = {
        "metadata": {"module": "QPS User Interface Thermo Dashboard", "artifact_class": "SSOT_DERIVATIVE", "source": {"document": TRACE["source_document"], "section": TRACE["source_section"], "table": TRACE["source_table"], "figure": TRACE["source_figure"], "requirement": TRACE["source_requirement"]}},
        "lineBasis": LINE_BASIS,
        "scenarios": SCENARIOS,
        "metrics": metric_dicts,
        "controls": controls,
        "warm": warm,
        "bLine": b_line,
        "distances": [{"label": label, "distance_m": distance} for label, distance in DISTANCES],
    }
    return json.dumps(payload, indent=2)


def page_template(title: str, payload: str, page_kind: str = "main") -> str:
    trace_badge = "CONTRACT → Table 7 / Table 9 / Figure 3 → SSOT_DERIVATIVE"
    body_class = "dark"
    if page_kind == "warm":
        body_class += " warm-only"
    if page_kind == "b_line":
        body_class += " b-line-only"
    slides_nav = "" if page_kind != "main" else """
      <button data-step="-1" title="Previous slide">◀</button>
      <span id="slideIndicator">1 / 7</span>
      <button data-step="1" title="Next slide">▶</button>
    """
    slides = {"main": main_slides, "warm": warm_slides, "b_line": b_line_slides}[page_kind]()
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{html.escape(title)}</title>
  <script src=\"https://cdn.plot.ly/plotly-2.35.2.min.js\"></script>
  <style>{css()}</style>
</head>
<body class=\"{body_class}\">
  <header class=\"topbar\">
    <div><strong>{html.escape(title)}</strong><span class=\"badge\" id=\"traceBadge\">{html.escape(trace_badge)}</span></div>
    <nav>{slides_nav}<button id=\"themeToggle\">Light mode</button><button id=\"exportCsv\">Export CSV</button><button id=\"exportPng\">Export PNG</button><button id=\"exportSvg\">Export SVG</button></nav>
  </header>
  <aside class=\"controls\" aria-label=\"dashboard toggles\">
    <label>Scenario<select id=\"scenario\"><option>2K-SB</option><option>2K-OP</option><option>BOTH</option></select></label>
    <label>Metric<select id=\"metric\"><option>Density</option><option>Velocity</option><option>Time-to-Reach</option></select></label>
    <label>Distance<select id=\"distance\"><option value=\"60m\">60 m</option><option value=\"91_5m\">91.5 m</option><option value=\"151_5m\">151.5 m</option></select></label>
    <label>Plot Type<select id=\"plotType\"><option>Violin</option><option>Boxplot</option><option>Both</option></select></label>
  </aside>
  <main id=\"deck\">{slides}</main>
  <script id=\"qps-data\" type=\"application/json\">{payload.replace("</", "<\\/")}</script>
  <script>{js()}</script>
</body>
</html>
"""


def main_slides() -> str:
    titles = [
        ("System Overview", "Figure 3 mapping, A/B/D/E/W interfaces, U/W/S warm interfaces, DN sizes, and route lengths."),
        ("Density Dashboard", "Density violin/box plots with Table 7 uncertainty envelope. Highlights B-line variability and E-line sensitivity."),
        ("Velocity Dashboard", "Velocity violin/box plots with Table 9 flow basis. Highlights W-line velocity and B-line spread."),
        ("Travel Time Dashboard", "60 m, 91.5 m, and 151.5 m route transit windows with min, expected, and max values."),
        ("Warm Piping Dashboard", "U, W, and S are separated from A/B/D/E with RTM-289, RTM-292, and RTM-296 derived calculations."),
        ("Controls Engineering View", "Transport lag, dead time, and first-order response estimates for 60 m, 91.5 m, and 151.5 m."),
        ("Controls Engineering", "Transport delay, residence time, deadtime, and sample period with uncertainty bands for A/B/D/E/W/U/S."),
    ]
    return "\n".join(slide_section(i, title, subtitle, i == 1) for i, (title, subtitle) in enumerate(titles, start=1))


def slide_section(i: int, title: str, subtitle: str, active: bool = False) -> str:
    return f"""
      <section class=\"slide{' active' if active else ''}\" data-slide=\"{i}\">
        <div class=\"slide-copy\"><p class=\"eyebrow\">Slide {i}</p><h1>{title}</h1><p>{subtitle}</p><div class=\"insights\" id=\"insights-{i}\"></div></div>
        <div class=\"plot-grid\"><div class=\"plot\" id=\"plot-{i}-a\"></div><div class=\"plot\" id=\"plot-{i}-b\"></div></div>
        <div class=\"data-table\" id=\"table-{i}\"></div>
      </section>"""


def warm_slides() -> str:
    return """
      <section class=\"slide active\" data-slide=\"1\">
        <div class=\"slide-copy\"><p class=\"eyebrow\">Warm-Piping Deep Dive</p><h1>U / W / S Recovery Analytics</h1><p>U conditioning/purge/guard replenishment, W 2K-SB/2K-OP/0–3 g/s, and S residual/100/150/200 g/s scenarios.</p><div class=\"insights\" id=\"insights-1\"></div></div>
        <div class=\"plot-grid\"><div class=\"plot\" id=\"plot-1-a\"></div><div class=\"plot\" id=\"plot-1-b\"></div></div>
        <div class=\"data-table\" id=\"table-1\"></div>
      </section>"""


def b_line_slides() -> str:
    return """
      <section class=\"slide active\" data-slide=\"1\">
        <div class=\"slide-copy\"><p class=\"eyebrow\">B-Line Deep Dive</p><h1>QCELL → QRB Transport Model</h1><p>Density, pressure, velocity, and transport lag from 31 mbar @ 2 K to 26 mbar @ 3.9 K.</p><div class=\"insights\" id=\"insights-1\"></div></div>
        <div class=\"plot-grid\"><div class=\"plot\" id=\"plot-1-a\"></div><div class=\"plot\" id=\"plot-1-b\"></div></div>
        <div class=\"data-table\" id=\"table-1\"></div>
      </section>"""


def css() -> str:
    return r"""
:root{color-scheme:dark;--bg:#08111f;--panel:#101c2f;--panel2:#162842;--text:#edf5ff;--muted:#9fb3ca;--accent:#59d0ff;--ok:#9cffc7;--warn:#ffd166;--border:#294766}body.light{color-scheme:light;--bg:#f4f7fb;--panel:#fff;--panel2:#eaf1fa;--text:#102033;--muted:#4e6178;--accent:#006de5;--ok:#007f5f;--warn:#9a6700;--border:#c7d5e6}*{box-sizing:border-box}body{margin:0;background:linear-gradient(135deg,var(--bg),#05070c);color:var(--text);font-family:Inter,Segoe UI,Roboto,Arial,sans-serif;overflow:hidden}.topbar{height:64px;display:flex;justify-content:space-between;align-items:center;padding:0 18px;border-bottom:1px solid var(--border);background:rgba(8,17,31,.88);backdrop-filter:blur(10px);position:fixed;inset:0 0 auto 0;z-index:3}.light .topbar{background:rgba(255,255,255,.88)}button,select{background:var(--panel2);color:var(--text);border:1px solid var(--border);border-radius:10px;padding:8px 10px}button{cursor:pointer}.badge{margin-left:12px;padding:6px 10px;border-radius:999px;background:rgba(89,208,255,.14);color:var(--accent);font-size:12px}.controls{position:fixed;top:76px;left:18px;width:240px;z-index:2;background:rgba(16,28,47,.88);border:1px solid var(--border);border-radius:18px;padding:14px;display:grid;gap:12px}.light .controls{background:rgba(255,255,255,.9)}label{display:grid;gap:5px;color:var(--muted);font-size:13px}#deck{height:100vh;width:100vw}.slide{display:none;height:100vh;width:100vw;padding:88px 24px 24px 282px;gap:14px;grid-template-columns:360px 1fr;grid-template-rows:auto 1fr;overflow:hidden}.slide.active{display:grid}.slide-copy,.plot,.data-table{background:rgba(16,28,47,.78);border:1px solid var(--border);border-radius:22px;box-shadow:0 18px 50px rgba(0,0,0,.24)}.light .slide-copy,.light .plot,.light .data-table{background:rgba(255,255,255,.92)}.slide-copy{padding:22px;grid-row:1/3}.eyebrow{color:var(--accent);text-transform:uppercase;letter-spacing:.14em;font-weight:700;font-size:12px}h1{font-size:42px;line-height:1;margin:8px 0 12px}.slide-copy p{color:var(--muted);font-size:16px}.insights{display:grid;gap:10px;margin-top:20px}.insights span{display:block;border-left:4px solid var(--accent);padding:10px 12px;background:rgba(89,208,255,.10);border-radius:10px}.plot-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;min-height:0}.plot{min-height:360px}.data-table{grid-column:2;padding:14px;overflow:auto;max-height:32vh}table{border-collapse:collapse;width:100%;font-size:13px}th,td{border-bottom:1px solid var(--border);padding:7px 9px;text-align:left;white-space:nowrap}th{color:var(--accent);position:sticky;top:0;background:var(--panel)}@media(max-width:1000px){body{overflow:auto}.topbar{position:sticky}.controls{position:static;width:auto;margin:76px 12px 0}.slide,.slide.active{display:block;height:auto;min-height:100vh;padding:12px}.slide:not(.active){display:none}.slide-copy,.plot,.data-table{margin-bottom:12px}.plot-grid{grid-template-columns:1fr}.plot{height:420px}}"""


def js() -> str:
    return r"""
const DATA = JSON.parse(document.getElementById('qps-data').textContent);
const WARM_ONLY = document.body.classList.contains('warm-only');
const B_LINE_ONLY = document.body.classList.contains('b-line-only');
let currentSlide = 1;
const totalSlides = (WARM_ONLY || B_LINE_ONLY) ? 1 : 7;
const controls = ['scenario','metric','distance','plotType'].reduce((acc,id)=>{acc[id]=document.getElementById(id); return acc;},{});
const template = () => document.body.classList.contains('light') ? 'plotly_white' : 'plotly_dark';
const chartMeta = () => ({source_document:DATA.metadata.source.document, source_table:DATA.metadata.source.table, source_figure:DATA.metadata.source.figure, source_requirement:DATA.metadata.source.requirement});
const govern = traces => traces.map(t => ({...t, meta: chartMeta(), customdata:(t.x||[]).map(()=>chartMeta()), hovertemplate:(t.hovertemplate||'%{x}<br>%{y}') + '<br>source_document=%{customdata.source_document}<br>source_table=%{customdata.source_table}<br>source_figure=%{customdata.source_figure}<br>source_requirement=%{customdata.source_requirement}<extra></extra>'}));
const layoutBase = title => ({title, template: template(), margin:{l:55,r:20,t:55,b:55}, paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', legend:{orientation:'h'}, meta:chartMeta()});
const config = {responsive:true, displaylogo:false, modeBarButtonsToAdd:[{name:'Export SVG', icon:Plotly.Icons.camera, click:gd=>Plotly.downloadImage(gd,{format:'svg',filename:gd.id})}]};
function scenarios(){return controls.scenario.value === 'BOTH' ? ['2K-SB','2K-OP'] : [controls.scenario.value];}
function metricRows(metric=controls.metric.value){return DATA.metrics.filter(r => scenarios().includes(r.scenario) && (WARM_ONLY ? r.family === 'warm' : true) && r.metric === (metric === 'Time-to-Reach' ? 'Velocity' : metric));}
function activePlotIds(){return [...document.querySelectorAll('.slide.active .plot')].map(e=>e.id);}
function syntheticValues(row){const mid=row.expected_value, min=row.min_value, max=row.max_value; return [min,(min+mid)/2,mid,(mid+max)/2,max].map(v=>Number(v.toFixed(3)));}
function plot(target, traces, layout){Plotly.react(target, govern(traces), layout, config);}
function renderDistribution(target, metric){
  const rows = metricRows(metric); let traces=[]; const type=controls.plotType.value;
  rows.forEach(r=>{const common={name:`${r.line} ${r.scenario}`, x:syntheticValues(r).map(()=>`${r.line}-${r.scenario}`), y:syntheticValues(r), box:{visible:true}, meanline:{visible:true}, points:'all'}; if(type==='Violin'||type==='Both') traces.push({...common,type:'violin'}); if(type==='Boxplot'||type==='Both') traces.push({name:`${r.line} ${r.scenario} box`,x:common.x,y:common.y,type:'box',boxpoints:'all'});});
  plot(target, traces, layoutBase(`${metric} envelope (${rows[0]?.unit||''})`));
}
function renderSystem(target){const basis=DATA.lineBasis.filter(r=>WARM_ONLY?r.family==='warm':true); plot(target,[{type:'bar',x:basis.map(r=>r.line),y:basis.map(r=>r.route_length_m),text:basis.map(r=>`${r.interface} / ${r.dn}`),marker:{color:basis.map(r=>r.family==='warm'?'#ffd166':'#59d0ff')}}],layoutBase('Figure 3 route length and interface map'));}
function renderFlow(target){const basis=DATA.lineBasis.filter(r=>WARM_ONLY?r.family==='warm':true); plot(target,[{type:'scatter',mode:'markers+text',x:basis.map(r=>r.flow_basis_g_s),y:basis.map(r=>r.route_length_m),text:basis.map(r=>`${r.line} ${r.dn}`),textposition:'top center',marker:{size:basis.map(r=>Math.max(14,r.flow_basis_g_s/2)),color:'#9cffc7'}}],layoutBase('Table 9 flow basis vs route length'));}
function renderTravel(target){const rows=metricRows('Velocity'); const key='travel_time_'+controls.distance.value; const c=DATA.controls.filter(r=>scenarios().includes(r.scenario)); plot(target,['min','expected','max'].map(k=>({type:'bar',name:k,x:c.map(r=>`${r.line}-${r.scenario}`),y:c.map(r=>r[`${key}_${k}`])})),layoutBase(`Time-to-reach envelope ${controls.distance.options[controls.distance.selectedIndex].text}`));}
function renderControls(target){const rows=DATA.controls.filter(r=>scenarios().includes(r.scenario) && (WARM_ONLY?['U','W','S'].includes(r.line):true)); const distKey='travel_time_'+controls.distance.value+'_expected'; plot(target,[{type:'bar',name:'transport delay',x:rows.map(r=>`${r.line}-${r.scenario}`),y:rows.map(r=>r.transport_delay_s),error_y:{type:'data',array:rows.map(r=>r.travel_time_151_5m_max-r.travel_time_151_5m_expected),arrayminus:rows.map(r=>r.travel_time_151_5m_expected-r.travel_time_151_5m_min),visible:true}},{type:'bar',name:'selected distance lag',x:rows.map(r=>`${r.line}-${r.scenario}`),y:rows.map(r=>r[distKey])},{type:'scatter',mode:'lines+markers',name:'effective deadtime',x:rows.map(r=>`${r.line}-${r.scenario}`),y:rows.map(r=>r.effective_deadtime_s)},{type:'scatter',mode:'lines+markers',name:'scan period',x:rows.map(r=>`${r.line}-${r.scenario}`),y:rows.map(r=>r.recommended_scan_period_s)}],layoutBase('Controls response model with uncertainty bands'));}
function renderWarmRecovery(target){const rows=DATA.warm.filter(r=>r.metric===controls.metric.value.replace('Time-to-Reach','Velocity')); plot(target,[{type:'bar',name:'warm scenario expected',x:rows.map(r=>`${r.line} ${r.scenario}`),y:rows.map(r=>r.expected_value),marker:{color:'#ffd166'}}],layoutBase('Warm scenario envelope'));}
function renderWarmDelay(target){const rows=DATA.warm.filter(r=>r.metric==='Velocity'); plot(target,[{type:'bar',name:'travel time 60 m',x:rows.map(r=>`${r.line} ${r.scenario}`),y:rows.map(r=>r.travel_time_60m_expected)},{type:'bar',name:'transport delay',x:rows.map(r=>`${r.line} ${r.scenario}`),y:rows.map(r=>r.transport_delay_s)}],layoutBase('Warm travel time and transport delay'));}
function renderBLine(targetA,targetB){const rows=DATA.bLine.filter(r=>scenarios().includes(r.scenario)); plot(targetA,[{type:'scatter',mode:'lines+markers',name:'pressure mbar',x:rows.map(r=>`${r.station} ${r.scenario}`),y:rows.map(r=>r.pressure_mbar)},{type:'scatter',mode:'lines+markers',name:'density',x:rows.map(r=>`${r.station} ${r.scenario}`),y:rows.map(r=>r.density),yaxis:'y2'}],{...layoutBase('B-line pressure and density evolution'),yaxis2:{overlaying:'y',side:'right',title:'density kg/m³'}}); plot(targetB,[{type:'scatter',mode:'lines+markers',name:'velocity',x:rows.map(r=>`${r.station} ${r.scenario}`),y:rows.map(r=>r.velocity)},{type:'bar',name:'transport lag',x:rows.map(r=>`${r.station} ${r.scenario}`),y:rows.map(r=>r.transport_lag_s)}],layoutBase('B-line velocity and transport lag'));}
function table(target, rows, cols){document.getElementById(target).innerHTML=`<table><thead><tr>${cols.map(c=>`<th>${c}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${cols.map(c=>`<td>${r[c]??''}</td>`).join('')}</tr>`).join('')}</tbody></table>`;}
function insights(id,items){document.getElementById(id).innerHTML=items.map(i=>`<span>${i}</span>`).join('');}
function renderSlide(){
  document.querySelectorAll('.slide').forEach(s=>s.classList.toggle('active',Number(s.dataset.slide)===currentSlide)); const ind=document.getElementById('slideIndicator'); if(ind) ind.textContent=`${currentSlide} / ${totalSlides}`; const metric=controls.metric.value;
  if(B_LINE_ONLY){renderBLine('plot-1-a','plot-1-b'); table('table-1',DATA.bLine.filter(r=>scenarios().includes(r.scenario)),['line','scenario','station','pressure_mbar','temperature_k','density','velocity','transport_lag_s','source_requirement']); insights('insights-1',['Basis: 31 mbar @ 2 K to 26 mbar @ 3.9 K.','Route: QCELL outlet → intermediate route → QRB interface.','Plotly traces carry CONTRACT governance metadata.']); return;}
  if(WARM_ONLY){renderWarmRecovery('plot-1-a'); renderWarmDelay('plot-1-b'); table('table-1',DATA.warm.filter(r=>r.metric==='Velocity'),['line','scenario','operating_basis','flow_basis_g_s','expected_value','travel_time_60m_expected','transport_delay_s','rtm_calculation','source_requirement']); insights('insights-1',['U: conditioning, purge, and guard replenishment.','W: 2K-SB, 2K-OP, and 0–3 g/s envelope.','S: residual, 100 g/s nominal, 150 g/s spike, and 200 g/s vacuum-break.']); return;}
  if(currentSlide===1){renderSystem('plot-1-a');renderFlow('plot-1-b');table('table-1',DATA.lineBasis,['line','family','interface','dn','route_length_m','flow_basis_g_s','notes']);insights('insights-1',['Figure 3 mapping is rendered as route/interface basis.','Warm U/W/S are labelled separately from cold A/B/D/E.']);}
  if(currentSlide===2){renderDistribution('plot-2-a','Density');renderDistribution('plot-2-b','Density');table('table-2',metricRows('Density'),['line','scenario','dn','min_value','expected_value','max_value','unit','source_table']);insights('insights-2',['B-line density variability is the widest cold-line envelope.','E-line density is flagged as sensitivity-critical due to smaller DN and trim role.']);}
  if(currentSlide===3){renderDistribution('plot-3-a','Velocity');renderDistribution('plot-3-b','Velocity');table('table-3',metricRows('Velocity'),['line','scenario','dn','flow_basis_g_s','min_value','expected_value','max_value','unit']);insights('insights-3',['W-line velocity is the warm-piping watch item.','B-line velocity spread is preserved for controls lag studies.']);}
  if(currentSlide===4){renderTravel('plot-4-a');renderControls('plot-4-b');table('table-4',DATA.controls.filter(r=>scenarios().includes(r.scenario)),['line','scenario','travel_time_60m_min','travel_time_60m_expected','travel_time_60m_max','travel_time_151_5m_min','travel_time_151_5m_expected','travel_time_151_5m_max']);insights('insights-4',['Transit time envelope uses Table 7 operational velocity bounds.','60 m, 91.5 m, and 151.5 m sections are selectable.']);}
  if(currentSlide===5){renderWarmRecovery('plot-5-a');renderWarmDelay('plot-5-b');table('table-5',DATA.warm.filter(r=>r.metric==='Velocity'),['line','scenario','operating_basis','rtm_calculation','flow_basis_g_s','expected_value','travel_time_60m_expected','transport_delay_s']);insights('insights-5',['RTM-289 (U), RTM-292 (W), and RTM-296 (S) calculations are derived rows.','Warm scenarios include conditioning, purge, guard, 0–3 g/s, spikes, and vacuum-break.']);}
  if(currentSlide===6){renderControls('plot-6-a');renderTravel('plot-6-b');table('table-6',DATA.controls.filter(r=>scenarios().includes(r.scenario)),['line','scenario','reynolds_number','volumetric_flow_m3_s','recommended_controller_bandwidth_hz','recommended_pid_update_period_s']);insights('insights-6',['Recommended dead time now uses effective controls deadtime.','Bandwidth, scan period, and PID update period are governed analytics outputs.']);}
  if(currentSlide===7){renderControls('plot-7-a');renderTravel('plot-7-b');table('table-7',DATA.controls.filter(r=>scenarios().includes(r.scenario)),['line','scenario','transport_delay_s','residence_time_s','effective_deadtime_s','recommended_scan_period_s','recommended_pid_update_period_s','source_requirement']);insights('insights-7',['Slide 7 is the controls response model layer under the visualization dashboard.','Uncertainty bands are plotted from min/max travel-time envelopes.']);}
}
document.querySelectorAll('[data-step]').forEach(b=>b.addEventListener('click',()=>{currentSlide=((currentSlide-1+Number(b.dataset.step)+totalSlides)%totalSlides)+1;renderSlide();}));
document.addEventListener('keydown',e=>{if(!WARM_ONLY&&!B_LINE_ONLY&&['ArrowRight','PageDown',' '].includes(e.key)){currentSlide=currentSlide%totalSlides+1;renderSlide();} if(!WARM_ONLY&&!B_LINE_ONLY&&['ArrowLeft','PageUp'].includes(e.key)){currentSlide=(currentSlide+totalSlides-2)%totalSlides+1;renderSlide();}});
Object.values(controls).forEach(el=>el.addEventListener('change',renderSlide));
document.getElementById('themeToggle').addEventListener('click',()=>{document.body.classList.toggle('light');document.body.classList.toggle('dark');document.getElementById('themeToggle').textContent=document.body.classList.contains('light')?'Dark mode':'Light mode';renderSlide();});
document.getElementById('exportCsv').addEventListener('click',()=>{const rows=B_LINE_ONLY?DATA.bLine:(WARM_ONLY||currentSlide===5?DATA.warm:(currentSlide>=6?DATA.controls:DATA.metrics)); const cols=Object.keys(rows[0]); const csv=[cols.join(','),...rows.map(r=>cols.map(c=>JSON.stringify(r[c]??'')).join(','))].join('\n'); const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'})); a.download=B_LINE_ONLY?'b_line_export.csv':(WARM_ONLY?'warm_piping_export.csv':`qps_slide_${currentSlide}_export.csv`); a.click();});
document.getElementById('exportPng').addEventListener('click',()=>{const id=activePlotIds()[0]; if(id) Plotly.downloadImage(id,{format:'png',filename:id});});
document.getElementById('exportSvg').addEventListener('click',()=>{const id=activePlotIds()[0]; if(id) Plotly.downloadImage(id,{format:'svg',filename:id});});
renderSlide();
"""


def build() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    metrics = [asdict(r) for r in metric_rows()]
    metric_objects = [MetricRow(**r) for r in metrics]
    controls = controls_rows(metric_objects)
    warm = warm_rows(metric_objects)
    b_line = b_line_rows()
    write_csv(METRICS_CSV, metrics)
    write_csv(CONTROLS_CSV, controls)
    write_csv(WARM_CSV, warm)
    write_csv(B_LINE_CSV, b_line)
    payload = embedded_payload(metrics, controls, warm, b_line)
    SLIDES_HTML.write_text(page_template("QPS User Interface Thermo Dashboard", payload), encoding="utf-8")
    WARM_HTML.write_text(page_template("QPS Warm Piping Dashboard", payload, page_kind="warm"), encoding="utf-8")
    B_LINE_HTML.write_text(page_template("QPS B-Line Dashboard", payload, page_kind="b_line"), encoding="utf-8")


if __name__ == "__main__":
    build()
