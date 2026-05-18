from gistau_ch15.visualization.backend_agreement import (
    BackendAgreementBuilder,
)
from gistau_ch15.visualization.expander_validation import (
    FallbackExpanderValidation,
)
from gistau_ch15.visualization.phase_map_sampling import (
    FallbackPhaseMapSampler,
)
from gistau_ch15.visualization.ts_reconstruction import (
    FallbackTSReconstructor,
)


def test_ts_reconstruction_returns_paths():
    paths = FallbackTSReconstructor().build_paths()

    assert len(paths) >= 1


def test_phase_map_sampler_returns_points():
    phase_map = FallbackPhaseMapSampler().sample()

    assert len(phase_map.pressure_kpa) > 0


def test_expander_validation_returns_points():
    points = FallbackExpanderValidation().build()

    assert len(points) >= 1


def test_backend_agreement_builder_returns_matrix():
    matrix = BackendAgreementBuilder().build()

    assert len(matrix.values) > 0
