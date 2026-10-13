"""The browser toolbox mirror (docs/gistau-ch15/assets/gistau_basic.js) must equal the Python engine."""
from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import asdict
from pathlib import Path

import pytest

from gistau_ch15.calculations.compressor import calculate_compressor
from gistau_ch15.calculations.equivalent_power import calculate_equivalent_power
from gistau_ch15.calculations.expander import calculate_expander
from gistau_ch15.calculations.heat_exchanger import calculate_heat_exchanger
from gistau_ch15.calculations.jt_valve import calculate_jt_valve
from gistau_ch15.properties.fallback_helium import FallbackHeliumBackend

REPO_ROOT = Path(__file__).resolve().parents[2]
JS = REPO_ROOT / "docs" / "gistau-ch15" / "assets" / "gistau_basic.js"
B = FallbackHeliumBackend()

STATES = [(100.0, 300.0), (1000.0, 300.0), (101.325, 50.0), (120.0, 4.5), (1400.0, 25.0)]
COMPRESSOR = [
    {"p1_kpa": 100.0, "t1_k": 300.0, "p2_kpa": 1200.0, "mdot_kg_s": 0.2, "eta_isothermal": 0.6, "eta_isentropic": 0.75},
    {"p1_kpa": 50.0, "t1_k": 5.0, "p2_kpa": 170.0, "mdot_kg_s": 0.4, "eta_isentropic": 0.75},
    {"p1_kpa": 100.0, "t1_k": 300.0, "p2_kpa": 600.0, "mdot_kg_s": 0.1, "eta_isentropic": None, "fluid": "nitrogen"},
]
JT = [{"p1_kpa": 1400.0, "t1_k": 20.0, "p2_kpa": 100.0, "mdot_kg_s": 0.05, "heat_leak_w": 100.0}]
EXPANDER = [{"p1_kpa": 1400.0, "t1_k": 25.0, "p2_kpa": 120.0, "mdot_kg_s": 0.05, "eta_isentropic": 0.75}]
HX = [{"hot_inlet_k": 300.0, "cold_inlet_k": 80.0, "hot_capacity_rate_wk": 500.0, "cold_capacity_rate_wk": 350.0, "effectiveness": 0.82}]
EQ = [{"compressor_power_w": 1.2e6, "expander_recovery_w": 3.0e4, "refrigeration_load_w": 2.0e3, "cold_temperature_k": 4.5}]

NODE_SCRIPT = """
const g = require(process.argv[1]);
const c = JSON.parse(process.argv[2]);
const strip = (o) => { const x = Object.assign({}, o); delete x.states; delete x.ideal_outlet_temperature_k; return x; };
console.log(JSON.stringify({
  constants: {R: g.R, CP: g.CP, T_REF_K: g.T_REF_K, P_REF_KPA: g.P_REF_KPA, DOMAIN_T_MIN_K: g.DOMAIN_T_MIN_K, DOMAIN_RHO_MAX_KG_M3: g.DOMAIN_RHO_MAX_KG_M3},
  states: c.states.map(([p, t]) => g.statePT(p, t)),
  ps_roundtrip: c.states.map(([p, t]) => g.statePS(p, g.statePT(p, t).entropy_j_kgk).temperature_k),
  compressor: c.compressor.map((a) => strip(g.compressor(a))),
  jt: c.jt.map((a) => strip(g.jtValve(a))),
  expander: c.expander.map((a) => strip(g.expander(a))),
  hx: c.hx.map((a) => g.heatExchanger(a)),
  eq: c.eq.map((a) => g.equivalentPower(a)),
}));
"""


def _approx_equal(js: dict, py: dict) -> None:
    assert set(js) == set(py), (sorted(js), sorted(py))
    for key, value in py.items():
        if isinstance(value, float):
            assert js[key] == pytest.approx(value, rel=1e-12, abs=1e-12), key
        else:
            assert js[key] == value, key


@pytest.fixture(scope="module")
def js():
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed; the JS parity check needs it")
    cases = {"states": STATES, "compressor": COMPRESSOR, "jt": JT, "expander": EXPANDER, "hx": HX, "eq": EQ}
    out = subprocess.run(
        [node, "-e", NODE_SCRIPT, str(JS), json.dumps(cases)], capture_output=True, text=True, check=True, timeout=60
    )
    return json.loads(out.stdout)


def test_constants_match(js):
    c = js["constants"]
    assert (c["R"], c["CP"], c["T_REF_K"], c["P_REF_KPA"]) == (B.R, B.CP, B.T_REF_K, B.P_REF_KPA)
    assert (c["DOMAIN_T_MIN_K"], c["DOMAIN_RHO_MAX_KG_M3"]) == (B.DOMAIN_T_MIN_K, B.DOMAIN_RHO_MAX_KG_M3)


def test_state_points_match(js):
    for (p, t), j in zip(STATES, js["states"]):
        st = asdict(B.state_pt("helium", p, t))
        st.pop("quality")
        _approx_equal(j, st)
    for (p, t), t_back in zip(STATES, js["ps_roundtrip"]):
        assert t_back == pytest.approx(t, rel=1e-12)


def test_compressor_matches(js):
    for args, j in zip(COMPRESSOR, js["compressor"]):
        kwargs = {"fluid": "helium", **args}
        _approx_equal(j, asdict(calculate_compressor(backend=B, **kwargs)))


def test_jt_valve_matches(js):
    for args, j in zip(JT, js["jt"]):
        _approx_equal(j, asdict(calculate_jt_valve(backend=B, fluid="helium", **args)))


def test_expander_matches(js):
    for args, j in zip(EXPANDER, js["expander"]):
        _approx_equal(j, asdict(calculate_expander(backend=B, fluid="helium", **args)))


def test_heat_exchanger_matches(js):
    for args, j in zip(HX, js["hx"]):
        _approx_equal(j, asdict(calculate_heat_exchanger(**args)))


def test_equivalent_power_matches(js):
    for args, j in zip(EQ, js["eq"]):
        _approx_equal(j, asdict(calculate_equivalent_power(**args)))


def test_committed_toolbox_page_is_current():
    import importlib.util

    spec = importlib.util.spec_from_file_location("render_gistau_toolbox", REPO_ROOT / "tools" / "render_gistau_toolbox.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    committed = (REPO_ROOT / "docs" / "gistau-ch15" / "toolbox.html").read_text(encoding="utf-8")
    assert committed == module.render(), "regenerate: python tools/render_gistau_toolbox.py"


def test_non_finite_inputs_rejected_in_js_and_python():
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    script = (
        "const g=require(process.argv[1]);const out=[];"
        "for (const f of [()=>g.statePT(100,Infinity),()=>g.statePT(Infinity,300),()=>g.statePT(NaN,300),()=>g.statePS(100,Infinity)])"
        "{try{f();out.push('accepted')}catch(e){out.push('rejected')}}"
        "out.push(g.inValidityDomain(100,Infinity)?'in':'out');console.log(JSON.stringify(out));"
    )
    res = json.loads(subprocess.run([node, "-e", script, str(JS)], capture_output=True, text=True, check=True).stdout)
    assert res == ["rejected"] * 4 + ["out"]
    for p, t in [(100.0, float("inf")), (float("inf"), 300.0), (float("nan"), 300.0)]:
        with pytest.raises(ValueError):
            B.state_pt("helium", p, t)
    with pytest.raises(ValueError):
        B.state_ps("helium", 100.0, float("inf"))
