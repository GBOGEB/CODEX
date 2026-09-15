from __future__ import annotations

import json

import numpy as np

from pca_engine.control_analytics import (
    closed_loop_transfer,
    confidence_interval,
    convergence_diagnostics,
    fourier_diagnostics,
    lu_decomposition,
    matrix_diagnostics,
    reverse_pressure,
    sigma_crossings,
    taylor_diagnostics,
    transfer_function_diagnostics,
)
from pca_engine.dynamic_response import step_response, transfer_to_state_space
from pca_engine.pca_core import fit_pca
from pca_engine.plotly_payloads import (
    covariance_heatmap_payload,
    eigen_spectrum_payload,
    frequency_spectrum_payload,
    metric_history_payload,
    pca_loadings_payload,
    pca_scree_payload,
    reverse_pressure_payload,
    time_response_payload,
)


def test_matrix_diagnostics_and_lu_are_reconstructable() -> None:
    x = np.array([[1.0, 2.0, 0.5], [2.0, 2.5, 1.0], [3.0, 4.0, 1.1], [4.0, 5.5, 2.2], [5.0, 7.0, 2.7]])
    result = matrix_diagnostics(x)
    assert len(result["eigenvalues"]) == 3
    assert abs(sum(result["explained_variance_ratio"]) - 1.0) < 1e-12
    assert result["numerical_rank"] >= 2

    a = np.array([[4.0, 3.0], [6.0, 3.0]])
    lu = lu_decomposition(a)
    p, l, u = map(np.asarray, (lu["P"], lu["L"], lu["U"]))
    assert np.allclose(p @ a, l @ u)
    assert lu["reconstruction_error"] < 1e-12


def test_confidence_sigma_and_convergence_receipts() -> None:
    ci = confidence_interval([9.8, 10.1, 10.0, 10.2, 9.9], confidence=0.95)
    assert ci["lower_bound"] < ci["estimate"] < ci["upper_bound"]
    boot = confidence_interval([9.8, 10.1, 10.0, 10.2, 9.9], method="bootstrap", bootstrap_samples=500, seed=7)
    assert boot["method"] == "bootstrap"

    sigma = sigma_crossings([0.0, 4.1, -5.2, 6.1], baseline_mean=0.0, baseline_std=1.0)
    assert sigma["receipts"][1]["highest_threshold_entered"] == 4.0
    assert sigma["receipts"][2]["direction"] == "LOW"
    assert sigma["receipts"][3]["highest_threshold_entered"] == 6.0
    assert sigma["threshold_counts"]["4.0"] == 3
    assert sigma["threshold_counts"]["6.0"] == 1

    convergence = convergence_diagnostics([10.0, 5.0, 2.5, 1.25, 0.62, 0.31])
    assert convergence["classification"] == "CONVERGING"


def test_reverse_pressure_is_separate_and_traceable() -> None:
    x = np.array([
        [1.0, 2.0, 5.0],
        [2.0, 2.2, 4.0],
        [3.0, 3.4, 3.0],
        [4.0, 4.1, 2.0],
        [5.0, 5.2, 1.0],
    ])
    pca = fit_pca(x, n_components=2, missing="error")
    pressure = reverse_pressure(pca, mode_pressure=[1.0, 0.5], source_gap=[1.0, 0.2, 0.8])
    assert pressure["authority"] == "NON_AUTHORITATIVE_DIAGNOSTIC"
    assert len(pressure["features"]) == 3
    assert "BT" in pressure["guard"]


def test_fourier_taylor_and_declared_transfer_diagnostics() -> None:
    n = 64
    t = np.arange(n, dtype=float)
    y = np.sin(2.0 * np.pi * 0.125 * t)
    spectrum = fourier_diagnostics(y, sample_interval=1.0)
    assert abs(spectrum["dominant_frequency"] - 0.125) < 1e-12

    local = taylor_diagnostics(lambda q: q[0] ** 2 + 3.0 * q[1], [2.0, -1.0])
    assert np.allclose(local["gradient"], [4.0, 3.0], atol=1e-5)
    assert np.allclose(np.asarray(local["hessian"]), [[2.0, 0.0], [0.0, 0.0]], atol=2e-4)

    diag = transfer_function_diagnostics([1.0], [1.0, 1.0], fast_time_constant=0.5, sluggish_time_constant=2.0)
    assert diag["stability_class"] == "STABLE"
    assert abs(diag["dominant_time_constant"] - 1.0) < 1e-12
    assert diag["responsiveness_class"] == "ACCEPTABLE"

    closed = closed_loop_transfer([1.0], [1.0, 1.0])
    assert np.allclose(closed["numerator"], [1.0])
    assert np.allclose(closed["denominator"], [1.0, 2.0])


def test_step_response_for_first_order_declared_model() -> None:
    ss = transfer_to_state_space([1.0], [1.0, 1.0])
    assert np.allclose(ss["A"], [[-1.0]])
    result = step_response([1.0], [1.0, 1.0], points=800)
    assert result["model_diagnostics"]["stability_class"] == "STABLE"
    assert result["response"][-1] > 0.999
    assert 2.0 < result["rise_time"] < 2.4
    assert 3.7 < result["settling_time"] < 4.1


def test_plotly_payloads_are_plain_json_and_authority_guarded() -> None:
    x = np.array([[1.0, 2.0], [2.0, 2.4], [3.0, 4.0], [4.0, 4.5]])
    pca = fit_pca(x, n_components=2, missing="error")
    pressure = reverse_pressure(pca)
    matrix = matrix_diagnostics(x)
    spectrum = fourier_diagnostics([0.0, 1.0, 0.0, -1.0] * 4)
    response = step_response([1.0], [1.0, 1.0], points=100)
    payloads = [
        metric_history_payload([1, 2, 3], [0.1, 0.2, 0.15], baseline_mean=0.0, baseline_std=0.05),
        covariance_heatmap_payload(matrix["covariance_matrix"], ["a", "b"]),
        pca_scree_payload(pca),
        pca_loadings_payload(pca),
        eigen_spectrum_payload(matrix["eigenvalues"]),
        reverse_pressure_payload(pressure["features"]),
        frequency_spectrum_payload(spectrum["frequencies"], spectrum["power"]),
        time_response_payload(response["time"], response["response"]),
    ]
    for payload in payloads:
        encoded = json.dumps(payload)
        assert encoded.startswith("{")
        assert "authority" in payload
