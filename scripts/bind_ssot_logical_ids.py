#!/usr/bin/env python3
"""Bind declared authority logical IDs into the W03 census without promoting inference."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import yaml
ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "ssot" / "registry" / "authority_registry.yaml"
CENSUS = ROOT / "reports" / "codex_2_0_ssot_candidate_census.json"
OUT = ROOT / "reports" / "codex_2_0_ssot_bound_census.json"
def mapping(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(value, dict): raise SystemExit(f"BIND_FAIL invalid mapping {path}")
    return value
def main() -> int:
    if not CENSUS.exists(): raise SystemExit("BIND_FAIL census missing")
    census = json.loads(CENSUS.read_text(encoding="utf-8")); rows = census.get("candidates") or []
    nodes = mapping(REGISTRY).get("nodes") or {}; by_path = {}; remote = []
    for logical_id, node in nodes.items():
        if not isinstance(node, dict): continue
        path = node.get("path")
        if path:
            key = str(path).replace("\\", "/")
            if key in by_path: raise SystemExit(f"BIND_FAIL duplicate declared path {key}")
            by_path[key] = (str(logical_id), node)
        elif node.get("authority_class") == "REMOTE_AUTHORITATIVE": remote.append(str(logical_id))
    bound = 0
    for row in rows:
        match = by_path.get(str(row.get("path", "")))
        if not match: continue
        logical_id, node = match; row["logical_id"] = logical_id; row["logical_id_status"] = "DECLARED"
        row["authority_classification"] = node.get("authority_class"); row["owner_classification"] = node.get("owner")
        row["classification_confidence"] = "DECLARED"; bound += 1
    result = {**{k:v for k,v in census.items() if k != "candidates"}, "binding": {
        "declared_registry_nodes": len(nodes), "declared_local_path_nodes": len(by_path), "declared_remote_nodes": len(remote),
        "bound_local_candidates": bound, "unresolved_candidate_count": len(rows)-bound,
        "logical_id_penetration_pct": round(bound/len(rows)*100 if rows else 0, 2), "remote_logical_ids": sorted(remote),
        "note": "remote authority IDs intentionally have no writable local census path"}, "candidates": rows}
    OUT.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(f"SSOT_BIND_PASS candidates={len(rows)} bound_local={bound} remote_declared={len(remote)} unresolved={len(rows)-bound}")
    return 0
if __name__ == "__main__": raise SystemExit(main())
