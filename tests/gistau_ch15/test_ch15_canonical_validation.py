"""Logic of tools/ch15_canonical_validation.py with an analytic stand-in provider (no CoolProp)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml

from gistau_ch15.properties.fallback_helium import FallbackHeliumBackend

REPO_ROOT = Path(__file__).resolve().parents[2]
B = FallbackHeliumBackend()


def _tool():
    spec = importlib.util.spec_from_file_location("ch15_canonical_validation", REPO_ROOT / "tools" / "ch15_canonical_validation.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ideal(t_k, p_kpa):
    s = B.state_pt("helium", p_kpa, t_k)
    return {"density_kg_m3": s.density_kg_m3, "enthalpy_J_kg": s.enthalpy_j_kg, "entropy_J_kgK": s.entropy_j_kgk}


@pytest.fixture(scope="module")
def tool():
    return _tool()


@pytest.fixture(scope="module")
def gate():
    return yaml.safe_load((REPO_ROOT / "governance/physics/CH15_CANONICAL_VALIDATION.yaml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def examples(gate):
    data = json.loads((REPO_ROOT / gate["source"]).read_text(encoding="utf-8"))
    return data if isinstance(data, list) else data["examples"]


def test_every_worked_example_is_checked_or_excluded_with_a_reason(gate, examples):
    ids = {e["example_id"] for e in examples}
    assert set(gate["checked"]) | set(gate["excluded"]) == ids
    assert not set(gate["checked"]) & set(gate["excluded"])
    assert all(isinstance(r, str) and r.strip() for r in gate["excluded"].values())


def test_inverse_solvers_recover_analytic_ideal_gas_answers(tool):
    t = tool._solve_t(ideal, 120.0, "enthalpy_J_kg", B.CP * 19.16)
    assert t == pytest.approx(19.16, abs=1e-6)
    s1 = ideal(25.0, 1400.0)["entropy_J_kgK"]
    t2s = tool._solve_t(ideal, 120.0, "entropy_J_kgK", s1)
    assert t2s == pytest.approx(25.0 * (120.0 / 1400.0) ** (B.R / B.CP), rel=1e-9)


def test_expander_and_compressor_follow_isentropic_efficiency(tool, examples):
    by_id = {e["example_id"]: e for e in examples}
    exp = tool.compute(by_id["WE-T04-CRYOGENIC-EXPANDER-001"], ideal)
    t2s = 25.0 * (1.2 / 14.0) ** (B.R / B.CP)
    assert exp["outlet_temperature_k"] == pytest.approx(25.0 - 0.75 * (25.0 - t2s), rel=1e-7)
    assert exp["power_w_visible"] < 0  # book sign convention: work extracted
    comp = tool.compute(by_id["WE-T05-CRYOGENIC-COMPRESSOR-001"], ideal)
    t2s_c = 5.0 * (1.7 / 0.5) ** (B.R / B.CP)
    assert comp["outlet_temperature_k"] == pytest.approx(5.0 + (t2s_c - 5.0) / 0.75, rel=1e-7)
    assert comp["power_w"] > 0


def test_free_expansion_adds_the_heat_input(tool, examples):
    by_id = {e["example_id"]: e for e in examples}
    out = tool.compute(by_id["WE-T02-FREE-EXPANSION-HEAT-001"], ideal)
    assert out["outlet_enthalpy_j_g"] - out["inlet_enthalpy_j_g"] == pytest.approx(100.0 / 50.0)  # 100 W / 50 g/s


def test_gate_fails_on_any_tolerance_breach_and_on_unaccounted_examples(tool, gate, examples):
    report = tool.validate(gate, examples, ideal)  # an ideal gas cannot reproduce real-fluid Ch15 values
    assert report["status"] == "FAIL" and report["failures"] > 0
    assert report["quantities_checked"] >= 10
    missing = dict(gate, excluded={k: v for k, v in gate["excluded"].items() if not k.startswith("WE-T06")})
    assert tool.validate(missing, examples, ideal)["unaccounted_examples"] == ["WE-T06-EQUIVALENT-POWER-001"]


def test_gate_passes_when_provider_reproduces_the_book(tool, gate, examples):
    by_id = {e["example_id"]: e for e in examples}
    real = {eid: tool.compute(by_id[eid], ideal) for eid in gate["checked"]}
    fake = [dict(e, expected_outputs={**e["expected_outputs"], **{k: v for k, v in real.get(e["example_id"], {}).items() if k in e["expected_outputs"]}}) for e in examples]
    assert tool.validate(gate, fake, ideal)["status"] == "PASS"
