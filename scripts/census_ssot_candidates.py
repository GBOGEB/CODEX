#!/usr/bin/env python3
"""Inventory, classify and bind governed CODEX 2.0 SSOT candidates.

Classification is evidence, not authority. Authority is established only by the
canonical manifest. The logical-ID registry may identify governed consumers and
compatibility surfaces but can never promote them into authority.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", "node_modules", ".venv", "venv", "dist", "build"}
TEXT_SUFFIXES = {".yaml", ".yml", ".json", ".ts", ".js", ".py"}
SSOT_TOKENS = ("ssot", "schema", "contract", "registry", "receipt", "manifest", "runtime", "federation", "agent", "mcp")


def candidate_class(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix().lower()
    name = path.name.lower()
    if "/receipts/" in f"/{rel}" or "receipt" in name:
        return "RECEIPT_CANDIDATE"
    if "schema" in rel:
        return "SCHEMA_CANDIDATE"
    if rel.startswith(("ssot/", "semantic_substrate/", "governance/policy/")):
        return "AUTHORITY_CANDIDATE"
    return "CONSUMER_OR_CONTRACT_CANDIDATE"


def infer_role(rel: str, cls: str) -> tuple[str, str, str]:
    lower = rel.lower()
    if cls == "RECEIPT_CANDIDATE":
        return "RECEIPT", "CODEX", "INFERRED"
    if cls == "SCHEMA_CANDIDATE":
        return "CONTRACT", "CODEX", "INFERRED"
    if lower.startswith(("semantic_substrate/", "governance/policy/", "ssot/")):
        return "LOCAL_AUTHORITY_CANDIDATE", "CODEX", "INFERRED"
    if any(token in lower for token in ("qps", "cryoplant")):
        return "REMOTE_ENGINEERING_REFERENCE_CANDIDATE", "GBOGEB/cryoplant-project", "INFERRED"
    if any(token in lower for token in ("abacus", "dow")):
        return "REMOTE_CHALLENGE_REFERENCE_CANDIDATE", "GBOGEB/ABACUS", "INFERRED"
    if any(token in lower for token in ("runtime", "mcp", "agent")):
        return "EXECUTABLE_CONSUMER_CANDIDATE", "CODEX", "INFERRED"
    return "UNCLASSIFIED", "UNCLASSIFIED", "UNCLASSIFIED"


def lifecycle(rel: str) -> str:
    lower = rel.lower()
    if any(token in lower for token in ("archive/", "historical/", "legacy/", "deprecated/")):
        return "HISTORICAL_OR_LEGACY_CANDIDATE"
    if any(token in lower for token in ("generated/", "output/", "reports/")):
        return "GENERATED_OR_DERIVED_CANDIDATE"
    return "ACTIVE_CANDIDATE"


def load_declared_ids() -> dict[str, dict[str, str]]:
    bindings: dict[str, dict[str, str]] = {}
    manifest = yaml.safe_load((ROOT / "ssot/manifest.yaml").read_text(encoding="utf-8")) or {}
    for section in ("authorities", "derived_or_compatibility"):
        for node in (manifest.get(section) or {}).values():
            path = node.get("path")
            logical_id = node.get("logical_id")
            if path and logical_id:
                bindings[path] = {
                    "logical_id": logical_id,
                    "logical_id_status": "DECLARED_AUTHORITY" if section == "authorities" else "DECLARED_VIEW_OR_COMPATIBILITY",
                }
    registry_path = ROOT / "ssot/registry/logical_id_registry.yaml"
    if registry_path.exists():
        registry = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
        for logical_id, node in (registry.get("nodes") or {}).items():
            path = node.get("path")
            if path:
                if path in bindings and bindings[path]["logical_id"] != logical_id:
                    raise ValueError(f"duplicate logical ID binding for {path}")
                bindings[path] = {"logical_id": logical_id, "logical_id_status": "DECLARED_GOVERNED_NODE"}
    return bindings


def main() -> int:
    bindings = load_declared_ids()
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
        cls = candidate_class(path)
        authority, owner, confidence = infer_role(rel_text, cls)
        data = path.read_bytes()
        binding = bindings.get(rel_text, {"logical_id": None, "logical_id_status": "UNRESOLVED"})
        rows.append({
            "path": rel_text,
            "suffix": path.suffix.lower(),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "candidate_class": cls,
            "authority_classification": authority,
            "owner_classification": owner,
            "classification_confidence": confidence,
            "lifecycle_state": lifecycle(rel_text),
            **binding,
        })

    def tally(field: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in rows:
            value = str(row[field])
            counts[value] = counts.get(value, 0) + 1
        return dict(sorted(counts.items()))

    classified = sum(row["classification_confidence"] != "UNCLASSIFIED" for row in rows)
    resolved = sum(row["logical_id"] is not None for row in rows)
    report = {
        "schema_version": "2.1",
        "purpose": "CODEX_2_0_SSOT_CLASSIFICATION_AND_ID_CENSUS",
        "constitutional_rule": "classification and governed IDs do not establish authority",
        "candidate_count": len(rows),
        "classified_candidate_count": classified,
        "classification_penetration_pct": round((classified / len(rows) * 100) if rows else 0.0, 2),
        "logical_id_resolved_count": resolved,
        "logical_id_penetration_pct": round((resolved / len(rows) * 100) if rows else 0.0, 2),
        "declared_binding_count": len(bindings),
        "counts": {
            "candidate_class": tally("candidate_class"),
            "authority_classification": tally("authority_classification"),
            "owner_classification": tally("owner_classification"),
            "classification_confidence": tally("classification_confidence"),
            "lifecycle_state": tally("lifecycle_state"),
            "logical_id_status": tally("logical_id_status"),
        },
        "candidates": rows,
    }
    out = ROOT / "reports" / "codex_2_0_ssot_candidate_census.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        "SSOT_CENSUS_PASS "
        f"candidates={len(rows)} classified={classified} resolved={resolved} "
        f"classification_penetration={report['classification_penetration_pct']}% "
        f"id_penetration={report['logical_id_penetration_pct']}% "
        f"output={out.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
