from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _load_module():
    path = ROOT / "tools" / "rex_lookup.py"
    spec = importlib.util.spec_from_file_location("rex_lookup", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _yaml(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def test_rex_taxonomy_has_control_lifecycle_and_required_fields():
    taxonomy = _yaml("federation/rex/GLOBAL_REX_TAXONOMY_v1.yaml")
    assert taxonomy["lifecycle_phase"] == "DMAIC_CONTROL"
    required = set(taxonomy["rex_record_required_fields"])
    assert {"rex_id", "signature", "severity_stars", "frequency", "recurrence"} <= required
    assert {"repair_method", "verification", "control_status", "lesson"} <= required


def test_seed_ledger_records_are_well_formed():
    taxonomy = _yaml("federation/rex/GLOBAL_REX_TAXONOMY_v1.yaml")
    ledger = _yaml("federation/rex/GLOBAL_REX_LEDGER_v1.yaml")
    required = set(taxonomy["rex_record_required_fields"])
    assert ledger["records"]
    for record in ledger["records"]:
        assert required <= set(record)
        stars = int(record["severity_stars"])
        assert 1 <= stars <= 5
        assert int(record["frequency"]["observed_count"]) >= 1
        assert record["recurrence"] in taxonomy["recurrence_classes"]
        assert record["control_status"] in taxonomy["control_status"]


def test_w112_summary_matches_seed_records():
    ledger = _yaml("federation/rex/GLOBAL_REX_LEDGER_v1.yaml")
    records = ledger["records"]
    assert ledger["summary"]["record_count"] == len(records) == 6
    assert sum(1 for record in records if record["severity_stars"] == 5) == 2
    assert sum(1 for record in records if record["control_status"] == "DEFERRED") == 1


def test_rex_lookup_filters_repo_stars_recurrence_and_query():
    module = _load_module()
    records = module.load_records()
    child = module.filter_records(records, repo="cryoplant-project")
    assert {r["rex_id"] for r in child} >= {"REX-W112-001", "REX-W112-006"}
    five = module.filter_records(records, stars=5)
    assert {r["rex_id"] for r in five} == {"REX-W112-001", "REX-W112-006"}
    recurring = module.filter_records(records, recurring=True)
    assert all(r["recurrence"] != "UNIQUE" for r in recurring)
    semantic = module.filter_records(records, query="semantic_readiness")
    assert [r["rex_id"] for r in semantic] == ["REX-W112-002"]


def test_rex_rank_prefers_severity_then_observed_count():
    module = _load_module()
    ranked = module.rank_records(module.load_records())
    assert ranked[0]["severity_stars"] == 5
    assert ranked[0]["frequency"]["observed_count"] >= ranked[1]["frequency"]["observed_count"]


def test_glob_rex_subresolver_points_to_canonical_rex_sources():
    lookup = _yaml("federation/rex/GLOB_REX_LOOKUP_v1.yaml")
    assert lookup["parent"] == "GLOB.yaml"
    assert lookup["role"] == "DMAIC_CONTROL_REX_SUBRESOLVER"
    assert lookup["sources"]["taxonomy"] == "federation/rex/GLOBAL_REX_TAXONOMY_v1.yaml"
    assert lookup["sources"]["ledger"] == "federation/rex/GLOBAL_REX_LEDGER_v1.yaml"
