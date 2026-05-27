"""Shared pipeline configuration for runtime execution control."""

from __future__ import annotations

# Pipeline steps that exist and can be executed
PIPELINE_STEPS = [
    'telemetry_pipeline.py',
    'dmaic_runtime_tracker.py',
    'pca_convergence_analysis.py',
    'plotly_wave_dashboard.py',
]
