# PCA mathematics

Given numeric observations `X`, the engine optionally centers and standardizes features, then forms the sample covariance matrix

`C = X^T X / (n-1)`.

Because `C` is symmetric, `numpy.linalg.eigh` returns an orthonormal eigenbasis. Eigenpairs are sorted from largest to smallest eigenvalue. The retained eigenvectors are the component directions; scores are `X V`; explained-variance ratios are `lambda_i / sum(lambda)`.

Loadings are defined here as `V * sqrt(lambda)`. Squared loadings sum by feature to communality for the retained component set.

Reconstruction projects retained scores back through the component matrix, then reverses scaling and centering. Reconstruction MSE/RMSE quantify information loss.

This implementation is linear PCA. It must not be described as NLPCA.
