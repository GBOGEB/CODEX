from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
A9 = ROOT / "abacus_render_pipeline" / "A9_multiformat_publication"
A7 = ROOT / "abacus_render_pipeline" / "A7_executable_semantic_runtime"
sys.path.insert(0, str(A9))

SNAPSHOT = HERE / "outputs" / "governance_snapshot.png"
SNAPSHOT_RECEIPT = HERE / "receipts" / "snapshot_execution_receipt.json"
A9_RECEIPT = A9 / "receipts" / "multiformat_execution_receipt.json"
TUPLE_LEDGER = A7 / "data" / "semantic_tuple_ledger.json"


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_and_validate(path: Path = SNAPSHOT_RECEIPT) -> dict[str, Any]:
    receipt = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "receipt_version", "publication_id", "source_commit", "snapshot_sha256",
        "snapshot_relpath", "snapshot_bytes", "source_html_sha256", "a9_receipt_sha256",
        "tuple_ledger_sha256", "renderer", "telemetry", "checks", "decision"
    }
    missing = sorted(required - set(receipt))
    if missing:
        raise ValueError(f"snapshot receipt missing fields: {missing}")
    if receipt["receipt_version"] != "A10.0":
        raise ValueError("unsupported snapshot receipt version")

    a9 = json.loads(A9_RECEIPT.read_text(encoding="utf-8"))
    html_rel = a9["formats"]["html"]["artifact_relpath"]
    html_path = A9 / html_rel
    expected = {
        "snapshot_sha256": sha256_path(SNAPSHOT),
        "source_html_sha256": sha256_path(html_path),
        "a9_receipt_sha256": sha256_path(A9_RECEIPT),
        "tuple_ledger_sha256": sha256_path(TUPLE_LEDGER),
    }
    mismatches = [f"{key}: receipt={receipt.get(key)} actual={value}" for key, value in expected.items() if receipt.get(key) != value]
    if mismatches:
        raise ValueError("snapshot content-address validation failed: " + "; ".join(mismatches))
    if receipt["snapshot_bytes"] != SNAPSHOT.stat().st_size:
        raise ValueError("snapshot byte-size mismatch")

    with Image.open(SNAPSHOT) as image:
        dims = receipt["checks"]["dimensions"]
        if image.format != "PNG":
            raise ValueError(f"snapshot format is {image.format}, expected PNG")
        if image.size != (dims["width_px"], dims["height_px"]):
            raise ValueError("snapshot dimensions do not match receipt")

    expected_decision = "accept" if all(bool(item.get("pass")) for item in receipt["checks"].values()) else "reject"
    if receipt["decision"] != expected_decision:
        raise ValueError(f"snapshot decision inconsistent: receipt={receipt['decision']} expected={expected_decision}")
    if a9.get("decision") != "accept":
        raise ValueError("A9 carrier receipt is not accepted")
    if receipt["source_commit"] != a9.get("source_commit"):
        raise ValueError("snapshot and A9 receipts are not bound to the same source commit")
    return receipt


if __name__ == "__main__":
    result = load_and_validate()
    print(json.dumps({"status": "PASS", "decision": result["decision"], "snapshot_sha256": result["snapshot_sha256"]}, indent=2))
    raise SystemExit(0 if result["decision"] == "accept" else 1)
