from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime_engine import telemetry_pipeline
from runtime_engine import dmaic_runtime_tracker
from runtime_engine import pca_convergence_analysis
from runtime_engine import runtime_control_center


def test_build_payload_structure() -> None:
    """Test that build_payload returns expected structure and keys."""
    payload = telemetry_pipeline.build_payload()
    
    # Check top-level keys
    assert 'waves' in payload
    assert 'telemetry' in payload
    assert 'claimed_vs_actual' in payload
    
    # Check waves structure
    assert isinstance(payload['waves'], list)
    assert len(payload['waves']) > 0
    for wave in payload['waves']:
        assert 'wave' in wave
        assert 'completion' in wave
        assert 'score' in wave
    
    # Check telemetry structure
    telemetry = payload['telemetry']
    assert 'average_completion' in telemetry
    assert 'average_score' in telemetry
    assert 'wave_velocity' in telemetry
    assert 'velocity_average' in telemetry
    assert 'kpi_score' in telemetry
    assert 'dmaic' in telemetry
    assert 'pca' in telemetry


def test_compute_wave_velocity() -> None:
    """Test that wave velocity is computed correctly."""
    velocities = telemetry_pipeline.compute_wave_velocity()
    
    # Should have one less velocity than waves
    assert len(velocities) == len(telemetry_pipeline.WAVES) - 1
    
    # Check first velocity calculation
    expected_first = telemetry_pipeline.WAVES[1]['score'] - telemetry_pipeline.WAVES[0]['score']
    assert velocities[0] == expected_first


def test_compute_kpi_score() -> None:
    """Test that KPI score is computed correctly."""
    score = telemetry_pipeline.compute_kpi_score()
    
    # Should be a float
    assert isinstance(score, float)
    
    # Should be positive
    assert score > 0


def test_build_dmaic_summary_structure() -> None:
    """Test that build_dmaic_summary returns expected structure."""
    summary = dmaic_runtime_tracker.build_dmaic_summary()
    
    # Check all DMAIC phases are present
    expected_phases = ['define', 'measure', 'analyze', 'improve', 'control']
    for phase in expected_phases:
        assert phase in summary
        assert 'current' in summary[phase]
        assert 'average' in summary[phase]
        assert 'delta' in summary[phase]


def test_dmaic_delta_calculation() -> None:
    """Test that DMAIC deltas are computed correctly."""
    summary = dmaic_runtime_tracker.build_dmaic_summary()
    
    # Check delta calculation for 'define' phase
    define_values = dmaic_runtime_tracker.DMAIC['define']
    expected_delta = define_values[-1] - define_values[0]
    assert summary['define']['delta'] == expected_delta
    
    # Check current value
    assert summary['define']['current'] == define_values[-1]


def test_compute_pca_summary_structure() -> None:
    """Test that compute_pca_summary returns expected structure."""
    summary = pca_convergence_analysis.compute_pca_summary()
    
    # Check required keys
    assert 'total_variance' in summary
    assert 'normalized_factors' in summary
    assert 'dominant_factor' in summary
    assert 'convergence_state' in summary


def test_pca_normalized_factors_sum() -> None:
    """Test that normalized PCA factors sum to approximately 1."""
    summary = pca_convergence_analysis.compute_pca_summary()
    
    normalized = summary['normalized_factors']
    total = sum(normalized.values())
    
    # Should sum to approximately 1 (within floating point tolerance)
    assert pytest.approx(total, abs=0.01) == 1.0


def test_pca_dominant_factor() -> None:
    """Test that dominant factor is correctly identified."""
    summary = pca_convergence_analysis.compute_pca_summary()
    
    # Dominant factor should be the one with highest value
    factors = pca_convergence_analysis.PCA_FACTORS
    expected_dominant = max(factors, key=factors.get)
    
    assert summary['dominant_factor'] == expected_dominant


def test_build_execution_summary_structure() -> None:
    """Test that build_execution_summary returns expected structure."""
    # Reset STATUS for clean test
    runtime_control_center.STATUS = {'SUCCESS': [], 'FAILED': []}
    
    summary = runtime_control_center.build_execution_summary()
    
    # Check required keys
    assert 'timestamp' in summary
    assert 'executed' in summary
    assert 'failed' in summary
    assert 'success_rate' in summary
    assert 'runtime_state' in summary


def test_success_rate_calculation() -> None:
    """Test that success rate is calculated correctly."""
    # Reset and set up test data
    runtime_control_center.STATUS = {
        'SUCCESS': ['script1.py', 'script2.py'],
        'FAILED': []
    }
    
    # Mock PIPELINE_STEPS to have 4 items
    original_steps = runtime_control_center.PIPELINE_STEPS
    
    summary = runtime_control_center.build_execution_summary()
    
    # With 2 successes out of 4 total, success rate should be 0.5
    expected_rate = 2 / len(original_steps)
    assert summary['success_rate'] == pytest.approx(expected_rate, abs=0.01)


def test_runtime_state_fully_operational() -> None:
    """Test that runtime state is FULLY_OPERATIONAL when all succeed."""
    # Set all pipelines as successful
    runtime_control_center.STATUS = {
        'SUCCESS': list(runtime_control_center.PIPELINE_STEPS),
        'FAILED': []
    }
    
    summary = runtime_control_center.build_execution_summary()
    
    assert summary['runtime_state'] == 'FULLY_OPERATIONAL'
    assert summary['success_rate'] == 1.0


def test_runtime_state_failed() -> None:
    """Test that runtime state is FAILED when all fail."""
    runtime_control_center.STATUS = {
        'SUCCESS': [],
        'FAILED': list(runtime_control_center.PIPELINE_STEPS)
    }
    
    summary = runtime_control_center.build_execution_summary()
    
    assert summary['runtime_state'] == 'FAILED'
    assert summary['success_rate'] == 0.0


def test_runtime_state_partial() -> None:
    """Test that runtime state is PARTIAL_OPERATIONAL for partial success."""
    runtime_control_center.STATUS = {
        'SUCCESS': [runtime_control_center.PIPELINE_STEPS[0]],
        'FAILED': runtime_control_center.PIPELINE_STEPS[1:]
    }
    
    summary = runtime_control_center.build_execution_summary()
    
    assert summary['runtime_state'] == 'PARTIAL_OPERATIONAL'
    assert 0 < summary['success_rate'] < 1


def test_empty_pipeline_edge_case() -> None:
    """Test handling of empty pipeline list."""
    # Temporarily replace PIPELINE_STEPS
    original_steps = runtime_control_center.PIPELINE_STEPS
    runtime_control_center.PIPELINE_STEPS = []
    runtime_control_center.STATUS = {'SUCCESS': [], 'FAILED': []}
    
    summary = runtime_control_center.build_execution_summary()
    
    assert summary['runtime_state'] == 'NO_PIPELINES'
    assert summary['success_rate'] == 0.0
    
    # Restore original
    runtime_control_center.PIPELINE_STEPS = original_steps


def test_timestamp_is_timezone_aware() -> None:
    """Test that timestamps are timezone-aware UTC."""
    runtime_control_center.STATUS = {'SUCCESS': [], 'FAILED': []}
    
    summary = runtime_control_center.build_execution_summary()
    
    # Timezone-aware timestamps should end with +00:00 or Z
    timestamp = summary['timestamp']
    assert '+' in timestamp or timestamp.endswith('Z')
