from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(ROOT))

from pca_engine.nlpca_autoencoder import OptionalDependencyError, fit_nlpca, tensorflow_available

if not tensorflow_available():
    print({"status": "DEFER_TENSORFLOW_NOT_INSTALLED"})
else:
    rng = np.random.default_rng(11)
    x = rng.normal(size=(128, 6)).astype("float32")
    try:
        result = fit_nlpca(x, latent_dim=2, epochs=2, verbose=0)
        print({"status": "PASS", "latent_shape": list(result["latent"].shape)})
    except OptionalDependencyError as exc:
        print({"status": "DEFER_TENSORFLOW_NOT_INSTALLED", "detail": str(exc)})
