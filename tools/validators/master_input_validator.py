"""Validate the W001 MASTER_input handover folder contract.

The validator checks that the expected W001 intake folders exist, reports
duplicate file names across those folders, and verifies a conservative naming
convention for visible files/directories. It writes both JSON and Markdown
reports and exits non-zero when validation errors are present.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MASTER_INPUT_ROOT = Path("MASTER_input")
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
NAMING_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_. -]*$")


@dataclass(frozen=True)
class FolderFinding:
    """A single MASTER_input validation finding."""

    severity: str
    code: str
    path: str
    message: str


def _is_visible(path: Path) -> bool:
    return not any(part.startswith(".") for part in path.parts)


def _scan_required_tree(root: Path) -> list[Path]:
    paths: list[Path] = []
    for folder in REQUIRED_FOLDERS:
        folder_path = root / folder
        if folder_path.exists():
            paths.extend(
                path
                for path in folder_path.rglob("*")
                if _is_visible(path.relative_to(root))
            )
    return paths


def _missing_folder_findings(root: Path) -> list[FolderFinding]:
    findings: list[FolderFinding] = []
    for folder in REQUIRED_FOLDERS:
        folder_path = root / folder
        if not folder_path.is_dir():
            findings.append(
                FolderFinding(
                    severity="error",
                    code="missing_folder",
                    path=str(folder_path),
                    message=f"Required MASTER_input folder is missing: {folder}",
                )
            )
    return findings


def _duplicate_file_findings(root: Path, paths: list[Path]) -> list[FolderFinding]:
    by_name: dict[str, list[Path]] = {}
    for path in paths:
        if path.is_file():
            by_name.setdefault(path.name.casefold(), []).append(path)

    findings: list[FolderFinding] = []
    for normalized_name, duplicates in sorted(by_name.items()):
        if len(duplicates) > 1:
            locations = ", ".join(str(path) for path in duplicates)
            findings.append(
                FolderFinding(
                    severity="error",
                    code="duplicate_file",
                    path=normalized_name,
                    message=f"Duplicate file name found in MASTER_input required folders: {locations}",
                )
            )
    return findings


def _naming_findings(root: Path, paths: list[Path]) -> list[FolderFinding]:
    findings: list[FolderFinding] = []
    for path in sorted(paths):
        relative = path.relative_to(root)
        for part in relative.parts:
            if part.startswith("."):
                continue
            if not NAMING_PATTERN.fullmatch(part):
                findings.append(
                    FolderFinding(
                        severity="error",
                        code="naming_convention",
                        path=str(path),
                        message=(
                            "Path component does not match naming convention "
                            f"{NAMING_PATTERN.pattern!r}: {part!r}"
                        ),
                    )
                )
                break
    return findings


def validate_master_input(
    root: str | Path = DEFAULT_MASTER_INPUT_ROOT,
) -> dict[str, object]:
    """Validate required MASTER_input folders, duplicates, and naming."""

    root_path = Path(root)
    findings: list[FolderFinding] = []
    if not root_path.is_dir():
        findings.append(
            FolderFinding(
                severity="error",
                code="missing_root",
                path=str(root_path),
                message=f"MASTER_input root is missing: {root_path}",
            )
        )
        paths: list[Path] = []
    else:
        findings.extend(_missing_folder_findings(root_path))
        paths = _scan_required_tree(root_path)
        findings.extend(_duplicate_file_findings(root_path, paths))
        findings.extend(_naming_findings(root_path, paths))

    return {
        "root": str(root_path),
        "required_folders": list(REQUIRED_FOLDERS),
        "valid": not any(finding.severity == "error" for finding in findings),
        "error_count": sum(1 for finding in findings if finding.severity == "error"),
        "findings": [asdict(finding) for finding in findings],
        "checked_paths": (
            [str(path) for path in sorted(paths)] if root_path.is_dir() else []
        ),
        "checked_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def _report_to_markdown(report: dict[str, object]) -> str:
    status = "PASS" if report["valid"] else "FAIL"
    lines = [
        "# MASTER_input Validation Report",
        "",
        f"- Status: **{status}**",
        f"- Root: `{report['root']}`",
        f"- Checked at: `{report['checked_at']}`",
        f"- Error count: **{report['error_count']}**",
        "",
        "## Required folders",
        "",
    ]
    for folder in report["required_folders"]:  # type: ignore[index]
        lines.append(f"- `{folder}`")
    lines.append("")

    findings = report["findings"]  # type: ignore[assignment]
    if findings:
        lines.append("## Findings")
        lines.append("")
        for finding in findings:  # type: ignore[union-attr]
            lines.append(
                f"- **{finding['severity']}** `{finding['code']}` `{finding['path']}`: {finding['message']}"
            )
        lines.append("")
    else:
        lines.append("No validation findings.")
        lines.append("")
    return "\n".join(lines)


def generate_report(
    report: dict[str, object],
    json_path: str | Path = DEFAULT_JSON_REPORT_PATH,
    markdown_path: str | Path = DEFAULT_MARKDOWN_REPORT_PATH,
) -> dict[str, Path]:
    """Write JSON and Markdown MASTER_input validation reports."""

    json_output = Path(json_path)
    markdown_output = Path(markdown_path)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    markdown_output.write_text(_report_to_markdown(report), encoding="utf-8")
    return {"json": json_output, "markdown": markdown_output}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the MASTER_input folder contract"
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_MASTER_INPUT_ROOT)
    parser.add_argument("--json-report", type=Path, default=DEFAULT_JSON_REPORT_PATH)
    parser.add_argument(
        "--markdown-report", type=Path, default=DEFAULT_MARKDOWN_REPORT_PATH
    )
    args = parser.parse_args(argv)

    report = validate_master_input(args.root)
    outputs = generate_report(report, args.json_report, args.markdown_report)
    if report["valid"]:
        print(
            f"MASTER_input validation passed: {outputs['json']} {outputs['markdown']}"
        )
        return 0
    print(f"MASTER_input validation failed with {report['error_count']} error(s):")
    for finding in report["findings"]:  # type: ignore[index]
        print(f"- {finding['code']} {finding['path']}: {finding['message']}")
    print(f"Reports written: {outputs['json']} {outputs['markdown']}")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
