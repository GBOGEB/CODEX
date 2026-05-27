#!/usr/bin/env python3
"""PR-007 governance header parser and gate for federation_runtime."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


HEADER_PATTERN = re.compile(r"## PR CLASSIFICATION\n(.*?)\n---", re.DOTALL)


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


def run_header_compliance_audit() -> None:
    print("[PR-007] Running federation governance parser...")
    root = Path(__file__).resolve().parents[1]
    follow_up_path = root / ".github" / "W003_PR_FOLLOW_UP.md"
    schema_path = root / "schema" / "governance_header.schema.json"

    if not follow_up_path.exists() or not schema_path.exists():
        print("[PR-007][ERROR] Missing required follow-up markdown or governance schema.")
        sys.exit(1)

    metadata = extract_governance_block(follow_up_path.read_text(encoding="utf-8"))
    if not metadata:
        print("[PR-007][ERROR] Could not parse mandatory governance header block.")
        sys.exit(1)

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    required = schema.get("required", [])
    for key in required:
        if key not in metadata:
            print(f"[PR-007][ERROR] Missing required key: {key}")
            sys.exit(1)

    pattern_map = {k: v.get("pattern") for k, v in schema.get("properties", {}).items() if isinstance(v, dict) and "pattern" in v}
    for key, pattern in pattern_map.items():
        if key in metadata and not re.match(pattern, metadata[key]):
            print(f"[PR-007][ERROR] Pattern mismatch for {key}: {metadata[key]}")
            sys.exit(1)

    for key, prop in schema.get("properties", {}).items():
        if key not in metadata:
            continue
        if "const" in prop and metadata[key] != prop["const"]:
            print(f"[PR-007][ERROR] Const mismatch for {key}: {metadata[key]}")
            sys.exit(1)
        if "enum" in prop and metadata[key] not in prop["enum"]:
            print(f"[PR-007][ERROR] Enum mismatch for {key}: {metadata[key]}")
            sys.exit(1)

    if metadata.get("TYPE") != "GOVERNANCE" and metadata.get("SCHEMA MUTATION") == "YES":
        print("[PR-007][ERROR] Unauthorized schema mutation outside GOVERNANCE type.")
        sys.exit(1)

    print("[PR-007] Governance header validated successfully.")


if __name__ == "__main__":
    run_header_compliance_audit()
