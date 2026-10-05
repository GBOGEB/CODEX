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
    path = next(
        p for p in candidate["integration_paths"]
        if p["id"] == "missioncontrol_executable_value_control"
    )
    path["executed"] = False
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


def test_gateway_runtime_rex_path_is_registered_and_executed():
    contract, registry, schema = loaded()
    errors, report = validate_registry(contract, registry, schema)
    assert errors == []
    path = next(
        p for p in registry["integration_paths"]
        if p["id"] == "missioncontrol_gateway_runtime_rex"
    )
    assert path["executed"] is True
    assert path["nodes"][-1] == "mc_control_loop"
    runtime = next(
        n for n in registry["nodes"]
        if n["id"] == "gateway_transport_runtime"
    )
    assert runtime["current_state"] == "REX_OBSERVABLE"
    assert runtime["value_scope"] == "V3_PROJECT_VALUE"
    assert "gateway_transport_runtime" not in report["tested_orphans"]
    assert report["executed_integration_path_count"] >= 2


def test_gmi_hosted_federation_path_is_registered_and_executed():
    contract, registry, schema = loaded()
    errors, report = validate_registry(contract, registry, schema)
    assert errors == []
    path = next(
        p for p in registry["integration_paths"]
        if p["id"] == "gmi_doceng_hosted_federation"
    )
    assert path["executed"] is True
    assert path["nodes"][-1] == "gmi_qps_w275_consumer"
    guard = next(n for n in registry["nodes"] if n["id"] == "gmi_guard_runtime")
    assert guard["current_state"] == "FEDERATION_HOSTED_MATERIALIZATION"
    assert guard["value_scope"] == "V4_FEDERATION_VALUE"
    assert "gmi_guard_runtime" not in report["tested_orphans"]
    assert report["value_scope_counts"]["V4_FEDERATION_VALUE"] >= 3


def test_semantic_runtime_repository_value_is_registered_without_child_credit():
    contract, registry, schema = loaded()
    errors, report = validate_registry(contract, registry, schema)
    assert errors == []
    path = next(
        p for p in registry["integration_paths"]
        if p["id"] == "semantic_runtime_repository_artifact_value"
    )
    assert path["executed"] is True
    assert path["nodes"][-1] == "semantic_artifact_publisher"
    workflow = next(n for n in registry["nodes"] if n["id"] == "semantic_runtime_workflow")
    assert workflow["value_scope"] == "V2_REPOSITORY_VALUE"
    publisher = next(n for n in registry["nodes"] if n["id"] == "semantic_artifact_publisher")
    assert publisher["current_state"] == "DOWNSTREAM_CONSUMER_CHILD_ACCEPTANCE_WITHHELD"
    assert "semantic_runtime_workflow" not in report["tested_orphans"]
    assert report["executed_integration_path_count"] >= 4


def test_leg5_bounded_scout_repository_value_path_is_registered():
    contract, registry, schema = loaded()
    errors, report = validate_registry(contract, registry, schema)
    assert errors == []
    path = next(
        p for p in registry["integration_paths"]
        if p["id"] == "leg5_bounded_filesystem_scout_value"
    )
    assert path["executed"] is True
    assert path["nodes"][-1] == "leg5_scout_consumer"
    runtime = next(n for n in registry["nodes"] if n["id"] == "leg5_scout_runtime")
    assert runtime["current_state"] == "PIPELINE_INTEGRATED"
    assert runtime["value_scope"] == "V2_REPOSITORY_VALUE"
    assert "leg5_scout_runtime" not in report["tested_orphans"]
    assert report["executed_integration_path_count"] >= 5


def test_missioncontrol_log_metrics_repository_value_path_is_registered():
    contract, registry, schema = loaded()
    errors, report = validate_registry(contract, registry, schema)
    assert errors == []
    path = next(
        p for p in registry["integration_paths"]
        if p["id"] == "missioncontrol_log_metrics_repository_value"
    )
    assert path["executed"] is True
    assert path["nodes"][-1] == "mc_metrics_validation_consumer"
    builder = next(n for n in registry["nodes"] if n["id"] == "mc_metrics_builder")
    assert builder["current_state"] == "PIPELINE_INTEGRATED"
    assert builder["value_scope"] == "V2_REPOSITORY_VALUE"
    assert "mc_log_analyzer" not in report["tested_orphans"]
    assert "mc_metrics_builder" not in report["tested_orphans"]
    assert "mc_metrics_validation_consumer" not in report["tested_orphans"]
    assert report["executed_integration_path_count"] >= 6


def test_ci_bridge_alignment_repository_value_preserves_soft_ruff_debt():
    contract, registry, schema = loaded()
    errors, report = validate_registry(contract, registry, schema)
    assert errors == []
    path = next(
        p for p in registry["integration_paths"]
        if p["id"] == "ci_bridge_alignment_repository_value"
    )
    assert path["executed"] is True
    assert path["nodes"][-1] == "ci_governance_artifact_consumer"
    runtime = next(n for n in registry["nodes"] if n["id"] == "ci_bridge_alignment_runtime")
    snapshot = next(
        n for n in registry["nodes"]
        if n["id"] == "ci_governance_snapshot_bridge_alignment"
    )
    assert runtime["value_scope"] == "V2_REPOSITORY_VALUE"
    assert snapshot["current_state"] == "BRIDGE_ALIGNMENT_PASS_GLOBAL_SNAPSHOT_RUFF_FAILED"
    assert "ci_bridge_alignment_runtime" not in report["tested_orphans"]
    assert report["executed_integration_path_count"] >= 7


def test_registration_debt_classifier_repository_value_path_is_registered():
    contract, registry, schema = loaded()
    errors, report = validate_registry(contract, registry, schema)
    assert errors == []
    path = next(
        p for p in registry["integration_paths"]
        if p["id"] == "missioncontrol_registration_debt_repository_value"
    )
    assert path["executed"] is True
    assert path["nodes"][-1] == "mc_registration_debt_artifact_publisher"
    runtime = next(
        n for n in registry["nodes"]
        if n["id"] == "mc_registration_debt_classifier"
    )
    assert runtime["current_state"] == "PIPELINE_INTEGRATED"
    assert runtime["value_scope"] == "V2_REPOSITORY_VALUE"
    assert "mc_registration_debt_classifier" not in report["tested_orphans"]
    assert report["executed_integration_path_count"] >= 8


def test_full_stack_abacus_export_repository_value_path_is_registered():
    contract, registry, schema = loaded()
    errors, report = validate_registry(contract, registry, schema)
    assert errors == []
    path = next(
        p for p in registry["integration_paths"]
        if p["id"] == "full_stack_abacus_export_repository_value"
    )
    assert path["executed"] is True
    assert path["nodes"][-1] == "full_stack_release_readiness_consumer"
    exporter = next(n for n in registry["nodes"] if n["id"] == "abacus_runtime_exporter")
    assert exporter["current_state"] == "PIPELINE_INTEGRATED"
    assert exporter["value_scope"] == "V2_REPOSITORY_VALUE"
    assert "abacus_runtime_exporter" not in report["tested_orphans"]
    assert report["executed_integration_path_count"] >= 9


def test_ci_ssot_census_binding_repository_value_path_is_registered():
    contract, registry, schema = loaded()
    errors, report = validate_registry(contract, registry, schema)
    assert errors == []
    path = next(
        p for p in registry["integration_paths"]
        if p["id"] == "ci_ssot_census_binding_repository_value"
    )
    assert path["executed"] is True
    assert path["nodes"][-1] == "ci_governance_artifact_consumer"
    for node_id in (
        "ssot_candidate_census_runtime",
        "ssot_logical_id_binder",
        "ssot_runtime_consumer_mapper",
    ):
        node = next(n for n in registry["nodes"] if n["id"] == node_id)
        assert node["current_state"] == "PIPELINE_INTEGRATED"
        assert node["value_scope"] == "V2_REPOSITORY_VALUE"
        assert node_id not in report["tested_orphans"]
    assert report["executed_integration_path_count"] >= 10


def test_qps_m03_official_mcp_repository_value_path_is_registered():
    contract, registry, schema = loaded()
    errors, report = validate_registry(contract, registry, schema)
    assert errors == []
    path = next(
        p for p in registry["integration_paths"]
        if p["id"] == "qps_m03_official_mcp_repository_value"
    )
    assert path["executed"] is True
    assert path["nodes"][-1] == "qps_m03_independent_consumer"
    workflow = next(
        n for n in registry["nodes"]
        if n["id"] == "qps_m03_consumer_workflow"
    )
    assert workflow["current_state"] == "PIPELINE_INTEGRATED"
    assert workflow["value_scope"] == "V2_REPOSITORY_VALUE"
    assert "qps_m03_consumer_workflow" not in report["tested_orphans"]
    assert report["executed_integration_path_count"] >= 11
