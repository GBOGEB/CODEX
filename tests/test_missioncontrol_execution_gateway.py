import json
from pathlib import Path

import yaml

from scripts.validate_missioncontrol_execution_gateway import validate

ROOT = Path(__file__).resolve().parents[1]


def test_gateway_design_contract_is_fail_closed() -> None:
    assert validate() == []
    contract = yaml.safe_load(
        (ROOT / "mission_control/mycelium/execution_gateway_contract.yaml").read_text()
    )
    assert contract["authorization"]["default"] == "DENY"
    assert contract["state"] == "BOUNDED_CODEX_APPLY_IMPLEMENTED_PENDING_RUNTIME_PROOF"
    assert contract["authentication"]["enabled_mutation_transports"] == [
        "OWNER_COMMENT_AUTOMATION_PR"
    ]
    apply_rule = contract["authorization"]["action_classes"]["APPLY_BOUNDED_CODEX"]
    assert apply_rule["enabled"] is True
    assert apply_rule["allowed_repositories"] == ["GBOGEB/CODEX"]
    assert apply_rule["allowed_intents"] == ["REFRESH_FEDERATION_HEADS"]
    assert apply_rule["direct_main_write"] is False
    assert apply_rule["review_pr_required"] is True
    bounded = contract["bounded_apply_runtime"]
    assert bounded["mutation_mode"] == "AUTOMATION_BRANCH_PR_ONLY"
    assert bounded["runtime_proof"] == "WITHHELD_OWNER_APPLY_COMMAND_REQUIRED"
    assert bounded["remote_authority_mutation"] is False


def test_execution_request_requires_exact_head_and_no_credit() -> None:
    schema = json.loads(
        (ROOT / "mission_control/mycelium/schemas/execution_request.schema.json").read_text()
    )
    target = schema["properties"]["target"]
    assert "expected_head_sha" in target["required"]
    assert target["properties"]["expected_head_sha"]["pattern"] == "^[0-9a-f]{40}$"
    assert schema["properties"]["authority_transfer"]["const"] is False
    assert schema["properties"]["formal_credit_delta"]["const"] == 0
    assert schema["properties"]["engineering_credit_delta"]["const"] == 0


def test_receipt_binds_authenticated_principal_and_observed_head() -> None:
    schema = json.loads(
        (ROOT / "mission_control/mycelium/schemas/execution_receipt.schema.json").read_text()
    )
    required = set(schema["required"])
    assert {"authenticated_principal", "observed_head_sha", "request_sha256"} <= required
