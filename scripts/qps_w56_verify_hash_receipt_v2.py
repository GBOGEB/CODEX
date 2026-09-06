from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import urllib.request

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "federation/qps/w56/QPS_W56_KEB_HASH_RECEIPT_v0.1.yaml"
CHILD_SHA = "f16d3c2e2f26309097f56cb962b3e8c25c970b13"
SOURCE_PATH = "ocd-adr/20_canonical/architecture/QPS_COMPONENT_UTILITY_ICD_SSOT_W55_v0.1.yaml"
PAYLOAD_PATH = "federation/QPS_W55_COMPONENT_UTILITY_ICD_FEDERATION_PAYLOAD_v0.1.json"
EXPECTED_BLOB_SHA1 = "dd9098b411bb1d5b447c1630c9401c9fb4b8af71"
RAW_ROOT = f"https://raw.githubusercontent.com/GBOGEB/cryoplant-project/{CHILD_SHA}/"


def fetch_bytes(path: str) -> bytes:
    with urllib.request.urlopen(RAW_ROOT + path, timeout=30) as response:
        return response.read()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def canonical_json_bytes(data: bytes) -> bytes:
    obj = json.loads(data.decode("utf-8"))
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def validate_semantics(source_bytes: bytes, payload_bytes: bytes) -> None:
    source = yaml.safe_load(source_bytes.decode("utf-8"))
    payload = json.loads(payload_bytes.decode("utf-8"))

    require(source["document_id"] == "QPS_COMPONENT_UTILITY_ICD_SSOT_W55", "source document id mismatch")
    require(source["utility_contract"]["cooling_water"]["provider"] == "PS01.PAB12", "CW provider mismatch")
    require(source["utility_contract"]["cooling_water"]["medium"] == "PG40", "CW medium mismatch")
    require(source["utility_contract"]["cooling_water"]["supply_temperature_C"] == 27, "CW supply mismatch")
    require(source["utility_contract"]["cooling_water"]["return_temperature_C"] == 37, "CW return mismatch")
    require(source["utility_contract"]["cooling_water"]["design_deltaT_K"] == 10, "CW deltaT mismatch")

    cooling_edges = source["canonical_edges"]["cooling_water"]
    cc_supply = [e for e in cooling_edges if e.get("relation") == "supplies_cooling_medium" and str(e.get("to", "")).startswith("QRB.CC")]
    require(len(cc_supply) == 3, f"expected exactly 3 CC CW supply branches, found {len(cc_supply)}")
    require({e["to"] for e in cc_supply} == {"QRB.CC01", "QRB.CC02", "QRB.CC03"}, "CC CW branch identities mismatch")
    require(all(e.get("hydraulic_control") == "PICV_or_equivalent" for e in cc_supply), "CC hydraulic control mismatch")

    expected_invariants = {
        "PVPS_PARENT_QPLANT",
        "WSH_PARENT_QPS",
        "WPS_EXTERNAL_TO_QPS",
        "PS01_PAB12_SITE_UTILITY_NOT_QPS_OWNED",
        "PG40_40WT_27C_37C_DT10K",
        "FOUR_WCS_HP_CW_BRANCH_IDENTITIES",
        "THREE_QRB_CC_CW_BRANCH_IDENTITIES",
        "THREE_QRB_CC_ELECTRICAL_FEEDS_45KW_CONTRACT_ENVELOPE",
        "NO_HVAC_DOUBLE_COUNT_OF_WATER_REJECTED_HEAT",
        "NO_PROMOTED_COMPONENT_WITHOUT_SOURCE_LOCATOR",
        "SAME_SOURCE_DOCUMENT_AND_DIGEST_ACROSS_ALL_PROJECTIONS",
    }
    require(set(payload["invariants"]) == expected_invariants, "payload invariant set mismatch")
    require(payload["source_document_id"] == source["document_id"], "payload/source document mismatch")
    require(payload["source_path"] == SOURCE_PATH, "payload source path mismatch")
    require(payload["mutation_rule"] == "PARENTS_MAY_APPEND_RECEIPTS_AND_FINDINGS_BUT_MUST_NOT_MUTATE_THE_GOVERNED_PAYLOAD", "mutation rule mismatch")


def main() -> int:
    source_bytes = fetch_bytes(SOURCE_PATH)
    payload_bytes = fetch_bytes(PAYLOAD_PATH)

    actual_blob_sha1 = git_blob_sha1(source_bytes)
    require(actual_blob_sha1 == EXPECTED_BLOB_SHA1, f"Git blob SHA-1 mismatch: {actual_blob_sha1}")

    source_hash = sha256(source_bytes)
    payload_hash = sha256(canonical_json_bytes(payload_bytes))
    validate_semantics(source_bytes, payload_bytes)

    receipt = yaml.safe_load(RECEIPT.read_text(encoding="utf-8"))
    expected_source = receipt["hash_contract"]["source_sha256"]
    expected_payload = receipt["hash_contract"]["canonical_payload_sha256"]

    print(f"QPS_W56_SOURCE_SHA256={source_hash}")
    print(f"QPS_W56_CANONICAL_PAYLOAD_SHA256={payload_hash}")
    print("QPS_W56_SEMANTIC_VALIDATION=PASS")
    print("QPS_W56_PROVENANCE_VALIDATION=PASS")

    if str(expected_source).startswith("PENDING_") or str(expected_payload).startswith("PENDING_"):
        print("HASH RECEIPT PENDING: commit the printed hashes, then rerun.")
        return 2
    require(expected_source == source_hash, f"source SHA256 mismatch: receipt={expected_source} computed={source_hash}")
    require(expected_payload == payload_hash, f"payload SHA256 mismatch: receipt={expected_payload} computed={payload_hash}")
    require(receipt.get("semantic_result") == "PASS", "semantic_result not PASS")
    require(receipt.get("provenance_result") == "PASS", "provenance_result not PASS")
    require(receipt.get("route_gate", {}).get("DOW_execution_allowed") is True, "DOW execution not allowed")

    print("QPS W56 KEB HASH GATE PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
