from __future__ import annotations

import builtins
import sys
import types

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


def test_build_coolprop_state_grid_report_returns_unavailable_rows_when_coolprop_missing(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("CoolProp"):
            raise ModuleNotFoundError("No module named 'CoolProp'")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    rows = build_coolprop_state_grid_report()

    assert len(rows) == 8
    assert {row["status"] for row in rows} == {"backend_unavailable"}
    assert {row["available"] for row in rows} == {False}
    assert all(row["notes"] == "CoolProp unavailable: optional backend not installed" for row in rows)


def test_build_coolprop_state_grid_report_marks_state_errors_unavailable(monkeypatch):
    fake_cp = types.ModuleType("CoolProp.CoolProp")

    def fake_props_si(*args):
        raise ValueError("simulated CoolProp failure")

    fake_cp.PropsSI = fake_props_si
    fake_package = types.ModuleType("CoolProp")
    fake_package.CoolProp = fake_cp

    monkeypatch.setitem(sys.modules, "CoolProp", fake_package)
    monkeypatch.setitem(sys.modules, "CoolProp.CoolProp", fake_cp)

    rows = build_coolprop_state_grid_report()

    assert len(rows) == 8
    assert {row["status"] for row in rows} == {"state_error"}
    assert {row["available"] for row in rows} == {False}
    assert all(row["enthalpy_j_kg"] is None for row in rows)
    assert all(row["notes"] == "simulated CoolProp failure" for row in rows)
