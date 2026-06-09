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
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

MODULE_DIR = Path(__file__).resolve().parent
DATA_DIR = MODULE_DIR / "data"
DOCS_DIR = MODULE_DIR / "docs"
SLIDES_HTML = MODULE_DIR / "qps_thermo_slideshow_dashboard.html"
WARM_HTML = MODULE_DIR / "warm_piping_dashboard.html"
CONTROLS_CSV = DATA_DIR / "qps_controls_response_dataset.csv"
METRICS_CSV = DATA_DIR / "qps_density_velocity_dataset.csv"
WARM_CSV = DATA_DIR / "qps_warm_piping_dataset.csv"

TRACE = {
    "source_document": "CONTRACT",
    "source_section": "3 Technical Requirements / QPS User Interfaces",
    "source_table": "Table 7 Helium Inventory; Table 9 QRB Measuring Points",
    "source_figure": "Figure 3 QPS interface mapping",
}

# SSOT-derived engineering envelope. Values are intentionally explicit in the
# derivative dataset so downstream controls/digital-twin studies do not scrape
# HTML. Density is kg/m^3 and velocity is m/s.
LINE_BASIS = [
    {"line": "A", "family": "cold", "interface": "A", "dn": "DN25", "route_length_m": 151.5, "flow_basis_g_s": 6.0, "notes": "QPS supply interface A"},
    {"line": "B", "family": "cold", "interface": "B", "dn": "DN40", "route_length_m": 151.5, "flow_basis_g_s": 12.0, "notes": "QPS return interface B; highest density variability"},
    {"line": "D", "family": "cold", "interface": "D", "dn": "DN32", "route_length_m": 151.5, "flow_basis_g_s": 9.0, "notes": "QPS distribution interface D"},
    {"line": "E", "family": "cold", "interface": "E", "dn": "DN20", "route_length_m": 151.5, "flow_basis_g_s": 4.0, "notes": "QPS trim/interface E; density-sensitive"},
    {"line": "W", "family": "warm", "interface": "W", "dn": "DN80", "route_length_m": 151.5, "flow_basis_g_s": 28.0, "notes": "Warm recovery W; high velocity watch item"},
    {"line": "U", "family": "warm", "interface": "U", "dn": "DN65", "route_length_m": 91.5, "flow_basis_g_s": 20.0, "notes": "Warm utility U, RTM-289 calculation basis"},
    {"line": "S", "family": "warm", "interface": "S", "dn": "DN150", "route_length_m": 60.0, "flow_basis_g_s": 45.0, "notes": "Warm safety/header S, RTM-296 calculation basis"},
]

SCENARIOS = {
    "2K-SB": {"density_factor": 1.18, "velocity_factor": 0.82, "description": "2 K standby / low-flow stabilization"},
    "2K-OP": {"density_factor": 0.82, "velocity_factor": 1.22, "description": "2 K operation / process-flow basis"},
}

BASE_DENSITY = {"A": 6.8, "B": 8.6, "D": 7.4, "E": 5.2, "W": 1.65, "U": 1.45, "S": 1.20}
BASE_VELOCITY = {"A": 3.8, "B": 4.6, "D": 4.2, "E": 3.3, "W": 8.8, "U": 6.4, "S": 4.9}
VARIABILITY = {"A": 0.10, "B": 0.24, "D": 0.13, "E": 0.20, "W": 0.18, "U": 0.14, "S": 0.12}
DISTANCES = [("60m", 60.0), ("91_5m", 91.5), ("151_5m", 151.5)]


@dataclass(frozen=True)
class MetricRow:
    line: str
    family: str
    interface: str
    scenario: str
    dn: str
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


def round3(value: float) -> float:
    return round(value, 3)


def envelope(expected: float, variability: float) -> tuple[float, float, float]:
    return (round3(expected * (1.0 - variability)), round3(expected), round3(expected * (1.0 + variability)))


def metric_rows() -> list[MetricRow]:
    rows: list[MetricRow] = []
    for line in LINE_BASIS:
        for scenario, factors in SCENARIOS.items():
            density_expected = BASE_DENSITY[line["line"]] * factors["density_factor"]
            velocity_expected = BASE_VELOCITY[line["line"]] * factors["velocity_factor"]
            density_env = envelope(density_expected, VARIABILITY[line["line"]])
            velocity_env = envelope(velocity_expected, VARIABILITY[line["line"]])
            for metric, values, unit in (
                ("Density", density_env, "kg/m^3"),
                ("Velocity", velocity_env, "m/s"),
            ):
                rows.append(
                    MetricRow(
                        line=line["line"],
                        family=line["family"],
                        interface=line["interface"],
                        scenario=scenario,
                        dn=line["dn"],
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


def controls_rows(rows: Iterable[MetricRow]) -> list[dict[str, object]]:
    lookup: dict[tuple[str, str, str], MetricRow] = {(r.line, r.scenario, r.metric): r for r in rows}
    controls: list[dict[str, object]] = []
    for line in LINE_BASIS:
        for scenario in SCENARIOS:
            density = lookup[(line["line"], scenario, "Density")].expected_value
            velocity = lookup[(line["line"], scenario, "Velocity")].expected_value
            times = {label: round3(distance / velocity) for label, distance in DISTANCES}
            max_time = max(times.values())
            controls.append(
                {
                    "line": line["line"],
                    "scenario": scenario,
                    "density": density,
                    "velocity": velocity,
                    "travel_time_60m": times["60m"],
                    "travel_time_91_5m": times["91_5m"],
                    "travel_time_151_5m": times["151_5m"],
                    "recommended_deadtime": round3(max_time),
                    "recommended_sample_period": round3(max(0.25, max_time / 10.0)),
                    "recommended_filter_constant": round3(max_time / 3.0),
                    **TRACE,
                }
            )
    return controls


def warm_rows(rows: Iterable[MetricRow]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in rows:
        if row.family != "warm":
            continue
        calc_ref = {"U": "RTM-289", "W": "RTM-292", "S": "RTM-296"}[row.line]
        emergency_multiplier = 1.35 if row.line == "W" else 1.20
        out.append(
            {
                **asdict(row),
                "rtm_calculation": calc_ref,
                "emergency_recovery_min": round3(row.min_value * emergency_multiplier),
                "emergency_recovery_expected": round3(row.expected_value * emergency_multiplier),
                "emergency_recovery_max": round3(row.max_value * emergency_multiplier),
            }
        )
    return out


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def embedded_payload(metric_dicts: list[dict[str, object]], controls: list[dict[str, object]], warm: list[dict[str, object]]) -> str:
    payload = {
        "metadata": {
            "module": "QPS User Interface Thermo Dashboard",
            "artifact_class": "SSOT_DERIVATIVE",
            "source": {
                "document": TRACE["source_document"],
                "section": TRACE["source_section"],
                "table": TRACE["source_table"],
                "figure": TRACE["source_figure"],
            },
        },
        "lineBasis": LINE_BASIS,
        "scenarios": SCENARIOS,
        "metrics": metric_dicts,
        "controls": controls,
        "warm": warm,
        "distances": [{"label": label, "distance_m": distance} for label, distance in DISTANCES],
    }
    return json.dumps(payload, indent=2)


def page_template(title: str, payload: str, warm_only: bool = False) -> str:
    trace_badge = "CONTRACT → Table 7 / Table 9 / Figure 3 → SSOT_DERIVATIVE"
    warm_class = " warm-only" if warm_only else ""
    slides_nav = "" if warm_only else """
      <button data-step="-1" title="Previous slide">◀</button>
      <span id="slideIndicator">1 / 6</span>
      <button data-step="1" title="Next slide">▶</button>
    """
    slides = warm_slides() if warm_only else main_slides()
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{html.escape(title)}</title>
  <script src=\"https://cdn.plot.ly/plotly-2.35.2.min.js\"></script>
  <style>{css()}</style>
</head>
<body class=\"dark{warm_class}\">
  <header class=\"topbar\">
    <div>
      <strong>{html.escape(title)}</strong>
      <span class=\"badge\" id=\"traceBadge\">{html.escape(trace_badge)}</span>
    </div>
    <nav>
      {slides_nav}
      <button id=\"themeToggle\">Light mode</button>
      <button id=\"exportCsv\">Export CSV</button>
      <button id=\"exportPng\">Export PNG</button>
      <button id=\"exportSvg\">Export SVG</button>
    </nav>
  </header>
  <aside class=\"controls\" aria-label=\"dashboard toggles\">
    <label>Scenario<select id=\"scenario\"><option>2K-SB</option><option>2K-OP</option><option>BOTH</option></select></label>
    <label>Metric<select id=\"metric\"><option>Density</option><option>Velocity</option><option>Time-to-Reach</option></select></label>
    <label>Distance<select id=\"distance\"><option value=\"60m\">60 m</option><option value=\"91_5m\">91.5 m</option><option value=\"151_5m\">151.5 m</option></select></label>
    <label>Plot Type<select id=\"plotType\"><option>Violin</option><option>Boxplot</option><option>Both</option></select></label>
  </aside>
  <main id=\"deck\">{slides}</main>
  <script id=\"qps-data\" type=\"application/json\">{payload.replace("</", "<\\/")}</script>
  <script>{js(warm_only=warm_only)}</script>
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
    ]
    sections = []
    for i, (title, subtitle) in enumerate(titles, start=1):
        active = " active" if i == 1 else ""
        sections.append(f"""
      <section class=\"slide{active}\" data-slide=\"{i}\">
        <div class=\"slide-copy\"><p class=\"eyebrow\">Slide {i}</p><h1>{title}</h1><p>{subtitle}</p><div class=\"insights\" id=\"insights-{i}\"></div></div>
        <div class=\"plot-grid\"><div class=\"plot\" id=\"plot-{i}-a\"></div><div class=\"plot\" id=\"plot-{i}-b\"></div></div>
        <div class=\"data-table\" id=\"table-{i}\"></div>
      </section>""")
    return "\n".join(sections)


def warm_slides() -> str:
    return """
      <section class=\"slide active\" data-slide=\"1\">
        <div class=\"slide-copy\"><p class=\"eyebrow\">Warm-Piping Deep Dive</p><h1>U / W / S Recovery Analytics</h1><p>Dedicated warm-piping dashboard with flow, density, velocity, emergency recovery scenarios, and W example calculations.</p><div class=\"insights\" id=\"insights-1\"></div></div>
        <div class=\"plot-grid\"><div class=\"plot\" id=\"plot-1-a\"></div><div class=\"plot\" id=\"plot-1-b\"></div></div>
        <div class=\"data-table\" id=\"table-1\"></div>
      </section>
    """


def css() -> str:
    return r"""
:root{color-scheme:dark;--bg:#08111f;--panel:#101c2f;--panel2:#162842;--text:#edf5ff;--muted:#9fb3ca;--accent:#59d0ff;--ok:#9cffc7;--warn:#ffd166;--border:#294766}body.light{color-scheme:light;--bg:#f4f7fb;--panel:#fff;--panel2:#eaf1fa;--text:#102033;--muted:#4e6178;--accent:#006de5;--ok:#007f5f;--warn:#9a6700;--border:#c7d5e6}*{box-sizing:border-box}body{margin:0;background:linear-gradient(135deg,var(--bg),#05070c);color:var(--text);font-family:Inter,Segoe UI,Roboto,Arial,sans-serif;overflow:hidden}.topbar{height:64px;display:flex;justify-content:space-between;align-items:center;padding:0 18px;border-bottom:1px solid var(--border);background:rgba(8,17,31,.88);backdrop-filter:blur(10px);position:fixed;inset:0 0 auto 0;z-index:3}.light .topbar{background:rgba(255,255,255,.88)}button,select{background:var(--panel2);color:var(--text);border:1px solid var(--border);border-radius:10px;padding:8px 10px}button{cursor:pointer}.badge{margin-left:12px;padding:6px 10px;border-radius:999px;background:rgba(89,208,255,.14);color:var(--accent);font-size:12px}.controls{position:fixed;top:76px;left:18px;width:240px;z-index:2;background:rgba(16,28,47,.88);border:1px solid var(--border);border-radius:18px;padding:14px;display:grid;gap:12px}.light .controls{background:rgba(255,255,255,.9)}label{display:grid;gap:5px;color:var(--muted);font-size:13px}#deck{height:100vh;width:100vw}.slide{display:none;height:100vh;width:100vw;padding:88px 24px 24px 282px;gap:14px;grid-template-columns:360px 1fr;grid-template-rows:auto 1fr;overflow:hidden}.slide.active{display:grid}.slide-copy,.plot,.data-table{background:rgba(16,28,47,.78);border:1px solid var(--border);border-radius:22px;box-shadow:0 18px 50px rgba(0,0,0,.24)}.light .slide-copy,.light .plot,.light .data-table{background:rgba(255,255,255,.92)}.slide-copy{padding:22px;grid-row:1/3}.eyebrow{color:var(--accent);text-transform:uppercase;letter-spacing:.14em;font-weight:700;font-size:12px}h1{font-size:42px;line-height:1;margin:8px 0 12px}.slide-copy p{color:var(--muted);font-size:16px}.insights{display:grid;gap:10px;margin-top:20px}.insights span{display:block;border-left:4px solid var(--accent);padding:10px 12px;background:rgba(89,208,255,.10);border-radius:10px}.plot-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;min-height:0}.plot{min-height:360px}.data-table{grid-column:2;padding:14px;overflow:auto;max-height:32vh}table{border-collapse:collapse;width:100%;font-size:13px}th,td{border-bottom:1px solid var(--border);padding:7px 9px;text-align:left;white-space:nowrap}th{color:var(--accent);position:sticky;top:0;background:var(--panel)}@media(max-width:1000px){body{overflow:auto}.topbar{position:sticky}.controls{position:static;width:auto;margin:76px 12px 0}.slide,.slide.active{display:block;height:auto;min-height:100vh;padding:12px}.slide:not(.active){display:none}.slide-copy,.plot,.data-table{margin-bottom:12px}.plot-grid{grid-template-columns:1fr}.plot{height:420px}}"""


def js(warm_only: bool = False) -> str:
    return r"""
const DATA = JSON.parse(document.getElementById('qps-data').textContent);
const WARM_ONLY = document.body.classList.contains('warm-only');
let currentSlide = 1;
const totalSlides = WARM_ONLY ? 1 : 6;
const controls = ['scenario','metric','distance','plotType'].reduce((acc,id)=>{acc[id]=document.getElementById(id); return acc;},{});
const template = () => document.body.classList.contains('light') ? 'plotly_white' : 'plotly_dark';
const layoutBase = (title) => ({title, template: template(), margin:{l:55,r:20,t:55,b:55}, paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', legend:{orientation:'h'}});
const config = {responsive:true, displaylogo:false, modeBarButtonsToAdd:[{name:'Export SVG', icon:Plotly.Icons.camera, click:(gd)=>Plotly.downloadImage(gd,{format:'svg',filename:gd.id})}]};
function scenarios(){return controls.scenario.value === 'BOTH' ? ['2K-SB','2K-OP'] : [controls.scenario.value];}
function metricRows(metric=controls.metric.value){return DATA.metrics.filter(r => scenarios().includes(r.scenario) && (WARM_ONLY ? r.family === 'warm' : true) && r.metric === (metric === 'Time-to-Reach' ? 'Velocity' : metric));}
function activePlotIds(){return [...document.querySelectorAll('.slide.active .plot')].map(e=>e.id);}
function syntheticValues(row){const mid=row.expected_value, min=row.min_value, max=row.max_value; return [min,(min+mid)/2,mid,(mid+max)/2,max].map(v=>Number(v.toFixed(3)));}
function renderDistribution(target, metric){
  const rows = metricRows(metric);
  let traces=[];
  const type=controls.plotType.value;
  rows.forEach(r=>{
    const common={name:`${r.line} ${r.scenario}`, x:syntheticValues(r).map(()=>`${r.line}-${r.scenario}`), y:syntheticValues(r), box:{visible:true}, meanline:{visible:true}, points:'all'};
    if(type==='Violin'||type==='Both') traces.push({...common, type:'violin'});
    if(type==='Boxplot'||type==='Both') traces.push({name:`${r.line} ${r.scenario} box`, x:common.x, y:common.y, type:'box', boxpoints:'all'});
  });
  Plotly.react(target, traces, layoutBase(`${metric} envelope (${rows[0]?.unit||''})`), config);
}
function renderSystem(target){
  const basis = DATA.lineBasis.filter(r => WARM_ONLY ? r.family === 'warm' : true);
  Plotly.react(target, [{type:'bar', x:basis.map(r=>r.line), y:basis.map(r=>r.route_length_m), text:basis.map(r=>`${r.interface} / ${r.dn}`), marker:{color:basis.map(r=>r.family==='warm'?'#ffd166':'#59d0ff')}}], layoutBase('Figure 3 route length and interface map'), config);
}
function renderFlow(target){
  const basis = DATA.lineBasis.filter(r => WARM_ONLY ? r.family === 'warm' : true);
  Plotly.react(target, [{type:'scatter', mode:'markers+text', x:basis.map(r=>r.flow_basis_g_s), y:basis.map(r=>r.route_length_m), text:basis.map(r=>`${r.line} ${r.dn}`), textposition:'top center', marker:{size:basis.map(r=>Math.max(14,r.flow_basis_g_s/2)), color:'#9cffc7'}}], layoutBase('Table 9 flow basis vs route length'), config);
}
function renderTravel(target){
  const rows = metricRows('Velocity');
  const distance = DATA.distances.find(d=>d.label===controls.distance.value).distance_m;
  const traces = ['min_value','expected_value','max_value'].map(key=>({type:'bar', name:key.replace('_value',''), x:rows.map(r=>`${r.line}-${r.scenario}`), y:rows.map(r=>Number((distance / r[key]).toFixed(3)))}));
  Plotly.react(target, traces, layoutBase(`Time-to-reach at ${distance} m`), config);
}
function renderControls(target){
  const rows = DATA.controls.filter(r=>scenarios().includes(r.scenario) && (WARM_ONLY ? ['U','W','S'].includes(r.line) : true));
  const distKey = 'travel_time_' + controls.distance.value;
  Plotly.react(target, [
    {type:'bar', name:'transport lag', x:rows.map(r=>`${r.line}-${r.scenario}`), y:rows.map(r=>r[distKey])},
    {type:'bar', name:'dead time', x:rows.map(r=>`${r.line}-${r.scenario}`), y:rows.map(r=>r.recommended_deadtime)},
    {type:'scatter', mode:'lines+markers', name:'filter τ', x:rows.map(r=>`${r.line}-${r.scenario}`), y:rows.map(r=>r.recommended_filter_constant)}
  ], layoutBase('Controls response estimate'), config);
}
function renderWarmRecovery(target){
  const rows = DATA.warm.filter(r=>scenarios().includes(r.scenario) && r.metric===controls.metric.value.replace('Time-to-Reach','Velocity'));
  Plotly.react(target, [{type:'bar', name:'emergency expected', x:rows.map(r=>`${r.line}-${r.scenario} ${r.rtm_calculation}`), y:rows.map(r=>r.emergency_recovery_expected), marker:{color:'#ffd166'}}], layoutBase('Warm emergency recovery envelope'), config);
}
function table(target, rows, cols){
  document.getElementById(target).innerHTML = `<table><thead><tr>${cols.map(c=>`<th>${c}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${cols.map(c=>`<td>${r[c]??''}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
}
function insights(id, items){document.getElementById(id).innerHTML = items.map(i=>`<span>${i}</span>`).join('');}
function renderSlide(){
  document.querySelectorAll('.slide').forEach(s=>s.classList.toggle('active', Number(s.dataset.slide)===currentSlide));
  const ind=document.getElementById('slideIndicator'); if(ind) ind.textContent = `${currentSlide} / ${totalSlides}`;
  const metric=controls.metric.value;
  if(WARM_ONLY){renderDistribution('plot-1-a', metric==='Time-to-Reach'?'Velocity':metric); renderWarmRecovery('plot-1-b'); table('table-1', DATA.warm.filter(r=>scenarios().includes(r.scenario)), ['line','scenario','metric','min_value','expected_value','max_value','rtm_calculation','emergency_recovery_expected','source_document','source_table']); insights('insights-1',['U/W/S only: cold A/B/D/E are intentionally excluded.','W RTM-292 example: emergency recovery envelope applies a 1.35 multiplier to the W expected value.','Trace badge confirms CONTRACT-derived governance.']); return;}
  if(currentSlide===1){renderSystem('plot-1-a');renderFlow('plot-1-b');table('table-1', DATA.lineBasis, ['line','family','interface','dn','route_length_m','flow_basis_g_s','notes']);insights('insights-1',['Figure 3 mapping is rendered as route/interface basis.','Warm U/W/S are labelled separately from cold A/B/D/E.']);}
  if(currentSlide===2){renderDistribution('plot-2-a','Density');renderDistribution('plot-2-b','Density');table('table-2', metricRows('Density'), ['line','scenario','dn','min_value','expected_value','max_value','unit','source_table']);insights('insights-2',['B-line density variability is the widest cold-line envelope.','E-line density is flagged as sensitivity-critical due to smaller DN and trim role.']);}
  if(currentSlide===3){renderDistribution('plot-3-a','Velocity');renderDistribution('plot-3-b','Velocity');table('table-3', metricRows('Velocity'), ['line','scenario','dn','flow_basis_g_s','min_value','expected_value','max_value','unit']);insights('insights-3',['W-line velocity is the warm-piping watch item.','B-line velocity spread is preserved for controls lag studies.']);}
  if(currentSlide===4){renderTravel('plot-4-a');renderControls('plot-4-b');table('table-4', DATA.controls.filter(r=>scenarios().includes(r.scenario)), ['line','scenario','travel_time_60m','travel_time_91_5m','travel_time_151_5m','source_document']);insights('insights-4',['Transit time is computed as distance divided by velocity envelope.','60 m, 91.5 m, and 151.5 m sections are selectable.']);}
  if(currentSlide===5){renderWarmRecovery('plot-5-a');renderDistribution('plot-5-b',metric==='Time-to-Reach'?'Velocity':metric);table('table-5', DATA.warm.filter(r=>scenarios().includes(r.scenario)), ['line','scenario','metric','rtm_calculation','min_value','expected_value','max_value','emergency_recovery_expected']);insights('insights-5',['RTM-289 (U), RTM-292 (W), and RTM-296 (S) calculations are derived rows.','Warm piping is isolated from A/B/D/E to support recovery studies.']);}
  if(currentSlide===6){renderControls('plot-6-a');renderTravel('plot-6-b');table('table-6', DATA.controls.filter(r=>scenarios().includes(r.scenario)), ['line','scenario','velocity','recommended_deadtime','recommended_sample_period','recommended_filter_constant']);insights('insights-6',['Recommended dead time uses the governing 151.5 m transit case.','Sample period targets one tenth of dead time with a 0.25 s floor.']);}
}
document.querySelectorAll('[data-step]').forEach(b=>b.addEventListener('click',()=>{currentSlide=((currentSlide-1+Number(b.dataset.step)+totalSlides)%totalSlides)+1; renderSlide();}));
document.addEventListener('keydown',e=>{if(!WARM_ONLY&&['ArrowRight','PageDown',' '].includes(e.key)){currentSlide=currentSlide%totalSlides+1;renderSlide();} if(!WARM_ONLY&&['ArrowLeft','PageUp'].includes(e.key)){currentSlide=(currentSlide+totalSlides-2)%totalSlides+1;renderSlide();}});
Object.values(controls).forEach(el=>el.addEventListener('change',renderSlide));
document.getElementById('themeToggle').addEventListener('click',()=>{document.body.classList.toggle('light');document.body.classList.toggle('dark');document.getElementById('themeToggle').textContent=document.body.classList.contains('light')?'Dark mode':'Light mode';renderSlide();});
document.getElementById('exportCsv').addEventListener('click',()=>{const rows = currentSlide===6 ? DATA.controls : (currentSlide===5 || WARM_ONLY ? DATA.warm : DATA.metrics); const cols=Object.keys(rows[0]); const csv=[cols.join(','),...rows.map(r=>cols.map(c=>JSON.stringify(r[c]??'')).join(','))].join('\n'); const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'})); a.download=WARM_ONLY?'warm_piping_export.csv':`qps_slide_${currentSlide}_export.csv`; a.click();});
document.getElementById('exportPng').addEventListener('click',()=>{const id=activePlotIds()[0]; if(id) Plotly.downloadImage(id,{format:'png',filename:id});});
document.getElementById('exportSvg').addEventListener('click',()=>{const id=activePlotIds()[0]; if(id) Plotly.downloadImage(id,{format:'svg',filename:id});});
renderSlide();
"""


def build() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    metrics = [asdict(r) for r in metric_rows()]
    controls = controls_rows([MetricRow(**r) for r in metrics])
    warm = warm_rows([MetricRow(**r) for r in metrics])
    write_csv(METRICS_CSV, metrics)
    write_csv(CONTROLS_CSV, controls)
    write_csv(WARM_CSV, warm)
    payload = embedded_payload(metrics, controls, warm)
    SLIDES_HTML.write_text(page_template("QPS User Interface Thermo Dashboard", payload), encoding="utf-8")
    WARM_HTML.write_text(page_template("QPS Warm Piping Dashboard", payload, warm_only=True), encoding="utf-8")


if __name__ == "__main__":
    build()
