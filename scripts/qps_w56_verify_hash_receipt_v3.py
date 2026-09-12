from __future__ import annotations

import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = ROOT / "federation/qps/w56"
RECEIPT = BASE / "QPS_W56_KEB_HASH_RECEIPT_v0.1.yaml"
CHILD_PROOF = BASE / "QPS_W56_KEB_CHILD_HASH_PROOF_v0.1.yaml"
INTAKE = BASE / "QPS_W56_KEB_COMPONENT_UTILITY_INTAKE_v0.1.yaml"
DOW_RETURN = BASE / "QPS_W56_DOW_NORMALIZED_RETURN_v0.1.yaml"

EXPECTED_CHILD_REPO = "GBOGEB/cryoplant-project"
EXPECTED_CHILD_SHA = "f16d3c2e2f26309097f56cb962b3e8c25c970b13"
EXPECTED_SOURCE_PATH = "ocd-adr/20_canonical/architecture/QPS_COMPONENT_UTILITY_ICD_SSOT_W55_v0.1.yaml"
EXPECTED_BLOB_SHA1 = "dd9098b411bb1d5b447c1630c9401c9fb4b8af71"
EXPECTED_SOURCE_SHA256 = "4afd7e4e77737297165368282471d1e9d926918510ddb9f05854a62c4496d557"
EXPECTED_PAYLOAD_SHA256 = "da745e3488a9eebf356056610b8612c8f53cea8afd71d459553c89bc27346b63"
EXPECTED_CHILD_RUN_ID = 34056861463
EXPECTED_CHILD_JOB_ID = 101550230565


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def load(path: pathlib.Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path.name}: expected mapping")
    return data


def main() -> int:
    receipt = load(RECEIPT)
    proof = load(CHILD_PROOF)
    intake = load(INTAKE)
    dow_return = load(DOW_RETURN)

    source = receipt.get("source") or {}
    hashes = receipt.get("hash_contract") or {}
    receipt_proof = receipt.get("proof") or {}
    route = receipt.get("route_gate") or {}
    intake_input = intake.get("input") or {}
    lineage = dow_return.get("lineage") or {}
    mutation = dow_return.get("mutation_assertion") or {}

    require(receipt.get("status") == "PASS", "KEB hash receipt is not PASS")
    require(source.get("child_repo") == EXPECTED_CHILD_REPO, "child repo mismatch")
    require(source.get("child_merge_sha") == EXPECTED_CHILD_SHA, "receipt child SHA mismatch")
    require(source.get("source_path") == EXPECTED_SOURCE_PATH, "receipt source path mismatch")
    require(source.get("git_blob_sha1") == EXPECTED_BLOB_SHA1, "receipt Git blob SHA-1 mismatch")
    require(hashes.get("source_sha256") == EXPECTED_SOURCE_SHA256, "receipt source SHA-256 mismatch")
    require(hashes.get("canonical_payload_sha256") == EXPECTED_PAYLOAD_SHA256, "receipt payload SHA-256 mismatch")

    require(proof.get("source_repo") == EXPECTED_CHILD_REPO, "child proof repo mismatch")
    require(proof.get("pinned_child_merge_sha") == EXPECTED_CHILD_SHA, "child proof SHA mismatch")
    require(proof.get("source_git_blob_sha1") == EXPECTED_BLOB_SHA1, "child proof blob SHA mismatch")
    require(proof.get("source_sha256") == EXPECTED_SOURCE_SHA256, "child proof source SHA-256 mismatch")
    require(proof.get("canonical_payload_sha256") == EXPECTED_PAYLOAD_SHA256, "child proof payload SHA-256 mismatch")
    require(proof.get("source_workflow_run_id") == EXPECTED_CHILD_RUN_ID, "child proof run ID mismatch")
    require(proof.get("source_job_id") == EXPECTED_CHILD_JOB_ID, "child proof job ID mismatch")
    require(proof.get("workflow_result") == "PASS", "child source-owner workflow result is not PASS")

    require(receipt_proof.get("child_proof_workflow_run_id") == EXPECTED_CHILD_RUN_ID, "receipt/proof run mismatch")
    require(receipt_proof.get("child_proof_job_id") == EXPECTED_CHILD_JOB_ID, "receipt/proof job mismatch")
    require(receipt_proof.get("child_proof_result") == "PASS", "receipt child proof result is not PASS")

    require(intake_input.get("child_repo") == EXPECTED_CHILD_REPO, "intake repo mismatch")
    require(intake_input.get("child_merge_sha") == EXPECTED_CHILD_SHA, "intake child SHA mismatch")
    require(intake_input.get("child_source_path") == EXPECTED_SOURCE_PATH, "intake source path mismatch")
    require(intake_input.get("child_source_git_blob_sha1") == EXPECTED_BLOB_SHA1, "intake blob SHA mismatch")

    require(lineage.get("child_merge_sha") == EXPECTED_CHILD_SHA, "DOW return child SHA mismatch")
    require(str(lineage.get("source_sha256", "")).strip() == EXPECTED_SOURCE_SHA256, "DOW return source hash mismatch")
    require(str(lineage.get("canonical_payload_sha256", "")).strip() == EXPECTED_PAYLOAD_SHA256, "DOW return payload hash mismatch")
    require(mutation.get("payload_mutated_by_keb") is False, "KEB mutation assertion violated")
    require(mutation.get("payload_mutated_by_dow") is False, "DOW mutation assertion violated")
    require(mutation.get("source_sha256_preserved") is True, "source digest preservation not asserted")
    require(mutation.get("canonical_payload_sha256_preserved") is True, "payload digest preservation not asserted")

    require(receipt.get("semantic_result") == "PASS", "semantic_result not PASS")
    require(receipt.get("provenance_result") == "PASS", "provenance_result not PASS")
    require(route.get("DOW_execution_allowed") is True, "DOW route not explicitly allowed")
    require(route.get("fail_closed") is True, "hash gate is not fail-closed")

    result = {
        "schema": "qps.w56.keb.returned_evidence_gate.v1",
        "result": "PASS",
        "transport": "LOCAL_RETURNED_RECEIPT_ONLY",
        "network_access": "NONE",
        "source_owner": EXPECTED_CHILD_REPO,
        "pinned_child_sha": EXPECTED_CHILD_SHA,
        "source_path": EXPECTED_SOURCE_PATH,
        "git_blob_sha1": EXPECTED_BLOB_SHA1,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "canonical_payload_sha256": EXPECTED_PAYLOAD_SHA256,
        "source_owner_run_id": EXPECTED_CHILD_RUN_ID,
        "source_owner_job_id": EXPECTED_CHILD_JOB_ID,
        "lineage_checked": [
            RECEIPT.name,
            CHILD_PROOF.name,
            INTAKE.name,
            DOW_RETURN.name,
        ],
        "architecture": "CHILD_EMITS_EXACT_RECEIPT_PARENT_CONSUMES_LOCAL_RETURN",
        "cross_repo_credential_required": False,
    }
    print(json.dumps(result, sort_keys=True))
    print("QPS W56 KEB RETURNED-EVIDENCE HASH GATE PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
