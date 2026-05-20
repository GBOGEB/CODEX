from types import SimpleNamespace

import pytest

from gistau_ch15.properties.refprop_adapter import REFPROPAdapter


class _FakeRefpropLibrary:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, str, float, float]] = []

    def REFPROPdll(self, fluid, inputs, output, i_units, i_mass, i_flag, x1, x2, z):
        self.calls.append((fluid, inputs, output, float(x1), float(x2)))
        table = {
            ("TP", "W"): 4.0,
            ("TP", "H"): 1000.0,
            ("TP", "S"): 10.0,
            ("TP", "D"): 2.0,
            ("TP", "Q"): -999.0,
            ("PH", "T"): 250.0,
            ("PH", "S"): 8.0,
            ("PH", "D"): 1.5,
            ("PH", "Q"): 0.25,
            ("PS", "T"): 240.0,
            ("PS", "H"): 900.0,
            ("PS", "D"): 1.2,
            ("PS", "Q"): 2.0,
            ("TQ", "P"): 50.0,
            ("TQ", "D"): 120.0 if x2 == 0.0 else 0.8,
            ("PQ", "T"): 2.0,
            ("PQ", "D"): 110.0 if x2 == 0.0 else 0.5,
        }
        return SimpleNamespace(Output=[table[(inputs, output)]], ierr=0, herr="")


def _build_adapter(monkeypatch: pytest.MonkeyPatch) -> tuple[REFPROPAdapter, _FakeRefpropLibrary]:
    fake = _FakeRefpropLibrary()
    monkeypatch.setattr(REFPROPAdapter, "_load", lambda self: fake)
    adapter = REFPROPAdapter()
    return adapter, fake


def test_refprop_adapter_state_pt_uses_kpa_and_converts_units(monkeypatch: pytest.MonkeyPatch):
    adapter, fake = _build_adapter(monkeypatch)

    state = adapter.state_pt("Helium", 101.325, 300.0)

    assert state.enthalpy_j_kg == pytest.approx(250000.0)
    assert state.entropy_j_kgk == pytest.approx(2500.0)
    assert state.density_kg_m3 == pytest.approx(8.0)
    assert ("HELIUM", "TP", "H", 300.0, 101.325) in fake.calls


def test_refprop_adapter_state_ph_state_ps_and_saturation_convert_units(
    monkeypatch: pytest.MonkeyPatch,
):
    adapter, fake = _build_adapter(monkeypatch)

    state_ph = adapter.state_ph("Helium", 500.0, 250000.0)
    state_ps = adapter.state_ps("Helium", 500.0, 2500.0)
    sat_t = adapter.saturation_t("Helium", 2.0)
    sat_p = adapter.saturation_p("Helium", 3.0)

    assert state_ph.temperature_k == pytest.approx(250.0)
    assert state_ph.entropy_j_kgk == pytest.approx(2000.0)
    assert state_ph.density_kg_m3 == pytest.approx(6.0)
    assert state_ph.quality == pytest.approx(0.25)
    assert state_ps.enthalpy_j_kg == pytest.approx(225000.0)
    assert state_ps.density_kg_m3 == pytest.approx(4.8)
    assert state_ps.quality is None
    assert sat_t.liquid_density_kg_m3 == pytest.approx(480.0)
    assert sat_t.vapor_density_kg_m3 == pytest.approx(3.2)
    assert sat_p.liquid_density_kg_m3 == pytest.approx(440.0)
    assert sat_p.vapor_density_kg_m3 == pytest.approx(2.0)
    assert ("HELIUM", "PH", "T", 500.0, 1000.0) in fake.calls
    assert ("HELIUM", "PS", "T", 500.0, 10.0) in fake.calls
