import pytest

from gistau_ch15.calculations.equivalent_power import calculate_equivalent_power
from gistau_ch15.calculations.expander import calculate_expander
from gistau_ch15.properties.fallback_helium import FallbackHeliumBackend


backend = FallbackHeliumBackend()


class FluidRecordingBackend(FallbackHeliumBackend):
    def __init__(self):
        super().__init__()
        self.fluids = []

    def state_pt(self, fluid: str, p_kpa: float, t_k: float):
        self.fluids.append(fluid)
        return super().state_pt(fluid, p_kpa, t_k)


def test_backend_contract_has_required_calls():
    assert hasattr(backend, 'state_pt')
    assert hasattr(backend, 'state_ph')
    assert hasattr(backend, 'state_ps')
    assert hasattr(backend, 'saturation_t')
    assert hasattr(backend, 'saturation_p')
    assert hasattr(backend, 'quality_ph')


def test_expander_positive_recovery():
    result = calculate_expander(
        backend=backend,
        fluid='helium',
        p1_kpa=1200.0,
        t1_k=80.0,
        p2_kpa=110.0,
        mdot_kg_s=0.05,
        eta_isentropic=0.82,
    )

    assert result.power_output_w >= 0.0
    assert result.outlet_temperature_k < result.inlet_temperature_k


def test_expander_defaults_to_helium_proxy():
    expected_state_pt_calls = 4
    recording_backend = FluidRecordingBackend()
    helium = calculate_expander(
        backend=recording_backend,
        fluid='helium',
        p1_kpa=1200.0,
        t1_k=80.0,
        p2_kpa=110.0,
        mdot_kg_s=0.05,
        eta_isentropic=0.82,
    )
    defaulted = calculate_expander(
        backend=recording_backend,
        fluid='',
        p1_kpa=1200.0,
        t1_k=80.0,
        p2_kpa=110.0,
        mdot_kg_s=0.05,
        eta_isentropic=0.82,
    )

    assert defaulted.outlet_temperature_k == helium.outlet_temperature_k
    assert defaulted.power_output_w == helium.power_output_w
    assert recording_backend.fluids == ['helium'] * expected_state_pt_calls


def test_expander_supports_other_cryogenic_fluid_proxies():
    pressure_ratio = 110.0 / 1200.0
    helium = calculate_expander(
        backend=backend,
        fluid='helium',
        p1_kpa=1200.0,
        t1_k=80.0,
        p2_kpa=110.0,
        mdot_kg_s=0.05,
        eta_isentropic=0.82,
    )
    nitrogen = calculate_expander(
        backend=backend,
        fluid='LN2',
        p1_kpa=1200.0,
        t1_k=80.0,
        p2_kpa=110.0,
        mdot_kg_s=0.05,
        eta_isentropic=0.82,
    )
    hydrogen = calculate_expander(
        backend=backend,
        fluid='H2',
        p1_kpa=1200.0,
        t1_k=80.0,
        p2_kpa=110.0,
        mdot_kg_s=0.05,
        eta_isentropic=0.82,
    )

    assert helium.outlet_temperature_k < nitrogen.outlet_temperature_k
    assert helium.outlet_temperature_k < hydrogen.outlet_temperature_k
    assert helium.outlet_temperature_k == pytest.approx(
        80.0 - 0.82 * (80.0 - 80.0 * pressure_ratio**0.4)
    )
    assert hydrogen.outlet_temperature_k == pytest.approx(nitrogen.outlet_temperature_k)
    assert nitrogen.outlet_temperature_k == pytest.approx(
        80.0 - 0.82 * (80.0 - 80.0 * pressure_ratio**0.28)
    )


def test_equivalent_power_positive():
    eq = calculate_equivalent_power(
        compressor_power_w=1200.0,
        expander_recovery_w=100.0,
        refrigeration_load_w=10.0,
        cold_temperature_k=4.5,
        ambient_temperature_k=300.0,
    )

    assert eq.equivalent_power_w > 0.0
    assert eq.carnot_factor > 1.0
