"""Report writers for W002 lineage outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_JSON_REPORT_PATH = Path("generated/lineage.json")
DEFAULT_MARKDOWN_REPORT_PATH = Path("generated/lineage.md")
DEFAULT_GRAPH_REPORT_PATH = Path("generated/lineage_graph.json")


def _render_markdown(report: dict[str, Any]) -> str:
    status = "PASS" if report["status"] == "pass" else "FAIL"
    lines = [
        "# Governance Lineage Report",
        "",
        f"- Status: **{status}**",
        f"- Checked at: `{report['checked_at']}`",
        f"- Node count: `{report['node_count']}`",
        f"- Error count: `{report['error_count']}`",
        "",
        "## Required Lineage Model",
        "",
        "ITT → Applicant Package → Review → Revision → Approval → Baseline",
        "",
        "## Traversal",
        "",
    ]

    if report["traversal"]:
        for index, node_id in enumerate(report["traversal"], start=1):
            node = next(node for node in report["nodes"] if node["id"] == node_id)
            lines.append(f"{index}. **{node['stage']}** — {node['title']} (`{node_id}`)")
    else:
        lines.append("No complete lineage traversal is available.")

    lines.extend([
        "",
        "## Nodes",
        "",
        "| Stage | Title | ID | Parent | Status | Created | Updated |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ])
    for node in report["nodes"]:
        lines.append(
            f"| {node['stage']} | {node['title']} | `{node['id']}` | "
            f"`{node['parent'] or ''}` | {node['status']} | {node['created']} | {node['updated']} |"
        )

    if report["errors"]:
        lines.extend(["", "## Errors", ""])
        for error in report["errors"]:
            node_suffix = f" (`{error['node_id']}`)" if "node_id" in error else ""
            lines.append(f"- `{error['code']}`{node_suffix}: {error['message']}")
    else:
        lines.extend(["", "No lineage validation errors detected."])

    lines.append("")
    return "\n".join(lines)


def build_graph(report: dict[str, Any]) -> dict[str, Any]:
    """Build a graph-oriented lineage payload for downstream tooling."""
    nodes = [
        {"id": node["id"], "label": node["title"], "stage": node["stage"], "status": node["status"]}
        for node in report["nodes"]
    ]
    edges = [
        {"source": node["parent"], "target": node["id"]}
        for node in report["nodes"]
        if node.get("parent")
    ]
    return {
        "status": report["status"],
        "checked_at": report["checked_at"],
        "nodes": nodes,
        "edges": edges,
        "errors": report["errors"],
    }


def generate_reports(
    report: dict[str, Any],
    json_report_path: Path | str = DEFAULT_JSON_REPORT_PATH,
    markdown_report_path: Path | str = DEFAULT_MARKDOWN_REPORT_PATH,
    graph_report_path: Path | str = DEFAULT_GRAPH_REPORT_PATH,
) -> dict[str, Path]:
    """Write lineage reports as JSON, Markdown, and graph JSON."""
    json_path = Path(json_report_path)
    markdown_path = Path(markdown_report_path)
    graph_path = Path(graph_report_path)
    for path in (json_path, markdown_path, graph_path):
        path.parent.mkdir(parents=True, exist_ok=True)

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(_render_markdown(report), encoding="utf-8")
    graph_path.write_text(json.dumps(build_graph(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path, "graph": graph_path}
