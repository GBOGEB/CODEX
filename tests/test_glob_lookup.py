from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _load_module():
    path = ROOT / "tools" / "glob_lookup.py"
    spec = importlib.util.spec_from_file_location("glob_lookup", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _yaml(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def test_status_and_action_namespaces_are_disjoint():
    glob = _yaml("GLOB.yaml")
    statuses = set(glob["status_namespace"]["reserved_keys"])
    actions = set(glob["action_namespace"]["monikers"])
    assert statuses
    assert actions
    assert statuses.isdisjoint(actions)


def test_action_taxonomy_matches_glob_and_legacy_map_is_total():
    glob = _yaml("GLOB.yaml")
    taxonomy = _yaml("federation/mesh/GLOBAL_ACTION_TAXONOMY_v1.yaml")
    actions = set(glob["action_namespace"]["monikers"])
    assert actions == set(taxonomy["action_monikers"])
    legacy = taxonomy["legacy_action_aliases"]["mapping"]
    assert set(legacy) == set(glob["status_namespace"]["reserved_keys"])
    assert set(legacy.values()) == actions


def test_every_action_has_where_used_and_ask_examples():
    glob = _yaml("GLOB.yaml")
    taxonomy = _yaml("federation/mesh/GLOBAL_ACTION_TAXONOMY_v1.yaml")
    where_used = _yaml("federation/mesh/GLOBAL_ACTION_WHERE_USED_v1.yaml")
    for moniker in glob["action_namespace"]["monikers"]:
        assert moniker in where_used["records"]
        assert where_used["records"][moniker]["first_use_case"]
        assert taxonomy["action_monikers"][moniker]["ask_examples"]


def test_glob_popup_contract_and_core_queries():
    module = _load_module()
    glob = module.load_glob()
    menu = module.ask_record(glob, "what can you do?")
    assert menu["identity"] == "GLOB"
    red = module.action_record(glob, "RED")
    assert red["identity"] == "RED"
    assert red["first_use_case"]
    bg = module.status_record(glob, "BG")
    assert bg["title"] == "Blocking Gate"
    codex = module.node_record(glob, "CODEX")
    assert codex["identity"] == "repo.codex"
    inbound = module.direction_record(glob, "IN")
    assert inbound["colour"] == "BLUE"


def test_dock_uses_action_monikers_not_legacy_action_classes():
    dock = _yaml(".mesh/MESH_DOCK.yaml")
    glob = _yaml("GLOB.yaml")
    assert "action_classes" not in dock
    assert set(dock["action_monikers"]) == set(glob["action_namespace"]["monikers"])
    assert set(dock["reserved_status_keys"]) == set(glob["status_namespace"]["reserved_keys"])
