#!/usr/bin/env python3
"""Fail-closed integrity guard for the GMI-DOCENG-001 handover bridge.

The guard validates filesystem/materialization and source-identity predicates.
Pointer-bound source identity is deliberately weaker than locally materialized,
byte-rehashed source evidence and never grants QPS engineering authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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

SOURCE_BINDING_PATH = "ARTIFACTS/input/source_binding.json"
SOURCE_BINDING_REQUIRED = (
    "repository",
    "indexed_source_commit",
    "path",
    "git_blob",
    "size_bytes",
    "sha256",
)
SOURCE_BINDING_STATUS = "POINTER_BOUND_BYTES_NOT_REHASHED"

RAW_HISTORY = (
    "RAW/conversation_export.json",
    "RAW/original_prompts.txt",
)

DOCUMENT_CORE_RECEIPT_PATH = "PROOFS/W275_DOCUMENT_CORE_REENTRY/w275_gmi_document_core_receipt.json"
DOCUMENT_CORE_RECEIPT_SCHEMA = "qps.gmi_doceng.document_core_reentry_provider_proof/v1"
DOCUMENT_CORE_PAYLOAD_SCHEMA = "gmi.document_core.requirements/v1"
DOCUMENT_CORE_DISPOSITION = "ACCEPT_DOCUMENT_CORE_INGRESS_ONLY"
EXPECTED_W274_QPS_MERGE_SHA = "34f04bf08dc2f957f196f33ea1d73ae1a5b07070"
EXPECTED_W275_CANONICAL_SHA256 = "5bed44a7ae2c0bcbd875e1162cdde292a7d9c8dc717e7328cf4a6d6f0cc13051"
EXPECTED_W275_SOURCE_SHA256 = "ac6627f0a6cbe8c020941686cad249619184d8071a9efca721d0c960d41d63c9"
EXPECTED_W275_RECORD_COUNT = 2692
EXPECTED_W275_SEMANTIC_SHA256 = "0feff7dea41f274f44d4150c6e0ce8706df0f0b4def24fe33856cd6cea78a0be"

OPTIONAL_TEMPLATE = "ARTIFACTS/templates/normal.dotm"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_source_binding(root: Path) -> tuple[dict[str, Any] | None, list[str]]:
    path = root / SOURCE_BINDING_PATH
    if not path.is_file():
        return None, []

    errors: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, [f"invalid_json:{exc.__class__.__name__}"]

    if not isinstance(payload, dict):
        return None, ["root_must_be_object"]

    for key in SOURCE_BINDING_REQUIRED:
        if key not in payload:
            errors.append(f"missing:{key}")

    if payload.get("status") != SOURCE_BINDING_STATUS:
        errors.append("status_not_pointer_bound")
    if payload.get("source_role") != "AUTHORITATIVE_MASTER_CANDIDATE":
        errors.append("source_role_not_authoritative_master_candidate")
    if not isinstance(payload.get("repository"), str) or "/" not in payload.get("repository", ""):
        errors.append("repository_invalid")
    if not HEX40.fullmatch(str(payload.get("indexed_source_commit", ""))):
        errors.append("indexed_source_commit_invalid")
    if not HEX40.fullmatch(str(payload.get("git_blob", ""))):
        errors.append("git_blob_invalid")
    if not HEX64.fullmatch(str(payload.get("sha256", ""))):
        errors.append("sha256_invalid")
    if not isinstance(payload.get("size_bytes"), int) or payload.get("size_bytes", 0) <= 0:
        errors.append("size_bytes_invalid")
    if not isinstance(payload.get("path"), str) or not payload.get("path", "").lower().endswith((".docx", ".md")):
        errors.append("path_invalid")

    return payload, errors



def _load_document_core_receipt(root: Path) -> tuple[dict[str, Any] | None, list[str]]:
    path = root / DOCUMENT_CORE_RECEIPT_PATH
    if not path.is_file():
        return None, []

    errors: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, [f"invalid_json:{exc.__class__.__name__}"]

    if not isinstance(payload, dict):
        return None, ["root_must_be_object"]

    if payload.get("schema") != DOCUMENT_CORE_RECEIPT_SCHEMA:
        errors.append("schema_invalid")
    if payload.get("wave") != "GMI-W275":
        errors.append("wave_invalid")
    if payload.get("disposition") != DOCUMENT_CORE_DISPOSITION:
        errors.append("disposition_invalid")
    if payload.get("parent_qps_w274_merge_sha") != EXPECTED_W274_QPS_MERGE_SHA:
        errors.append("parent_w274_merge_invalid")

    canonical = payload.get("canonical_input")
    if not isinstance(canonical, dict):
        errors.append("canonical_input_missing")
    else:
        if canonical.get("expected_sha256") != EXPECTED_W275_CANONICAL_SHA256:
            errors.append("canonical_expected_sha_invalid")
        if canonical.get("observed_sha256") != EXPECTED_W275_CANONICAL_SHA256:
            errors.append("canonical_observed_sha_invalid")
        if canonical.get("source_sha256") != EXPECTED_W275_SOURCE_SHA256:
            errors.append("source_sha_invalid")
        if canonical.get("expected_record_count") != EXPECTED_W275_RECORD_COUNT:
            errors.append("expected_record_count_invalid")
        if canonical.get("observed_record_count") != EXPECTED_W275_RECORD_COUNT:
            errors.append("observed_record_count_invalid")

    core = payload.get("document_core")
    if not isinstance(core, dict):
        errors.append("document_core_missing")
    else:
        if core.get("schema") != DOCUMENT_CORE_PAYLOAD_SCHEMA:
            errors.append("document_core_schema_invalid")
        if core.get("record_count") != EXPECTED_W275_RECORD_COUNT:
            errors.append("document_core_record_count_invalid")
        if core.get("semantic_sha256") != EXPECTED_W275_SEMANTIC_SHA256:
            errors.append("document_core_semantic_sha_invalid")

    checks = payload.get("checks")
    if not isinstance(checks, dict):
        errors.append("checks_missing")
    else:
        for key in (
            "canonical_identity",
            "population_identity",
            "requirement_local_shape",
            "deterministic_normalization",
        ):
            if checks.get(key) != "PASS":
                errors.append(f"{key}_not_pass")
        for key in (
            "llm_invoked",
            "source_or_requirement_mutation",
            "canonical_lock_or_tag_performed",
        ):
            if checks.get(key) is not False:
                errors.append(f"{key}_must_be_false")

    return payload, errors

def build_receipt(root: Path, expected_cli_sha256: str) -> dict[str, Any]:
    missing_core = [rel for rel in CORE_PATHS if not (root / rel).is_file()]
    cli_path = root / "ARTIFACTS/cli.py"
    cli_sha256 = sha256_file(cli_path) if cli_path.is_file() else None
    cli_hash_match = cli_sha256 == expected_cli_sha256 if cli_sha256 else False

    source_present = [rel for rel in SOURCE_CANDIDATES if (root / rel).is_file()]
    binding_path = root / SOURCE_BINDING_PATH
    binding_present = binding_path.is_file()
    binding, binding_errors = _load_source_binding(root)
    binding_valid = binding_present and binding is not None and not binding_errors

    document_core_path = root / DOCUMENT_CORE_RECEIPT_PATH
    document_core_present = document_core_path.is_file()
    document_core_receipt, document_core_errors = _load_document_core_receipt(root)
    document_core_valid = (
        document_core_present
        and document_core_receipt is not None
        and not document_core_errors
    )
    if document_core_valid and not binding_valid:
        document_core_errors.append("valid_source_binding_required")
        document_core_valid = False

    missing_raw = [rel for rel in RAW_HISTORY if not (root / rel).is_file()]
    template_present = (root / OPTIONAL_TEMPLATE).is_file()

    if missing_core or not cli_hash_match:
        disposition = "REJECT"
        source_verification_level = "NOT_EVALUATED"
    elif binding_present and not binding_valid:
        disposition = "REJECT"
        source_verification_level = "INVALID_POINTER_BINDING"
    elif document_core_present and not document_core_valid:
        disposition = "REJECT"
        source_verification_level = "INVALID_DOCUMENT_CORE_PROVIDER_PROOF"
    elif document_core_valid:
        disposition = "ACCEPT_DOCUMENT_CORE_PROVIDER_PROOF_BOUND"
        source_verification_level = "PROVIDER_BYTE_VERIFIED_DOCUMENT_CORE_INGRESS"
    elif source_present:
        disposition = "ACCEPT_MATERIALIZED_CORE"
        source_verification_level = "LOCAL_SOURCE_PRESENT"
    elif binding_valid:
        disposition = "ACCEPT_SOURCE_POINTER_BOUND"
        source_verification_level = "POINTER_BOUND_BYTES_NOT_REHASHED"
    else:
        disposition = "DEFER_SOURCE_BINDING"
        source_verification_level = "NO_SOURCE_IDENTITY"

    return {
        "schema": "gmi.doceng.bridge.guard/v3",
        "package": "GMI-DOCENG-001",
        "scope": "filesystem_materialization_cli_source_binding_and_document_core_provider_proof",
        "root": str(root.resolve()),
        "required_core_paths": list(CORE_PATHS),
        "missing_core_paths": missing_core,
        "cli_sha256": cli_sha256,
        "expected_cli_sha256": expected_cli_sha256,
        "cli_hash_match": cli_hash_match,
        "authoritative_source_candidates": list(SOURCE_CANDIDATES),
        "authoritative_source_present": source_present,
        "source_binding_path": SOURCE_BINDING_PATH,
        "source_binding_present": binding_present,
        "source_binding_valid": binding_valid,
        "source_binding_errors": binding_errors,
        "source_binding": binding if binding_valid else None,
        "source_verification_level": source_verification_level,
        "document_core_receipt_path": DOCUMENT_CORE_RECEIPT_PATH,
        "document_core_receipt_present": document_core_present,
        "document_core_receipt_valid": document_core_valid,
        "document_core_receipt_errors": document_core_errors,
        "document_core_receipt": document_core_receipt if document_core_valid else None,
        "missing_raw_history": missing_raw,
        "normal_dotm_present": template_present,
        "disposition": disposition,
        "non_compensating_note": (
            "ACCEPT_DOCUMENT_CORE_PROVIDER_PROOF_BOUND binds an independently hosted provider "
            "proof of byte-verified canonical ingress only. It does not perform semantic "
            "requirement validation/editing, canonical lock/tag, replay equivalence, Alexandria "
            "integration, QPS engineering acceptance, or production readiness."
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
