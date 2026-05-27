from physics.helium_refrigeration_core import CryogenicHeliumEngineG8


def test_calculate_g8_covariance_correlation_tracks_linear_relation():
    engine = CryogenicHeliumEngineG8()

    covariance, correlation = engine.calculate_g8_covariance_correlation([1, 2, 3], [2, 4, 6])

    assert covariance == 2.0
    assert correlation == 1.0


def test_calculate_g8_covariance_correlation_constant_vector_returns_zero_corr():
    engine = CryogenicHeliumEngineG8()

    covariance, correlation = engine.calculate_g8_covariance_correlation([1, 1, 1], [2, 3, 4])

    assert covariance == 0.0
    assert correlation == 0.0


def test_calculate_g8_anova_alias_matches_covariance_correlation():
    engine = CryogenicHeliumEngineG8()
    claimed = [0.2, 0.4, 0.6]
    actual = [0.2, 0.41, 0.59]

    assert engine.calculate_g8_anova(claimed, actual) == engine.calculate_g8_covariance_correlation(claimed, actual)


def test_compute_g8_exergy_efficiency_nitrogen_assist_increases_output():
    engine = CryogenicHeliumEngineG8()
    kwargs = dict(mass_flow_he=2.0, h_in=10.0, h_out=60.0, s_in=0.01, s_out=0.02, power_input_kw=200.0)

    without_assist = engine.compute_g8_exergy_efficiency(nitrogen_assist=False, **kwargs)
    with_assist = engine.compute_g8_exergy_efficiency(nitrogen_assist=True, **kwargs)

    assert with_assist > without_assist


def test_compute_g8_exergy_efficiency_nonpositive_power_returns_zero():
    engine = CryogenicHeliumEngineG8()

    value = engine.compute_g8_exergy_efficiency(
        mass_flow_he=2.0,
        h_in=10.0,
        h_out=60.0,
        s_in=0.01,
        s_out=0.02,
        power_input_kw=0.0,
    )

    assert value == 0.0
