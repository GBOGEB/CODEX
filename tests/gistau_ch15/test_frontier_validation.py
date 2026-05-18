from gistau_ch15.properties.experimental_correlation import ExperimentalCorrelation
from gistau_ch15.properties.fallback_helium import FallbackHeliumBackend
from gistau_ch15.properties.refprop_verification import RefpropVerificationRunner
from gistau_ch15.properties.uncertainty_quantification import UncertaintyQuantification
from gistau_ch15.properties.wetness_validation import WetnessValidationRunner



def test_uncertainty_quantification_basic_statistics():
    uq = UncertaintyQuantification()

    result = uq.summarize(
        quantity="enthalpy",
        backend_name="fallback",
        values=[100.0, 102.0, 98.0, 101.0],
    )

    assert result.sample_count == 4
    assert result.standard_deviation >= 0.0
    assert result.relative_uncertainty_percent >= 0.0



def test_experimental_correlation_residuals():
    corr = ExperimentalCorrelation()

    row = corr.compare(
        experiment_id="EXP-001",
        tuple_id="JT-001",
        backend_name="fallback",
        quantity="temperature",
        measured_value=4.2,
        predicted_value=4.1,
    )

    assert abs(row.absolute_residual) > 0.0



def test_refprop_verification_runner_fallback_safe():
    backend = FallbackHeliumBackend()
    runner = RefpropVerificationRunner()

    rows = runner.run(backend=backend, backend_name="fallback")

    assert rows
    assert any(r.status == "ok" for r in rows)



def test_wetness_validation_runner_executes():
    backend = FallbackHeliumBackend()
    runner = WetnessValidationRunner()

    rows = runner.run(
        backend=backend,
        backend_name="fallback",
    )

    assert rows
    assert all(r.status in {"ok", "backend_unavailable_or_failed"} for r in rows)
