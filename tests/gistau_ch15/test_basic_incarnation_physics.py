"""The fallback backend is the cross-check incarnation: its ideal-gas physics must be right."""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from gistau_ch15.calculations.expander_replay import CryogenicExpanderReplay
from gistau_ch15.properties.fallback_helium import (
    IDEAL_GAS_DOMAIN,
    OUTSIDE_IDEAL_GAS_DOMAIN,
    FallbackHeliumBackend,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
B = FallbackHeliumBackend()


def _worked_example(example_id: str) -> dict:
    data = json.loads((REPO_ROOT / "docs" / "gistau-ch15" / "data" / "worked_examples.json").read_text(encoding="utf-8"))
    rows = data if isinstance(data, list) else data["examples"]
    return next(r for r in rows if r["example_id"] == example_id)


def test_density_matches_ch15_worked_example_in_domain():
    ex = _worked_example("WE-T00-REFPROP-HSD-PT-002")
    p_kpa = ex["inputs"]["pressure_bar"] * 100.0
    st = B.state_pt("helium", p_kpa, ex["inputs"]["temperature_k"])
    assert st.validity == IDEAL_GAS_DOMAIN
    assert st.density_kg_m3 == pytest.approx(ex["expected_outputs"]["density_kg_m3"], rel=2e-3)


def test_entropy_is_zero_at_reference_state():
    assert B.entropy_pt(B.P_REF_KPA, B.T_REF_K) == pytest.approx(0.0, abs=1e-9)


def test_isothermal_entropy_change_is_minus_r_ln_pressure_ratio():
    s1 = B.entropy_pt(100.0, 300.0)
    s2 = B.entropy_pt(1000.0, 300.0)
    assert s2 - s1 == pytest.approx(-B.R * math.log(10.0), rel=1e-12)


def test_entropy_is_not_the_old_cp_times_t_placeholder():
    st = B.state_pt("helium", 100.0, 300.0)
    assert st.entropy_j_kgk != pytest.approx(st.enthalpy_j_kg)


@pytest.mark.parametrize("p1,t1,p2", [(1400.0, 25.0, 120.0), (101.325, 300.0, 1200.0), (500.0, 80.0, 50.0)])
def test_isentropic_path_follows_ideal_gas_relation(p1, t1, p2):
    s1 = B.state_pt("helium", p1, t1).entropy_j_kgk
    t2 = B.state_ps("helium", p2, s1).temperature_k
    assert t2 == pytest.approx(t1 * (p2 / p1) ** (B.R / B.CP), rel=1e-12)


def test_state_ph_and_state_ps_round_trip():
    st = B.state_pt("helium", 350.0, 42.0)
    assert B.state_ph("helium", 350.0, st.enthalpy_j_kg).temperature_k == pytest.approx(42.0, rel=1e-12)
    assert B.state_ps("helium", 350.0, st.entropy_j_kgk).temperature_k == pytest.approx(42.0, rel=1e-12)


@pytest.mark.parametrize(
    "p_kpa,t_k,expected",
    [
        (100.0, 300.0, IDEAL_GAS_DOMAIN),
        (1000.0, 300.0, IDEAL_GAS_DOMAIN),     # rho 1.6 kg/m3
        (101.325, 50.0, IDEAL_GAS_DOMAIN),     # rho 0.98 kg/m3
        (1000.0, 150.0, OUTSIDE_IDEAL_GAS_DOMAIN),  # rho 3.2 kg/m3
        (50.0, 30.0, OUTSIDE_IDEAL_GAS_DOMAIN),     # below 50 K
        (120.0, 4.5, OUTSIDE_IDEAL_GAS_DOMAIN),
    ],
)
def test_states_are_tagged_with_validity(p_kpa, t_k, expected):
    assert B.state_pt("helium", p_kpa, t_k).validity == expected


@pytest.mark.parametrize("p_kpa,t_k", [(0.0, 300.0), (100.0, 0.0), (-1.0, 10.0)])
def test_non_physical_inputs_are_rejected(p_kpa, t_k):
    with pytest.raises(ValueError):
        B.state_pt("helium", p_kpa, t_k)


def test_expander_replay_now_uses_a_real_isentropic_path():
    r = CryogenicExpanderReplay().replay(
        backend=B, fluid="helium", p1_kpa=1400.0, t1_k=25.0, p2_kpa=120.0, eta_isentropic=0.75, mdot_kg_s=0.05
    )
    t2s = 25.0 * (120.0 / 1400.0) ** (B.R / B.CP)
    assert r.outlet_temperature_k == pytest.approx(25.0 - 0.75 * (25.0 - t2s), rel=1e-9)


@pytest.mark.parametrize("p1,t1,p2", [(100.0, 300.0, 1200.0), (101.325, 80.0, 300.0)])
def test_compressor_isentropic_outlet_is_consistent_with_basic_incarnation_entropy(p1, t1, p2):
    from gistau_ch15.calculations.compressor import calculate_compressor

    r = calculate_compressor(backend=B, fluid="helium", p1_kpa=p1, t1_k=t1, p2_kpa=p2, mdot_kg_s=0.1)
    t2s = B.state_ps("helium", p2, B.state_pt("helium", p1, t1).entropy_j_kgk).temperature_k
    assert r.outlet_temperature_k == pytest.approx(t2s, rel=2e-3)  # 0.4 vs R/cp = 0.39998
