import numpy as np

from pca_engine import fit_pca
from pca_engine.pca_loadings import communality, loadings, top_features
from pca_engine.pca_reconstruction import reconstruction_metrics


def test_loadings_and_reconstruction_improve_with_components():
    rng = np.random.default_rng(9)
    x = rng.normal(size=(250, 5))
    x[:, 4] = x[:, 0] + 0.2 * x[:, 1] + rng.normal(scale=0.03, size=250)
    result = fit_pca(x, n_components=5)
    assert loadings(result).shape == (5, 5)
    assert communality(result).shape == (5,)
    assert len(top_features(result, 0, 3)) == 3
    one = reconstruction_metrics(result, n_components=1)
    full = reconstruction_metrics(result, n_components=5)
    assert full["mse"] < one["mse"]
    assert full["mse"] < 1e-20
