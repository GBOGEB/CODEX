#!/usr/bin/env python3
"""Resolve CODEX SSOT logical IDs through the canonical root manifest.

This module is the single resolver implementation. Compatibility imports may
re-export it, but consumers must resolve logical IDs rather than hard-coded
authority paths. Remote authorities are references and never writable local
engineering truth.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "ssot" / "manifest.yaml"


class SsotResolutionError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    if not path.is_file():
        raise SsotResolutionError(f"MISSING_MANIFEST:{path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SsotResolutionError("INVALID_MANIFEST_ROOT")
    return data


def resolve_ssot(
    logical_id: str,
    manifest_path: Path = DEFAULT_MANIFEST,
    *,
    require_local: bool = False,
) -> dict[str, Any]:
    """Resolve exactly one active authority by logical ID and fail closed."""
    manifest = load_manifest(manifest_path)
    authorities = manifest.get("authorities", {})
    if not isinstance(authorities, dict):
        raise SsotResolutionError("INVALID_AUTHORITIES")

    matches = []
    for key, node in authorities.items():
        if isinstance(node, dict) and node.get("logical_id") == logical_id:
            matches.append((key, node))

    if not matches:
        raise SsotResolutionError(f"UNKNOWN_ID:{logical_id}")
    if len(matches) != 1:
        raise SsotResolutionError(f"DUPLICATE_AUTHORITY:{logical_id}:{len(matches)}")

    key, node = matches[0]
    if node.get("lifecycle", "ACTIVE") != "ACTIVE":
        raise SsotResolutionError(f"NON_ACTIVE_AUTHORITY:{logical_id}")

    authority_class = str(node.get("authority_class", ""))
    if authority_class not in {"LOCAL_AUTHORITATIVE", "REMOTE_AUTHORITATIVE"}:
        raise SsotResolutionError(f"INVALID_AUTHORITY_CLASS:{logical_id}")

    if require_local and authority_class == "REMOTE_AUTHORITATIVE":
        raise SsotResolutionError(f"REMOTE_AUTHORITY:{logical_id}")

    writable = authority_class == "LOCAL_AUTHORITATIVE"
    mutation_allowed = node.get("mutation_allowed", writable)
    if authority_class == "REMOTE_AUTHORITATIVE" and mutation_allowed is not False:
        raise SsotResolutionError(f"REMOTE_MUTATION_ALLOWED:{logical_id}")

    result: dict[str, Any] = {
        "key": key,
        "logical_id": logical_id,
        "authority_class": authority_class,
        "owner": node.get("owner") or node.get("owner_repository"),
        "mutation_allowed": mutation_allowed,
        "writable": writable,
    }
    if node.get("owner_repository"):
        result["owner_repository"] = node["owner_repository"]

    raw_path = node.get("path")
    if raw_path:
        resolved = ROOT / str(raw_path)
        if not resolved.is_file():
            raise SsotResolutionError(f"MISSING_FILE:{logical_id}:{raw_path}")
        result.update({
            "path": str(raw_path),
            "resolved_path": str(resolved),
            "sha256": _sha256(resolved),
        })
    elif authority_class != "REMOTE_AUTHORITATIVE":
        raise SsotResolutionError(f"MISSING_FILE:{logical_id}:no-path")

    if node.get("schema"):
        schema_path = ROOT / str(node["schema"])
        if not schema_path.is_file():
            raise SsotResolutionError(f"MISSING_SCHEMA:{logical_id}:{node['schema']}")
        result["schema"] = str(node["schema"])
        result["schema_sha256"] = _sha256(schema_path)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logical_id")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--require-local", action="store_true")
    args = parser.parse_args()
    try:
        result = resolve_ssot(
            args.logical_id,
            args.manifest,
            require_local=args.require_local,
        )
    except SsotResolutionError as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps({"status": "PASS", "node": result}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
