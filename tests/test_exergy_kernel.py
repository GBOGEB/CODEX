from gistau_ch15.kernels.exergy import specific_flow_exergy


def test_specific_flow_exergy_reference_state() -> None:
    assert specific_flow_exergy(1000.0, 10.0, 1000.0, 10.0, 300.0) == 0.0


def test_specific_flow_exergy_sign_and_scale_positive_case() -> None:
    ex = specific_flow_exergy(
        h_j_kg=150000.0,
        s_j_kgk=500.0,
        h0_j_kg=100000.0,
        s0_j_kgk=400.0,
        t0_k=300.0,
    )
    assert ex == 20000.0


def test_specific_flow_exergy_sign_negative_case() -> None:
    ex = specific_flow_exergy(
        h_j_kg=110000.0,
        s_j_kgk=700.0,
        h0_j_kg=100000.0,
        s0_j_kgk=400.0,
        t0_k=300.0,
    )
    assert ex < 0.0
