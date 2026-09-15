from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(ROOT))

from pca_engine import fit_pca
from pca_engine.pca_reconstruction import reconstruction_metrics

rng = np.random.default_rng(7)
x = rng.normal(size=(200, 4))
x[:, 3] = 0.8 * x[:, 0] - 0.2 * x[:, 1] + rng.normal(scale=0.1, size=200)
result = fit_pca(x, n_components=3)
print({"ratio": result.explained_variance_ratio_.tolist(), "reconstruction": reconstruction_metrics(result)})
