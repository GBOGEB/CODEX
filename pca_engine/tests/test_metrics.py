import numpy as np

from pca_engine.pca_metrics import components_for_threshold, compression_ratio, cumulative_variance


def test_component_threshold():
    ratios = np.array([0.60, 0.25, 0.10, 0.05])
    assert np.allclose(cumulative_variance(ratios), [0.60, 0.85, 0.95, 1.0])
    assert components_for_threshold(ratios, 0.90) == 3
    assert components_for_threshold(ratios, 0.80) == 2


def test_compression_ratio():
    assert compression_ratio(1000, 20, 3) > 1.0
