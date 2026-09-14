"""Optional TensorFlow/Keras autoencoder scaffold for nonlinear PCA experiments."""
from __future__ import annotations


class OptionalDependencyError(RuntimeError):
    pass


def tensorflow_available() -> bool:
    try:
        import tensorflow  # noqa: F401
    except ImportError:
        return False
    return True


def build_autoencoder(input_dim: int, latent_dim: int, hidden_dims: tuple[int, ...] = (32, 16)):
    try:
        from tensorflow import keras
    except ImportError as exc:
        raise OptionalDependencyError("TensorFlow is optional; install pca-engine[nlpca]") from exc
    if not 0 < latent_dim < input_dim:
        raise ValueError("latent_dim must satisfy 0 < latent_dim < input_dim")

    inputs = keras.Input(shape=(input_dim,), name="features")
    x = inputs
    for width in hidden_dims:
        x = keras.layers.Dense(width, activation="relu")(x)
    latent = keras.layers.Dense(latent_dim, name="latent")(x)
    x = latent
    for width in reversed(hidden_dims):
        x = keras.layers.Dense(width, activation="relu")(x)
    outputs = keras.layers.Dense(input_dim, name="reconstruction")(x)
    autoencoder = keras.Model(inputs, outputs, name="nlpca_autoencoder")
    encoder = keras.Model(inputs, latent, name="nlpca_encoder")
    autoencoder.compile(optimizer="adam", loss="mse")
    return autoencoder, encoder


def fit_nlpca(data, *, latent_dim: int, epochs: int = 50, batch_size: int = 32, verbose: int = 0):
    autoencoder, encoder = build_autoencoder(int(data.shape[1]), latent_dim)
    history = autoencoder.fit(data, data, epochs=epochs, batch_size=batch_size, verbose=verbose)
    latent = encoder.predict(data, verbose=0)
    return {"autoencoder": autoencoder, "encoder": encoder, "history": history, "latent": latent}
