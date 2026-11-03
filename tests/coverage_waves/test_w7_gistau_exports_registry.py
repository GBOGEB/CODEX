"""Coverage wave 7 (L3): GISTAU ch15 export helpers, CoolProp adapter (against a
fake CoolProp), backend registry checker and executable-value consumer.

Every default output path that points into the repo is redirected or patched.
"""
from __future__ import annotations

import hashlib
import json
import sys
import types

import pytest

from gistau_ch15.properties import (
    coolprop_adapter,
    export_coolprop_state_grid,
    json_export,
)
from gistau_ch15.properties.errors import PropertyBackendUnavailable
from gistau_ch15.visualization import (
    overlay_artifact_manifest,
    pages_artifact_refresh,
    saturation_sampling,
    trace_json_export,
    workbook_export_bundle,
)
from tests.coverage_waves._loader import load

REGISTRY = "scripts/check_backend_registry.py"
CONSUME = "scripts/consume_executable_value_report.py"


# ---------------------------------------------------------------- saturation + workbook + json export
def test_fallback_saturation_curve_is_monotone():
    c = saturation_sampling.FallbackSaturationSampler().sample()
    assert c.temperature_liquid == c.temperature_vapor
    assert c.entropy_liquid == sorted(c.entropy_liquid)
    assert c.entropy_vapor == sorted(c.entropy_vapor, reverse=True)
    assert all(lo < hi for lo, hi in zip(c.entropy_liquid, c.entropy_vapor))


def test_workbook_bundle_writes_manifest(tmp_path):
    (path,) = workbook_export_bundle.WorkbookExportBundle().export(tmp_path / "wb")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["status"] == "scaffold" and len(data["artifacts"]) == 3


def test_json_export_writer(tmp_path):
    w = json_export.JsonExportWriter(str(tmp_path / "out"))
    paths = w.write_backend_reports([{"b": 2, "a": 1}], {"n": 1}, {"m": []})
    assert [p.name for p in paths] == ["backend_comparison_report.json", "backend_delta_summary.json",
                                       "backend_heatmap_matrix.json"]
    assert paths[0].read_text(encoding="utf-8").index('"a"') < paths[0].read_text(encoding="utf-8").index('"b"')


# ---------------------------------------------------------------- trace export + pages refresh
def test_trace_export_payload(tmp_path):
    path = trace_json_export.PlotlyTraceJSONExporter().export(tmp_path / "d" / "t.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert set(payload) == {"saturation", "agreement"}


def _bad_agreement(monkeypatch, values, tuples, backends):
    class Fake:
        def build(self):
            return types.SimpleNamespace(values=values, tuples=tuples, backends=backends)

    monkeypatch.setattr(trace_json_export, "BackendAgreementBuilder", Fake)


def test_trace_export_rejects_row_mismatch(tmp_path, monkeypatch):
    _bad_agreement(monkeypatch, [[1]], ["t1", "t2"], ["b"])
    with pytest.raises(ValueError, match="rows must align"):
        trace_json_export.PlotlyTraceJSONExporter().export(tmp_path / "x.json")


def test_trace_export_rejects_column_mismatch(tmp_path, monkeypatch):
    _bad_agreement(monkeypatch, [[1, 2]], ["t1"], ["b"])
    with pytest.raises(ValueError, match="columns must align"):
        trace_json_export.PlotlyTraceJSONExporter().export(tmp_path / "x.json")


def test_pages_refresh_with_explicit_outputs(tmp_path):
    out = pages_artifact_refresh.PagesArtifactRefresh().refresh(
        overlay_output=tmp_path / "o.json", trace_output=tmp_path / "t.json")
    assert [p.name for p in out] == ["o.json", "t.json"] and all(p.is_file() for p in out)


def test_pages_refresh_defaults_use_default_writers(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(pages_artifact_refresh, "regenerate", lambda *a: calls.append(("overlay", a)) or "o")

    class Exporter:
        def export(self, *a):
            calls.append(("trace", a))
            return "t"

    monkeypatch.setattr(pages_artifact_refresh, "PlotlyTraceJSONExporter", Exporter)
    assert pages_artifact_refresh.PagesArtifactRefresh().refresh() == ["o", "t"]
    assert calls == [("overlay", ()), ("trace", ())]


# ---------------------------------------------------------------- overlay manifest
def test_overlay_manifest_records_and_write(tmp_path):
    a = tmp_path / "b_art.json"
    a.write_text("{}", encoding="utf-8")
    outside = tmp_path.parent / f"{tmp_path.name}_outside.json"
    outside.write_text("xyz", encoding="utf-8")
    try:
        builder = overlay_artifact_manifest.OverlayArtifactManifestBuilder()
        recs = builder.build_records([a, outside], root=tmp_path)
        by_key = {r.key: r for r in recs}
        assert by_key["b_art"].path == "b_art.json"
        assert by_key["b_art"].sha256 == hashlib.sha256(b"{}").hexdigest() and by_key["b_art"].size_bytes == 2
        assert by_key[outside.stem].path == outside.resolve().as_posix()
        path = builder.write_manifest([a], tmp_path / "m" / "manifest.json", root=tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["artifact_count"] == 1 and data["artifacts"][0]["key"] == "b_art"
    finally:
        outside.unlink()


def test_overlay_manifest_defaults_to_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "x.json").write_text("1", encoding="utf-8")
    (rec,) = overlay_artifact_manifest.OverlayArtifactManifestBuilder().build_records([tmp_path / "x.json"])
    assert rec.path == "x.json"


# ---------------------------------------------------------------- coolprop state-grid export
def test_write_coolprop_state_grid_report(tmp_path, monkeypatch, capsys):
    rows = export_coolprop_state_grid.write_coolprop_state_grid_report(tmp_path / "g" / "r.json")
    assert json.loads((tmp_path / "g" / "r.json").read_text(encoding="utf-8")) == rows
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(export_coolprop_state_grid, "build_coolprop_state_grid_report",
                        lambda: [{"available": True}, {"available": False}])
    monkeypatch.setattr(export_coolprop_state_grid.write_coolprop_state_grid_report, "__defaults__",
                        (tmp_path / "docs" / "grid.json",))
    export_coolprop_state_grid.main()
    assert "wrote 2 CoolProp state-grid rows (1 flagged available" in capsys.readouterr().out


# ---------------------------------------------------------------- coolprop adapter (fake backend)
class _FakeCP:
    def __init__(self, q=0.5):
        self.q = q
        self.calls = []

    def PropsSI(self, out, k1, v1, k2, v2, fluid):
        self.calls.append((out, k1, v1, k2, v2, fluid))
        if out == "Q":
            return self.q
        return {"H": 1000.0, "S": 50.0, "D": 125.0, "T": 4.2, "P": 100000.0}[out]


@pytest.fixture
def fake_coolprop(monkeypatch):
    cp = _FakeCP()
    inner = types.ModuleType("CoolProp.CoolProp")
    inner.PropsSI = cp.PropsSI
    pkg = types.ModuleType("CoolProp")
    pkg.CoolProp = inner
    monkeypatch.setitem(sys.modules, "CoolProp", pkg)
    monkeypatch.setitem(sys.modules, "CoolProp.CoolProp", inner)
    return cp


def test_coolprop_adapter_unavailable(monkeypatch):
    monkeypatch.setitem(sys.modules, "CoolProp", None)
    monkeypatch.setitem(sys.modules, "CoolProp.CoolProp", None)
    with pytest.raises(PropertyBackendUnavailable):
        coolprop_adapter.CoolPropAdapter()


def test_coolprop_adapter_states(fake_coolprop):
    ad = coolprop_adapter.CoolPropAdapter()
    s = ad.state_pt("Helium", 100.0, 4.5)
    assert (s.enthalpy_j_kg, s.entropy_j_kgk, s.density_kg_m3, s.quality) == (1000.0, 50.0, 125.0, None)
    assert fake_coolprop.calls[0] == ("H", "P", 100000.0, "T", 4.5, "Helium")
    ph = ad.state_ph("Helium", 100.0, 900.0)
    assert ph.temperature_k == 4.2 and ph.quality == 0.5 and ph.enthalpy_j_kg == 900.0
    ps = ad.state_ps("Helium", 100.0, 40.0)
    assert ps.enthalpy_j_kg == 1000.0 and ps.entropy_j_kgk == 40.0 and ps.quality == 0.5
    sat_t = ad.saturation_t("Helium", 4.2)
    assert sat_t.pressure_kpa == 100.0 and sat_t.liquid_density_kg_m3 == 125.0
    sat_p = ad.saturation_p("Helium", 100.0)
    assert sat_p.temperature_k == 4.2
    assert ad.quality_ph("Helium", 100.0, 900.0) == 0.5
    assert ad.entropy_tq("Helium", 4.2, 0.3) == 50.0


@pytest.mark.parametrize("q", [-1.0, 2.0])
def test_coolprop_adapter_single_phase_quality_is_none(fake_coolprop, q):
    fake_coolprop.q = q
    ad = coolprop_adapter.CoolPropAdapter()
    assert ad.quality_ph("He", 1.0, 1.0) is None
    assert ad.state_ph("He", 1.0, 1.0).quality is None
    assert ad.state_ps("He", 1.0, 1.0).quality is None


# ---------------------------------------------------------------- backend registry checker
def _registry(tmp_path, text):
    p = tmp_path / "registry.yaml"
    p.write_text(text, encoding="utf-8")
    return p


GOOD_FIELDS = "description: d\n    version: '1'\n    capabilities: []"


def test_registry_passes(tmp_path, capsys):
    m = load(REGISTRY)
    reg = _registry(tmp_path, f"backends:\n  json:\n    {GOOD_FIELDS}\n    available: true\n"
                              f"    entrypoint: json.JSONDecoder\n  off:\n    {GOOD_FIELDS}\n"
                              f"    available: false\n    entrypoint: ''\n")
    assert m.main(["--registry", str(reg)]) == 0
    assert "PASS: backend registry valid" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("text", "needle"),
    [
        (None, "registry not found"),
        ("", "no backends defined"),
        ("backends:\n  a: {available: false}\n", "missing required fields"),
        ("backends:\n  a: {available: false}\n", "no backend has available=true"),
        ("backends:\n  a: {available: true, entrypoint: ''}\n", "entrypoint is empty"),
        ("backends:\n  a: {available: true, entrypoint: nodots}\n", "must be 'module.ClassName'"),
        ("backends:\n  a: {available: true, entrypoint: json.NoSuchClass}\n", "class 'NoSuchClass' not found"),
        ("backends:\n  a: {available: true, entrypoint: no_such_mod_l3.Cls}\n", "cannot import"),
    ],
)
def test_registry_failures(tmp_path, capsys, text, needle):
    m = load(REGISTRY)
    reg = tmp_path / "missing.yaml" if text is None else _registry(tmp_path, text)
    assert m.validate_registry(reg) == 1
    assert needle in capsys.readouterr().err


def test_registry_default_repo_file_is_valid():
    m = load(REGISTRY)
    assert m.main([]) == 0


# ---------------------------------------------------------------- executable value consumer
def _report(unregistered, orphans):
    return {"inventory": {"unregistered_asset_count": unregistered, "global_integration_complete": False},
            "control": {"registration_debt_queue_required": unregistered > 0,
                        "tested_orphan_queue_required": bool(orphans)},
            "tested_orphans": orphans}


@pytest.mark.parametrize(
    ("unreg", "orphans", "action"),
    [(3, [], "CLASSIFY_EXECUTABLE_REGISTRATION_DEBT"), (0, ["t"], "CLASSIFY_TESTED_ORPHANS"),
     (0, [], "PRESERVE_CONTROL")],
)
def test_consume_next_action(tmp_path, unreg, orphans, action):
    m = load(CONSUME)
    rep = tmp_path / "r.json"
    rep.write_text(json.dumps(_report(unreg, orphans)), encoding="utf-8")
    out = tmp_path / "obs.json"
    obs = m.consume(rep, out)
    assert obs["next_control_action"] == action
    assert obs["tested_orphan_count"] == len(orphans) and obs["authority_transfer"] is False
    assert json.loads(out.read_text(encoding="utf-8")) == obs
    assert b"\r\n" not in out.read_bytes()


def test_consume_main(tmp_path, monkeypatch, capsys):
    m = load(CONSUME)
    rep = tmp_path / "r.json"
    rep.write_text(json.dumps(_report(0, [])), encoding="utf-8")
    monkeypatch.setattr(m.consume, "__defaults__", (rep, tmp_path / "o.json"))
    assert m.main() == 0
    assert "PRESERVE_CONTROL / 0 unregistered / 0 tested orphans" in capsys.readouterr().out
