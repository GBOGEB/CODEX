import numpy as np
import pandas as pd

from pca_engine.preprocessing import prepare_numeric


def test_numeric_selection_imputation_and_scaling():
    frame = pd.DataFrame({"a": [1.0, 2.0, np.nan, 4.0], "b": [2.0, 4.0, 6.0, 8.0], "label": list("wxyz")})
    result = prepare_numeric(frame, missing="mean", center=True, scale=True)
    assert result.feature_names == ["a", "b"]
    assert result.matrix.shape == (4, 2)
    assert np.isfinite(result.matrix).all()
    assert np.allclose(result.matrix.mean(axis=0), 0.0, atol=1e-12)


def test_constant_column_is_safe():
    result = prepare_numeric([[1.0, 5.0], [2.0, 5.0], [3.0, 5.0]])
    assert result.scale[1] == 1.0
    assert np.allclose(result.matrix[:, 1], 0.0)
