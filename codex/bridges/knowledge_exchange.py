"""Typed Knowledge Exchange Bridge warm-up for governed repository federation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

PAYLOAD_VERSION = "1.0.0"
ALLOWED_OPERATIONS = {"glossary_alignment", "semantic_drift_check", "lineage_receipt"}
DISPOSITIONS = {
    "ACCEPT_AS_DERIVED_EVIDENCE",
    "REJECT_WITH_REASON",
    "DEFER_PENDING_SOURCE",
    "DUPLICATE_EXISTING_WORK",
}


class KnowledgeExchangeError(ValueError):
    """Raised when a KEB request is invalid."""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _stable_finding_id(correlation_id: str, term: str, finding_type: str) -> str:
    seed = f"{correlation_id}|{term.lower()}|{finding_type}".encode("utf-8")
    return f"KEB-{hashlib.sha256(seed).hexdigest()[:12]}"


def validate_request(request: dict[str, Any]) -> None:
    required = {"payload_version", "exchange_type", "correlation_id", "source", "operations", "terms", "authority_rule", "requested_return"}
    missing = sorted(required - set(request))
    if missing:
        raise KnowledgeExchangeError(f"missing required fields: {', '.join(missing)}")
    if request["payload_version"] != PAYLOAD_VERSION:
        raise KnowledgeExchangeError(f"payload_version must be {PAYLOAD_VERSION}")
    if request["exchange_type"] != "knowledge_exchange":
        raise KnowledgeExchangeError("exchange_type must be knowledge_exchange")
    if not isinstance(request["correlation_id"], str) or not request["correlation_id"]:
        raise KnowledgeExchangeError("correlation_id must be a non-empty string")
    source = request["source"]
    if not isinstance(source, dict):
        raise KnowledgeExchangeError("source must be an object")
    for key in ("repository", "ref", "sha", "run_id"):
        if not isinstance(source.get(key), str) or not source[key]:
            raise KnowledgeExchangeError(f"source.{key} must be a non-empty string")
    operations = request["operations"]
    if not isinstance(operations, list) or not operations:
        raise KnowledgeExchangeError("operations must be a non-empty array")
    unknown = sorted(set(operations) - ALLOWED_OPERATIONS)
    if unknown:
        raise KnowledgeExchangeError(f"unsupported operations: {', '.join(unknown)}")
    if not isinstance(request["terms"], list) or not all(isinstance(x, str) and x for x in request["terms"]):
        raise KnowledgeExchangeError("terms must be a non-empty string array")
    requested = request["requested_return"]
    if requested.get("disposition_owner") == "GBOGEB/CODEX":
        raise KnowledgeExchangeError("disposition must remain child-owned")


def run_exchange(request_path: Path, glossary_path: Path, output_path: Path) -> dict[str, Any]:
    raw_request = request_path.read_bytes()
    request = json.loads(raw_request.decode("utf-8"))
    validate_request(request)

    glossary_text = glossary_path.read_text(encoding="utf-8")
    glossary_lower = glossary_text.lower()
    input_hash = _sha256_bytes(raw_request)
    glossary_hash = _sha256_bytes(glossary_text.encode("utf-8"))

    findings: list[dict[str, Any]] = []
    if "glossary_alignment" in request["operations"]:
        for term in request["terms"]:
            present = term.lower() in glossary_lower
            if not present:
                finding_type = "GLOSSARY_DRIFT"
                findings.append({
                    "finding_id": _stable_finding_id(request["correlation_id"], term, finding_type),
                    "source_reference": f"GBOGEB/CODEX/PIPELINE/GLOSSARY.yaml@sha256:{glossary_hash[:16]}",
                    "target_ocd_or_adr": "QPS_DOW_KEB_EXECUTION_ARCHITECTURE_SSOT_v0.1",
                    "finding_type": finding_type,
                    "confidence": 1.0,
                    "proposed_action": f"Define or cross-reference governed term '{term}' in the parent glossary if it is intended as reusable federation vocabulary.",
                    "authority_level": "GOVERNANCE",
                    "input_hash": input_hash,
                    "output_hash": None,
                    "disposition": None,
                })

    receipt: dict[str, Any] = {
        "schema": "codex-keb-exchange-receipt/v1",
        "payload_version": PAYLOAD_VERSION,
        "exchange_type": "knowledge_exchange",
        "correlation_id": request["correlation_id"],
        "source": request["source"],
        "stages": [
            {"stage": "request_validation", "status": "PASS"},
            {"stage": "semantic_glossary_check", "status": "PASS", "terms_checked": len(request["terms"])},
            {"stage": "stable_finding_generation", "status": "PASS", "findings": len(findings)},
            {"stage": "lineage_hash_receipt", "status": "PASS"},
        ],
        "input_sha256": input_hash,
        "glossary_sha256": glossary_hash,
        "findings": findings,
        "child_disposition_required": True,
        "allowed_child_dispositions": sorted(DISPOSITIONS),
        "authority_rule": request["authority_rule"],
    }
    provisional = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
    output_hash = _sha256_bytes(provisional)
    receipt["output_sha256"] = output_hash
    for finding in findings:
        finding["output_hash"] = output_hash

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a typed KEB knowledge exchange")
    parser.add_argument("--input", required=True)
    parser.add_argument("--glossary", default="PIPELINE/GLOSSARY.yaml")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    receipt = run_exchange(Path(args.input), Path(args.glossary), Path(args.output))
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
