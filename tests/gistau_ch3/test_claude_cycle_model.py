"""Claude-cycle model: balance logic on an analytic fluid, and the committed CoolProp record and page stay faithful."""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _tool():
    spec = importlib.util.spec_from_file_location("claude_cycle_model", REPO_ROOT / "tools/claude_cycle_model.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class IdealHelium:
    """Perfect gas with a non-ideal pressure term so h depends on p (JT effect sign as for helium below inversion)."""

    cp, r = 5.193, 2.0773

    def h(self, t, p):
        return self.cp * t + 0.6 * p * (1 - 25.0 / t)

    def s(self, t, p):
        return self.cp * math.log(t) - self.r * math.log(p)

    def h_ps(self, s, p):
        t = math.exp((s + self.r * math.log(p)) / self.cp)
        return self.h(t, p)

    def h_liq_sat(self, p):
        return 10.0


def test_energy_envelope_closes_and_flows_add_up():
    tool = _tool()
    r = tool.solve(IdealHelium(), 20.0)
    assert abs(r["energy_closure_w"]) < 1e-6
    assert math.isclose(r["cycle_hp_mass_flow_g_s"], r["jt_mass_flow_g_s"] + r["brayton_mass_flow_g_s"])
    assert math.isclose(r["cycle_hp_mass_flow_g_s"] - r["cycle_lp_return_mass_flow_g_s"], 0.5)
    assert r["turbine_inlet_t_k"] > r["turbine_discharge_t_k"] and r["turbine_power_w"] < 0


def test_optimum_is_a_minimum_of_the_sweep():
    tool = _tool()
    p = IdealHelium()
    opt = tool.optimise(p)
    m = opt["cycle_lp_return_mass_flow_g_s"]
    for dt in (-1.0, -0.2, 0.2, 1.0):
        assert tool.solve(p, opt["turbine_discharge_t_k"] + dt)["cycle_lp_return_mass_flow_g_s"] >= m - 1e-9


def test_committed_record_reproduces_the_book_within_tolerance():
    rec = json.loads((REPO_ROOT / "docs/gistau-ch3/data/claude_cycle_reproduction.json").read_text(encoding="utf-8"))
    st = rec["stats"]
    assert st["n"] == len(rec["deviations"]) >= 18
    assert st["within_tolerance"] == st["n"] and st["max_abs_rel_dev"] <= st["tolerance_rel"]
    assert abs(rec["initial"]["energy_closure_w"]) < 1e-3 and abs(rec["optimised"]["energy_closure_w"]) < 1e-3
    assert rec["authority"] == "REFERENCE_REPRODUCTION_NOT_QPS_DESIGN"
    totals = [r["total"] for r in rec["sweep"]]
    assert min(totals) >= rec["optimised"]["cycle_lp_return_mass_flow_g_s"] - 1e-3


def test_committed_page_is_current():
    tool = _tool()
    assert (REPO_ROOT / "docs/gistau-ch3/claude_cycle_model.html").read_text(encoding="utf-8") == tool.render(), \
        "regenerate: python tools/claude_cycle_model.py --write"


def test_initial_case_uses_the_benchmark_input():
    bench = json.loads((REPO_ROOT / "docs/gistau-ch3/data/claude_cycle_benchmarks.json").read_text(encoding="utf-8"))
    rec = json.loads((REPO_ROOT / "docs/gistau-ch3/data/claude_cycle_reproduction.json").read_text(encoding="utf-8"))
    init = next(b for b in bench["benchmarks"] if b["benchmark_id"] == "G3-3.5.3.1-ONE-TURBINE-INITIAL")
    assert rec["initial"]["turbine_discharge_t_k"] == init["inputs"]["turbine_discharge_t_k"]


def test_parallel_two_turbine_cold_box_closes():
    tool = _tool()
    p, c = IdealHelium(), tool.TwoTurbine()
    r = tool.solve_parallel(p, 50.0, 10.0, c)
    m_jt, m1, m2 = r["jt_mass_flow_g_s"], r["warm_turbine_mass_flow_g_s"], r["cold_turbine_mass_flow_g_s"]
    dh1 = p.h(r["warm_turbine_inlet_t_k"], c.p_high_bar) - p.h(50.0, c.p_low_bar)
    dh2 = p.h(r["cold_turbine_inlet_t_k"], c.p_high_bar) - p.h(10.0, c.p_low_bar)
    m_hp, liq = m_jt + m1 + m2, c.liquefaction_g_s
    energy_in = m_hp * p.h(c.t_warm_k, c.p_high_bar) + c.refrigeration_w
    energy_out = (m_hp - liq) * p.h(c.t_warm_k - c.warm_end_dt_k, c.p_low_bar) + liq * p.h_liq_sat(c.p_low_bar) \
        + m1 * dh1 + m2 * dh2
    assert abs(energy_in - energy_out) < 1e-6
    assert math.isclose(r["cycle_lp_return_mass_flow_g_s"], m_hp - liq)


def test_series_closure_drives_the_warm_residual_to_zero():
    tool = _tool()
    p, c = IdealHelium(), tool.Series()
    lo = tool.solve_series(p, 70.0, 20.0, c)["warm_section_residual_w"]
    hi = tool.solve_series(p, 140.0, 20.0, c)["warm_section_residual_w"]
    assert lo * hi < 0
    assert abs(tool.close_series(p, 20.0, c)["warm_section_residual_w"]) < 1e-3


def test_committed_two_turbine_record_supports_the_page_findings():
    rec = json.loads((REPO_ROOT / "docs/gistau-ch3/data/claude_cycle_reproduction.json").read_text(encoding="utf-8"))
    tt = rec["two_turbine"]
    st = tt["stats_parallel_and_ln2"]
    by = {c["id"]: c for c in tt["cases"]}
    rows = [r for c in tt["cases"] for r in c["deviations"]]
    misses = [r for r in rows if not (abs(r["rel_dev"]) <= st["tolerance_rel"] or r["within_print_precision"])]
    assert st["n"] == len(rows) >= 40 and st["within_tolerance_or_print_precision"] == st["n"] - len(misses)
    # The only misses are the LN2 refrigerator's nitrogen rows, from the book's 0.22 K HX0 boundary gap
    # (cold box returns LP at 79.00 K, HX0 starts at 78.78 K); with the book's boundary the duty matches.
    assert {(r["case"], r["quantity"]) for r in misses} <= {("ln2_refrigerator", "nitrogen_flow_g_s"),
                                                           ("ln2_refrigerator", "nitrogen_power_w")}
    for cid, book_w in (("ln2_refrigerator", 108.41), ("liquefier_ln2", 1228.94)):
        assert abs(by[cid]["at_book_point"]["ln2_duty_book_convention_w"] / book_w - 1) < 0.01
    bench = json.loads((REPO_ROOT / "docs/gistau-ch3/data/claude_cycle_benchmarks.json").read_text(encoding="utf-8"))
    liq = next(b for b in bench["benchmarks"] if b["benchmark_id"] == "G3-3.6.4.2-LN2-LIQUEFIER")["expected_outputs"]
    for cid, key in (("liquefier_reference", "reference"), ("liquefier_ln2", "ln2")):
        o = by[cid]["optimum"]
        assert abs(o["warm_turbine_discharge_t_k"] - liq[key]["warm_turbine"]["discharge_t_k"]) < 0.05
        assert abs(o["cold_turbine_discharge_t_k"] - liq[key]["cold_turbine"]["discharge_t_k"]) < 0.05
    for cid in ("parallel", "ln2_refrigerator"):
        assert by[cid]["optimum"]["cycle_lp_return_mass_flow_g_s"] < by[cid]["at_book_point"]["cycle_lp_return_mass_flow_g_s"]
    se = tt["series"]
    assert se["jt_flow_implied_by_book_jt_stage_g_s"] > 1.03 * se["jt_flow_printed_g_s"]
    assert abs(se["closed"]["warm_section_residual_w"]) < 1e-2
    assert se["closed"]["cycle_lp_return_mass_flow_g_s"] > by["parallel"]["optimum"]["cycle_lp_return_mass_flow_g_s"]
