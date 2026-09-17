#!/usr/bin/env python3
"""Fail-closed integrity guard for the GMI-DOCENG-001 handover bridge.

The guard validates only filesystem/materialization predicates. It does not
promote document-engineering, Alexandria, or QPS acceptance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

DEFAULT_CLI_SHA256 = "07ee6369982bcb473b293782fa0e76f56cae3dfc8eb45d41323f694fbe138893"

CORE_PATHS = (
    "HANDOVER/LOSSLESS_HANDOVER.md",
    "HANDOVER/MIGRATION_GAP_RECEIPT.md",
    "HANDOVER/ARCHITECTURE_SPEC.md",
    "MANIFEST/manifest.yaml",
    "MANIFEST/environment.lock",
    "MANIFEST/sha256.txt",
    "ARTIFACTS/cli.py",
    "ARTIFACTS/config.json",
    "ARTIFACTS/input/requirements.json",
    "ARTIFACTS/templates/README_TEMPLATES.md",
)

SOURCE_CANDIDATES = (
    "ARTIFACTS/input/Master.md",
    "ARTIFACTS/input/Master.docx",
)

RAW_HISTORY = (
    "RAW/conversation_export.json",
    "RAW/original_prompts.txt",
)

OPTIONAL_TEMPLATE = "ARTIFACTS/templates/normal.dotm"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_receipt(root: Path, expected_cli_sha256: str) -> dict[str, Any]:
    missing_core = [rel for rel in CORE_PATHS if not (root / rel).is_file()]
    cli_path = root / "ARTIFACTS/cli.py"
    cli_sha256 = sha256_file(cli_path) if cli_path.is_file() else None
    cli_hash_match = cli_sha256 == expected_cli_sha256 if cli_sha256 else False

    source_present = [rel for rel in SOURCE_CANDIDATES if (root / rel).is_file()]
    missing_raw = [rel for rel in RAW_HISTORY if not (root / rel).is_file()]
    template_present = (root / OPTIONAL_TEMPLATE).is_file()

    if missing_core or not cli_hash_match:
        disposition = "REJECT"
    elif not source_present:
        disposition = "DEFER_SOURCE_BINDING"
    else:
        disposition = "ACCEPT_MATERIALIZED_CORE"

    return {
        "schema": "gmi.doceng.bridge.guard/v1",
        "package": "GMI-DOCENG-001",
        "scope": "filesystem_materialization_and_cli_identity_only",
        "root": str(root.resolve()),
        "required_core_paths": list(CORE_PATHS),
        "missing_core_paths": missing_core,
        "cli_sha256": cli_sha256,
        "expected_cli_sha256": expected_cli_sha256,
        "cli_hash_match": cli_hash_match,
        "authoritative_source_candidates": list(SOURCE_CANDIDATES),
        "authoritative_source_present": source_present,
        "missing_raw_history": missing_raw,
        "normal_dotm_present": template_present,
        "disposition": disposition,
        "non_compensating_note": (
            "ACCEPT_MATERIALIZED_CORE does not imply QPS engineering acceptance, "
            "Alexandria integration, replay equivalence, or production readiness."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="Local mirror of GMI-DOCENG-001")
    parser.add_argument("--cli-sha256", default=DEFAULT_CLI_SHA256)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument(
        "--allow-defer",
        action="store_true",
        help="Return zero for DEFER_SOURCE_BINDING while preserving the DEFER receipt.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    receipt = build_receipt(args.root, args.cli_sha256)
    payload = json.dumps(receipt, indent=2, sort_keys=True)
    print(payload)
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(payload + "\n", encoding="utf-8")

    disposition = receipt["disposition"]
    if disposition == "REJECT":
        return 1
    if disposition == "DEFER_SOURCE_BINDING" and not args.allow_defer:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
