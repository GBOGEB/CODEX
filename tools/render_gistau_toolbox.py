"""Render the GISTAU Ch15 toolbox page (and, optionally, its matplotlib figure).

Inputs:  governance/physics/HE4_PROPERTY_AUTHORITY_PIN.yaml (authority, grid)
         src/gistau_ch15/properties/fallback_helium.py (basic-incarnation domain)
Outputs: docs/gistau-ch15/toolbox.html
         docs/gistau-ch15/assets/ideal_gas_domain_map.svg   (--figures, needs matplotlib)

The calculators run docs/gistau-ch15/assets/gistau_basic.js, a browser mirror of
the Python basic incarnation whose parity is tested in
tests/gistau_ch15/test_toolbox_js_parity.py. The HTML is a pure function of the
inputs, so a test can detect a stale page. Regenerate with:
    python tools/render_gistau_toolbox.py [--figures]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from string import Template
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PIN_PATH = REPO_ROOT / "governance" / "physics" / "HE4_PROPERTY_AUTHORITY_PIN.yaml"
OUTPUT = REPO_ROOT / "docs" / "gistau-ch15" / "toolbox.html"
FIGURE = REPO_ROOT / "docs" / "gistau-ch15" / "assets" / "ideal_gas_domain_map.svg"
PLOTLY = "https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"


def _backend():
    src = str(REPO_ROOT / "src")
    if src not in sys.path:
        sys.path.append(src)
    from gistau_ch15.properties.fallback_helium import FallbackHeliumBackend

    return FallbackHeliumBackend()


def config() -> dict[str, Any]:
    pin = yaml.safe_load(PIN_PATH.read_text(encoding="utf-8"))
    xc = pin["output_crosscheck"]
    b = _backend()
    grid = [[float(t), float(p)] for t in xc["grid_T_K"] for p in xc["grid_p_kPa"]]
    probes = [[float(t), float(p)] for t, p in xc["probes_T_K_p_kPa"]]
    return {
        "authority": {
            "repository": pin["authority"]["repository"],
            "commit": pin["authority"]["commit_sha"],
            "runtime": pin["authority"]["runtime_dependency"],
            "output_checksum": xc["output_checksum_sha256"],
        },
        "domain": {"t_min_k": b.DOMAIN_T_MIN_K, "rho_max_kg_m3": b.DOMAIN_RHO_MAX_KG_M3, "status": b.DOMAIN_STATUS},
        "tolerances": xc["tolerances_in_domain"],
        "crosscheck_points": [{"T_K": t, "p_kPa": p, "in_domain": b.in_validity_domain(p, t)} for t, p in grid + probes],
    }


PAGE = Template(r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>GISTAU Ch15 Toolbox</title>
<style>
/* Layout: portal header, calculator tabs over a two-column work area (inputs + results | chart), domain map below; stacks on phones. */
:root {
  --bg: #ffffff; --panel: #ffffff; --fg: #111111; --muted: #5a5a5a; --line: #111111; --soft: #e6e6e6;
  --ok: #007a33; --bad: #b00020; --warn-bg: #fff4e5; --accent: #1f5fa8; --accent-2: #b5651d;
  --font: Arial, "Helvetica Neue", Helvetica, sans-serif; --mono: Consolas, "Liberation Mono", monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #181421; --panel: #241d33; --fg: #f5f2ff; --muted: #cfc2ef; --line: #8f7abd; --soft: #3a3150;
  --ok: #9cf2be; --bad: #ffb3b3; --warn-bg: #3b2a00; --accent: #8cb8ff; --accent-2: #ffc285; color-scheme: dark;
} }
:root[data-theme="dark"] {
  --bg: #181421; --panel: #241d33; --fg: #f5f2ff; --muted: #cfc2ef; --line: #8f7abd; --soft: #3a3150;
  --ok: #9cf2be; --bad: #ffb3b3; --warn-bg: #3b2a00; --accent: #8cb8ff; --accent-2: #ffc285; color-scheme: dark;
}
body { background: var(--bg); color: var(--fg); font-family: var(--font); margin: 0; line-height: 1.45; }
.page { padding-inline: 16px; padding-block: 0 24px; max-width: 1180px; margin-inline: auto; }
.topbar { padding-block: 16px; border-bottom: 4px solid var(--line); }
.topbar h1 { margin: 0 0 6px; font-size: 1.5rem; text-wrap: balance; }
.topbar p { margin: 0; color: var(--muted); max-width: 70ch; }
.strip { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.pill { border: 2px solid var(--line); border-radius: 999px; padding: 3px 10px; font-weight: bold; font-size: .82rem; }
.pill.ok { border-color: var(--ok); color: var(--ok); } .pill.warn { border-color: var(--bad); color: var(--bad); }
.tabs { display: flex; gap: 8px; overflow-x: auto; padding-block: 14px 4px; }
.tabs button { flex: none; font: inherit; font-weight: bold; color: var(--fg); background: var(--panel); border: 2px solid var(--line); border-radius: 999px; padding: 6px 14px; cursor: pointer; }
.tabs button[aria-selected="true"] { background: var(--fg); color: var(--bg); }
.tabs button:focus-visible, input:focus-visible, a:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }
.work { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 340px), 1fr)); gap: 16px; padding-block: 12px; }
.card { border: 3px solid var(--line); border-radius: 12px; padding: 16px; background: var(--panel); min-width: 0; }
.card h2 { margin: 0 0 6px; font-size: 1.1rem; } .card p { margin: 0 0 10px; color: var(--muted); max-width: 70ch; }
.fields { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
.fields label { display: grid; gap: 3px; font-size: .85rem; color: var(--muted); }
.fields input { font: inherit; font-variant-numeric: tabular-nums; color: var(--fg); background: var(--bg); border: 2px solid var(--line); border-radius: 8px; padding: 6px 8px; min-width: 0; }
table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; font-size: .9rem; margin-top: 12px; }
th, td { border: 1px solid var(--line); padding: 5px 8px; text-align: left; }
th { background: var(--fg); color: var(--bg); } td.num { text-align: right; }
.badge { display: inline-block; border-radius: 999px; padding: 1px 8px; font-size: .78rem; font-weight: bold; border: 2px solid currentColor; }
.badge.in { color: var(--ok); } .badge.out { color: var(--bad); }
.error { color: var(--bad); font-weight: bold; min-height: 1.2em; margin-top: 8px; }
.note { font-size: .85rem; color: var(--muted); margin-top: 10px; }
.chart { width: 100%; min-height: 340px; }
.wide { grid-column: 1 / -1; }
.links { display: flex; flex-wrap: wrap; gap: 10px; }
.links a { color: var(--fg); font-weight: bold; }
code { font-family: var(--mono); font-size: .88em; }
</style></head>
<body>
<div class="page">
<header class="topbar">
<h1>GISTAU Ch15 Toolbox</h1>
<p>Engineering calculators for the Chapter 15 tuples, running the ideal-gas basic incarnation in your browser. Governing helium-4 values come from ABACUS; these are cross-check numbers, and every state is marked inside or outside the measured ideal-gas domain.</p>
<div class="strip">
<span class="pill warn">Basic incarnation · CROSSCHECK_ONLY</span>
<span class="pill ok">Governing: $repository @ $commit_short</span>
<span class="pill">$runtime</span>
<span class="pill">Ideal-gas domain: T ≥ $t_min K, ρ ≤ $rho_max kg/m³</span>
</div>
</header>

<nav class="tabs" role="tablist" aria-label="Calculators" id="tabs"></nav>

<main>
<section class="work">
<div class="card" id="calc-card">
<h2 id="calc-title">—</h2>
<p id="calc-note">—</p>
<form class="fields" id="calc-form" onsubmit="return false"></form>
<div class="error" id="calc-error" role="status"></div>
<div style="overflow-x:auto"><table id="calc-results"><thead><tr><th>Result</th><th>Value</th><th>Unit</th></tr></thead><tbody></tbody></table></div>
</div>
<div class="card">
<h2 id="chart-title">—</h2>
<p id="chart-note">—</p>
<div class="chart" id="calc-chart" role="img" aria-label="Process chart"></div>
</div>
<div class="card wide">
<h2>Where the basic incarnation is valid</h2>
<p>Temperature–pressure map of the measured ideal-gas domain (shaded). Dots are the ABACUS cross-check grid ($n_points points, output checksum <code>$checksum_short…</code>); larger markers are the states of the calculator above.</p>
<div class="chart" id="domain-chart" role="img" aria-label="Validity domain map"></div>
<p class="note">Inside the domain the ideal gas stays within $tol_rho % in density, $tol_dh % of cp·T in Δh and $tol_ds J/kg·K in Δs of the governing provider. Outside it, the numbers are indicative only.</p>
</div>
<div class="card wide">
<h2>More in the portal</h2>
<div class="links">
<a href="index.html">GISTAU Ch15 portal</a>
<a href="physics_authority.html">Physics authority review</a>
<a href="tool_values.html">Operating points</a>
<a href="assets/ideal_gas_domain_map.svg">Static domain figure (matplotlib, SVG)</a>
</div>
</div>
</section>
</main>
</div>

<script>window.GISTAU_TOOLBOX_CONFIG = $config_json;</script>
<script src="$plotly"></script>
<script src="assets/gistau_basic.js"></script>
<script>
(function () {
  "use strict";
  var G = window.GistauBasic, CFG = window.GISTAU_TOOLBOX_CONFIG;
  var fmt = function (v, d) { return (v === null || v === undefined) ? "—" : Number(v).toLocaleString("en", { maximumFractionDigits: d === undefined ? 3 : d }); };
  var css = function (n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); };

  function tsChart(states, pressures, title) {
    var traces = [];
    var Ts = []; for (var t = 4; t <= 420; t *= 1.08) Ts.push(t);
    pressures.forEach(function (p, i) {
      traces.push({ x: Ts.map(function (t) { return G.entropyPT(p, t) / 1000; }), y: Ts, mode: "lines", name: "isobar " + fmt(p, 1) + " kPa",
        line: { width: 1.5, dash: i ? "dot" : "solid", color: css(i ? "--accent-2" : "--accent") }, hoverinfo: "skip" });
    });
    traces.push({ x: states.map(function (s) { return s.entropy_j_kgk / 1000; }), y: states.map(function (s) { return s.temperature_k; }),
      mode: "lines+markers", name: "process", line: { width: 3, color: css("--fg") },
      marker: { size: 11, color: states.map(function (s) { return s.validity === "IDEAL_GAS_DOMAIN" ? css("--ok") : css("--bad"); }), line: { width: 1, color: css("--fg") } },
      text: states.map(function (s, i) { return "State " + (i + 1) + "<br>" + fmt(s.temperature_k, 2) + " K, " + fmt(s.pressure_kpa, 1) + " kPa<br>" + (s.validity === "IDEAL_GAS_DOMAIN" ? "inside domain" : "outside domain"); }),
      hovertemplate: "%{text}<extra></extra>" });
    draw("calc-chart", traces, { xaxis: { title: "s [kJ/kg·K] (ref. 300 K, 1 atm)" }, yaxis: { title: "T [K]", type: "log" } });
  }

  function draw(id, traces, layout) {
    var axis = { gridcolor: css("--soft"), zerolinecolor: css("--soft"), linecolor: css("--line"), color: css("--fg") };
    var base = { paper_bgcolor: css("--panel"), plot_bgcolor: css("--panel"), font: { family: "Arial, sans-serif", color: css("--fg"), size: 12 },
      margin: { l: 60, r: 12, t: 10, b: 50 }, legend: { orientation: "h", y: -0.25 }, showlegend: true };
    layout.xaxis = Object.assign({}, axis, layout.xaxis); layout.yaxis = Object.assign({}, axis, layout.yaxis);
    if (window.Plotly) window.Plotly.react(id, traces, Object.assign(base, layout), { displaylogo: false, responsive: true });
    else document.getElementById(id).textContent = "Charts need Plotly, which did not load.";
  }

  var current = { states: [] };

  function domainChart() {
    var T = [], P = [];
    for (var t = CFG.domain.t_min_k; t <= 400; t *= 1.05) { T.push(t); P.push(CFG.domain.rho_max_kg_m3 * G.R * t / 1000); }
    var poly = { x: [CFG.domain.t_min_k].concat(T, [T[T.length - 1], CFG.domain.t_min_k]), y: [1].concat(P, [1, 1]),
      fill: "toself", mode: "lines", name: "ideal-gas domain", line: { color: css("--ok"), width: 1 }, fillcolor: css("--ok"), opacity: 0.18, hoverinfo: "skip" };
    var pts = CFG.crosscheck_points;
    var grid = { x: pts.map(function (q) { return q.T_K; }), y: pts.map(function (q) { return q.p_kPa; }), mode: "markers", name: "ABACUS cross-check point",
      marker: { size: 7, symbol: pts.map(function (q) { return q.in_domain ? "circle" : "x"; }), color: pts.map(function (q) { return q.in_domain ? css("--ok") : css("--bad"); }) },
      text: pts.map(function (q) { return q.T_K + " K, " + q.p_kPa + " kPa, " + (q.in_domain ? "in domain" : "outside"); }), hovertemplate: "%{text}<extra></extra>" };
    var mine = { x: current.states.map(function (s) { return s.temperature_k; }), y: current.states.map(function (s) { return s.pressure_kpa; }),
      mode: "lines+markers", name: "this calculation", line: { color: css("--fg"), width: 2 }, marker: { size: 13, color: css("--accent"), line: { width: 2, color: css("--fg") } } };
    draw("domain-chart", [poly, grid, mine], { xaxis: { title: "T [K]", type: "log", range: [Math.log10(3), Math.log10(400)] }, yaxis: { title: "p [kPa]", type: "log", range: [Math.log10(10), Math.log10(3000)] } });
  }

  var CALCS = [
    { id: "state", label: "State point", note: "Density, enthalpy and entropy of helium-4 at a given pressure and temperature.",
      fields: [["p_kpa", "Pressure", "kPa", 101.325], ["t_k", "Temperature", "K", 300]],
      run: function (v) { var s = G.statePT(v.p_kpa, v.t_k); return { states: [s], pressures: [v.p_kpa],
        rows: [["Density", s.density_kg_m3, "kg/m³", 4], ["Enthalpy (h = cp·T)", s.enthalpy_j_kg / 1000, "kJ/kg"], ["Entropy", s.entropy_j_kgk / 1000, "kJ/kg·K", 4]] }; } },
    { id: "compressor", label: "Compressor", note: "Isothermal shaft power and isentropic outlet for a helium stage (Ch15 T01).",
      fields: [["p1_kpa", "Inlet pressure", "kPa", 100], ["t1_k", "Inlet temperature", "K", 300], ["p2_kpa", "Outlet pressure", "kPa", 1200], ["mdot_kg_s", "Mass flow", "kg/s", 0.2], ["eta_isothermal", "Isothermal efficiency", "–", 0.6], ["eta_isentropic", "Isentropic efficiency", "–", 0.75]],
      run: function (v) { var r = G.compressor(v); return { states: r.states, pressures: [v.p1_kpa, v.p2_kpa],
        rows: [["Isentropic outlet temperature", r.outlet_temperature_k, "K", 2], ["Isothermal shaft power", r.shaft_power_w / 1000, "kW"], ["Isentropic shaft power", r.isentropic_shaft_power_w / 1000, "kW"]] }; } },
    { id: "jt", label: "JT valve", note: "Isenthalpic expansion with heat leak (Ch15 T02). An ideal gas has no Joule–Thomson effect, so only the heat leak moves the temperature.",
      fields: [["p1_kpa", "Inlet pressure", "kPa", 1400], ["t1_k", "Inlet temperature", "K", 20], ["p2_kpa", "Outlet pressure", "kPa", 100], ["mdot_kg_s", "Mass flow", "kg/s", 0.05], ["heat_leak_w", "Heat leak", "W", 100]],
      run: function (v) { var r = G.jtValve(v); return { states: r.states, pressures: [v.p1_kpa, v.p2_kpa],
        rows: [["Outlet temperature", r.outlet_temperature_k, "K", 3], ["Outlet enthalpy", r.outlet_enthalpy_j_kg / 1000, "kJ/kg"], ["Energy residual", r.energy_residual_j_kg, "J/kg", 6]] }; } },
    { id: "expander", label: "Expander", note: "Isentropic expansion with efficiency and recovered power (Ch15 T04).",
      fields: [["p1_kpa", "Inlet pressure", "kPa", 1400], ["t1_k", "Inlet temperature", "K", 25], ["p2_kpa", "Outlet pressure", "kPa", 120], ["mdot_kg_s", "Mass flow", "kg/s", 0.05], ["eta_isentropic", "Isentropic efficiency", "–", 0.75]],
      run: function (v) { var r = G.expander(v); return { states: r.states, pressures: [v.p1_kpa, v.p2_kpa],
        rows: [["Isentropic outlet temperature", r.ideal_outlet_temperature_k, "K", 2], ["Actual outlet temperature", r.outlet_temperature_k, "K", 2], ["Recovered power", r.power_output_w / 1000, "kW"]] }; } },
    { id: "hx", label: "Heat exchanger", note: "Effectiveness method for a counterflow exchanger (Ch15 T03).",
      fields: [["hot_inlet_k", "Hot inlet", "K", 300], ["cold_inlet_k", "Cold inlet", "K", 80], ["hot_capacity_rate_wk", "Hot capacity rate", "W/K", 500], ["cold_capacity_rate_wk", "Cold capacity rate", "W/K", 350], ["effectiveness", "Effectiveness", "–", 0.82]],
      run: function (v) { var r = G.heatExchanger(v); return { states: [], hx: r,
        rows: [["Heat duty", r.q_transfer_w / 1000, "kW"], ["Hot outlet", r.hot_outlet_k, "K", 2], ["Cold outlet", r.cold_outlet_k, "K", 2]] }; } },
    { id: "eq", label: "Equivalent power", note: "Ambient-equivalent power: compressor minus recovery plus Carnot-weighted refrigeration (Ch15 T06).",
      fields: [["compressor_power_w", "Compressor power", "W", 1200000], ["expander_recovery_w", "Expander recovery", "W", 30000], ["refrigeration_load_w", "Refrigeration load", "W", 2000], ["cold_temperature_k", "Cold temperature", "K", 4.5], ["ambient_temperature_k", "Ambient temperature", "K", 300]],
      run: function (v) { var r = G.equivalentPower(v); return { states: [], eq: r,
        rows: [["Carnot factor", r.carnot_factor, "–", 2], ["Equivalent power", r.equivalent_power_w / 1000, "kW", 1]] }; } }
  ];

  var active = CALCS[0];

  function renderChart(out) {
    var title = document.getElementById("chart-title"), note = document.getElementById("chart-note");
    if (out.hx) {
      title.textContent = "End temperatures"; note.textContent = "Hot and cold streams from inlet to outlet (straight lines join the end temperatures).";
      draw("calc-chart", [
        { x: [0, 1], y: [out.hx.hot_inlet_k, out.hx.hot_outlet_k], mode: "lines+markers", name: "hot stream", line: { width: 3, color: css("--accent-2") } },
        { x: [1, 0], y: [out.hx.cold_inlet_k, out.hx.cold_outlet_k], mode: "lines+markers", name: "cold stream", line: { width: 3, color: css("--accent") } }
      ], { xaxis: { title: "position along exchanger [–]" }, yaxis: { title: "T [K]" } });
    } else if (out.eq) {
      title.textContent = "Power breakdown"; note.textContent = "Contributions to the ambient-equivalent power.";
      var r = out.eq;
      draw("calc-chart", [{ type: "bar", x: ["Compressor", "Expander recovery", "Refrigeration × Carnot", "Equivalent"],
        y: [r.compressor_power_w, -r.expander_recovery_w, r.refrigeration_load_w * r.carnot_factor, r.equivalent_power_w].map(function (w) { return w / 1000; }),
        marker: { color: [css("--accent"), css("--ok"), css("--accent-2"), css("--fg")] }, hovertemplate: "%{x}: %{y:,.1f} kW<extra></extra>" }],
        { xaxis: { title: "" }, yaxis: { title: "power [kW]" }, showlegend: false });
    } else {
      title.textContent = "T–s diagram"; note.textContent = "Ideal-gas isobars and the process states (green inside the domain, red outside).";
      tsChart(out.states, out.pressures);
    }
  }

  function compute() {
    var v = {}, err = document.getElementById("calc-error"), body = document.querySelector("#calc-results tbody");
    active.fields.forEach(function (f) { v[f[0]] = parseFloat(document.getElementById("in-" + f[0]).value); });
    err.textContent = ""; body.textContent = "";
    var out;
    try { out = active.run(v); } catch (e) { err.textContent = e.message; current.states = []; domainChart(); return; }
    out.rows.forEach(function (r) {
      var tr = document.createElement("tr");
      [r[0], fmt(r[1], r[3]), r[2]].forEach(function (c, i) { var td = document.createElement("td"); td.textContent = c; if (i === 1) td.className = "num"; tr.appendChild(td); });
      body.appendChild(tr);
    });
    out.states.forEach(function (s, i) {
      var tr = document.createElement("tr"), a = document.createElement("td"), b = document.createElement("td"), c = document.createElement("td");
      a.textContent = "State " + (i + 1) + " (" + fmt(s.temperature_k, 2) + " K, " + fmt(s.pressure_kpa, 1) + " kPa)";
      var badge = document.createElement("span"); badge.className = "badge " + (s.validity === "IDEAL_GAS_DOMAIN" ? "in" : "out");
      badge.textContent = s.validity === "IDEAL_GAS_DOMAIN" ? "inside domain" : "outside domain"; b.appendChild(badge);
      c.textContent = "ρ " + fmt(s.density_kg_m3, 3) + " kg/m³"; tr.append(a, b, c); body.appendChild(tr);
    });
    current.states = out.states; renderChart(out); domainChart();
  }

  function select(calc) {
    active = calc;
    document.querySelectorAll("#tabs button").forEach(function (b) { b.setAttribute("aria-selected", String(b.dataset.id === calc.id)); });
    document.getElementById("calc-title").textContent = calc.label;
    document.getElementById("calc-note").textContent = calc.note;
    var form = document.getElementById("calc-form"); form.textContent = "";
    calc.fields.forEach(function (f) {
      var label = document.createElement("label"), input = document.createElement("input");
      label.htmlFor = "in-" + f[0]; label.textContent = f[1] + " [" + f[2] + "]";
      input.id = "in-" + f[0]; input.type = "number"; input.step = "any"; input.value = f[3]; input.inputMode = "decimal";
      input.addEventListener("input", compute); label.appendChild(input); form.appendChild(label);
    });
    compute();
    try { history.replaceState(null, "", "#" + calc.id); } catch (e) {}
  }

  var tabs = document.getElementById("tabs");
  CALCS.forEach(function (c) {
    var b = document.createElement("button"); b.type = "button"; b.setAttribute("role", "tab"); b.dataset.id = c.id; b.textContent = c.label;
    b.addEventListener("click", function () { select(c); }); tabs.appendChild(b);
  });
  var start = CALCS.filter(function (c) { return "#" + c.id === location.hash; })[0] || CALCS[0];
  select(start);
  if (window.matchMedia) window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", compute);
})();
</script>
</body></html>
""")


def render() -> str:
    cfg = config()
    auth, dom, tol = cfg["authority"], cfg["domain"], cfg["tolerances"]
    return PAGE.substitute(
        repository=auth["repository"],
        commit_short=auth["commit"][:7],
        runtime=auth["runtime"],
        t_min=f"{dom['t_min_k']:g}",
        rho_max=f"{dom['rho_max_kg_m3']:g}",
        n_points=len(cfg["crosscheck_points"]),
        checksum_short=auth["output_checksum"][:12],
        tol_rho=f"{tol['density_rel'] * 100:g}",
        tol_dh=f"{tol['delta_h_frac_of_cpT'] * 100:g}",
        tol_ds=f"{tol['delta_s_abs_J_kgK']:g}",
        config_json=json.dumps(cfg, sort_keys=True, separators=(",", ":")),
        plotly=PLOTLY,
    )


def render_figure(path: Path = FIGURE) -> Path:
    """Static domain map for reports (matplotlib; deterministic SVG)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    matplotlib.rcParams["svg.hashsalt"] = "gistau-ch15"
    cfg = config()
    b = _backend()
    t_line = [cfg["domain"]["t_min_k"] * 1.05**i for i in range(40) if cfg["domain"]["t_min_k"] * 1.05**i <= 400]
    p_line = [cfg["domain"]["rho_max_kg_m3"] * b.R * t / 1000 for t in t_line]
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=100)
    ax.fill_between(t_line, 1, p_line, color="#2e9d55", alpha=0.18, label="ideal-gas domain")
    ax.plot(t_line, p_line, color="#2e9d55", lw=1.2)
    ax.axvline(cfg["domain"]["t_min_k"], color="#2e9d55", lw=1.2)
    pts = cfg["crosscheck_points"]
    inside = [q for q in pts if q["in_domain"]]
    outside = [q for q in pts if not q["in_domain"]]
    ax.scatter([q["T_K"] for q in inside], [q["p_kPa"] for q in inside], s=28, color="#007a33", label="cross-check point, in domain", zorder=3)
    ax.scatter([q["T_K"] for q in outside], [q["p_kPa"] for q in outside], s=36, marker="x", color="#b00020", label="cross-check point, outside", zorder=3)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(3, 400)
    ax.set_ylim(10, 3000)
    ax.set_xlabel("T [K]")
    ax.set_ylabel("p [kPa]")
    ax.set_title(
        f"He-4 ideal-gas validity vs ABACUS @ {cfg['authority']['commit'][:7]} ({cfg['authority']['runtime']})", fontsize=10
    )
    ax.grid(True, which="both", color="#dddddd", lw=0.6)
    ax.legend(loc="upper left", fontsize=8, frameon=False)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, format="svg", metadata={"Date": None})
    plt.close(fig)
    return path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--figures", action="store_true", help="also render the matplotlib SVG (needs matplotlib)")
    args = ap.parse_args(argv)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(REPO_ROOT)}")
    if args.figures:
        print(f"wrote {render_figure().relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
