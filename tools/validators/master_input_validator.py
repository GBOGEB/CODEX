"""Validate the MASTER_input governance handover folder structure."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DEFAULT_INPUT_ROOT = Path("MASTER_input")
DEFAULT_JSON_REPORT_PATH = Path("generated/master_input_validation.json")
DEFAULT_MARKDOWN_REPORT_PATH = Path("generated/master_input_validation.md")

REQUIRED_FOLDERS = (
    "ITT",
    "Applicant",
    "SoR",
    "Contracts",
    "Interfaces",
    "Compliance",
    "Traceability",
)
IGNORED_FILENAMES = {".gitkeep", ".DS_Store", "Thumbs.db"}
NAMING_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _iter_files(root: Path) -> Iterable[Path]:
    """Yield files under ``root`` in deterministic order."""
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file())


def _sha256(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative(path: Path, root: Path) -> str:
    """Return a POSIX relative path where possible."""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def validate_master_input(input_root: Path | str = DEFAULT_INPUT_ROOT) -> dict[str, object]:
    """Validate required folders, duplicate files, and file naming conventions."""
    root = Path(input_root)
    errors: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []

    if not root.exists():
        errors.append(
            {
                "code": "missing_input_root",
                "path": str(root),
                "message": f"MASTER_input root does not exist: {root}",
            }
        )
    elif not root.is_dir():
        errors.append(
            {
                "code": "input_root_not_directory",
                "path": str(root),
                "message": f"MASTER_input root is not a directory: {root}",
            }
        )

    required_paths = [root / folder for folder in REQUIRED_FOLDERS]
    for folder_path in required_paths:
        if not folder_path.is_dir():
            errors.append(
                {
                    "code": "missing_required_folder",
                    "path": folder_path.as_posix(),
                    "message": f"Missing required MASTER_input folder: {folder_path.as_posix()}",
                }
            )

    existing_required_paths = [path for path in required_paths if path.is_dir()]
    files: list[Path] = []
    for folder_path in existing_required_paths:
        files.extend(_iter_files(folder_path))

    files = [path for path in files if path.name not in IGNORED_FILENAMES]

    by_name: dict[str, list[Path]] = defaultdict(list)
    by_digest: dict[str, list[Path]] = defaultdict(list)
    for file_path in files:
        by_name[file_path.name.casefold()].append(file_path)
        by_digest[_sha256(file_path)].append(file_path)

        if not NAMING_PATTERN.match(file_path.name):
            errors.append(
                {
                    "code": "invalid_file_name",
                    "path": _relative(file_path, root),
                    "message": (
                        "Invalid file name; use letters, numbers, dots, underscores, "
                        f"and hyphens only: {_relative(file_path, root)}"
                    ),
                }
            )

    for duplicate_paths in by_name.values():
        if len(duplicate_paths) > 1:
            errors.append(
                {
                    "code": "duplicate_file_name",
                    "paths": [_relative(path, root) for path in duplicate_paths],
                    "message": "Duplicate file name found across MASTER_input required folders: "
                    + ", ".join(_relative(path, root) for path in duplicate_paths),
                }
            )

    for duplicate_paths in by_digest.values():
        if len(duplicate_paths) > 1:
            warnings.append(
                {
                    "code": "duplicate_file_content",
                    "paths": [_relative(path, root) for path in duplicate_paths],
                    "message": "Duplicate file content found across MASTER_input required folders: "
                    + ", ".join(_relative(path, root) for path in duplicate_paths),
                }
            )

    folder_status = {
        folder: {
            "path": (root / folder).as_posix(),
            "exists": (root / folder).is_dir(),
        }
        for folder in REQUIRED_FOLDERS
    }

    return {
        "status": "pass" if not errors else "fail",
        "input_root": str(root),
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "required_folders": folder_status,
        "file_count": len(files),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "naming_convention": NAMING_PATTERN.pattern,
    }


def _render_markdown(report: dict[str, object]) -> str:
    status = "PASS" if report["status"] == "pass" else "FAIL"
    lines = [
        "# MASTER_input Validation Report",
        "",
        f"- Status: **{status}**",
        f"- Input root: `{report['input_root']}`",
        f"- Checked at: `{report['checked_at']}`",
        f"- File count: `{report['file_count']}`",
        f"- Error count: `{report['error_count']}`",
        f"- Warning count: `{report['warning_count']}`",
        "",
        "## Required folders",
        "",
    ]

    required_folders = report["required_folders"]
    assert isinstance(required_folders, dict)
    for folder, details in required_folders.items():
        assert isinstance(details, dict)
        marker = "present" if details["exists"] else "missing"
        lines.append(f"- `{folder}`: {marker} (`{details['path']}`)")

    errors = report["errors"]
    assert isinstance(errors, list)
    if errors:
        lines.extend(["", "## Errors", ""])
        for error in errors:
            assert isinstance(error, dict)
            lines.append(f"- `{error['code']}`: {error['message']}")
    else:
        lines.extend(["", "No blocking validation errors detected."])

    warnings = report["warnings"]
    assert isinstance(warnings, list)
    if warnings:
        lines.extend(["", "## Warnings", ""])
        for warning in warnings:
            assert isinstance(warning, dict)
            lines.append(f"- `{warning['code']}`: {warning['message']}")

    lines.append("")
    return "\n".join(lines)


def generate_report(
    result: dict[str, object],
    json_report_path: Path | str = DEFAULT_JSON_REPORT_PATH,
    markdown_report_path: Path | str = DEFAULT_MARKDOWN_REPORT_PATH,
) -> dict[str, Path]:
    """Write JSON and Markdown MASTER_input validation reports."""
    json_path = Path(json_report_path)
    markdown_path = Path(markdown_report_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)

    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(_render_markdown(result), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}


def main() -> int:
    """CLI entrypoint. Returns non-zero when validation errors are present."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--json-report", type=Path, default=DEFAULT_JSON_REPORT_PATH)
    parser.add_argument("--markdown-report", type=Path, default=DEFAULT_MARKDOWN_REPORT_PATH)
    args = parser.parse_args()

    result = validate_master_input(args.input_root)
    generate_report(result, args.json_report, args.markdown_report)

    if result["status"] == "fail":
        print(f"MASTER_input validation failed with {result['error_count']} error(s).")
        for error in result["errors"]:
            print(f"- {error['message']}")
        return 1

    print(f"MASTER_input validation passed for {args.input_root}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
