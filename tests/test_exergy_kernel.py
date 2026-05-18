from gistau_ch15.kernels.exergy import specific_flow_exergy


def test_specific_flow_exergy_reference_state() -> None:
    assert specific_flow_exergy(1000.0, 10.0, 1000.0, 10.0, 300.0) == 0.0


def test_specific_flow_exergy_positive() -> None:
    ex = specific_flow_exergy(
        h_j_kg=2000.0,
        s_j_kgk=5.0,
        h0_j_kg=1000.0,
        s0_j_kgk=1.0,
        t0_k=300.0,
    )
    assert isinstance(ex, float)
