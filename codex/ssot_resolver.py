"""Shared CODEX SSOT authority resolver.

Engineering-aware, engineering-non-authoritative: remote engineering nodes are
resolved as references and never returned as writable local authorities.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "ssot" / "registry" / "authority_registry.yaml"


class SSOTResolutionError(RuntimeError):
    pass


def _load_registry() -> dict[str, Any]:
    if not REGISTRY.exists():
        raise SSOTResolutionError("MISSING_AUTHORITY_REGISTRY")
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    nodes = data.get("nodes")
    if not isinstance(nodes, dict):
        raise SSOTResolutionError("INVALID_AUTHORITY_REGISTRY")
    return nodes


def resolve_ssot(logical_id: str, *, require_local: bool = False) -> dict[str, Any]:
    nodes = _load_registry()
    node = nodes.get(logical_id)
    if not isinstance(node, dict):
        raise SSOTResolutionError(f"UNKNOWN_ID:{logical_id}")

    authority_class = node.get("authority_class")
    if authority_class not in {"LOCAL_AUTHORITATIVE", "REMOTE_AUTHORITATIVE"}:
        raise SSOTResolutionError(f"INVALID_AUTHORITY_CLASS:{logical_id}")

    if node.get("lifecycle") != "ACTIVE":
        raise SSOTResolutionError(f"NON_ACTIVE_AUTHORITY:{logical_id}")

    if authority_class == "REMOTE_AUTHORITATIVE":
        if require_local:
            raise SSOTResolutionError(f"REMOTE_AUTHORITY:{logical_id}")
        if logical_id == "QPS_ENGINEERING_TRUTH" and node.get("mutation_allowed") is not False:
            raise SSOTResolutionError("REMOTE_ENGINEERING_MUTATION_NOT_FORBIDDEN")
        return {"logical_id": logical_id, **node, "writable": False}

    path = node.get("path")
    if not path:
        raise SSOTResolutionError(f"MISSING_PATH:{logical_id}")
    resolved = ROOT / str(path)
    if not resolved.exists():
        raise SSOTResolutionError(f"MISSING_FILE:{logical_id}:{path}")
    return {"logical_id": logical_id, **node, "resolved_path": str(resolved), "writable": True}
