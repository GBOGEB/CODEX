from __future__ import annotations

from gistau_ch15.properties.coolprop_state_grid import build_coolprop_state_grid_report


def test_state_grid_rows_exist() -> None:
    rows = build_coolprop_state_grid_report()
    assert rows
    assert len(rows) >= 4


def test_state_grid_schema() -> None:
    row = build_coolprop_state_grid_report()[0]
    expected_keys = {
        "point_id",
        "region",
        "temperature_k",
        "pressure_mbar",
        "backend",
        "available",
        "enthalpy_j_kg",
        "entropy_j_kgk",
        "density_kg_m3",
        "specific_volume_m3_kg",
        "gibbs_j_kg",
        "exergy_j_kg",
        "status",
        "notes",
    }
    assert expected_keys.issubset(set(row.keys()))


def test_backend_unavailable_rows_are_explicit() -> None:
    rows = build_coolprop_state_grid_report()
    unavailable_rows = [r for r in rows if not r["available"]]
    for row in unavailable_rows:
        assert row["status"] in {"backend_unavailable", "state_error"}
