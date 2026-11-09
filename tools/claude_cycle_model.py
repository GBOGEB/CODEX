"""Gistau Ch3 Claude cycles: thermodynamic balances, optimisation, sweeps and statistics.

Reproduces, from fluid properties, G. Gistau Baguer, *Cryogenic Helium Refrigeration for Middle and
Large Powers* (Springer, 2020): the one-turbine cycle (Sect. 3.5.3.1, Figs. 3.46-3.48), two turbines in
parallel (Fig. 3.51) and in series (Fig. 3.53), and the LN2-precooled refrigerator and liquefier
(Figs. 3.60-3.61, Table 3.8). Reports how far each reproduction is from the printed values.

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

    def n2_vaporise_and_warm(self, p_bar, t_out_k):
        """J/g to vaporise saturated liquid nitrogen at p_bar and warm the vapour to t_out_k."""
        return (self._p("H", "T", t_out_k, "P", p_bar * 1e5, "Nitrogen")
                - self._p("H", "P", p_bar * 1e5, "Q", 0, "Nitrogen")) / 1e3


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


# ---------------------------------------------------------------- two turbines (Sect. 3.5.3.2-3.5.3.3, 3.6.4)

@dataclass(frozen=True)
class TwoTurbine:
    """Parallel two-turbine Claude cycle (Fig. 3.49 topology). Warm turbine T1 takes HP after HX1 and discharges into
    LP between HX2 and HX3; cold turbine T2 takes HP after HX3 and discharges into LP between HX4 and HX5.
    ``t_warm_k`` is the cold-box warm end: 300 K, or 80 K behind an LN2 pre-cooler (HX0)."""

    refrigeration_w: float = 50.0
    liquefaction_g_s: float = 0.5
    p_high_bar: float = 14.0
    p_low_bar: float = 1.2
    t_warm_k: float = 300.0
    warm_end_dt_k: float = 3.0
    hx3_warm_end_dt_k: float = 0.5
    jt_hx_warm_end_dt_k: float = 0.2
    turbine_isentropic_efficiency: float = 0.75
    t_compressor_k: float = 300.0


def _turbine_inlet(props: Props, t_out_k: float, p_in: float, p_out: float, eta: float, t_max: float) -> float:
    h_out = props.h(t_out_k, p_out)

    def resid(t_in):
        h_in = props.h(t_in, p_in)
        return h_in - eta * (h_in - props.h_ps(props.s(t_in, p_in), p_out)) - h_out

    return _bisect(resid, t_out_k, t_max)


def _w_iso_kw(m_g_s: float, t_k: float, ph: float, pl: float) -> float:
    return m_g_s * 1e-3 * (R_UNIVERSAL / M_HELIUM) * 1e3 * t_k * math.log(ph / pl) / 1e3


def solve_parallel(props: Props, td1_k: float, td2_k: float, c: TwoTurbine) -> dict[str, float]:
    """Flows and turbine powers for warm/cold turbine discharge temperatures td1_k / td2_k.

    JT envelope (HX5 + bath):          m_jt h_HP(Td2+dT5) + Q = L h_l + (m_jt - L) h_LP(Td2)
    Cold envelope (HX3..HX5 + T2):     (m_jt+m2) h_HP(Td1+dT3) + Q = L h_l + (m_jt+m2-L) h_LP(Td1) + m2 dh2
    Cold box (HX1..HX5 + T1 + T2):     m_hp h_HP(Tw) + Q = L h_l + (m_hp-L) h_LP(Tw-dTw) + m1 dh1 + m2 dh2
    """
    q, liq, ph, pl, eta = c.refrigeration_w, c.liquefaction_g_s, c.p_high_bar, c.p_low_bar, c.turbine_isentropic_efficiency
    h_l = props.h_liq_sat(pl)
    h_lp2, h_hp4 = props.h(td2_k, pl), props.h(td2_k + c.jt_hx_warm_end_dt_k, ph)
    m_jt = (q + liq * (h_lp2 - h_l)) / (h_lp2 - h_hp4)
    ti2 = _turbine_inlet(props, td2_k, ph, pl, eta, c.t_warm_k)
    dh2 = props.h(ti2, ph) - h_lp2
    h_hp3, h_lp1 = props.h(td1_k + c.hx3_warm_end_dt_k, ph), props.h(td1_k, pl)
    m2 = ((m_jt - liq) * h_lp1 + liq * h_l - m_jt * h_hp3 - q) / (h_hp3 - h_lp1 - dh2)
    ti1 = _turbine_inlet(props, td1_k, ph, pl, eta, c.t_warm_k)
    dh1 = props.h(ti1, ph) - h_lp1
    h_hp1, h_lpw = props.h(c.t_warm_k, ph), props.h(c.t_warm_k - c.warm_end_dt_k, pl)
    m1 = ((m_jt + m2 - liq) * h_lpw + liq * h_l + m2 * dh2 - (m_jt + m2) * h_hp1 - q) / (h_hp1 - h_lpw - dh1)
    m_hp = m_jt + m1 + m2
    return {
        "warm_turbine_discharge_t_k": td1_k, "cold_turbine_discharge_t_k": td2_k,
        "warm_turbine_inlet_t_k": ti1, "cold_turbine_inlet_t_k": ti2,
        "jt_mass_flow_g_s": m_jt, "warm_turbine_mass_flow_g_s": m1, "cold_turbine_mass_flow_g_s": m2,
        "cycle_hp_mass_flow_g_s": m_hp, "cycle_lp_return_mass_flow_g_s": m_hp - liq,
        "warm_turbine_power_w": -m1 * dh1, "cold_turbine_power_w": -m2 * dh2,
        "total_turbine_power_w": -(m1 * dh1 + m2 * dh2),
        "isothermal_compressor_power_kw": _w_iso_kw(m_hp, c.t_compressor_k, ph, pl),
    }


def optimise_parallel(props: Props, c: TwoTurbine, x0: tuple[float, float]) -> dict[str, float]:
    """Pattern search for the (Td1, Td2) minimising compressor flow, keeping all flows positive and
    every HX section with positive length (Ti1 > Td1+dT3 > Ti2 > Td2+dT5)."""

    def f(x):
        try:
            r = solve_parallel(props, x[0], x[1], c)
        except ValueError:
            return math.inf
        ok = (min(r["jt_mass_flow_g_s"], r["warm_turbine_mass_flow_g_s"], r["cold_turbine_mass_flow_g_s"]) > 0
              and r["warm_turbine_inlet_t_k"] > x[0] + c.hx3_warm_end_dt_k > r["cold_turbine_inlet_t_k"]
              > x[1] + c.jt_hx_warm_end_dt_k)
        return r["cycle_lp_return_mass_flow_g_s"] if ok else math.inf

    x, fx, step = list(x0), f(x0), 2.0
    while step > 1e-4:
        moved = False
        for i in (0, 1):
            for s in (step, -step):
                y = x[:]
                y[i] += s
                fy = f(y)
                if fy < fx:
                    x, fx, moved = y, fy, True
        if not moved:
            step /= 2
    return solve_parallel(props, x[0], x[1], c)


def ln2_precooler(props: Props, r: dict[str, float], c: TwoTurbine, lp_in_t_k: float, n2_latent_plus_sensible_j_g: float,
                  t_room_k: float = 300.0, warm_dt_k: float = 3.0) -> dict[str, float]:
    """HX0 duty that the nitrogen must absorb: HP cooled from room to c.t_warm_k, LP rewarmed from lp_in_t_k."""
    duty = (r["cycle_hp_mass_flow_g_s"] * (props.h(t_room_k, c.p_high_bar) - props.h(c.t_warm_k, c.p_high_bar))
            - r["cycle_lp_return_mass_flow_g_s"] * (props.h(t_room_k - warm_dt_k, c.p_low_bar) - props.h(lp_in_t_k, c.p_low_bar)))
    return {"ln2_duty_w": duty, "nitrogen_flow_g_s": duty / n2_latent_plus_sensible_j_g}


@dataclass(frozen=True)
class Series:
    """Series two-turbine Claude cycle (Fig. 3.52): T1 expands HP -> p_mid after HX1, the p_mid stream is cooled in
    HX3 with the JT stream, then T2 expands p_mid -> LP into the LP stream between HX4 and HX5."""

    refrigeration_w: float = 50.0
    liquefaction_g_s: float = 0.5
    p_high_bar: float = 16.0
    p_mid_bar: float = 7.0
    p_low_bar: float = 1.2
    t_warm_k: float = 300.0
    warm_end_dt_k: float = 2.97
    hx3_warm_end_dt_k: float = 0.68
    jt_hx_warm_end_dt_k: float = 0.2
    turbine_isentropic_efficiency: float = 0.75


def solve_series(props: Props, ti1_k: float, ti2_k: float, c: Series) -> dict[str, float]:
    """Series cycle from the turbine inlet temperatures (the book's input cells). The JT and cold envelopes fix
    m_jt and the Brayton flow; the warm section (HX1+HX2+T1) is then over-determined, and its energy residual
    is returned (the book prints it as the Brayton 1 balance)."""
    q, liq, ph, pm, pl, eta = (c.refrigeration_w, c.liquefaction_g_s, c.p_high_bar, c.p_mid_bar, c.p_low_bar,
                               c.turbine_isentropic_efficiency)
    h_l = props.h_liq_sat(pl)

    def expand(t_in, p_in, p_out):
        h_in = props.h(t_in, p_in)
        return h_in - eta * (h_in - props.h_ps(props.s(t_in, p_in), p_out))

    h1o, h2o = expand(ti1_k, ph, pm), expand(ti2_k, pm, pl)
    td1 = _bisect(lambda t: props.h(t, pm) - h1o, 2.5, ti1_k)
    td2 = _bisect(lambda t: props.h(t, pl) - h2o, 2.5, ti2_k)
    h_lp2 = props.h(td2, pl)
    m_jt = (q + liq * (h_lp2 - h_l)) / (h_lp2 - props.h(td2 + c.jt_hx_warm_end_dt_k, ph))
    h_lp3 = props.h(td1 - c.hx3_warm_end_dt_k, pl)
    dh2 = props.h(ti2_k, pm) - h2o
    m_b = ((m_jt - liq) * h_lp3 + liq * h_l - m_jt * props.h(td1, ph) - q) / (props.h(td1, pm) - h_lp3 - dh2)
    m_hp, dh1 = m_jt + m_b, props.h(ti1_k, ph) - h1o
    resid = ((m_hp * props.h(c.t_warm_k, ph) + (m_hp - liq) * h_lp3)
             - (m_jt * props.h(td1, ph) + m_b * props.h(td1, pm) + (m_hp - liq) * props.h(c.t_warm_k - c.warm_end_dt_k, pl)
                + m_b * dh1))
    return {
        "warm_turbine_inlet_t_k": ti1_k, "cold_turbine_inlet_t_k": ti2_k,
        "warm_turbine_discharge_t_k": td1, "cold_turbine_discharge_t_k": td2,
        "jt_mass_flow_g_s": m_jt, "brayton_mass_flow_g_s": m_b,
        "cycle_hp_mass_flow_g_s": m_hp, "cycle_lp_return_mass_flow_g_s": m_hp - liq,
        "warm_turbine_power_w": -m_b * dh1, "cold_turbine_power_w": -m_b * dh2,
        "warm_section_residual_w": resid,
    }


def close_series(props: Props, ti2_k: float, c: Series, lo: float = 70.0, hi: float = 140.0) -> dict[str, float]:
    """Warm turbine inlet temperature at which the series cycle balances (residual 0)."""
    t = _bisect(lambda x: solve_series(props, x, ti2_k, c)["warm_section_residual_w"], lo, hi, tol=1e-6)
    return solve_series(props, t, ti2_k, c)


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
        "two_turbine": build_two_turbine(props, props.n2_vaporise_and_warm(1.2, 297.0)),
    }


def _flat(d: dict[str, Any], pre: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(_flat(v, f"{pre}{k}."))
        else:
            out[f"{pre}{k}"] = v
    return out


_MAP = {
    "cycle_flow_g_s": "cycle_lp_return_mass_flow_g_s",
    "turbine_power_w": "total_turbine_power_w",
    "nitrogen_power_w": "ln2_duty_w",
    "warm_turbine.mass_flow_g_s": "warm_turbine_mass_flow_g_s",
    "cold_turbine.mass_flow_g_s": "cold_turbine_mass_flow_g_s",
}


def _model_key(book_key: str, series: bool) -> str:
    if series and book_key == "warm_turbine.mass_flow_g_s":
        return "brayton_mass_flow_g_s"
    if book_key in _MAP:
        return _MAP[book_key]
    return book_key.replace("warm_turbine.", "warm_turbine_").replace("cold_turbine.", "cold_turbine_")


def _compare(case: str, book: dict[str, Any], got: dict[str, float], skip: set[str], series: bool = False) -> list[dict[str, Any]]:
    rows = []
    for bk, exp in _flat(book).items():
        mk = _model_key(bk, series)
        if bk in skip or mk not in got or not isinstance(exp, (int, float)) or not exp:
            continue
        val = got[mk]
        if "power" in bk:  # the book prints turbine powers with either sign; compare magnitudes
            exp, val = abs(float(exp)), abs(val)
        decimals = len(repr(float(exp)).split(".")[1].rstrip("0")) if "." in repr(float(exp)) else 0
        half_ulp = 0.5 * 10 ** -decimals
        rows.append({"case": case, "quantity": bk, "book": float(exp), "model": round(val, 4),
                     "abs_dev": round(val - exp, 4), "rel_dev": round((val - exp) / exp, 6),
                     "within_print_precision": abs(val - exp) <= half_ulp + 1e-12})
    return rows


def _stats2(rows: list[dict[str, Any]], tol_rel: float) -> dict[str, Any]:
    st = _stats(rows, tol_rel)
    st["within_tolerance_or_print_precision"] = sum(
        abs(r["rel_dev"]) <= tol_rel or r["within_print_precision"] for r in rows)
    return st


def build_two_turbine(props: Props, n2_dh_j_g: float) -> dict[str, Any]:
    """Reproduce Figs. 3.51, 3.53, 3.60, 3.61 and Table 3.8 from the transcribed inputs, and optimise each."""
    bench = {b["benchmark_id"]: b for b in json.loads(BENCH.read_text(encoding="utf-8"))["benchmarks"]}
    par_b = bench["G3-3.5.3.2-PARALLEL-OPTIMISED-STATES"]
    ser_b = bench["G3-3.5.3.3-SERIES-OPTIMISED-STATES"]
    ref_b = bench["G3-3.6.4.1-LN2-REFRIGERATOR"]["expected_outputs"]
    liq_b = bench["G3-3.6.4.2-LN2-LIQUEFIER"]["expected_outputs"]
    tab = bench["G3-TABLE-3.8-LN2-COMPARISON"]["expected_outputs"]
    hx0_lp_in = 78.78  # Figs. 3.60/3.61: LP leaves HX1 and enters HX0 at 78.78 K (1.22 K below the 80 K HP)
    skip = {"warm_turbine.discharge_t_k", "cold_turbine.discharge_t_k"}
    rnd = lambda r: {k: round(v, 4) for k, v in r.items()}

    po, pi = par_b["expected_outputs"], par_b["inputs"]
    c_par = TwoTurbine(hx3_warm_end_dt_k=pi["hx3_warm_end_dt_k"], jt_hx_warm_end_dt_k=pi["jt_hx_warm_end_dt_k"])
    ln2_ref = TwoTurbine(refrigeration_w=100.0, liquefaction_g_s=0.0, t_warm_k=80.0, warm_end_dt_k=1.0)
    ref_ref = TwoTurbine(refrigeration_w=100.0, liquefaction_g_s=0.0)
    liq_ref = TwoTurbine(refrigeration_w=0.0, liquefaction_g_s=1.0)
    ln2_liq = TwoTurbine(refrigeration_w=0.0, liquefaction_g_s=1.0, t_warm_k=80.0, warm_end_dt_k=1.0)

    cases = []

    def add(cid, label, figure, c, book, td, x0, ln2=False):
        r = None
        if book:
            r = solve_parallel(props, td[0], td[1], c)
            if ln2:
                r.update(ln2_precooler(props, r, c, hx0_lp_in, n2_dh_j_g))
        o = optimise_parallel(props, c, x0)
        if ln2:
            o.update(ln2_precooler(props, o, c, hx0_lp_in, n2_dh_j_g))
        rows = _compare(cid, book, r, skip) if book else []
        cases.append({"id": cid, "label": label, "figure": figure, "design": asdict(c),
                      "at_book_point": rnd(r) if r else None, "optimum": rnd(o), "deviations": rows,
                      "stats": _stats2(rows, 0.01) if rows else None})

    add("parallel", "Two parallel turbines, 50 W + 0.5 g/s", "Fig. 3.51", c_par, po,
        (po["warm_turbine"]["discharge_t_k"], po["cold_turbine"]["discharge_t_k"]), (50.0, 10.0))
    rl = ref_b["ln2"]
    add("ln2_refrigerator", "LN2-precooled refrigerator, 100 W", "Fig. 3.60 (right)", ln2_ref, rl,
        (rl["warm_turbine"]["discharge_t_k"], rl["cold_turbine"]["discharge_t_k"]), (25.0, 11.0), ln2=True)
    add("reference_refrigerator", "Refrigerator without LN2, 100 W (no valid sheet)", "Table 3.8", ref_ref, None,
        None, (50.0, 10.0))
    for key, c, lab, fig, x0, ln2 in (("reference", liq_ref, "Liquefier without LN2, 1 g/s", "Fig. 3.61 (left)", (50.0, 10.0), False),
                                      ("ln2", ln2_liq, "LN2-precooled liquefier, 1 g/s", "Fig. 3.61 (right)", (25.0, 9.0), True)):
        b = liq_b[key]
        add(f"liquefier_{key}", lab, fig, c, b, (b["warm_turbine"]["discharge_t_k"], b["cold_turbine"]["discharge_t_k"]), x0, ln2)

    so, si = ser_b["expected_outputs"], ser_b["inputs"]
    c_ser = Series(p_high_bar=si["p_high_bar"], p_mid_bar=si["p_intermediate_bar"], warm_end_dt_k=si["warm_end_dt_k"],
                   hx3_warm_end_dt_k=si["hx3_warm_end_dt_k"], jt_hx_warm_end_dt_k=si["jt_hx_warm_end_dt_k"])
    s_book = solve_series(props, so["warm_turbine"]["inlet_t_k"], so["cold_turbine"]["inlet_t_k"], c_ser)
    s_closed = close_series(props, so["cold_turbine"]["inlet_t_k"], c_ser)
    s_rows = _compare("series", so, s_book, {"warm_turbine.inlet_t_k", "cold_turbine.inlet_t_k", "warm_turbine.discharge_p_bar"},
                      series=True)
    # JT flow implied by the book's own JT-stage warm-end term (-(m_jt - L) * (h_LP - h_HP) at the HX5 warm end)
    dh_warm = props.h(so["cold_turbine"]["discharge_t_k"], c_ser.p_low_bar) - props.h(so["hp_states"]["after_hx4_t_k"], c_ser.p_high_bar)
    implied_jt = abs(so["jt_stage"]["warm_end_w"]) / dh_warm + c_ser.liquefaction_g_s
    series = {
        "design": asdict(c_ser), "at_book_inputs": rnd(s_book), "closed": rnd(s_closed),
        "deviations": s_rows, "stats": _stats2(s_rows, 0.01),
        "book_brayton1_balance_w": so["balances"]["brayton1_w"],
        "jt_flow_implied_by_book_jt_stage_g_s": round(implied_jt, 3), "jt_flow_printed_g_s": so["jt_mass_flow_g_s"],
        "warm_end_dh_j_g": round(dh_warm, 3),
    }

    by = {c["id"]: c for c in cases}
    table = []
    for row_key, cid_no, cid_ln2 in (("claude_2t_refrigerator_100w", "reference_refrigerator", "ln2_refrigerator"),
                                      ("claude_2t_liquefier_1gs", "liquefier_reference", "liquefier_ln2")):
        t = tab[row_key]
        table.append({"row": row_key, "book_flow_no_ln2_g_s": t["flow_no_ln2_g_s"], "book_flow_ln2_g_s": t["flow_ln2_g_s"],
                      "model_opt_flow_no_ln2_g_s": round(by[cid_no]["optimum"]["cycle_lp_return_mass_flow_g_s"], 3),
                      "model_opt_flow_ln2_g_s": round(by[cid_ln2]["optimum"]["cycle_lp_return_mass_flow_g_s"], 3),
                      "book_turbine_no_ln2_w": t["turbine_no_ln2_w"], "book_turbine_ln2_w": t["turbine_ln2_w"],
                      "model_opt_turbine_no_ln2_w": round(abs(by[cid_no]["optimum"]["total_turbine_power_w"]), 1),
                      "model_opt_turbine_ln2_w": round(abs(by[cid_ln2]["optimum"]["total_turbine_power_w"]), 1)})
    rows = [r for c in cases for r in c["deviations"]]
    return {"cases": cases, "series": series, "table_3_8": table, "stats_parallel_and_ln2": _stats2(rows, 0.01),
            "hx0_lp_inlet_t_k": hx0_lp_in, "nitrogen_dh_j_g": round(n2_dh_j_g, 3)}


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


def _dot_chart(rows: list[tuple[str, float | None, float | None, float]]) -> str:
    """Cycle flow per case: book (ring), model at the book's inputs (dot), model optimum (diamond)."""
    w, row_h, ml, mr, mt, mb = 720, 34, 200, 24, 10, 40
    h = mt + mb + row_h * len(rows)
    vals_all = [v for r in rows for v in r[1:] if v is not None]
    xmin, xmax = 2.0 * math.floor(min(vals_all) / 2.0 - 0.5), 2.0 * math.ceil(max(vals_all) / 2.0 + 0.5)
    sx = lambda x: ml + (x - xmin) / (xmax - xmin) * (w - ml - mr)
    p = [f"<div class='scroll'><svg viewBox='0 0 {w} {h}' role='img' aria-labelledby='dot-t dot-d' class='chart wide'>",
         "<title id='dot-t'>Cycle compressor flow: book, model at the book's inputs, model optimum</title>",
         "<desc id='dot-d'>One row per cycle; the table below lists every value.</desc>"]
    for x in range(int(xmin), int(xmax) + 1, 2):
        p.append(f"<line class='grid' x1='{sx(x):.1f}' x2='{sx(x):.1f}' y1='{mt}' y2='{h - mb}'/>"
                 f"<text class='tick' x='{sx(x):.1f}' y='{h - mb + 16}' text-anchor='middle'>{x}</text>")
    p.append(f"<text class='axis' x='{(ml + w - mr) / 2}' y='{h - 6}' text-anchor='middle'>Cycle compressor flow (g/s); rows are Gistau figures</text>")
    for i, (label, book, model, opt) in enumerate(rows):
        y = mt + row_h * i + row_h / 2
        p.append(f"<text class='tick' x='{ml - 10}' y='{y + 4:.1f}' text-anchor='end'>{_e(label)}</text>")
        vals = [v for v in (book, model, opt) if v is not None]
        p.append(f"<line class='grid' x1='{sx(min(vals)):.1f}' x2='{sx(max(vals)):.1f}' y1='{y}' y2='{y}'/>")
        x = sx(opt)
        p.append(f"<path class='dia s2f' d='M{x:.1f} {y - 6:.1f}L{x + 6:.1f} {y:.1f}L{x:.1f} {y + 6:.1f}L{x - 6:.1f} {y:.1f}Z' "
                 "/>")
        if model is not None:
            p.append(f"<circle class='dot s1f' cx='{sx(model):.1f}' cy='{y}' r='4'/>")
        if book is not None:
            p.append(f"<circle class='ring' cx='{sx(book):.1f}' cy='{y}' r='7'/>")
        tip = " · ".join(x for x in (
            f"book {book:.2f}" if book is not None else "", f"model at book inputs {model:.2f}" if model is not None else "",
            f"model optimum {opt:.2f} g/s") if x)
        p.append(f"<rect class='rowhit' x='{ml}' y='{y - row_h / 2:.1f}' width='{w - ml - mr}' height='{row_h}' "
                 f"data-tip='{_e(label)}: {_e(tip)}'/>")
    p.append("</svg></div>")
    return "".join(p)


def _two_section(tt: dict[str, Any]) -> str:
    by = {c["id"]: c for c in tt["cases"]}
    st, se = tt["stats_parallel_and_ln2"], tt["series"]
    flow = "cycle_lp_return_mass_flow_g_s"
    book_flow = {"parallel": 12.60, "ln2_refrigerator": 9.94, "reference_refrigerator": 10.81,
                 "liquefier_reference": 15.64, "liquefier_ln2": 7.76}
    short = {"parallel": "3.51 parallel, 50 W + 0.5 g/s", "reference_refrigerator": "Refrigerator, no LN2 (T. 3.8)",
             "ln2_refrigerator": "3.60 refrigerator, LN2", "liquefier_reference": "3.61 liquefier, no LN2",
             "liquefier_ln2": "3.61 liquefier, LN2"}
    rows = [(short[c], book_flow[c],
             by[c]["at_book_point"][flow] if by[c]["at_book_point"] else None, by[c]["optimum"][flow])
            for c in ("parallel", "reference_refrigerator", "ln2_refrigerator", "liquefier_reference", "liquefier_ln2")]
    rows.insert(1, ("3.53 series, 16/7 bar", 13.28, se["at_book_inputs"][flow], se["closed"][flow]))
    ref, ln2r = by["reference_refrigerator"]["optimum"], by["ln2_refrigerator"]
    tiles = "".join(f"<div class='tile'><b>{v}</b><span>{_e(k)}</span></div>" for k, v in (
        (f"Parallel and LN2 sheets: values matched ({st['n']})",
         f"{st['within_tolerance_or_print_precision']} / {st['n']}"),
        ("RMS deviation, parallel and LN2 sheets", f"{st['rms_rel_dev'] * 100:.2f} %"),
        ("Series JT flow: printed vs implied by its own JT stage",
         f"{se['jt_flow_printed_g_s']:.2f} vs {se['jt_flow_implied_by_book_jt_stage_g_s']:.2f} g/s"),
        ("LN2 refrigerator: book sheet vs model optimum",
         f"{ln2r['at_book_point'][flow]:.2f} vs {ln2r['optimum'][flow]:.2f} g/s"),
    ))
    dev_rows = by["parallel"]["deviations"] + by["ln2_refrigerator"]["deviations"] + \
        by["liquefier_reference"]["deviations"] + by["liquefier_ln2"]["deviations"] + se["deviations"]

    def cls(r):
        return "ok" if abs(r["rel_dev"]) <= st["tolerance_rel"] or r["within_print_precision"] else "hi"

    dev = "".join(
        f"<tr><td>{_e(r['case'])}</td><td>{_e(r['quantity'])}</td><td>{r['book']:g}</td><td>{r['model']:g}</td>"
        f"<td class='{cls(r)}'>{r['rel_dev'] * 100:+.2f} %</td><td>{'yes' if r['within_print_precision'] else 'no'}</td></tr>"
        for r in dev_rows)
    t38 = "".join(
        f"<tr><td>{_e(r['row'])}</td><td>{r['book_flow_no_ln2_g_s']:g}</td><td>{r['model_opt_flow_no_ln2_g_s']:.2f}</td>"
        f"<td>{r['book_flow_ln2_g_s']:g}</td><td>{r['model_opt_flow_ln2_g_s']:.2f}</td>"
        f"<td>{r['book_turbine_no_ln2_w']:g}</td><td>{r['model_opt_turbine_no_ln2_w']:.0f}</td>"
        f"<td>{r['book_turbine_ln2_w']:g}</td><td>{r['model_opt_turbine_ln2_w']:.0f}</td></tr>" for r in tt["table_3_8"])
    par_gap = 1 - by["parallel"]["optimum"][flow] / by["parallel"]["at_book_point"][flow]
    return f"""
<h2>Two turbines and LN2 pre-cooling (Figs. 3.51, 3.53, 3.60, 3.61, Table 3.8)</h2>
<div class="tiles">{tiles}</div>
<div class="legend"><span><svg width="14" height="14"><circle class="ring" cx="7" cy="7" r="5"/></svg> Book</span>
<span><svg width="14" height="14"><circle class="dot s1f" cx="7" cy="7" r="4"/></svg> Model at the book's inputs</span>
<span><svg width="14" height="14"><path class="dia s2f" d="M7 1L13 7L7 13L1 7Z"/></svg> Model optimum (closed balance for the series cycle)</span></div>
{_dot_chart(rows)}
<p class="ref">Where the model reproduces the book and the book's point is also the optimum (the two liquefiers, and Fig. 3.51 to
0.05 g/s), the three markers coincide. Hover any marker for its value; every value is in the tables below.</p>
<h3>What the reproduction shows</h3>
<ul class="findings">
<li><b>Liquefier sheets are true optima.</b> Starting the optimiser elsewhere, it lands on the book's turbine discharge
temperatures for both Fig. 3.61 cycles (to 0.01 K), and on the Table 3.8 flows (15.64 and 7.76 g/s).</li>
<li><b>Refrigerator sheets are not at this model's optimum.</b> With the same equations that reproduce the book's own points,
the parallel cycle reaches {by['parallel']['optimum'][flow]:.2f} g/s (book 12.60, {par_gap * 100:.1f} % lower), the LN2 refrigerator
{ln2r['optimum'][flow]:.2f} g/s (book 9.94) and the refrigerator without LN2 {ref[flow]:.2f} g/s (Table 3.8: 10.81). All flows stay
positive and every HX keeps its end-temperature differences. The book does not state the extra constraint its solver used,
so treat the book's refrigerator figures as conservative, not as optima.</li>
<li><b>The series sheet is unconverged.</b> Its printed Brayton 1 balance is {se['book_brayton1_balance_w']:+.2f} W (model at its inputs:
{se['at_book_inputs']['warm_section_residual_w']:+.1f} W), and its own JT-stage warm-end term implies
{se['jt_flow_implied_by_book_jt_stage_g_s']:.2f} g/s through the JT valve against {se['jt_flow_printed_g_s']:.2f} g/s printed. Closing the
balance (warm turbine inlet {se['closed']['warm_turbine_inlet_t_k']:.2f} K) gives {se['closed'][flow]:.2f} g/s, still above the parallel
cycle at a lower 14 bar: the book's conclusion that parallel is better holds.</li>
<li><b>LN2 duty.</b> HX0 with the LP entering at {tt['hx0_lp_inlet_t_k']} K, as printed, reproduces the nitrogen duty
(Fig. 3.60: {ln2r['at_book_point']['ln2_duty_w']:.1f} W; Fig. 3.61: {by['liquefier_ln2']['at_book_point']['ln2_duty_w']:.1f} W) with
{tt['nitrogen_dh_j_g']:.1f} J/g to vaporise nitrogen at 1.2 bar and warm it to 297 K.</li>
</ul>
<h3>Table 3.8 against the model optimum</h3>
<div class="scroll"><table><thead><tr><th>Row</th><th>Flow, no LN2 (book)</th><th>(model)</th><th>Flow, LN2 (book)</th><th>(model)</th>
<th>Turbines, no LN2 W (book)</th><th>(model)</th><th>Turbines, LN2 W (book)</th><th>(model)</th></tr></thead><tbody>{t38}</tbody></table></div>
<h3>Deviation from the printed values</h3>
<p class="ref">Parallel and LN2 sheets: {st['within_tolerance_or_print_precision']} of {st['n']} values within
{st['tolerance_rel'] * 100:.0f} % or the printed rounding (RMS {st['rms_rel_dev'] * 100:.2f} %). Turbine discharge temperatures are inputs and
are not compared. The series rows compare the unconverged sheet; their deviations follow from the finding above.</p>
<div class="scroll"><table><thead><tr><th>Case</th><th>Quantity</th><th>Book</th><th>Model</th><th>Δ rel</th><th>Within print rounding</th></tr></thead>
<tbody>{dev}</tbody></table></div>
"""


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
.mark{fill:var(--bg);stroke:var(--ink);stroke-width:2}.ring{fill:none;stroke:var(--ink);stroke-width:2}.rowhit{fill:transparent}.rowhit:hover{fill:var(--grid);fill-opacity:.35}
.dot,.dia{stroke:var(--card);stroke-width:2}.s1f{fill:var(--s1)}.s2f{fill:var(--s2)}h3{font-size:1rem;margin:1.4rem 0 .4rem}
.chart.wide{min-width:640px}.findings{padding-left:1.2rem}.findings li{margin:.4rem 0}.hit{fill:transparent}.xhair{stroke:var(--muted);stroke-width:1;opacity:0}
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
document.querySelectorAll('[data-tip]:not(.hit)').forEach(m=>{m.addEventListener('mousemove',e=>{tip.textContent=m.dataset.tip;
tip.style.opacity=1;tip.style.left=(e.clientX+12)+'px';tip.style.top=(e.clientY+12)+'px'});
m.addEventListener('mouseleave',()=>{tip.style.opacity=0})});
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
{_two_section(rec['two_turbine']) if 'two_turbine' in rec else ''}
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
