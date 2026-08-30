#!/usr/bin/env python3
"""Validate the QPS W04 KEB receipt fixture contract.

This validator is intentionally schema/semantic-domain/authority focused. It
returns governance validation only and does not promote QPS engineering claims.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required to run this validator") from exc

EXPECTED_CORRELATION = "QPS-FED-W04-T10-SAFE-CTRL"
REQUIRED_FIELDS = {
    "run_id",
    "artifact_id",
    "parent_commit_sha",
    "correlation_id",
    "input_hash",
    "output_hash",
    "requested_operations",
    "executed_operations",
    "operation_status",
    "typed_semantic_findings",
    "authority_boundary",
}
REQUIRED_DOMAINS = {
    "Table10_failure_class_and_preserved_state",
    "Safety_non_compensating_gate",
    "RAMS_RCM_Inspectability",
    "lifecycle_L1_L8",
    "QPS_CIS_MCS_MIS_MIT",
    "support_system_permissive",
    "softlock_interlock_permissive",
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not parse as a YAML mapping")
    return data


def validate_fixture(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("correlation_id") != EXPECTED_CORRELATION:
        errors.append("fixture correlation_id does not match W04 correlation")

    receipt = data.get("example_valid_receipt")
    if not isinstance(receipt, dict):
        return errors + ["example_valid_receipt missing or not a mapping"]

    missing = sorted(REQUIRED_FIELDS - set(receipt))
    if missing:
        errors.append(f"example_valid_receipt missing required fields: {', '.join(missing)}")

    if receipt.get("correlation_id") != EXPECTED_CORRELATION:
        errors.append("receipt correlation_id does not match W04 correlation")

    requested = receipt.get("requested_operations")
    executed = receipt.get("executed_operations")
    status = receipt.get("operation_status")
    if not isinstance(requested, list) or not requested:
        errors.append("requested_operations must be a non-empty list")
    if not isinstance(executed, list) or not executed:
        errors.append("executed_operations must be a non-empty list")
    if isinstance(requested, list) and isinstance(executed, list):
        missing_exec = [op for op in requested if op not in executed]
        if missing_exec:
            errors.append(f"executed_operations missing requested operations: {', '.join(missing_exec)}")
    if not isinstance(status, dict):
        errors.append("operation_status must be a mapping")
    elif isinstance(executed, list):
        missing_status = [op for op in executed if op not in status]
        if missing_status:
            errors.append(f"operation_status missing entries for: {', '.join(missing_status)}")

    findings = receipt.get("typed_semantic_findings")
    if not isinstance(findings, list):
        errors.append("typed_semantic_findings must be a list")

    domains = data.get("semantic_domains_for_regression")
    if not isinstance(domains, list):
        errors.append("semantic_domains_for_regression must be a list")
    else:
        missing_domains = sorted(REQUIRED_DOMAINS - set(domains))
        if missing_domains:
            errors.append(f"missing semantic regression domains: {', '.join(missing_domains)}")

    boundary = str(receipt.get("authority_boundary", ""))
    if "QPS_child_disposes" not in boundary:
        errors.append("authority_boundary must state that QPS child disposes findings")

    return errors


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else Path("tests/fixtures/qps_w04_keb_receipt_fixture.yaml")
    errors = validate_fixture(load_yaml(path))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {path} satisfies QPS W04 KEB receipt fixture contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
