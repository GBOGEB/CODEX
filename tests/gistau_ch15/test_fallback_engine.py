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
        eta_isentropic=0.75,
    )

    assert result.shaft_power_w > 0.0
    assert result.outlet_pressure_kpa > result.inlet_pressure_kpa
    assert result.outlet_temperature_k > result.inlet_temperature_k
