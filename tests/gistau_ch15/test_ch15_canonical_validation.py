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
    open_items = set(gate.get("source_check_required", {}))
    assert set(gate["checked"]) | set(gate["excluded"]) | open_items == ids
    assert not set(gate["checked"]) & set(gate["excluded"])
    assert not open_items & (set(gate["checked"]) | set(gate["excluded"]))
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
    t2s_c = 5.0 * (1.2 / 0.5) ** (B.R / B.CP)
    assert comp["outlet_temperature_k"] == pytest.approx(5.0 + (t2s_c - 5.0) / 0.75, rel=1e-7)
    assert comp["power_w"] > 0
    # Sect. 15.8.5: real rise = isentropic rise / eta (the printed Fig. 15.31 multiplies instead).
    assert comp["real_enthalpy_change_j_g"] == pytest.approx(comp["isentropic_enthalpy_change_j_g"] / 0.75, rel=1e-12)
    assert comp["power_w"] == pytest.approx(400.0 * comp["real_enthalpy_change_j_g"], rel=1e-12)


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


def test_source_check_items_are_reported_but_never_counted_as_passing(tool, gate, examples):
    # Synthetic open item: move one checked example to source_check_required.
    moved = "WE-T05-CRYOGENIC-COMPRESSOR-001"
    gate = dict(gate, checked=[e for e in gate["checked"] if e != moved],
                source_check_required={**(gate.get("source_check_required") or {}), moved: "synthetic"})
    by_id = {e["example_id"]: e for e in examples}
    real = {eid: tool.compute(by_id[eid], ideal) for eid in gate["checked"]}
    fake = [dict(e, expected_outputs={**e["expected_outputs"], **{k: v for k, v in real.get(e["example_id"], {}).items() if k in e["expected_outputs"]}}) for e in examples]
    report = tool.validate(gate, fake, ideal)
    assert report["status"] == "PASS"
    open_rows = [r for r in report["rows"] if r["example_id"] in gate["source_check_required"]]
    assert open_rows and all(r["verdict"].startswith("OPEN_") for r in open_rows)
    assert report["examples_checked"] == len(gate["checked"])


def test_book_errata_are_never_compared(gate, examples):
    """An erratum cell stays recorded in the transcription but is not an expected output."""
    by_id = {e["example_id"]: e for e in examples}
    for eid, erratum in (gate.get("book_errata") or {}).items():
        ex = by_id[eid]
        assert any(b["cell"] == erratum["cell"].split()[0] and b["printed"] == erratum["printed"] for b in ex["source_verification"]["book_errata"])
        assert erratum["printed"] not in ex["expected_outputs"].values()
        assert erratum["finding"].strip()


def test_t05_printed_cells_are_internally_consistent(examples):
    """Fig. 15.31: h2 = h1 + dH real and power = mdot x dH real, as printed."""
    ex = {e["example_id"]: e for e in examples}["WE-T05-CRYOGENIC-COMPRESSOR-001"]
    o, i = ex["expected_outputs"], ex["inputs"]
    assert i["outlet_pressure_bar"] == 1.20
    assert o["outlet_enthalpy_j_g"] == pytest.approx(o["inlet_enthalpy_j_g"] + o["real_enthalpy_change_j_g"], abs=0.011)
    assert o["power_w"] == pytest.approx(i["mass_flow_g_s"] * o["real_enthalpy_change_j_g"], rel=1e-3)
