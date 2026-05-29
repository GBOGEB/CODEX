#!/usr/bin/env python3
"""PR-007 governance header parser and gate for federation_runtime."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from jsonschema import ValidationError, validate


HEADER_PATTERN = re.compile(r"## PR CLASSIFICATION\n(.*?)\n---", re.DOTALL)
SCHEMA_MUTATION_VALUES = {"YES", "CONTROLLED"}


def extract_governance_block(markdown_text: str) -> dict[str, str] | None:
    match = HEADER_PATTERN.search(markdown_text)
    if not match:
        return None

    metadata: dict[str, str] = {}
    for raw_line in match.group(1).strip().splitlines():
        line = raw_line.strip()
        if not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata


def validate_governance_header(markdown_text: str, schema: dict[str, object]) -> dict[str, str]:
    metadata = extract_governance_block(markdown_text)
    if not metadata:
        raise ValueError("Could not parse mandatory governance header block.")

    try:
        validate(instance=metadata, schema=schema)
    except ValidationError as exc:
        json_path = " -> ".join(str(part) for part in exc.path)
        detail = f"{json_path}: {exc.message}" if json_path else exc.message
        raise ValueError(detail) from exc

    if metadata.get("TYPE") != "GOVERNANCE" and metadata.get("SCHEMA MUTATION") in SCHEMA_MUTATION_VALUES:
        raise ValueError("Unauthorized schema mutation outside GOVERNANCE type.")

    return metadata


def run_header_compliance_audit(
    markdown_path: Path | None = None,
    schema_path: Path | None = None,
    source: str | None = None,
) -> None:
    print("[PR-007] Running federation governance parser...")
    root = Path(__file__).resolve().parents[1]
    follow_up_path = markdown_path or root / ".github" / "W003_PR_FOLLOW_UP.md"
    schema_path = schema_path or root / "schema" / "governance_header.schema.json"
    source = source or str(follow_up_path)

    if not follow_up_path.exists() or not schema_path.exists():
        print("[PR-007][ERROR] Missing required follow-up markdown or governance schema.")
        sys.exit(1)

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validate_governance_header(follow_up_path.read_text(encoding="utf-8"), schema)
    except ValueError as exc:
        print(f"[PR-007][ERROR] {exc}")
        sys.exit(1)

    print(f"[PR-007] Governance header validated successfully from {source}.")


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--markdown",
        type=Path,
        default=root / ".github" / "W003_PR_FOLLOW_UP.md",
        help="Path to the markdown source containing the governance header.",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=root / "schema" / "governance_header.schema.json",
        help="Path to the governance header JSON schema.",
    )
    parser.add_argument(
        "--source",
        default=None,
        help="Human-readable label for the governance input being validated.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_header_compliance_audit(markdown_path=args.markdown, schema_path=args.schema, source=args.source)
