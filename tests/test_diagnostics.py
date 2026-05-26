#!/usr/bin/env python3
import pytest

from src.artstyle.cdx_engine import CdxDiagnosticsEngine


@pytest.fixture
def engine():
    return CdxDiagnosticsEngine()


def test_contrast_ratio_enforcement(engine):
    stream = engine.collect_telemetry_stream()
    assert stream["measured_wcag_contrast"] >= engine.contrast_min


def test_color_fidelity_drift(engine):
    stream = engine.collect_telemetry_stream()
    color_drift = 1.0 - stream["c_fidelity"]
    assert color_drift < 0.020


def test_progress_realism_delta_direction(engine):
    stream = engine.collect_telemetry_stream()
    delta = stream["actual_progress"] - stream["claimed_progress"]
    assert round(delta, 3) == -0.050
