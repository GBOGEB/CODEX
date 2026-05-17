from gistau_ch15.calculations.heat_exchanger import calculate_heat_exchanger
from gistau_ch15.calculations.jt_valve import calculate_jt_valve
from gistau_ch15.properties.fallback_helium import FallbackHeliumBackend


backend = FallbackHeliumBackend()


def test_jt_valve_idempotent():
    r1 = calculate_jt_valve(
        backend=backend,
        fluid='helium',
        p1_kpa=1200.0,
        t1_k=18.0,
        p2_kpa=110.0,
        mdot_kg_s=0.05,
    )

    r2 = calculate_jt_valve(
        backend=backend,
        fluid='helium',
        p1_kpa=1200.0,
        t1_k=18.0,
        p2_kpa=110.0,
        mdot_kg_s=0.05,
    )

    assert r1 == r2


def test_heat_exchanger_bounds():
    hx = calculate_heat_exchanger(
        hot_inlet_k=300.0,
        cold_inlet_k=80.0,
        hot_capacity_rate_wk=500.0,
        cold_capacity_rate_wk=350.0,
        effectiveness=0.82,
    )

    assert hx.hot_outlet_k < hx.hot_inlet_k
    assert hx.cold_outlet_k > hx.cold_inlet_k
    assert hx.q_transfer_w > 0.0
