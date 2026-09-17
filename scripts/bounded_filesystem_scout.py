#!/usr/bin/env python3
"""Bounded filesystem census with explicit incompleteness receipts.

The scout only traverses user-supplied roots. Permission/path failures are recorded and
make the receipt PARTIAL; they are never silently converted into a complete census.
No files are modified.
"""
from __future__ import annotations

import argparse
import errno
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class SkipRecord:
    path: str
    operation: str
    error_type: str
    errno: int | None
    message: str


def _windows_native_path(path: Path) -> str:
    """Return a Windows long-path-capable native path without changing display lineage."""
    value = str(path.resolve())
    if os.name != "nt":
        return value
    if value.startswith("\\\\?\\"):
        return value
    if value.startswith("\\\\"):
        return "\\\\?\\UNC\\" + value.lstrip("\\")
    return "\\\\?\\" + value


def _reason(exc: OSError) -> str:
    if isinstance(exc, PermissionError) or exc.errno in {errno.EACCES, errno.EPERM}:
        return "PERMISSION_DENIED"
    if exc.errno == errno.ENAMETOOLONG:
        return "PATH_TOO_LONG"
    if isinstance(exc, FileNotFoundError) or exc.errno == errno.ENOENT:
        return "NOT_FOUND_DURING_SCAN"
    return type(exc).__name__.upper()


def scan_roots(roots: Iterable[Path], *, follow_symlinks: bool = False) -> dict:
    files: list[str] = []
    directories: list[str] = []
    skips: list[SkipRecord] = []
    root_rows: list[dict] = []

    def walk(display_path: Path) -> None:
        directories.append(str(display_path))
        native = _windows_native_path(display_path)
        try:
            with os.scandir(native) as iterator:
                entries = sorted(list(iterator), key=lambda entry: entry.name.casefold())
        except OSError as exc:
            skips.append(
                SkipRecord(
                    path=str(display_path),
                    operation="scandir",
                    error_type=_reason(exc),
                    errno=exc.errno,
                    message=str(exc),
                )
            )
            return

        for entry in entries:
            child = display_path / entry.name
            try:
                is_dir = entry.is_dir(follow_symlinks=follow_symlinks)
                is_file = entry.is_file(follow_symlinks=follow_symlinks)
                is_link = entry.is_symlink()
            except OSError as exc:
                skips.append(
                    SkipRecord(
                        path=str(child),
                        operation="classify",
                        error_type=_reason(exc),
                        errno=exc.errno,
                        message=str(exc),
                    )
                )
                continue

            if is_link and not follow_symlinks:
                files.append(str(child))
            elif is_dir:
                walk(child)
            elif is_file:
                files.append(str(child))
            else:
                files.append(str(child))

    for root in roots:
        resolved = root.expanduser().resolve()
        row = {"requested": str(root), "resolved": str(resolved)}
        if not resolved.exists():
            skips.append(
                SkipRecord(
                    path=str(resolved),
                    operation="root",
                    error_type="ROOT_NOT_FOUND",
                    errno=errno.ENOENT,
                    message="requested root does not exist",
                )
            )
            row["accepted"] = False
        elif not resolved.is_dir():
            skips.append(
                SkipRecord(
                    path=str(resolved),
                    operation="root",
                    error_type="ROOT_NOT_DIRECTORY",
                    errno=None,
                    message="requested root is not a directory",
                )
            )
            row["accepted"] = False
        else:
            row["accepted"] = True
            walk(resolved)
        root_rows.append(row)

    files = sorted(set(files), key=str.casefold)
    directories = sorted(set(directories), key=str.casefold)
    skips = sorted(skips, key=lambda item: (item.path.casefold(), item.operation, item.error_type))
    complete = len(skips) == 0
    return {
        "schema": "codex-bounded-filesystem-scout/1.0",
        "status": "COMPLETE" if complete else "PARTIAL",
        "complete": complete,
        "roots": root_rows,
        "follow_symlinks": follow_symlinks,
        "file_count": len(files),
        "directory_count": len(directories),
        "skipped_count": len(skips),
        "files": files,
        "directories": directories,
        "skipped": [asdict(item) for item in skips],
        "authority": "DISCOVERY_RECEIPT_ONLY",
        "formal_credit_delta": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", type=Path, help="bounded roots to scan")
    parser.add_argument("--output", type=Path, help="optional JSON receipt path")
    parser.add_argument("--follow-symlinks", action="store_true", help="follow symlinked directories (off by default)")
    args = parser.parse_args()

    receipt = scan_roots(args.roots, follow_symlinks=args.follow_symlinks)
    rendered = json.dumps(receipt, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if receipt["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
