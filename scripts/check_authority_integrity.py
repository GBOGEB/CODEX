#!/usr/bin/env python3
"""Fail-closed CODEX authority integrity preflight."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "ssot" / "manifest.yaml"
LOCAL_AUTHORITY = "LOCAL_AUTHORITATIVE"
REMOTE_AUTHORITY = "REMOTE_AUTHORITATIVE"
AUTHORITY_CLASSES = {LOCAL_AUTHORITY, REMOTE_AUTHORITY}


def fail(message: str) -> None:
    raise SystemExit(f"AUTHORITY_INTEGRITY_FAIL: {message}")


def main() -> int:
    if not MANIFEST.exists():
        fail("ssot/manifest.yaml missing")

    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    authorities = data.get("authorities") or {}
    if not isinstance(authorities, dict) or not authorities:
        fail("authorities registry missing or empty")

    logical_ids: list[str] = []
    for key, node in authorities.items():
        if not isinstance(node, dict):
            fail(f"authority node {key!r} is not a mapping")
        logical_id = node.get("logical_id")
        authority_class = node.get("authority_class")
        if not logical_id:
            fail(f"authority node {key!r} has no logical_id")
        if authority_class not in AUTHORITY_CLASSES:
            fail(f"authority node {key!r} has invalid authority_class {authority_class!r}")
        logical_ids.append(str(logical_id))

        if authority_class == LOCAL_AUTHORITY:
            path = node.get("path")
            if not path:
                fail(f"local authority {logical_id} has no path")
            if not (ROOT / str(path)).exists():
                fail(f"local authority {logical_id} path does not exist: {path}")

        if authority_class == REMOTE_AUTHORITY:
            if not node.get("owner_repository"):
                fail(f"remote authority {logical_id} has no owner_repository")
            if node.get("mutation_allowed") is not False and logical_id == "QPS_ENGINEERING_TRUTH":
                fail("QPS engineering authority must be explicitly read-only in CODEX")

    duplicates = sorted(k for k, count in Counter(logical_ids).items() if count > 1)
    if duplicates:
        fail("duplicate logical authority IDs: " + ", ".join(duplicates))

    invariants = data.get("invariants") or {}
    required_true = (
        "one_authority_per_logical_fact",
        "remote_engineering_mutation_forbidden",
        "receipt_cannot_become_engineering_source",
        "derived_view_cannot_become_authority",
        "dow_result_cannot_auto_promote_child_state",
        "child_disposition_remains_child_owned",
    )
    missing = [name for name in required_true if invariants.get(name) is not True]
    if missing:
        fail("required invariants not enabled: " + ", ".join(missing))

    print(f"AUTHORITY_INTEGRITY_PASS authorities={len(authorities)} logical_ids={len(logical_ids)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
