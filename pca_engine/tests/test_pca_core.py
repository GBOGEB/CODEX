import numpy as np

from pca_engine.pca_core import fit_pca, inverse_transform


def fixture():
    rng = np.random.default_rng(5)
    x = rng.normal(size=(300, 4))
    x[:, 3] = 1.5 * x[:, 0] - 0.4 * x[:, 1] + rng.normal(scale=0.05, size=300)
    return x


def test_shapes_orthogonality_and_variance_ratios():
    result = fit_pca(fixture(), n_components=4)
    assert result.scores_.shape == (300, 4)
    assert result.components_.shape == (4, 4)
    assert np.allclose(result.components_ @ result.components_.T, np.eye(4), atol=1e-10)
    assert np.isclose(result.explained_variance_ratio_.sum(), 1.0, atol=1e-12)
    assert np.all(np.diff(result.eigenvalues_) <= 1e-12)


def test_full_component_reconstruction_is_exact_to_numerical_precision():
    result = fit_pca(fixture(), n_components=4)
    rebuilt = inverse_transform(result, result.scores_)
    assert np.allclose(rebuilt, result.input_matrix_, atol=1e-10)
