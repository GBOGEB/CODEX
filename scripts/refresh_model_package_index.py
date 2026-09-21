#!/usr/bin/env python3
"""Refresh a deterministic index.json for a reusable engineering model package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

DEFAULT_EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache"}
DEFAULT_INDEX_NAME = "index.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_index(root: Path, index_name: str = DEFAULT_INDEX_NAME) -> dict[str, object]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"package root is not a directory: {root}")

    entries: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in DEFAULT_EXCLUDED_DIRS for part in relative.parts):
            continue
        if not path.is_file() or relative.as_posix() == index_name:
            continue
        entries.append(
            {
                "path": relative.as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )

    return {
        "schema": "codex-model-package-index/v1",
        "root": ".",
        "entry_count": len(entries),
        "entries": entries,
    }


def refresh_index(root: Path, index_name: str = DEFAULT_INDEX_NAME) -> Path:
    payload = build_index(root, index_name=index_name)
    output = root / index_name
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Refresh a deterministic index.json for an engineering model package."
    )
    parser.add_argument("root", type=Path, help="Package root directory")
    parser.add_argument(
        "--index-name",
        default=DEFAULT_INDEX_NAME,
        help="Index file name relative to package root (default: index.json)",
    )
    args = parser.parse_args()
    output = refresh_index(args.root, index_name=args.index_name)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
