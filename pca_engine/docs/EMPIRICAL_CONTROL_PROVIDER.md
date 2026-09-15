# Empirical control provider

`gbogeb-pca-engine` 0.2 adds reusable analytics for engineering-control workflows while retaining zero engineering authority.

## Added surfaces

- matrix diagnostics: covariance, correlation, determinant/log-determinant, numerical rank, condition number, eigenspectrum, SVD, QR and explicit LU;
- 95% confidence intervals using declared normal approximation or deterministic percentile bootstrap;
- signed 3/4/5/6-sigma threshold-entry receipts;
- PCA reverse pressure: variance-weighted back-projection from unresolved modes to original metrics/source gaps;
- convergence classification for ordered residual histories;
- FFT/periodogram diagnostics;
- finite-difference Taylor gradient/Hessian for an explicitly supplied local model;
- declared continuous-time transfer-function poles, zeros, time constants, damping, stability and responsiveness;
- negative-feedback closed-loop polynomial construction;
- deterministic RK4 unit-step response for declared proper SISO transfer functions;
- dependency-free Plotly-ready JSON payloads for metric history/CI/sigma bands, covariance, PCA, eigenspectrum, reverse pressure, frequency and time response.

## Authority boundary

The provider computes observables only. It does not:

- create source evidence;
- decide QPS engineering closure, DOV, DOD, compliance, acceptance or release;
- convert a PCA score into a Bradley-Terry weight;
- permit reverse pressure to override a source or execution gate;
- equate a 6-sigma observation with Six Sigma process capability;
- infer a physical transfer function from sparse KPI or project-wave history;
- overwrite raw observations with empirical substitutions.

QPS owns profiles, thresholds, evidence classes, gate semantics and interpretation. The provider stays generic and reusable.

## Sigma note

A signed z-score crossing 4, 5 or 6 standard deviations is a control/special-cause observation relative to the declared baseline. It is not the same claim as long-term Six Sigma capability. In particular, the conventional 3.4 DPMO figure depends on a separate 1.5-sigma shift convention and process/specification assumptions.

## Dynamic model note

Laplace/transfer-function outputs are emitted only from caller-supplied numerator/denominator coefficients. Time constants and sluggish/fast labels therefore describe the declared model, not a model inferred by the provider.
