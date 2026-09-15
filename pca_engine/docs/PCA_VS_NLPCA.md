# PCA vs NLPCA

## PCA

Linear, deterministic for fixed preprocessing/eigensolver inputs, and based on orthogonal directions that maximize variance. The core package implements this path with NumPy and does not require sklearn.

## NLPCA scaffold

The optional `nlpca_autoencoder` module uses a neural autoencoder when TensorFlow/Keras is installed. Its latent coordinates are nonlinear learned representations and do not inherit PCA orthogonality, eigenvalue, or explained-variance semantics automatically.

TensorFlow is deliberately optional. If absent, the NLPCA path returns/raises a clear dependency defer rather than breaking linear PCA.

Do not compare PCA and NLPCA components as though they were mathematically identical objects.
