from __future__ import annotations

import json
from pathlib import Path

from gistau_ch15.kernels.saturation_stub import saturation_state_stub

REQUIRED_KEYS = {
    "point_id",
    "source",
    "source_type",
    "T_K",
    "P_kPa",
    "expected_h_J_kg",
    "expected_s_J_kgK",
    "expected_rho_kg_m3",
    "expected_quality",
    "uncertainty_or_tolerance",
    "notes",
}

REQUIRED_POINT_IDS = {
    "NIST-HE-300K-1BAR",
    "NIST-HE-SAT-4P222K-1ATM",
    "GISTAU-VLP-2K-26MBAR",
    "GISTAU-SHE-4P5K-3BAR",
    "GISTAU-WE-T00-HSD-PT-002",
}

FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "gistau-ch15"
    / "data"
    / "nist_validation_points.json"
)


def _load_points() -> list[dict[str, object]]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_fixture_schema_and_required_keys() -> None:
    points = _load_points()
    assert isinstance(points, list)
    assert points

    for point in points:
        assert REQUIRED_KEYS.issubset(point)
        assert isinstance(point["point_id"], str)
        assert isinstance(point["source"], str)
        assert isinstance(point["source_type"], str)
        assert point["T_K"] > 0.0
        assert point["P_kPa"] >= 0.0
        assert point["uncertainty_or_tolerance"] >= 0.0

        quality = point["expected_quality"]
        assert quality is None or 0.0 <= quality <= 1.0


def test_required_baseline_points_present() -> None:
    point_ids = {row["point_id"] for row in _load_points()}
    assert REQUIRED_POINT_IDS.issubset(point_ids)


def test_reference_only_status_is_explicit_when_values_are_missing() -> None:
    for point in _load_points():
        missing_primary_values = all(
            point[field] is None
            for field in (
                "expected_h_J_kg",
                "expected_s_J_kgK",
                "expected_rho_kg_m3",
            )
        )
        if missing_primary_values:
            assert point["source_type"] == "reference_only"
            assert "reference-only" in str(point["notes"]).lower()


def test_fixture_paths_run_without_optional_backend_imports() -> None:
    points = _load_points()
    assert points

    sat = saturation_state_stub(temperature_k=4.222, pressure_kpa=101.325)
    assert sat.validation_status == "reference_only"
    assert "placeholder" in sat.approximation_note
