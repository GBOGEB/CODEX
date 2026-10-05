import json
from copy import deepcopy

from scripts.validate_executable_integration_value import (
    CONTRACT,
    REGISTRY,
    SCHEMA,
    load_yaml,
    validate_registry,
)


def loaded():
    contract = load_yaml(CONTRACT)
    registry = load_yaml(REGISTRY)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    return contract, registry, schema


def test_registry_contract_is_valid_and_reports_migration_debt():
    contract, registry, schema = loaded()
    errors, report = validate_registry(contract, registry, schema)
    assert errors == []
    assert report["registered_node_count"] >= 7
    assert report["inventory"]["asset_count"] >= report["inventory"]["registered_asset_count"]
    assert report["control"]["pipeline_integrated_requires_executed_traversal"] is True
    assert report["authority_transfer"] is False


def test_pipeline_integrated_claim_requires_executed_traversal():
    contract, registry, schema = loaded()
    candidate = deepcopy(registry)
    candidate["nodes"][0]["current_state"] = "PIPELINE_INTEGRATED"
    candidate["integration_paths"][0]["executed"] = False
    errors, _ = validate_registry(contract, candidate, schema)
    assert any("PIPELINE_INTEGRATED claim lacks executed traversal" in e for e in errors)


def test_v4_requires_real_federation_edge():
    contract, registry, schema = loaded()
    candidate = deepcopy(registry)
    node = next(n for n in candidate["nodes"] if n["id"] == "mc_integration_validator")
    node["value_scope"] = "V4_FEDERATION_VALUE"
    errors, _ = validate_registry(contract, candidate, schema)
    assert any("V4_FEDERATION_VALUE claim lacks federation edge" in e for e in errors)


def test_tested_orphan_is_detected():
    contract, registry, schema = loaded()
    candidate = deepcopy(registry)
    candidate["nodes"].append({
        "id": "orphan",
        "type": "PYTHON_SCRIPT",
        "repository": "GBOGEB/CODEX",
        "path": "scripts/orphan.py",
        "owner": "CODEX_UI_GOVERNANCE",
        "exact_revision": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
        "purpose": "fixture",
        "inputs": [],
        "outputs": [],
        "execution_surface": "pytest",
        "test_proof_evidence": ["pytest"],
        "current_state": "TESTED",
        "authority_class": "LOCAL",
        "tested": True,
        "value_scope": "V0_TESTED_ONLY",
        "value_evidence": ["pytest"],
    })
    errors, report = validate_registry(contract, candidate, schema)
    assert errors == []
    assert "orphan" in report["tested_orphans"]


def test_value_scope_requires_tested_true():
    contract, registry, schema = loaded()
    candidate = deepcopy(registry)
    candidate["nodes"][0]["tested"] = False
    errors, _ = validate_registry(contract, candidate, schema)
    assert any("value scope requires tested=true" in e for e in errors)


def test_executed_path_requires_roles_and_terminal_consumer():
    contract, registry, schema = loaded()
    candidate = deepcopy(registry)
    candidate["integration_paths"][0]["roles"][-1] = "EXECUTION"
    errors, _ = validate_registry(contract, candidate, schema)
    assert any("required roles/edges/terminal consumer" in e for e in errors)
