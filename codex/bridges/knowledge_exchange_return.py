"""Validate child-owned KEB dispositions and emit deterministic closure metrics."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from codex.bridges.knowledge_exchange import DISPOSITIONS, KnowledgeExchangeError

CHILD_RETURN_SCHEMA = "codex-keb-child-disposition/v1"
RETURN_RECEIPT_SCHEMA = "codex-keb-return-receipt/v1"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _require_string(record: dict[str, Any], key: str, context: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value:
        raise KnowledgeExchangeError(f"{context}.{key} must be a non-empty string")
    return value


def _validate_metrics(value: Any) -> dict[str, float | int]:
    if value is None:
        value = {}
    if not isinstance(value, dict):
        raise KnowledgeExchangeError("metrics must be an object")
    obligation_closures = value.get("obligation_closures", 0)
    semantic_debt_delta = value.get("semantic_debt_delta", 0)
    if isinstance(obligation_closures, bool) or not isinstance(obligation_closures, int) or obligation_closures < 0:
        raise KnowledgeExchangeError("metrics.obligation_closures must be a non-negative integer")
    if isinstance(semantic_debt_delta, bool) or not isinstance(semantic_debt_delta, (int, float)):
        raise KnowledgeExchangeError("metrics.semantic_debt_delta must be numeric")
    return {
        "obligation_closures": obligation_closures,
        "semantic_debt_delta": semantic_debt_delta,
    }


def validate_child_return(
    parent_receipt: dict[str, Any], child_return: dict[str, Any]
) -> list[dict[str, str]]:
    if child_return.get("schema") != CHILD_RETURN_SCHEMA:
        raise KnowledgeExchangeError(f"child return schema must be {CHILD_RETURN_SCHEMA}")
    if child_return.get("correlation_id") != parent_receipt.get("correlation_id"):
        raise KnowledgeExchangeError("child return correlation_id does not match parent receipt")
    if child_return.get("receipt_output_sha256") != parent_receipt.get("output_sha256"):
        raise KnowledgeExchangeError("child return receipt_output_sha256 does not match parent receipt")

    governed_owner = parent_receipt.get("disposition_owner") or parent_receipt.get("source", {}).get("repository")
    if not isinstance(governed_owner, str) or not governed_owner:
        raise KnowledgeExchangeError("parent receipt has no governed disposition owner")
    if child_return.get("disposition_owner") != governed_owner:
        raise KnowledgeExchangeError("child return disposition_owner does not match parent receipt")

    dispositions = child_return.get("dispositions")
    if not isinstance(dispositions, list) or not all(isinstance(x, dict) for x in dispositions):
        raise KnowledgeExchangeError("dispositions must be an object array")

    findings = parent_receipt.get("findings")
    if not isinstance(findings, list) or not all(isinstance(x, dict) for x in findings):
        raise KnowledgeExchangeError("parent receipt findings must be an object array")
    expected_ids = {
        _require_string(finding, "finding_id", "parent finding")
        for finding in findings
    }

    normalized: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, record in enumerate(dispositions):
        context = f"dispositions[{index}]"
        finding_id = _require_string(record, "finding_id", context)
        if finding_id in seen:
            raise KnowledgeExchangeError(f"duplicate child disposition for finding_id {finding_id}")
        if finding_id not in expected_ids:
            raise KnowledgeExchangeError(f"unknown finding_id in child disposition: {finding_id}")
        disposition = _require_string(record, "disposition", context)
        if disposition not in DISPOSITIONS:
            raise KnowledgeExchangeError(f"unsupported child disposition: {disposition}")
        rationale = _require_string(record, "rationale", context)
        seen.add(finding_id)
        normalized.append(
            {
                "finding_id": finding_id,
                "disposition": disposition,
                "rationale": rationale,
            }
        )

    if seen != expected_ids:
        missing = sorted(expected_ids - seen)
        raise KnowledgeExchangeError(
            "missing child dispositions for finding IDs: " + ", ".join(missing)
        )

    return normalized


def apply_child_return(
    parent_receipt_path: Path,
    child_return_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    parent_raw = parent_receipt_path.read_bytes()
    child_raw = child_return_path.read_bytes()
    parent_receipt = json.loads(parent_raw.decode("utf-8"))
    child_return = json.loads(child_raw.decode("utf-8"))

    normalized = validate_child_return(parent_receipt, child_return)
    child_metrics = _validate_metrics(child_return.get("metrics"))

    counts = {disposition: 0 for disposition in sorted(DISPOSITIONS)}
    for record in normalized:
        counts[record["disposition"]] += 1

    metrics = {
        "findings_returned": len(parent_receipt.get("findings", [])),
        "dispositions_received": len(normalized),
        "accepted": counts["ACCEPT_AS_DERIVED_EVIDENCE"],
        "rejected": counts["REJECT_WITH_REASON"],
        "duplicate": counts["DUPLICATE_EXISTING_WORK"],
        "deferred": counts["DEFER_PENDING_SOURCE"],
        "obligation_closures": child_metrics["obligation_closures"],
        "semantic_debt_delta": child_metrics["semantic_debt_delta"],
    }

    result: dict[str, Any] = {
        "schema": RETURN_RECEIPT_SCHEMA,
        "status": "PASS_NO_FINDINGS" if metrics["findings_returned"] == 0 else "PASS_DISPOSITIONED",
        "correlation_id": parent_receipt["correlation_id"],
        "parent_receipt_output_sha256": parent_receipt["output_sha256"],
        "parent_receipt_file_sha256": _sha256_bytes(parent_raw),
        "child_return_file_sha256": _sha256_bytes(child_raw),
        "disposition_owner": child_return["disposition_owner"],
        "dispositions": normalized,
        "metrics": metrics,
        "authority_transfer": False,
        "formal_credit_delta": 0,
    }

    provisional = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    result["output_sha256"] = _sha256_bytes(provisional)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a child-owned KEB disposition return and emit closure metrics"
    )
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--disposition", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = apply_child_return(
        Path(args.receipt),
        Path(args.disposition),
        Path(args.output),
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
