#!/usr/bin/env python3
"""PR-007 governance header parser and gate for federation_runtime."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HEADER_PATTERN = re.compile(r"## PR CLASSIFICATION\n(.*?)\n---", re.DOTALL)
EXPECTED_SCHEMA_MUTATION_TYPE = "GOVERNANCE"
SCHEMA_MUTATION_ENABLED_VALUE = "YES"


def extract_governance_block(markdown_text: str) -> dict[str, str] | None:
    """Extract PR classification metadata from markdown.

    Returns metadata key-value pairs, or None when no governance block is found.
    """
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


def validate_metadata_against_schema(metadata: dict[str, str], schema: dict) -> tuple[bool, list[str]]:
    """Validate parsed governance metadata against the supplied schema.

    Returns a tuple of (is_valid, error_list).
    """
    errors: list[str] = []
    properties = schema.get("properties", {})

    if schema.get("additionalProperties") is False:
        for key in sorted(set(metadata) - set(properties)):
            errors.append(f"Unexpected key: {key}. Allowed keys: {', '.join(sorted(properties))}")

    for key in schema.get("required", []):
        if key not in metadata:
            errors.append(f"Missing required key: {key}")

    for key, prop in properties.items():
        if key not in metadata:
            continue
        value = metadata[key]
        pattern = prop.get("pattern")
        if pattern and not re.fullmatch(pattern, value):
            errors.append(f"Pattern mismatch for {key}: {value}")
        const = prop.get("const")
        if const and value != const:
            errors.append(f"Const mismatch for {key}: {value}")
        enum = prop.get("enum")
        if enum and value not in enum:
            errors.append(f"Enum mismatch for {key}: {value}")

    if (
        metadata.get("TYPE") != EXPECTED_SCHEMA_MUTATION_TYPE
        and metadata.get("SCHEMA MUTATION") == SCHEMA_MUTATION_ENABLED_VALUE
    ):
        errors.append(
            f"SCHEMA MUTATION=YES is only allowed when TYPE={EXPECTED_SCHEMA_MUTATION_TYPE}. "
            f"Current TYPE: {metadata.get('TYPE')}"
        )

    return (len(errors) == 0, errors)


def validate_pr_classification_header(target_file: Path, schema_path: Path) -> int:
    """Validate the PR classification header for a target markdown file.

    Returns 0 on success and 1 on failure.
    """
    print("[PR-007] Running federation governance parser...")

    if not target_file.exists() or not schema_path.exists():
        print("[PR-007][ERROR] Missing follow-up markdown or governance schema.")
        return 1

    metadata = extract_governance_block(target_file.read_text(encoding="utf-8"))
    if not metadata:
        print("[PR-007][ERROR] Could not parse mandatory governance header block.")
        return 1

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    valid, errors = validate_metadata_against_schema(metadata, schema)
    if not valid:
        for err in errors:
            print(f"[PR-007][ERROR] {err}")
        return 1

    print(f"[PR-007] PR-ID={metadata.get('PR-ID')} WAVE={metadata.get('WAVE')} TYPE={metadata.get('TYPE')}")
    print("[PR-007] Governance header validated successfully.")
    return 0


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Validate federation governance PR header markdown")
    parser.add_argument(
        "--target",
        default=str(root / ".github" / "W003_PR_FOLLOW_UP.md"),
        help="Path to markdown file containing mandatory governance header",
    )
    parser.add_argument(
        "--schema",
        default=str(root / "schema" / "governance_header.schema.json"),
        help="Path to governance header schema",
    )
    args = parser.parse_args()
    sys.exit(validate_pr_classification_header(Path(args.target), Path(args.schema)))
