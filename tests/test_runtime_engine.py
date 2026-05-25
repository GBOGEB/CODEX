"""Unit tests for runtime_engine modules."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

# Import the modules under test
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime_engine.telemetry_pipeline import (
    build_payload,
    compute_wave_velocity,
    compute_kpi_score,
    WAVES,
    KPI_WEIGHTS,
    DMAIC,
)
from runtime_engine.plotly_wave_dashboard import render_dashboard, TELEMETRY


def test_compute_wave_velocity_returns_list():
    """Test that compute_wave_velocity returns a list of velocity deltas."""
    velocities = compute_wave_velocity()
    
    assert isinstance(velocities, list)
    assert len(velocities) == len(WAVES) - 1
    assert all(isinstance(v, (int, float)) for v in velocities)


def test_compute_wave_velocity_calculates_deltas_correctly():
    """Test that velocity deltas are calculated as score differences."""
    velocities = compute_wave_velocity()
    
    # First delta should be W2 score - W1 score = 62 - 48 = 14
    assert velocities[0] == 14
    # Second delta should be W3 score - W2 score = 74 - 62 = 12
    assert velocities[1] == 12


def test_compute_kpi_score_returns_float():
    """Test that compute_kpi_score returns a numeric value."""
    score = compute_kpi_score()
    
    assert isinstance(score, float)
    assert score > 0


def test_compute_kpi_score_uses_weights():
    """Test that KPI score calculation uses the defined weights."""
    score = compute_kpi_score()
    
    # The score should be a weighted sum, so it should be within reasonable bounds
    # Given the weights sum to 1.0 and individual scores range from 38-72,
    # the result should be between 38 and 72
    assert 38 <= score <= 72


def test_build_payload_returns_dict():
    """Test that build_payload returns a dictionary with expected structure."""
    payload = build_payload()
    
    assert isinstance(payload, dict)
    assert 'waves' in payload
    assert 'telemetry' in payload
    assert 'claimed_vs_actual' in payload


def test_build_payload_waves_structure():
    """Test that the waves section has the correct structure."""
    payload = build_payload()
    
    assert payload['waves'] == WAVES
    assert len(payload['waves']) == 7
    
    for wave in payload['waves']:
        assert 'wave' in wave
        assert 'completion' in wave
        assert 'score' in wave


def test_build_payload_telemetry_structure():
    """Test that the telemetry section has all required fields."""
    payload = build_payload()
    telemetry = payload['telemetry']
    
    assert 'average_completion' in telemetry
    assert 'average_score' in telemetry
    assert 'wave_velocity' in telemetry
    assert 'velocity_average' in telemetry
    assert 'kpi_score' in telemetry
    assert 'dmaic' in telemetry
    assert 'pca' in telemetry


def test_build_payload_telemetry_numeric_values():
    """Test that telemetry numeric values are calculated correctly."""
    payload = build_payload()
    telemetry = payload['telemetry']
    
    # Check that averages are reasonable
    assert isinstance(telemetry['average_completion'], (int, float))
    assert isinstance(telemetry['average_score'], (int, float))
    assert isinstance(telemetry['velocity_average'], (int, float))
    assert isinstance(telemetry['kpi_score'], (int, float))
    
    # Verify average_completion is within expected range
    assert 0 <= telemetry['average_completion'] <= 100
    
    # Verify average_score is within expected range
    assert 0 <= telemetry['average_score'] <= 100


def test_build_payload_dmaic_structure():
    """Test that DMAIC data is included correctly."""
    payload = build_payload()
    dmaic = payload['telemetry']['dmaic']
    
    assert dmaic == DMAIC
    assert 'define' in dmaic
    assert 'measure' in dmaic
    assert 'analyze' in dmaic
    assert 'improve' in dmaic
    assert 'control' in dmaic


def test_build_payload_pca_structure():
    """Test that PCA factors are included with correct structure."""
    payload = build_payload()
    pca = payload['telemetry']['pca']
    
    assert 'factor_1_governance' in pca
    assert 'factor_2_validation' in pca
    assert 'factor_3_topology' in pca
    assert 'factor_4_runtime' in pca
    assert 'factor_5_entropy' in pca
    
    # All PCA factors should be between 0 and 1
    for factor_value in pca.values():
        assert 0 <= factor_value <= 1


def test_build_payload_claimed_vs_actual_structure():
    """Test that claimed_vs_actual section has expected structure."""
    payload = build_payload()
    claimed_vs_actual = payload['claimed_vs_actual']
    
    assert 'claimed' in claimed_vs_actual
    assert 'actual' in claimed_vs_actual
    assert 'missing_execution' in claimed_vs_actual
    
    assert isinstance(claimed_vs_actual['claimed'], list)
    assert isinstance(claimed_vs_actual['actual'], list)
    assert isinstance(claimed_vs_actual['missing_execution'], list)


def test_build_payload_json_serializable():
    """Test that the payload can be serialized to JSON."""
    payload = build_payload()
    
    # This should not raise an exception
    json_str = json.dumps(payload, indent=2)
    
    # Verify we can deserialize it back
    deserialized = json.loads(json_str)
    assert deserialized == payload


def test_render_dashboard_fails_without_telemetry(tmp_path):
    """Test that render_dashboard raises FileNotFoundError when telemetry is missing."""
    # This test verifies the error handling behavior
    # We can't easily test the actual rendering without creating the telemetry file
    # but we can verify the error message is helpful
    
    if not TELEMETRY.exists():
        with pytest.raises(FileNotFoundError) as exc_info:
            render_dashboard()
        
        assert 'telemetry_pipeline.py' in str(exc_info.value)
        assert str(TELEMETRY) in str(exc_info.value)
