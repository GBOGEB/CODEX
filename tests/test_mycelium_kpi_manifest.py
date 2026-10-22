import importlib.util
import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("measure_mycelium_kpis", ROOT / "scripts" / "measure_mycelium_kpis.py")
kpis = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kpis)

MANIFEST = yaml.safe_load(kpis.MANIFEST.read_text(encoding="utf-8"))
SELECTOR_KEYS = ("numerator", "denominator", "status_from")


def _selectors(entry):
    for key in SELECTOR_KEYS + ("left", "right"):
        if key in entry:
            yield entry[key]


def _kpi(**overrides):
    base = {
        "id": "T-01",
        "dimension": "execution",
        "name": "test",
        "unit": "pct",
        "formula": {"kind": "ratio_pct"},
        "numerator": {"source": "s", "path": "num"},
        "denominator": {"source": "s", "path": "den"},
        "direction": "higher_is_better",
        "target": 100,
        "bands": {"green": 80, "amber": 50},
    }
    base.update(overrides)
    return base


def test_manifest_ids_are_unique_and_dimensions_declared():
    ids = [k["id"] for k in MANIFEST["kpis"]] + [c["id"] for c in MANIFEST["checks"]]
    assert len(ids) == len(set(ids))
    for kpi in MANIFEST["kpis"]:
        assert kpi["dimension"] in MANIFEST["dimensions"], kpi["id"]
        assert kpi["purpose"], kpi["id"]
        assert kpi["formula"]["kind"] in {"value", "ratio", "ratio_pct"}, kpi["id"]
        if kpi["formula"]["kind"] != "value":
            assert "denominator" in kpi, kpi["id"]


def test_every_dimension_has_question_decision_and_kpis():
    used = {k["dimension"] for k in MANIFEST["kpis"]}
    for name, dim in MANIFEST["dimensions"].items():
        assert dim["question"] and dim["decision"], name
        assert name in used, name


def test_bands_match_direction():
    for kpi in MANIFEST["kpis"]:
        if kpi["direction"] == "info":
            assert "bands" not in kpi, kpi["id"]
            continue
        bands = kpi["bands"]
        assert "target" in kpi, kpi["id"]
        if kpi["direction"] == "higher_is_better":
            assert bands["green"] >= bands["amber"], kpi["id"]
        else:
            assert kpi["direction"] == "lower_is_better", kpi["id"]
            assert bands["green"] <= bands["amber"], kpi["id"]


def test_selectors_reference_declared_sources_and_unlock_targets_exist():
    kpi_ids = {k["id"] for k in MANIFEST["kpis"]}
    for entry in MANIFEST["kpis"] + MANIFEST["checks"]:
        for selector in _selectors(entry):
            assert selector["source"] in MANIFEST["sources"], entry["id"]
    assert set(MANIFEST["unlock"]) <= kpi_ids


def test_declared_source_files_exist():
    for alias, spec in MANIFEST["sources"].items():
        if spec.get("generator"):
            continue
        assert (ROOT / spec["path"]).is_file(), alias


def test_live_measurement_has_no_binding_errors_and_is_deterministic():
    first = kpis.measure()
    second = kpis.measure()
    assert kpis.render(first) == kpis.render(second)
    assert first["summary"]["overall"]["binding_errors"] == 0
    assert first["composite_score"] is None
    assert {r["id"] for r in first["kpis"]} == {k["id"] for k in MANIFEST["kpis"]}


def test_committed_report_covers_current_manifest():
    committed = json.loads(kpis.OUTPUT.read_text(encoding="utf-8"))
    assert [r["id"] for r in committed["kpis"]] == [k["id"] for k in MANIFEST["kpis"]]
    assert [c["id"] for c in committed["checks"]] == [c["id"] for c in MANIFEST["checks"]]


def test_ratio_and_band():
    row = kpis.evaluate_kpi(_kpi(), {"s": {"num": 3, "den": 4}}, {})
    assert row["status"] == "MEASURED"
    assert row["value"] == 75.0
    assert row["band"] == "AMBER"


@pytest.mark.parametrize(
    ("sources", "reason"),
    [
        ({}, "not available"),
        ({"s": {"num": 1, "den": 0}}, "denominator is zero"),
        ({"s": {"num": {"status": "WITHHELD"}, "den": 2}}, "WITHHELD upstream"),
        ({"s": {"num": None, "den": 2}}, "null upstream"),
    ],
)
def test_withheld_never_defaults_to_a_number(sources, reason):
    row = kpis.evaluate_kpi(_kpi(), sources, {"T-01": "do the thing"})
    assert row["status"] == "WITHHELD"
    assert row["value"] is None
    assert reason in row["reason"]
    assert row["unlock"] == "do the thing"


def test_upstream_status_withholds_value():
    kpi = _kpi(
        formula={"kind": "value"},
        numerator={"source": "s", "path": "x/value"},
        status_from={"source": "s", "path": "x/status"},
        direction="info",
    )
    row = kpis.evaluate_kpi(kpi, {"s": {"x": {"status": "WITHHELD", "value": 5}}}, {})
    assert row["status"] == "WITHHELD"


def test_missing_key_in_present_source_is_a_binding_error():
    row = kpis.evaluate_kpi(_kpi(), {"s": {"num": 1}}, {})
    assert row["status"] == "BINDING_ERROR"


def test_lower_is_better_bands():
    kpi = _kpi(direction="lower_is_better", bands={"green": 0, "amber": 3})
    assert kpis.band(0, kpi) == "GREEN"
    assert kpis.band(3, kpi) == "AMBER"
    assert kpis.band(4, kpi) == "RED"
    assert kpis.band(4, _kpi(direction="info")) == "INFO"


def test_wildcard_aggregates_skip_nodes_without_the_key():
    sources = {"s": {"nodes": {"a": {"logs": {"status": "MEASURED"}}, "b": {}, "c": {"logs": {"status": "WITHHELD"}}}}}
    measured = kpis.select(
        sources,
        {"source": "s", "path": "nodes/*/logs/status", "agg": "count_where", "where": {"op": "eq", "value": "MEASURED"}},
    )
    assert measured == 1
    assert kpis.select(sources, {"source": "s", "path": "nodes", "agg": "len"}) == 3
    assert kpis.select(sources, {"source": "s", "path": "nodes/*/logs/status", "agg": "distribution"}) == {
        "MEASURED": 1,
        "WITHHELD": 1,
    }


def test_check_reports_disagreement_instead_of_reconciling():
    check = {"id": "C", "name": "c", "left": {"source": "s", "path": "a"}, "right": {"source": "s", "path": "b"}}
    assert kpis.evaluate_check(check, {"s": {"a": 1, "b": 2}})["status"] == "FAIL"
    assert kpis.evaluate_check(check, {"s": {"a": 2, "b": 2}})["status"] == "PASS"
    assert kpis.evaluate_check(check, {})["status"] == "WITHHELD"


def test_write_uses_lf_and_check_detects_staleness(tmp_path, monkeypatch):
    out = tmp_path / "report.json"
    monkeypatch.setattr(kpis, "OUTPUT", out)
    assert kpis.main([]) == 0
    assert b"\r\n" not in out.read_bytes()
    assert kpis.main(["--check"]) == 0
    out.write_text("{}\n", encoding="utf-8", newline="\n")
    assert kpis.main(["--check"]) == 1
