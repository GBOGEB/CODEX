"""Report writers for dependency trace matrix outputs."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

DEFAULT_JSON_REPORT_PATH = Path("generated/trace_matrix.json")
DEFAULT_MARKDOWN_REPORT_PATH = Path("generated/trace_matrix.md")
DEFAULT_CSV_REPORT_PATH = Path("generated/trace_matrix.csv")


def _render_markdown(report: dict[str, Any]) -> str:
    status = "PASS" if report["status"] == "pass" else "FAIL"
    lines = [
        "# Dependency Trace Matrix",
        "",
        f"- Status: **{status}**",
        f"- Checked at: `{report['checked_at']}`",
        f"- Node count: `{report['node_count']}`",
        f"- Error count: `{report['error_count']}`",
        "",
        "## Required Trace Model",
        "",
        "Requirement → Applicant Response → Review → Change Request → Approval → Generated Artifact",
        "",
        "## Nodes",
        "",
        "| Stage | Title | ID | Parent |",
        "| --- | --- | --- | --- |",
    ]

    for node in report["nodes"]:
        lines.append(
            f"| {node['stage']} | {node['title']} | `{node['id']}` | "
            f"`{node['parent'] or ''}` |"
        )

    if report["errors"]:
        lines.extend(["", "## Errors", ""])
        for error in report["errors"]:
            node_suffix = f" (`{error['node_id']}`)" if "node_id" in error else ""
            lines.append(f"- `{error['code']}`{node_suffix}: {error['message']}")
    else:
        lines.extend(["", "No dependency trace validation errors detected."])

    lines.append("")
    return "\n".join(lines)


def generate_reports(
    report: dict[str, Any],
    json_report_path: Path | str = DEFAULT_JSON_REPORT_PATH,
    markdown_report_path: Path | str = DEFAULT_MARKDOWN_REPORT_PATH,
    csv_report_path: Path | str = DEFAULT_CSV_REPORT_PATH,
) -> dict[str, Path]:
    """Write dependency trace reports as JSON, Markdown, and CSV."""
    json_path = Path(json_report_path)
    markdown_path = Path(markdown_report_path)
    csv_path = Path(csv_report_path)
    for path in (json_path, markdown_path, csv_path):
        path.parent.mkdir(parents=True, exist_ok=True)

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(_render_markdown(report), encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["stage", "title", "id", "parent", "source_path"])
        writer.writeheader()
        for node in report["nodes"]:
            writer.writerow(
                {
                    "stage": node["stage"],
                    "title": node["title"],
                    "id": node["id"],
                    "parent": node.get("parent") or "",
                    "source_path": node.get("source_path") or "",
                }
            )

    return {"json": json_path, "markdown": markdown_path, "csv": csv_path}
