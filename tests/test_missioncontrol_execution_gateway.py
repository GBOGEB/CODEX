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
    assert contract["authentication"]["enabled_mutation_transports"] == []
    assert contract["authorization"]["action_classes"]["APPLY_BOUNDED_CODEX"]["enabled"] is False


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


def test_bounded_apply_is_proven_but_mutation_stays_withheld() -> None:
    contract = yaml.safe_load(
        (ROOT / "mission_control/mycelium/execution_gateway_contract.yaml").read_text()
    )
    policy = yaml.safe_load(
        (ROOT / "mission_control/mycelium/bounded_apply_policy.yaml").read_text()
    )
    proof = json.loads(
        (
            ROOT
            / "mission_control/mycelium/receipts/BOUNDED_APPLY_DISABLED_V01_PR894_PROOF.json"
        ).read_text()
    )
    assert contract["state"] == "BOUNDED_APPLY_IMPLEMENTED_DISABLED_EXACT_HEAD_GREEN"
    assert policy["state"] == "IMPLEMENTED_DISABLED_EXACT_HEAD_GREEN"
    assert proof["proof_conclusion"] == "EXACT_HEAD_GREEN"
    assert proof["mutation_enabled"] is False
    assert proof["execute_permitted"] is False
    assert contract["authentication"]["enabled_mutation_transports"] == []
    assert contract["authorization"]["action_classes"]["APPLY_BOUNDED_CODEX"]["enabled"] is False
    assert (
        contract["promotion"]["mutation_promotion_state"]
        == "WITHHELD_EXPLICIT_PROMOTION_REQUIRED"
    )
