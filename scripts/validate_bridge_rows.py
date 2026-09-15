#!/usr/bin/env python3
"""Validate QPS/DOW/KEB bridge row completeness.

This is deliberately small: it checks required fields and receipt binding
without requiring jsonschema. It is a first-pass guard for source PR/SHA/file
hash discipline.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("Missing dependency: pyyaml. Install with: pip install pyyaml") from exc

REQUIRED = {
    "qps_rows": [
        "qps_item_id",
        "object_type",
        "source_repo",
        "source_locator",
        "requirement_id",
        "offer_ref",
        "state",
        "confidence",
        "next_evidence_needed",
        "receipt_binding",
        "lineage",
    ],
    "dow_rows": [
        "dow_item_id",
        "object_type",
        "source_repo",
        "source_pr",
        "source_sha",
        "receipt_id",
        "disposition",
        "predicate",
        "reason",
        "next_action",
        "file_digest",
        "lineage",
    ],
    "keb_rows": [
        "keb_item_id",
        "object_type",
        "source_repo",
        "source_pr",
        "source_sha",
        "source_locator",
        "source_digest",
        "replay_status",
        "validation_result",
        "downstream_consumer",
        "next_action",
        "lineage",
    ],
}

LINEAGE_REQUIRED = ["chat_session", "originating_prompt", "created_by"]


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("root YAML value must be a mapping")
    return data


def is_missing(value: Any, allow_tbd: bool) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, str) and value.strip().upper() == "TBD" and not allow_tbd:
        return True
    return False


def validate_lineage(row_name: str, lineage: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(lineage, dict):
        return [f"{row_name}: lineage must be a mapping"]
    for key in LINEAGE_REQUIRED:
        if is_missing(lineage.get(key), allow_tbd=False):
            errors.append(f"{row_name}: lineage.{key} is required")
    return errors


def validate_receipt_binding(row_name: str, binding: Any, allow_tbd: bool) -> list[str]:
    errors: list[str] = []
    if not isinstance(binding, dict):
        return [f"{row_name}: receipt_binding must be a mapping"]
    for key in ["source_pr", "source_sha", "file_digest"]:
        if is_missing(binding.get(key), allow_tbd=allow_tbd):
            errors.append(f"{row_name}: receipt_binding.{key} is required")
    return errors


def validate_group(name: str, rows: Any, allow_tbd: bool) -> list[str]:
    errors: list[str] = []
    if not isinstance(rows, list):
        return [f"{name}: must be a list"]
    for index, row in enumerate(rows):
        row_name = f"{name}[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{row_name}: row must be a mapping")
            continue
        for key in REQUIRED[name]:
            if key == "lineage":
                errors.extend(validate_lineage(row_name, row.get(key)))
            elif key == "receipt_binding":
                errors.extend(validate_receipt_binding(row_name, row.get(key), allow_tbd=allow_tbd))
            elif is_missing(row.get(key), allow_tbd=allow_tbd):
                errors.append(f"{row_name}: {key} is required")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate QPS/DOW/KEB bridge rows")
    parser.add_argument("path", nargs="?", default="ssot/bridge_rows/sample_qps_dow_keb_receipts.yaml")
    parser.add_argument("--strict", action="store_true", help="Treat TBD as missing")
    args = parser.parse_args()

    data = load_yaml(Path(args.path))
    errors: list[str] = []
    for group in ["qps_rows", "dow_rows", "keb_rows"]:
        errors.extend(validate_group(group, data.get(group), allow_tbd=not args.strict))

    if errors:
        print(f"FAIL: {args.path} contains {len(errors)} row completeness error(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    mode = "strict" if args.strict else "draft"
    print(f"PASS: {args.path} bridge rows are complete in {mode} mode")
    return 0


if __name__ == "__main__":
    sys.exit(main())
