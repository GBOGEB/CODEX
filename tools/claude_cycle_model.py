"""Gistau Ch3 §3.5.3.1 one-turbine Claude cycle: thermodynamic balance, optimisation, sweep and statistics.

Reproduces Figs. 3.46 / 3.47 / 3.48 of G. Gistau Baguer, *Cryogenic Helium Refrigeration for
Middle and Large Powers* (Springer, 2020) from fluid properties, and reports how far the
reproduction is from the printed values.

Property tier: CoolProp (tier1 reference, NOT the governing ABACUS He-4 provider). The model
itself is provider-agnostic: ``solve`` takes any object with the ``Props`` methods below, so the
governing provider can be swapped in when it exposes saturation and (p, s) inversion.

Balance (all enthalpies in J/g, flows in g/s, the book's envelopes):

  JT envelope (HX3 + valve + bath):
      m_jt * h_HP(T3) + Q = L * h_liq_sat(p_LP) + (m_jt - L) * h_LP(T7)
  Brayton envelope (HX1 + HX2 + turbine), turbine discharge at T7 (mixes with JT return):
      m_hp * h_HP(T_warm) + (m_jt - L) * h_LP(T7)
          = (m_hp - L) * h_LP(T_warm - dT_w) + m_jt * h_HP(T3) + m_t * dh_t
      m_hp = m_jt + m_t,  dh_t = eta * (h_in - h_is) with T_in solved so that the real outlet is T7
  T3 = T7 + dT_jt (HX3 warm-end pinch).

Usage:
    python tools/claude_cycle_model.py --write     # needs CoolProp; writes JSON record and HTML page
    python tools/claude_cycle_model.py --check     # page is current with the committed JSON (no CoolProp)
"""
from __future__ import annotations

import argparse
import html
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol

REPO_ROOT = Path(__file__).resolve().parents[1]
BENCH = REPO_ROOT / "docs" / "gistau-ch3" / "data" / "claude_cycle_benchmarks.json"
RECORD = REPO_ROOT / "docs" / "gistau-ch3" / "data" / "claude_cycle_reproduction.json"
PAGE = REPO_ROOT / "docs" / "gistau-ch3" / "claude_cycle_model.html"
R_UNIVERSAL = 8.314472
M_HELIUM = 4.0026  # g/mol, as used in the book (Ch15 Sect. 15.8.1)


class Props(Protocol):
    def h(self, t_k: float, p_bar: float) -> float: ...            # J/g
    def s(self, t_k: float, p_bar: float) -> float: ...            # J/g/K
    def h_ps(self, s_j_gk: float, p_bar: float) -> float: ...      # J/g
    def h_liq_sat(self, p_bar: float) -> float: ...                # J/g


class CoolPropHelium:
    """Tier-1 reference adapter (CoolProp HEOS helium)."""

    name = "CoolProp"

    def __init__(self) -> None:
        import CoolProp
        from CoolProp.CoolProp import PropsSI

        self._p = PropsSI
        self.version = CoolProp.__version__

    def h(self, t_k, p_bar):
        return self._p("H", "T", t_k, "P", p_bar * 1e5, "Helium") / 1e3

    def s(self, t_k, p_bar):
        return self._p("S", "T", t_k, "P", p_bar * 1e5, "Helium") / 1e3

    def h_ps(self, s_j_gk, p_bar):
        return self._p("H", "S", s_j_gk * 1e3, "P", p_bar * 1e5, "Helium") / 1e3

    def h_liq_sat(self, p_bar):
        return self._p("H", "P", p_bar * 1e5, "Q", 0, "Helium") / 1e3


@dataclass(frozen=True)
class Design:
    refrigeration_w: float = 50.0
    liquefaction_g_s: float = 0.5
    p_high_bar: float = 14.0
    p_low_bar: float = 1.2
    t_warm_k: float = 300.0
    warm_end_dt_k: float = 3.0
    jt_hx_warm_end_dt_k: float = 0.2
    turbine_isentropic_efficiency: float = 0.75


def _bisect(f, lo: float, hi: float, tol: float = 1e-9) -> float:
    f_lo = f(lo)
    if f_lo * f(hi) > 0:
        raise ValueError(f"root not bracketed in [{lo}, {hi}]")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        f_mid = f(mid)
        if (f_mid > 0) == (f_lo > 0):
            lo, f_lo = mid, f_mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


def turbine_inlet_t(props: Props, t_out_k: float, d: Design) -> float:
    """Inlet temperature at p_high whose real expansion (eta) to p_low ends at t_out_k."""
    h_out = props.h(t_out_k, d.p_low_bar)
    eta = d.turbine_isentropic_efficiency

    def resid(t_in):
        h_in = props.h(t_in, d.p_high_bar)
        h_is = props.h_ps(props.s(t_in, d.p_high_bar), d.p_low_bar)
        return h_in - eta * (h_in - h_is) - h_out

    return _bisect(resid, t_out_k, d.t_warm_k)


def solve(props: Props, t7_k: float, d: Design | None = None) -> dict[str, float]:
    """Mass flows, turbine and HX duties for turbine discharge temperature t7_k (LP side of HX3 warm end)."""
    d = d or Design()
    q, liq, ph, pl = d.refrigeration_w, d.liquefaction_g_s, d.p_high_bar, d.p_low_bar
    t3 = t7_k + d.jt_hx_warm_end_dt_k
    h_hp3, h_lp7, h_l = props.h(t3, ph), props.h(t7_k, pl), props.h_liq_sat(pl)
    m_jt = (q + liq * (h_lp7 - h_l)) / (h_lp7 - h_hp3)
    t_in = turbine_inlet_t(props, t7_k, d)
    h_tin = props.h(t_in, ph)
    dh_t = h_tin - h_lp7
    h_hp1, h_lp_w = props.h(d.t_warm_k, ph), props.h(d.t_warm_k - d.warm_end_dt_k, pl)
    m_t = (m_jt * (h_lp_w + h_hp3 - h_hp1 - h_lp7) - liq * h_lp_w + liq * h_lp7) / (h_hp1 - h_lp_w - dh_t)
    m_hp, m_lp = m_jt + m_t, m_jt + m_t - liq
    # HX2: HP m_jt from t_in to t3; LP m_lp from t7 up to the HX1/HX2 junction
    q_hx2 = m_jt * (h_tin - h_hp3)
    h_lp_mid = h_lp7 + q_hx2 / m_lp
    q_hx1 = m_hp * (h_hp1 - h_tin)
    w_iso = m_hp * 1e-3 * (R_UNIVERSAL / M_HELIUM) * 1e3 * d.t_warm_k * math.log(ph / pl)  # W
    # Envelope closure (should be ~0): energy in minus energy out across the whole cold box
    closure = (m_hp * h_hp1 + q) - ((m_lp) * h_lp_w + liq * h_l + m_t * dh_t)
    return {
        "turbine_discharge_t_k": t7_k,
        "jt_hx_hp_inlet_t_k": t3,
        "turbine_inlet_t_k": t_in,
        "jt_mass_flow_g_s": m_jt,
        "brayton_mass_flow_g_s": m_t,
        "cycle_hp_mass_flow_g_s": m_hp,
        "cycle_lp_return_mass_flow_g_s": m_lp,
        "turbine_power_w": -m_t * dh_t,
        "isothermal_compressor_power_kw": w_iso / 1e3,
        "hx1_q_w": q_hx1,
        "hx2_q_w": q_hx2,
        "lp_t_between_hx2_hx1_k": _bisect(lambda t: props.h(t, pl) - h_lp_mid, t7_k, d.t_warm_k),
        "energy_closure_w": closure,
    }


def optimise(props: Props, d: Design | None = None, lo: float = 8.0, hi: float = 30.0) -> dict[str, float]:
    """Golden-section minimum of the LP return (= compressor) flow over turbine discharge temperature."""
    d = d or Design()
    g = (math.sqrt(5) - 1) / 2
    a, b = lo, hi
    c, e = b - g * (b - a), a + g * (b - a)
    fc, fe = solve(props, c, d)["cycle_lp_return_mass_flow_g_s"], solve(props, e, d)["cycle_lp_return_mass_flow_g_s"]
    while b - a > 1e-4:
        if fc < fe:
            b, e, fe = e, c, fc
            c = b - g * (b - a)
            fc = solve(props, c, d)["cycle_lp_return_mass_flow_g_s"]
        else:
            a, c, fc = c, e, fe
            e = a + g * (b - a)
            fe = solve(props, e, d)["cycle_lp_return_mass_flow_g_s"]
    return solve(props, 0.5 * (a + b), d)


def _deviation_rows(book: dict[str, Any], got: dict[str, float], case: str) -> list[dict[str, Any]]:
    keys = {
        "jt_mass_flow_g_s": "jt_mass_flow_g_s",
        "brayton_mass_flow_g_s": "brayton_mass_flow_g_s",
        "cycle_lp_return_mass_flow_g_s": "cycle_lp_return_mass_flow_g_s",
        "cycle_hp_mass_flow_g_s": "cycle_hp_mass_flow_g_s",
        "isothermal_compressor_power_kw": "isothermal_compressor_power_kw",
        "turbine_inlet_t_k": "turbine_inlet_t_k",
        "turbine_power_w": "turbine_power_w",
        "turbine_discharge_t_k": "turbine_discharge_t_k",
    }
    rows = []
    for bk, gk in keys.items():
        if bk not in book or not isinstance(book[bk], (int, float)):
            continue
        exp, val = float(book[bk]), got[gk]
        rows.append({"case": case, "quantity": bk, "book": exp, "model": round(val, 4),
                     "abs_dev": round(val - exp, 4), "rel_dev": round((val - exp) / exp, 6)})
    for hx, qk in (("hx1", "hx1_q_w"), ("hx2", "hx2_q_w")):
        if isinstance(book.get(hx), dict) and "q_w" in book[hx]:
            exp, val = float(book[hx]["q_w"]), got[qk]
            rows.append({"case": case, "quantity": f"{hx}_q_w", "book": exp, "model": round(val, 2),
                         "abs_dev": round(val - exp, 2), "rel_dev": round((val - exp) / exp, 6)})
    return rows


def _stats(rows: list[dict[str, Any]], tol_rel: float) -> dict[str, Any]:
    rel = [abs(r["rel_dev"]) for r in rows]
    return {
        "n": len(rel),
        "max_abs_rel_dev": round(max(rel), 6),
        "rms_rel_dev": round(math.sqrt(sum(x * x for x in rel) / len(rel)), 6),
        "mean_abs_rel_dev": round(sum(rel) / len(rel), 6),
        "within_tolerance": sum(x <= tol_rel for x in rel),
        "tolerance_rel": tol_rel,
    }


def build_record(props: Props) -> dict[str, Any]:
    bench = {b["benchmark_id"]: b for b in json.loads(BENCH.read_text(encoding="utf-8"))["benchmarks"]}
    b_init = bench["G3-3.5.3.1-ONE-TURBINE-INITIAL"]["expected_outputs"]
    b_opt = bench["G3-3.5.3.1-ONE-TURBINE-OPTIMISED"]["expected_outputs"]
    d = Design()
    # Input taken from the benchmark (Fig. 3.46: HP 20.00 K, LP / turbine discharge 19.80 K).
    t7_init = float(bench["G3-3.5.3.1-ONE-TURBINE-INITIAL"]["inputs"]["turbine_discharge_t_k"])
    init = solve(props, t7_init, d)
    opt = optimise(props, d)
    rows = _deviation_rows(b_init, init, "initial") + _deviation_rows(b_opt, opt, "optimised")
    sweep = [solve(props, t / 4, d) for t in range(40, 101)]  # 10.00 .. 25.00 K, 0.25 K
    m_min = opt["cycle_lp_return_mass_flow_g_s"]
    band = [r["turbine_discharge_t_k"] for r in sweep if r["cycle_lp_return_mass_flow_g_s"] <= 1.01 * m_min]
    eta_study = []
    for eta in (0.65, 0.70, 0.75, 0.80, 0.85):
        o = optimise(props, Design(turbine_isentropic_efficiency=eta))
        eta_study.append({"eta": eta, "opt_t_k": round(o["turbine_discharge_t_k"], 3),
                          "min_flow_g_s": round(o["cycle_lp_return_mass_flow_g_s"], 3),
                          "w_iso_kw": round(o["isothermal_compressor_power_kw"], 3)})
    rnd = lambda r: {k: round(v, 4) for k, v in r.items()}
    return {
        "schema": "codex-gistau-ch3-claude-cycle-reproduction/v1",
        "authority": "REFERENCE_REPRODUCTION_NOT_QPS_DESIGN",
        "source": "Gistau Baguer 2020, Ch. 3 §3.5.3.1, Figs. 3.46-3.48 (book pp. 123-125)",
        "property_tier": f"tier1_coolprop {props.version} (reference, not the governing ABACUS provider)",
        "design": asdict(d),
        "initial": rnd(init),
        "optimised": rnd(opt),
        "deviations": rows,
        "stats": _stats(rows, 0.01),
        "flat_optimum_band_1pct_k": [band[0], band[-1]],
        "sweep": [{"t7_k": r["turbine_discharge_t_k"], "jt": round(r["jt_mass_flow_g_s"], 4),
                   "brayton": round(r["brayton_mass_flow_g_s"], 4),
                   "total": round(r["cycle_lp_return_mass_flow_g_s"], 4)} for r in sweep],
        "eta_sensitivity": eta_study,
    }


# ---------------------------------------------------------------- page

def _e(x: Any) -> str:
    return html.escape(str(x))


def _chart(sweep: list[dict[str, float]], init: dict, opt: dict) -> str:
    w, h, ml, mr, mt, mb = 720, 340, 52, 128, 16, 44
    xs = [r["t7_k"] for r in sweep]
    x0, x1, y0 = min(xs), max(xs), 0.0
    y1 = 10.0 * math.ceil(max(max(r['total'], r['jt'], r['brayton']) for r in sweep) / 10.0)
    sx = lambda x: ml + (x - x0) / (x1 - x0) * (w - ml - mr)
    sy = lambda y: mt + (1 - (y - y0) / (y1 - y0)) * (h - mt - mb)
    parts = [f"<svg viewBox='0 0 {w} {h}' role='img' aria-labelledby='fig-t fig-d' class='chart'>",
             "<title id='fig-t'>Mass flows versus turbine discharge temperature</title>",
             ("<desc id='fig-d'>JT flow falls and Brayton flow rises as the turbine discharge temperature drops; "
              f"their sum is minimum at {opt['turbine_discharge_t_k']:.2f} K.</desc>")]
    for y in range(0, int(y1) + 1, 10):
        parts.append(f"<line class='grid' x1='{ml}' x2='{w - mr}' y1='{sy(y):.1f}' y2='{sy(y):.1f}'/>"
                     f"<text class='tick' x='{ml - 8}' y='{sy(y) + 4:.1f}' text-anchor='end'>{y}</text>")
    for x in range(int(x0), int(x1) + 1, 5):
        parts.append(f"<text class='tick' x='{sx(x):.1f}' y='{h - mb + 18}' text-anchor='middle'>{x}</text>")
    parts.append(f"<text class='axis' x='{(ml + w - mr) / 2}' y='{h - 6}' text-anchor='middle'>Turbine discharge temperature T7 (K)</text>"
                 f"<text class='axis' transform='translate(14 {(mt + h - mb) / 2}) rotate(-90)' text-anchor='middle'>Mass flow (g/s)</text>")
    for key, cls, label in (("total", "s1", "Cycle (total)"), ("brayton", "s2", "Brayton (turbine)"), ("jt", "s3", "JT")):
        pts = " ".join(f"{sx(r['t7_k']):.1f},{sy(r[key]):.1f}" for r in sweep)
        last = sweep[-1]
        parts.append(f"<polyline class='line {cls}' points='{pts}'/>"
                     f"<text class='dlabel' x='{sx(last['t7_k']) + 6:.1f}' y='{sy(last[key]) + 4:.1f}'>{label}</text>")
    for case, r, tag in (("Book Fig. 3.46", init, "initial"), ("Book Fig. 3.48", opt, "optimum")):
        x, y = sx(r["turbine_discharge_t_k"]), sy(r["cycle_lp_return_mass_flow_g_s"])
        parts.append(f"<circle class='mark' cx='{x:.1f}' cy='{y:.1f}' r='5'/>"
                     f"<text class='note' x='{x:.1f}' y='{y - 10:.1f}' text-anchor='middle'>{tag} {r['cycle_lp_return_mass_flow_g_s']:.2f}</text>")
    parts.append(f"<g class='hover'><line class='xhair' y1='{mt}' y2='{h - mb}'/></g>")
    for r in sweep:
        x = sx(r["t7_k"])
        parts.append(f"<rect class='hit' x='{x - 3.5:.1f}' y='{mt}' width='7' height='{h - mt - mb}' "
                     f"data-tip='T7 {r['t7_k']:.2f} K · total {r['total']:.2f} · Brayton {r['brayton']:.2f} · JT {r['jt']:.2f} g/s'/>")
    parts.append("</svg>")
    return "".join(parts)


CSS = """
:root{--bg:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#8a8984;--grid:#e6e5e0;--card:#fff;
--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--good:#008300;--warn:#b46a00}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;
--muted:#8f8e86;--grid:#33332f;--card:#222220;--s1:#3987e5;--s2:#d95926;--s3:#199e70;--good:#3fae3f;--warn:#e0a040}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font-family:Aptos,"Segoe UI",system-ui,sans-serif;line-height:1.5}
a{color:var(--s1)}main{max-width:980px;margin:0 auto;padding:24px 16px 48px}h1{font-size:1.6rem;margin:.2rem 0}
h2{font-size:1.15rem;margin:2rem 0 .5rem}.ref{color:var(--ink2);font-size:.9rem}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:16px 0}
.tile{background:var(--card);border:1px solid var(--grid);border-radius:8px;padding:12px}
.tile b{display:block;font-size:1.5rem}.tile span{color:var(--ink2);font-size:.85rem}
.chart{width:100%;height:auto;background:var(--card);border:1px solid var(--grid);border-radius:8px}
.grid{stroke:var(--grid);stroke-width:1}.tick,.axis,.dlabel,.note{fill:var(--ink2);font-size:12px}
.axis{fill:var(--ink)}.line{fill:none;stroke-width:2}.s1{stroke:var(--s1)}.s2{stroke:var(--s2)}.s3{stroke:var(--s3)}
.mark{fill:var(--bg);stroke:var(--ink);stroke-width:2}.hit{fill:transparent}.xhair{stroke:var(--muted);stroke-width:1;opacity:0}
.tip{position:fixed;pointer-events:none;background:var(--card);color:var(--ink);border:1px solid var(--grid);
border-radius:6px;padding:6px 8px;font-size:.85rem;opacity:0}
.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:.9rem;font-variant-numeric:tabular-nums}
th,td{border-bottom:1px solid var(--grid);padding:6px 8px;text-align:right}th:first-child,td:first-child,
th:nth-child(2),td:nth-child(2){text-align:left}th{color:var(--ink2);font-weight:600}
.ok{color:var(--good)}.hi{color:var(--warn)}.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:.9rem;color:var(--ink2)}
.legend i{display:inline-block;width:18px;height:2px;vertical-align:middle;margin-right:6px}
.box{border-left:3px solid var(--grid);padding:4px 12px;color:var(--ink2)}
"""

JS = """
const tip=document.querySelector('.tip'),xh=document.querySelector('.xhair');
document.querySelectorAll('.hit').forEach(r=>{r.addEventListener('mousemove',e=>{tip.textContent=r.dataset.tip;
tip.style.opacity=1;tip.style.left=(e.clientX+12)+'px';tip.style.top=(e.clientY+12)+'px';
const x=+r.getAttribute('x')+3.5;xh.setAttribute('x1',x);xh.setAttribute('x2',x);xh.style.opacity=1});
r.addEventListener('mouseleave',()=>{tip.style.opacity=0;xh.style.opacity=0})});
"""


def render(rec: dict[str, Any] | None = None) -> str:
    rec = rec or json.loads(RECORD.read_text(encoding="utf-8"))
    ini, opt, st = rec["initial"], rec["optimised"], rec["stats"]
    band = rec["flat_optimum_band_1pct_k"]
    saving = 1 - opt["cycle_lp_return_mass_flow_g_s"] / ini["cycle_lp_return_mass_flow_g_s"]
    tiles = "".join(f"<div class='tile'><b>{v}</b><span>{_e(k)}</span></div>" for k, v in (
        ("Optimum turbine discharge T7", f"{opt['turbine_discharge_t_k']:.2f} K"),
        ("Cycle flow, initial → optimised", f"{ini['cycle_lp_return_mass_flow_g_s']:.2f} → {opt['cycle_lp_return_mass_flow_g_s']:.2f} g/s"),
        ("Compressor flow saving", f"{saving * 100:.1f} %"),
        (f"Max deviation from book ({st['n']} values)", f"{st['max_abs_rel_dev'] * 100:.2f} %"),
    ))
    dev = "".join(
        f"<tr><td>{_e(r['case'])}</td><td>{_e(r['quantity'])}</td><td>{r['book']:g}</td><td>{r['model']:g}</td>"
        f"<td>{r['abs_dev']:+g}</td><td class='{'ok' if abs(r['rel_dev']) <= st['tolerance_rel'] else 'hi'}'>"
        f"{r['rel_dev'] * 100:+.2f} %</td></tr>" for r in rec["deviations"])
    eta = "".join(f"<tr><td>{r['eta']:.2f}</td><td></td><td>{r['opt_t_k']:.2f}</td><td>{r['min_flow_g_s']:.2f}</td>"
                  f"<td>{r['w_iso_kw']:.2f}</td><td></td></tr>" for r in rec["eta_sensitivity"])
    sw = "".join(f"<tr><td>{r['t7_k']:.2f}</td><td></td><td>{r['jt']:.2f}</td><td>{r['brayton']:.2f}</td>"
                 f"<td>{r['total']:.2f}</td><td></td></tr>" for r in rec["sweep"][::4])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Claude Cycle Model</title><style>{CSS}</style></head><body><main>
<p class="ref"><a href="index.html">Chapter 3</a> · <a href="../gistau/index.html">Book navigator</a></p>
<h1>One-turbine Claude cycle: reproduction of Gistau §3.5.3.1</h1>
<p class="ref">{_e(rec['source'])}. Properties: {_e(rec['property_tier'])}.</p>
<div class="tiles">{tiles}</div>
<h2>Fig. 3.47 reproduced: where the JT and Brayton flows balance</h2>
<div class="legend"><span><i style="background:var(--s1)"></i>Cycle (total)</span><span><i style="background:var(--s2)"></i>Brayton (turbine)</span>
<span><i style="background:var(--s3)"></i>JT</span><span>○ book points (Figs. 3.46, 3.48)</span></div>
{_chart(rec['sweep'], ini, opt)}<div class="tip" role="status"></div>
<p class="ref">The total stays within 1 % of its minimum for T7 between {band[0]:.2f} and {band[1]:.2f} K: the optimum is flat, so
turbine discharge temperature can be chosen for HX3 and turbine margins inside that band at almost no flow cost.</p>
<h2>Deviation from the printed values</h2>
<p class="ref">{st['within_tolerance']} of {st['n']} values within {st['tolerance_rel'] * 100:.0f} %;
RMS {st['rms_rel_dev'] * 100:.3f} %, mean |dev| {st['mean_abs_rel_dev'] * 100:.3f} %, max {st['max_abs_rel_dev'] * 100:.3f} %.</p>
<div class="scroll"><table><thead><tr><th>Case</th><th>Quantity</th><th>Book</th><th>Model</th><th>Δ</th><th>Δ rel</th></tr></thead>
<tbody>{dev}</tbody></table></div>
<h2>Turbine efficiency sensitivity (optimised each time)</h2>
<div class="scroll"><table><thead><tr><th>η turbine</th><th></th><th>Optimum T7 (K)</th><th>Min flow (g/s)</th><th>W iso (kW)</th><th></th></tr></thead>
<tbody>{eta}</tbody></table></div>
<h2>Sweep data (every 1 K)</h2>
<div class="scroll"><table><thead><tr><th>T7 (K)</th><th></th><th>JT (g/s)</th><th>Brayton (g/s)</th><th>Total (g/s)</th><th></th></tr></thead>
<tbody>{sw}</tbody></table></div>
<h2>Model</h2>
<p class="box">JT envelope: ṁ<sub>JT</sub>·h<sub>HP</sub>(T3) + Q = L·h<sub>l,sat</sub> + (ṁ<sub>JT</sub> − L)·h<sub>LP</sub>(T7), with T3 = T7 + 0.2 K.<br>
Brayton envelope: turbine inlet solved so the η = 0.75 expansion ends at T7; ṁ<sub>t</sub> from the cold-box energy balance with a 3 K warm-end difference.<br>
Optimum: golden-section minimum of the compressor (LP return) flow. Isothermal power: ṁ<sub>HP</sub>·(R/M)·T·ln(P<sub>H</sub>/P<sub>L</sub>).</p>
<p class="ref">Reference reproduction for testing design alternatives. Not a QPS design target and not evidence of contract compliance.
Generated by <code>tools/claude_cycle_model.py</code> from <code>docs/gistau-ch3/data/claude_cycle_reproduction.json</code>.</p>
</main><script>{JS}</script></body></html>
"""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="recompute with CoolProp and write the record and page")
    ap.add_argument("--check", action="store_true", help="fail unless the page is current with the committed record")
    args = ap.parse_args(argv)
    if args.write:
        rec = build_record(CoolPropHelium())
        RECORD.parent.mkdir(parents=True, exist_ok=True)
        RECORD.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
        PAGE.write_text(render(rec), encoding="utf-8")
        print(f"wrote {RECORD.relative_to(REPO_ROOT)} and {PAGE.relative_to(REPO_ROOT)}; stats {rec['stats']}")
    if (args.check or not args.write) and PAGE.read_text(encoding="utf-8") != render():
        print("stale: run python tools/claude_cycle_model.py --write", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
