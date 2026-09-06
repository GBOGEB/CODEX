from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "federation/qps/w56/QPS_W56_KEB_HASH_RECEIPT_v0.1.yaml"
CHILD_DIR = ROOT / ".tmp-qps-w56-child"
CHILD_SHA = "f16d3c2e2f26309097f56cb962b3e8c25c970b13"
SOURCE_PATH = pathlib.Path("ocd-adr/20_canonical/architecture/QPS_COMPONENT_UTILITY_ICD_SSOT_W55_v0.1.yaml")
PAYLOAD_PATH = pathlib.Path("federation/QPS_W55_COMPONENT_UTILITY_ICD_FEDERATION_PAYLOAD_v0.1.json")


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(path: pathlib.Path) -> bytes:
    obj = json.loads(path.read_text(encoding="utf-8"))
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def main() -> int:
    if CHILD_DIR.exists():
        run("rm", "-rf", str(CHILD_DIR))
    run("git", "clone", "--filter=blob:none", "--no-checkout", "https://github.com/GBOGEB/cryoplant-project.git", str(CHILD_DIR))
    run("git", "-C", str(CHILD_DIR), "fetch", "--depth=1", "origin", CHILD_SHA)
    run("git", "-C", str(CHILD_DIR), "checkout", "--detach", "FETCH_HEAD")

    actual_head = subprocess.check_output(["git", "-C", str(CHILD_DIR), "rev-parse", "HEAD"], text=True).strip()
    if actual_head != CHILD_SHA:
        raise SystemExit(f"child HEAD mismatch: {actual_head} != {CHILD_SHA}")

    source_bytes = (CHILD_DIR / SOURCE_PATH).read_bytes()
    source_hash = sha256(source_bytes)
    payload_hash = sha256(canonical_json_bytes(CHILD_DIR / PAYLOAD_PATH))

    receipt = yaml.safe_load(RECEIPT.read_text(encoding="utf-8"))
    expected_source = receipt["hash_contract"]["source_sha256"]
    expected_payload = receipt["hash_contract"]["canonical_payload_sha256"]

    print(f"QPS_W56_SOURCE_SHA256={source_hash}")
    print(f"QPS_W56_CANONICAL_PAYLOAD_SHA256={payload_hash}")

    pending = str(expected_source).startswith("PENDING_") or str(expected_payload).startswith("PENDING_")
    if pending:
        print("HASH RECEIPT PENDING: commit the two values printed above, then rerun this gate.")
        return 2

    if expected_source != source_hash:
        print(f"source SHA256 mismatch: receipt={expected_source} computed={source_hash}")
        return 1
    if expected_payload != payload_hash:
        print(f"payload SHA256 mismatch: receipt={expected_payload} computed={payload_hash}")
        return 1

    if receipt.get("semantic_result") != "PASS" or receipt.get("provenance_result") != "PASS":
        print("receipt hashes match, but semantic/provenance results are not PASS")
        return 1
    if receipt.get("route_gate", {}).get("DOW_execution_allowed") is not True:
        print("receipt hashes match, but DOW execution is not explicitly allowed")
        return 1

    print("QPS W56 KEB HASH GATE PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
