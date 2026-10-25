#!/usr/bin/env python3
"""
Asset Validator — GBOGEB/CODEX (GBC)
======================================

Binary and SVG asset validation engine providing:
  • SHA256 hash generation for integrity verification
  • .mock sidecar file creation (mirrors GBA verification_hook pattern)
  • File format and size validation
  • Metadata extraction from SVG files
  • Integration with lineage_tracker for manifest updates

Usage:
    python asset_validator.py --input-dir assets/canonical/
    python asset_validator.py --verify assets/canonical/cryomodule_schematic.svg
    python asset_validator.py --status
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ALLOWED_EXTENSIONS: set[str] = {".svg", ".png", ".drawio", ".jpg", ".jpeg", ".pdf"}
MAX_FILE_SIZE_KB: int = 500
HASH_ALGORITHM: str = "SHA256"
MOCK_EXTENSION: str = ".mock"
MANIFEST_FILENAME: str = "lineage_manifest.json"

# ---------------------------------------------------------------------------
# Core Functions
# ---------------------------------------------------------------------------

def sha256_hash(filepath: str | Path) -> str:
    """Compute SHA256 hex digest for a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def now_iso() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_mime_type(filepath: str | Path) -> str:
    """Infer MIME type from file extension."""
    mime, _ = mimetypes.guess_type(str(filepath))
    if mime:
        return mime
    ext = Path(filepath).suffix.lower()
    mime_map = {
        ".svg": "image/svg+xml",
        ".drawio": "application/xml",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".pdf": "application/pdf",
    }
    return mime_map.get(ext, "application/octet-stream")


def get_git_commit() -> str:
    """Get current git HEAD commit hash, or 'unknown'."""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def extract_svg_metadata(filepath: str | Path) -> dict[str, Any]:
    """Extract basic metadata from an SVG file."""
    meta: dict[str, Any] = {"has_viewbox": False, "has_title": False, "id_count": 0}
    try:
        content = Path(filepath).read_text(encoding="utf-8")
        meta["has_viewbox"] = bool(re.search(r'viewBox\s*=', content))
        meta["has_title"] = bool(re.search(r'<title\b', content))
        meta["id_count"] = len(re.findall(r'\bid\s*=\s*"', content))
        # Extract dimensions
        w_match = re.search(r'width\s*=\s*"(\d+)', content)
        h_match = re.search(r'height\s*=\s*"(\d+)', content)
        if w_match:
            meta["width"] = int(w_match.group(1))
        if h_match:
            meta["height"] = int(h_match.group(1))
        vb_match = re.search(r'viewBox\s*=\s*"([^"]+)"', content)
        if vb_match:
            meta["viewbox"] = vb_match.group(1)
    except Exception:
        pass
    return meta


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class ValidationResult:
    """Structured validation result."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.sha256: str = ""
        self.file_size: int = 0
        self.mime_type: str = ""
        self.svg_metadata: dict[str, Any] = {}

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "filepath": self.filepath,
            "passed": self.passed,
            "sha256": self.sha256,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "errors": self.errors,
            "warnings": self.warnings,
            "svg_metadata": self.svg_metadata,
        }


def validate_asset(filepath: str | Path) -> ValidationResult:
    """
    Validate a visual asset file.

    Checks:
      1. File exists
      2. Extension is in ALLOWED_EXTENSIONS
      3. File size ≤ MAX_FILE_SIZE_KB
      4. SHA256 hash computable
      5. SVG-specific: has viewBox, has <title>
    """
    path = Path(filepath)
    result = ValidationResult(str(path))

    # Existence
    if not path.exists():
        result.errors.append(f"File not found: {path}")
        return result

    # Extension
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        result.errors.append(
            f"Unsupported extension '{path.suffix}'. "
            f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Size
    result.file_size = path.stat().st_size
    size_kb = result.file_size / 1024
    if size_kb > MAX_FILE_SIZE_KB:
        result.warnings.append(
            f"File size {size_kb:.1f} KB exceeds recommended max {MAX_FILE_SIZE_KB} KB"
        )

    # Hash
    try:
        result.sha256 = sha256_hash(path)
    except Exception as e:
        result.errors.append(f"Hash computation failed: {e}")

    # MIME
    result.mime_type = get_mime_type(path)

    # SVG-specific checks
    if path.suffix.lower() == ".svg":
        meta = extract_svg_metadata(path)
        result.svg_metadata = meta
        if not meta.get("has_viewbox"):
            result.warnings.append("SVG missing viewBox attribute")
        if not meta.get("has_title"):
            result.warnings.append("SVG missing <title> element (accessibility)")

    return result


# ---------------------------------------------------------------------------
# Mock Sidecar Creation
# ---------------------------------------------------------------------------

def create_mock_sidecar(
    filepath: str | Path,
    output_dir: str | Path | None = None,
) -> Path:
    """
    Create a .mock JSON sidecar file for a validated asset.

    The sidecar contains immutable metadata:
      - filename, sha256, file_size, mime_type
      - ingested_at, git_commit, processing_status
      - svg_metadata (if applicable)
    """
    path = Path(filepath)
    vr = validate_asset(path)

    if output_dir:
        mock_dir = Path(output_dir)
    else:
        mock_dir = path.parent

    mock_dir.mkdir(parents=True, exist_ok=True)
    mock_path = mock_dir / f"{path.name}{MOCK_EXTENSION}"

    sidecar = {
        "filename": path.name,
        "sha256": vr.sha256,
        "file_size": vr.file_size,
        "mime_type": vr.mime_type,
        "ingested_at": now_iso(),
        "git_commit": get_git_commit(),
        "processing_status": "verified" if vr.passed else "failed",
        "validation_errors": vr.errors,
        "validation_warnings": vr.warnings,
    }

    if vr.svg_metadata:
        sidecar["svg_metadata"] = vr.svg_metadata

    with open(mock_path, "w", encoding="utf-8") as f:
        json.dump(sidecar, f, indent=2)

    return mock_path


# ---------------------------------------------------------------------------
# Batch Processing
# ---------------------------------------------------------------------------

def process_directory(
    input_dir: str | Path,
    output_dir: str | Path | None = None,
) -> list[ValidationResult]:
    """
    Process all visual assets in a directory.

    Returns list of ValidationResult objects.
    """
    input_path = Path(input_dir)
    if not input_path.is_dir():
        print(f"ERROR: Not a directory: {input_path}", file=sys.stderr)
        return []

    results: list[ValidationResult] = []
    for fpath in sorted(input_path.iterdir()):
        if fpath.is_file() and fpath.suffix.lower() in ALLOWED_EXTENSIONS:
            vr = validate_asset(fpath)
            results.append(vr)
            create_mock_sidecar(fpath, output_dir)
            status = "✓ PASS" if vr.passed else "✗ FAIL"
            print(f"  {status}  {fpath.name}  ({vr.sha256[:12]}...)")

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="GBOGEB/CODEX — Asset Validator"
    )
    parser.add_argument(
        "--input-dir", type=Path,
        help="Directory containing assets to validate",
    )
    parser.add_argument(
        "--verify", type=Path,
        help="Validate a single asset file",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=None,
        help="Output directory for .mock sidecar files",
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Show validation summary",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output results as JSON",
    )
    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════════╗")
    print("║  GBOGEB/CODEX — Asset Validator                     ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    if args.verify:
        vr = validate_asset(args.verify)
        if args.json:
            print(json.dumps(vr.to_dict(), indent=2))
        else:
            status = "PASS" if vr.passed else "FAIL"
            print(f"  File:    {vr.filepath}")
            print(f"  Status:  {status}")
            print(f"  SHA256:  {vr.sha256}")
            print(f"  Size:    {vr.file_size} bytes")
            print(f"  MIME:    {vr.mime_type}")
            if vr.errors:
                for e in vr.errors:
                    print(f"  ERROR:   {e}")
            if vr.warnings:
                for w in vr.warnings:
                    print(f"  WARN:    {w}")
            if vr.svg_metadata:
                print(f"  SVG:     viewBox={vr.svg_metadata.get('has_viewbox')}, "
                      f"title={vr.svg_metadata.get('has_title')}, "
                      f"IDs={vr.svg_metadata.get('id_count', 0)}")
        mock = create_mock_sidecar(args.verify, args.output_dir)
        print(f"\n  Mock:    {mock}")

    elif args.input_dir:
        print(f"Processing: {args.input_dir}\n")
        results = process_directory(args.input_dir, args.output_dir)
        passed = sum(1 for r in results if r.passed)
        print(f"\n  Total: {len(results)}, Passed: {passed}, Failed: {len(results) - passed}")
        if args.json:
            print(json.dumps([r.to_dict() for r in results], indent=2))

    elif args.status:
        # Show manifest status
        manifest_path = Path("lineage_manifest.json")
        if manifest_path.exists():
            data = json.loads(manifest_path.read_text())
            print(f"  Manifest version: {data.get('version', 'unknown')}")
            print(f"  Assets tracked:   {len(data.get('assets', []))}")
            print(f"  Last updated:     {data.get('last_updated', 'unknown')}")
        else:
            print("  No lineage_manifest.json found.")

    else:
        parser.print_help()

    sys.exit(0)


if __name__ == "__main__":
    main()
