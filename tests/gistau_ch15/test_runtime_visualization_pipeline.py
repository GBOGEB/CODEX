from gistau_ch15.visualization.backend_delta_matrix import (
    FallbackBackendDeltaBuilder,
)
from gistau_ch15.visualization.coolprop_saturation_curves import (
    CoolPropSaturationCurveGenerator,
)
from gistau_ch15.visualization.executable_ts_paths import (
    ExecutableTSPathGenerator,
)
from gistau_ch15.visualization.phase_region_classifier import (
    PhaseRegionClassifier,
)
from gistau_ch15.visualization.plotly_trace_builder import (
    PlotlyTraceBuilder,
)


def test_coolprop_curve_generator_returns_curve():
    curve = CoolPropSaturationCurveGenerator().generate()

    assert len(curve.temperature_liquid) > 0


def test_executable_ts_generator_returns_paths():
    paths = ExecutableTSPathGenerator().generate()

    assert len(paths) > 0


def test_backend_delta_builder_returns_backends():
    delta = FallbackBackendDeltaBuilder().build()

    assert len(delta.backends) > 0


def test_phase_region_classifier_returns_region():
    region = PhaseRegionClassifier().classify(100.0, 2.0)

    assert region == "two-phase"


def test_plotly_trace_builder_returns_traces():
    builder = PlotlyTraceBuilder()

    traces = builder.saturation_traces(
        {
            "entropy_liquid": [1.0, 2.0],
            "temperature_liquid": [2.0, 3.0],
            "entropy_vapor": [5.0, 6.0],
            "temperature_vapor": [2.0, 3.0],
        }
    )

    assert len(traces) == 2
