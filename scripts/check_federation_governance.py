#!/usr/bin/env python3
"""Federation governance bridge health-check.

Reports on the real-code vs scaffold status across CODEX, ABACUS, and the
MCP bridge layer.  Intended as both a local utility and a CI step in
.github/workflows/full-stack-governance.yml.

Exit codes:
  0 – all checks passed
  1 – one or more checks failed
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Inventory: real executable code vs scaffold/documentation stubs
# ---------------------------------------------------------------------------
REAL_CODE: list[tuple[str, str]] = [
    ("federation_runtime/engines/governance_parser.py", "PR-007 governance header parser"),
    ("federation_runtime/schema/governance_header.schema.json", "governance header JSON schema"),
    ("federation_runtime/governance/traceability_manifest.json", "W003 traceability manifest"),
    ("federation_runtime/governance/pr_track.yml", "PR stream order tracker"),
    ("federation_runtime/governance/wave_recreation_plan.yml", "wave execution plan"),
    ("federation_runtime/contracts/mcp_runtime_directive.yml", "MCP ingress contract"),
    ("tests/test_governance_parser.py", "governance parser tests"),
    (".github/workflows/w003-governance-gate.yml", "W003 root governance gate CI"),
    (".github/workflows/full-stack-governance.yml", "CODEX/ABACUS/bridge stack CI"),
    ("docs/wave_packages/runtime/federation_bridge_cli.py", "federation bridge CLI"),
    ("docs/wave_packages/runtime/federation_repo_coverage.py", "federation repo coverage report"),
    ("bridge_manifest.yaml", "CODEX↔ABACUS bridge manifest"),
    ("abacus_render_pipeline/A6_renderer_governance/TUPLE_OFFLOAD/tuple_offload_executor.py", "tuple offload executor"),
]

SCAFFOLD_ONLY: list[tuple[str, str]] = [
    (
        "output/federation_bridge",
        "deprecated output namespace; canonical path is outputs/html/federation_bridge/ (generated in CI)",
    ),
]


def _check_paths(entries: list[tuple[str, str]], label: str) -> list[str]:
    """Return list of error strings for missing paths."""
    missing = []
    for rel_path, description in entries:
        path = ROOT / rel_path
        if not path.exists():
            missing.append(f"  MISSING  [{label}] {rel_path}  ({description})")
    return missing


def _validate_governance_parser() -> list[str]:
    """Ensure the parser compiles and the schema is valid JSON."""
    errors: list[str] = []
    parser_path = ROOT / "federation_runtime" / "engines" / "governance_parser.py"
    schema_path = ROOT / "federation_runtime" / "schema" / "governance_header.schema.json"

    if not parser_path.exists():
        return [f"  MISSING  governance parser: {parser_path}"]

    import py_compile
    try:
        py_compile.compile(str(parser_path), doraise=True)
    except py_compile.PyCompileError as exc:
        errors.append(f"  SYNTAX ERROR  governance_parser.py: {exc}")

    if schema_path.exists():
        try:
            json.loads(schema_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"  JSON ERROR  governance_header.schema.json: {exc}")
    return errors


def _validate_bridge_manifest() -> list[str]:
    """Confirm bridge manifest declares both CODEX and ABACUS repos.

    Checks for top-level or nested ``codex:`` and ``abacus:`` YAML keys
    (case-insensitive) so that superficial mentions in comments do not
    satisfy the assertion.
    """
    errors: list[str] = []
    manifest_path = ROOT / "bridge_manifest.yaml"
    if not manifest_path.exists():
        return [f"  MISSING  bridge_manifest.yaml at {manifest_path}"]
    text = manifest_path.read_text(encoding="utf-8")
    import re
    for required_key in ("codex", "abacus"):
        # Match a YAML key (possibly indented) followed by a colon
        if not re.search(rf"^\s*{re.escape(required_key)}\s*:", text, re.IGNORECASE | re.MULTILINE):
            errors.append(f"  MISSING  bridge_manifest.yaml does not define a '{required_key}:' key")
    return errors


def main() -> int:
    print("=" * 60)
    print("Federation Governance Bridge Audit")
    print(f"Root: {ROOT}")
    print("=" * 60)

    all_errors: list[str] = []

    # 1. Real-code inventory
    print("\n[1] Real executable artifacts:")
    real_missing = _check_paths(REAL_CODE, "real")
    for path, desc in REAL_CODE:
        status = "✓" if (ROOT / path).exists() else "✗"
        print(f"  {status}  {path}  ({desc})")
    all_errors.extend(real_missing)

    # 2. Scaffold inventory (informational – not a failure)
    print("\n[2] Known scaffold/documentation stubs (informational):")
    for path, desc in SCAFFOLD_ONLY:
        status = "~" if (ROOT / path).exists() else "○"
        print(f"  {status}  {path}")
        print(f"       {desc}")

    # 3. Deeper parser + schema validation
    print("\n[3] Governance parser syntax & schema integrity:")
    parser_errors = _validate_governance_parser()
    if parser_errors:
        all_errors.extend(parser_errors)
        for e in parser_errors:
            print(e)
    else:
        print("  ✓  governance_parser.py compiles cleanly")
        print("  ✓  governance_header.schema.json is valid JSON")

    # 4. Bridge manifest validation
    print("\n[4] Bridge manifest CODEX↔ABACUS declarations:")
    bridge_errors = _validate_bridge_manifest()
    if bridge_errors:
        all_errors.extend(bridge_errors)
        for e in bridge_errors:
            print(e)
    else:
        print("  ✓  bridge_manifest.yaml references both codex and abacus")

    print("\n" + "=" * 60)
    if all_errors:
        print(f"RESULT: FAIL  ({len(all_errors)} issue(s))")
        for e in all_errors:
            print(e)
        return 1

    print(f"RESULT: PASS  ({len(REAL_CODE)} real artifacts verified, {len(SCAFFOLD_ONLY)} stubs noted)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
