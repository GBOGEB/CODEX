import json
from pathlib import Path


CONTRACT = Path("federation/triage/qps_w43_keb_execution_contract.json")


def test_qps_w43_keb_contract_is_semantically_fail_closed():
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert data["role"] == "KNOWLEDGE_EXCHANGE_BRIDGE"
    assert data["execution"]["mode"] == "PARALLEL_WITH_DOW"
    assert len(data["execution"]["required_operations"]) == 6
    assert data["formal_credit_delta"] == 0
    assert "KEB means Knowledge Exchange Bridge" in data["guards"]
    assert "KEB is not a scheduler or execution backbone" in data["guards"]

    required = set(data["return_schema"]["required"])
    assert {"source_child_sha", "executed_operations", "semantic_findings", "lineage_findings", "return_hash"} <= required
    assert data["input_control"]["buildings_utilities_candidate_mapping"] == "26/53 = 49.06%"
    assert data["input_control"]["raw_msg_exact_attribution"] == "0/53 pending"
