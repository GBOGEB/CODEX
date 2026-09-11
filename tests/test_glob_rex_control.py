from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_module():
    path = ROOT / "tools" / "glob_lookup.py"
    spec = importlib.util.spec_from_file_location("glob_lookup", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_glob_menu_exposes_rex_control_namespace():
    module = _load_module()
    glob = module.load_glob()
    menu = module.menu(glob)
    assert menu["rex"]["lifecycle_phase"] == "DMAIC_CONTROL"
    assert menu["rex"]["ledger"].endswith("GLOBAL_REX_LEDGER_v1.yaml")


def test_glob_can_resolve_specific_rex():
    module = _load_module()
    glob = module.load_glob()
    record = module.rex_record(glob, "REX-W112-006")
    assert record["identity"] == "REX-W112-006"
    assert record["severity_stars"] == 5
    assert record["observed_count"] == 8
    assert record["recurrence"] == "CROSS_WORKFLOW_RECURRING"
    assert record["action_moniker"] == "RUNTIME"


def test_glob_natural_ask_returns_repo_rex():
    module = _load_module()
    glob = module.load_glob()
    group = module.ask_record(glob, "show REX for cryoplant-project")
    ids = {record["rex_id"] for record in group["records"]}
    assert "REX-W112-006" in ids
    assert group["kind"] == "rex_group"


def test_glob_natural_ask_returns_five_star_rex():
    module = _load_module()
    glob = module.load_glob()
    group = module.ask_record(glob, "show five-star REX")
    assert {record["rex_id"] for record in group["records"]} == {
        "REX-W112-001",
        "REX-W112-006",
    }


def test_glob_top_frequency_ask_ranks_namespace_collision_first():
    module = _load_module()
    glob = module.load_glob()
    group = module.ask_record(glob, "what failed most often in W112?")
    assert group["records"][0]["rex_id"] == "REX-W112-001"
    assert group["records"][0]["count"] == 13


def test_glob_open_control_blockers_only_returns_deferred_or_open():
    module = _load_module()
    glob = module.load_glob()
    group = module.ask_record(glob, "show open Control-phase blockers")
    assert [record["rex_id"] for record in group["records"]] == ["REX-W112-006"]
