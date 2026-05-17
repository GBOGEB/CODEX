import pytest

from gistau_ch15.properties.fallback_helium import FallbackHeliumBackend
from gistau_ch15.calculations.compressor import calculate_compressor


def test_fallback_backend_state_pt():
    backend = FallbackHeliumBackend()
    st = backend.state_pt('helium', 101.3, 300.0)

    assert st.temperature_k == 300.0
    assert st.pressure_kpa == 101.3
    assert st.density_kg_m3 > 0.0


def test_compressor_tuple_positive_power():
    backend = FallbackHeliumBackend()

    result = calculate_compressor(
        backend=backend,
        fluid='helium',
        p1_kpa=101.3,
        t1_k=300.0,
        p2_kpa=1200.0,
        mdot_kg_s=0.2,
        eta_isothermal=0.75,
        eta_isentropic=0.75,
    )

    assert result.shaft_power_w > 0.0
    assert result.isentropic_shaft_power_w is not None
    assert result.isentropic_shaft_power_w > 0.0
    assert result.outlet_pressure_kpa > result.inlet_pressure_kpa
    assert result.outlet_temperature_k > result.inlet_temperature_k


def test_compressor_defaults_to_half_efficiencies():
    backend = FallbackHeliumBackend()

    result = calculate_compressor(
        backend=backend,
        fluid='helium',
        p1_kpa=101.3,
        t1_k=300.0,
        p2_kpa=500.0,
        mdot_kg_s=0.1,
    )

    assert result.isothermal_efficiency == 0.5
    assert result.isentropic_efficiency == 0.5


def test_compressor_isentropic_output_can_be_disabled():
    backend = FallbackHeliumBackend()

    result = calculate_compressor(
        backend=backend,
        fluid='helium',
        p1_kpa=101.3,
        t1_k=300.0,
        p2_kpa=600.0,
        mdot_kg_s=0.1,
        eta_isentropic=None,
    )

    assert result.shaft_power_w > 0.0
    assert result.isentropic_shaft_power_w is None
    assert result.isentropic_efficiency is None


@pytest.mark.parametrize(
    "kwargs",
    [
        {"p1_kpa": 0.0},
        {"p2_kpa": 100.0},
        {"t1_k": 0.0},
        {"mdot_kg_s": 0.0},
        {"eta_isothermal": 0.0},
        {"eta_isentropic": 1.1},
    ],
)
def test_compressor_invalid_inputs_raise_value_error(kwargs):
    backend = FallbackHeliumBackend()
    args = {
        "backend": backend,
        "fluid": "helium",
        "p1_kpa": 101.3,
        "t1_k": 300.0,
        "p2_kpa": 600.0,
        "mdot_kg_s": 0.1,
        "eta_isothermal": 0.6,
        "eta_isentropic": 0.7,
    }
    args.update(kwargs)

    with pytest.raises(ValueError):
        calculate_compressor(**args)
