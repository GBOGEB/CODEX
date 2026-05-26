import pytest

from gistau_ch15.properties.experimental_correlation import ExperimentalCorrelation
from gistau_ch15.properties.fallback_helium import FallbackHeliumBackend
from gistau_ch15.properties.base import State
from gistau_ch15.properties.refprop_verification import RefpropVerificationRunner
from gistau_ch15.properties.uncertainty_quantification import UncertaintyQuantification
from gistau_ch15.properties.wetness_validation import WetnessValidationRunner
from gistau_ch15.properties.validation_dataset import ValidationPoint



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


def test_wetness_validation_two_phase_uses_quality_and_lambda_phase():
    class _TwoPhaseBackend(FallbackHeliumBackend):
        def state_pt(self, fluid: str, p_kpa: float, t_k: float) -> State:
            return State(
                pressure_kpa=p_kpa,
                temperature_k=t_k,
                enthalpy_j_kg=100.0,
                entropy_j_kgk=10.0,
                density_kg_m3=1.0,
                quality=0.25,
            )

    row = WetnessValidationRunner().run(
        backend=_TwoPhaseBackend(),
        backend_name="hepak",
        points=[
            ValidationPoint(
                example_id="WE-T02-SAT-LIQUID-HELIUM-003",
                tuple_id="two-phase-2k",
                fluid="Helium",
                pressure_kpa=3.2,
                temperature_k=2.0,
            )
        ],
    )[0]

    assert row.quality == pytest.approx(0.25)
    assert row.wetness_fraction == pytest.approx(0.75)
    assert row.phase_region == "lambda_region_two_phase"
