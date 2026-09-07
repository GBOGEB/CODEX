#!/usr/bin/env python3
"""Inventory non-binary SSOT candidates for CODEX 2.0 convergence."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", "node_modules", ".venv", "venv", "dist", "build"}
TEXT_SUFFIXES = {".yaml", ".yml", ".json", ".ts", ".js", ".py"}
SSOT_TOKENS = ("ssot", "schema", "contract", "registry", "receipt", "manifest", "runtime", "federation", "agent", "mcp")


def classify(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix().lower()
    name = path.name.lower()
    if "/receipts/" in f"/{rel}" or "receipt" in name:
        return "RECEIPT_CANDIDATE"
    if "schema" in rel:
        return "SCHEMA_CANDIDATE"
    if rel.startswith("ssot/") or rel.startswith("semantic_substrate/") or rel.startswith("governance/policy/"):
        return "AUTHORITY_CANDIDATE"
    if rel.startswith("SSOT/".lower()):
        return "AUTHORITY_CANDIDATE"
    return "CONSUMER_OR_CONTRACT_CANDIDATE"


def main() -> int:
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        rel = path.relative_to(ROOT)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        rel_text = rel.as_posix()
        lower = rel_text.lower()
        if not any(token in lower for token in SSOT_TOKENS):
            continue
        rows.append({
            "path": rel_text,
            "suffix": path.suffix.lower(),
            "bytes": path.stat().st_size,
            "candidate_class": classify(path),
            "authority": "UNCLASSIFIED",
            "owner": "UNCLASSIFIED",
            "logical_id": None,
        })

    counts = {}
    for row in rows:
        counts[row["candidate_class"]] = counts.get(row["candidate_class"], 0) + 1

    report = {
        "schema_version": "1.0",
        "purpose": "CODEX_2_0_SSOT_DISCOVERY",
        "candidate_count": len(rows),
        "counts": counts,
        "candidates": rows,
    }
    out = ROOT / "reports" / "codex_2_0_ssot_candidate_census.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"SSOT_CENSUS_PASS candidates={len(rows)} output={out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
