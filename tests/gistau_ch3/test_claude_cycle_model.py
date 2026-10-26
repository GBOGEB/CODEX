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
