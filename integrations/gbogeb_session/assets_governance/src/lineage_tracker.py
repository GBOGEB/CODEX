#!/usr/bin/env python3
"""
Lineage Tracker — GBOGEB/CODEX (GBC)
======================================

Manages the lineage_manifest.json for visual asset traceability:
  • Add/update asset entries with SHA256 hashes
  • Track version history and previous hashes
  • Cross-reference with GBA (GBOGEB/ABACUS) manifest
  • Generate lineage reports
  • Validate manifest integrity

Usage:
    python lineage_tracker.py --add assets/canonical/cryomodule_schematic.svg
    python lineage_tracker.py --status
    python lineage_tracker.py --validate
    python lineage_tracker.py --export lineage_report.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Import from sibling module
try:
    from src.asset_validator import sha256_hash, get_mime_type, now_iso, get_git_commit
except ImportError:
    # Direct execution fallback
    sys.path.insert(0, str(Path(__file__).parent))
    from asset_validator import sha256_hash, get_mime_type, now_iso, get_git_commit


# ============================================================================
# Constants
# ============================================================================
DEFAULT_MANIFEST_PATH: str = "lineage_manifest.json"
MANIFEST_VERSION: str = "1.0.0"


# ============================================================================
# Manifest CRUD
# ============================================================================

def load_manifest(path: str | Path = DEFAULT_MANIFEST_PATH) -> dict[str, Any]:
    """Load or initialize the lineage manifest."""
    p = Path(path)
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "version": MANIFEST_VERSION,
        "last_updated": now_iso(),
        "repository": "GBOGEB/CODEX",
        "assets": [],
        "lineage": [],
    }


def save_manifest(
    manifest: dict[str, Any],
    path: str | Path = DEFAULT_MANIFEST_PATH,
) -> None:
    """Write manifest to disk with updated timestamp."""
    manifest["last_updated"] = now_iso()
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def find_asset(manifest: dict[str, Any], filename: str) -> dict[str, Any] | None:
    """Find an asset entry by filename."""
    for asset in manifest.get("assets", []):
        if asset.get("filename") == filename:
            return asset
    return None


def add_asset(
    manifest: dict[str, Any],
    filepath: str | Path,
    *,
    category: str = "visual_asset",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """
    Add or update an asset in the manifest.

    If the asset already exists and its hash changed, the old hash is
    recorded in previous_sha256 and updated_at is set.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Asset not found: {path}")

    new_hash = sha256_hash(path)
    existing = find_asset(manifest, path.name)

    if existing:
        # Update existing entry
        old_hash = existing.get("sha256", "")
        if old_hash != new_hash:
            existing["previous_sha256"] = old_hash
            existing["sha256"] = new_hash
            existing["file_size"] = path.stat().st_size
            existing["updated_at"] = now_iso()
            existing["git_commit"] = get_git_commit()
            existing["processing_status"] = "updated"
        return existing
    else:
        # New entry
        entry = {
            "filename": path.name,
            "sha256": new_hash,
            "file_size": path.stat().st_size,
            "mime_type": get_mime_type(path),
            "category": category,
            "tags": tags or [],
            "ingested_at": now_iso(),
            "git_commit": get_git_commit(),
            "processing_status": "verified",
            "canonical_path": str(path),
            "mock_file": f"{path.name}.mock",
        }
        manifest["assets"].append(entry)
        return entry


def add_lineage_edge(
    manifest: dict[str, Any],
    source_file: str,
    target_file: str,
    relation: str = "derived_from",
    description: str = "",
) -> None:
    """Add a lineage edge tracking a derivation relationship."""
    edge = {
        "source": source_file,
        "target": target_file,
        "relation": relation,
        "description": description,
        "created_at": now_iso(),
    }
    manifest.setdefault("lineage", []).append(edge)


# ============================================================================
# Validation
# ============================================================================

def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    """
    Validate manifest integrity.

    Checks:
      1. Required top-level fields
      2. Asset entries have required fields
      3. SHA256 hashes are 64-char hex
      4. No duplicate filenames
    """
    errors: list[str] = []

    # Top-level structure
    required_top = {"version", "last_updated", "assets"}
    missing_top = required_top - set(manifest.keys())
    if missing_top:
        errors.append(f"Missing top-level fields: {missing_top}")

    # Asset entries
    required_asset = {"filename", "sha256", "file_size", "processing_status"}
    seen_files: set[str] = set()

    for i, asset in enumerate(manifest.get("assets", [])):
        missing = required_asset - set(asset.keys())
        if missing:
            errors.append(f"Asset [{i}] missing fields: {missing}")

        sha = asset.get("sha256", "")
        if len(sha) != 64:
            errors.append(f"Asset [{i}] SHA256 wrong length: {len(sha)} (expected 64)")

        fname = asset.get("filename", "")
        if fname in seen_files:
            errors.append(f"Duplicate filename: {fname}")
        seen_files.add(fname)

    return errors


def verify_hashes(manifest: dict[str, Any], base_dir: str | Path = ".") -> list[str]:
    """
    Verify that stored SHA256 hashes match actual files on disk.
    Returns list of mismatches.
    """
    mismatches: list[str] = []
    base = Path(base_dir)

    for asset in manifest.get("assets", []):
        canonical = asset.get("canonical_path", "")
        if not canonical:
            continue
        fpath = base / canonical
        if not fpath.exists():
            mismatches.append(f"File not found: {canonical}")
            continue
        actual_hash = sha256_hash(fpath)
        if actual_hash != asset.get("sha256", ""):
            mismatches.append(
                f"Hash mismatch for {asset['filename']}: "
                f"manifest={asset['sha256'][:12]}... actual={actual_hash[:12]}..."
            )

    return mismatches


# ============================================================================
# Reporting
# ============================================================================

def generate_report(manifest: dict[str, Any]) -> dict[str, Any]:
    """Generate a summary report from the manifest."""
    assets = manifest.get("assets", [])
    lineage = manifest.get("lineage", [])

    categories: dict[str, int] = {}
    statuses: dict[str, int] = {}
    total_size = 0

    for a in assets:
        cat = a.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
        st = a.get("processing_status", "unknown")
        statuses[st] = statuses.get(st, 0) + 1
        total_size += a.get("file_size", 0)

    return {
        "summary": {
            "total_assets": len(assets),
            "total_size_bytes": total_size,
            "total_size_kb": round(total_size / 1024, 1),
            "total_lineage_edges": len(lineage),
            "categories": categories,
            "statuses": statuses,
            "manifest_version": manifest.get("version", "unknown"),
            "last_updated": manifest.get("last_updated", "unknown"),
        },
        "assets": assets,
        "lineage": lineage,
    }


# ============================================================================
# CLI
# ============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="GBOGEB/CODEX — Lineage Tracker"
    )
    parser.add_argument(
        "--manifest", type=Path, default=Path(DEFAULT_MANIFEST_PATH),
        help=f"Manifest path (default: {DEFAULT_MANIFEST_PATH})",
    )
    parser.add_argument("--add", type=Path, help="Add/update an asset in the manifest")
    parser.add_argument("--category", default="visual_asset", help="Asset category")
    parser.add_argument("--tags", nargs="*", default=[], help="Asset tags")
    parser.add_argument("--status", action="store_true", help="Show manifest status")
    parser.add_argument("--validate", action="store_true", help="Validate manifest integrity")
    parser.add_argument("--verify-hashes", action="store_true", help="Verify file hashes against manifest")
    parser.add_argument("--export", type=Path, help="Export lineage report to JSON")
    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════════╗")
    print("║  GBOGEB/CODEX — Lineage Tracker                     ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    manifest = load_manifest(args.manifest)

    if args.add:
        entry = add_asset(manifest, args.add, category=args.category, tags=args.tags)
        save_manifest(manifest, args.manifest)
        print(f"  ✓ Added: {entry['filename']} ({entry['sha256'][:12]}...)")
        print(f"    Status: {entry['processing_status']}")

    elif args.status:
        report = generate_report(manifest)
        s = report["summary"]
        print(f"  Manifest:    {args.manifest}")
        print(f"  Version:     {s['manifest_version']}")
        print(f"  Last updated: {s['last_updated']}")
        print(f"  Assets:      {s['total_assets']}")
        print(f"  Total size:  {s['total_size_kb']} KB")
        print(f"  Lineage:     {s['total_lineage_edges']} edges")
        if s["categories"]:
            print(f"  Categories:  {s['categories']}")
        if s["statuses"]:
            print(f"  Statuses:    {s['statuses']}")

    elif args.validate:
        errors = validate_manifest(manifest)
        if errors:
            print("  ✗ Validation FAILED:")
            for e in errors:
                print(f"    - {e}")
            sys.exit(1)
        else:
            print("  ✓ Manifest is valid")

    elif args.verify_hashes:
        mismatches = verify_hashes(manifest)
        if mismatches:
            print("  ✗ Hash verification FAILED:")
            for m in mismatches:
                print(f"    - {m}")
            sys.exit(1)
        else:
            print("  ✓ All hashes verified")

    elif args.export:
        report = generate_report(manifest)
        args.export.parent.mkdir(parents=True, exist_ok=True)
        with open(args.export, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"  ✓ Report exported: {args.export}")

    else:
        parser.print_help()

    sys.exit(0)


if __name__ == "__main__":
    main()
