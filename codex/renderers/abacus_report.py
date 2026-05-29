"""Render ABACUS telemetry payloads as CODEX technical Markdown reports."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from string import Formatter
from typing import Any

DEFAULT_TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "technical_status_report.md.j2"


class ReportRenderError(ValueError):
    """Raised when telemetry cannot be rendered into a report."""


class _SafeFormatter(Formatter):
    def get_value(self, key: Any, args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
        if isinstance(key, str):
            return kwargs.get(key, "")
        return super().get_value(key, args, kwargs)


def load_payload(path: str | Path) -> dict[str, Any]:
    """Load a repository_dispatch client payload from disk."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ReportRenderError("ABACUS payload must be a JSON object")
    return payload


def render_report(payload: Mapping[str, Any], template_path: str | Path = DEFAULT_TEMPLATE) -> str:
    """Render an ABACUS telemetry payload to Markdown."""

    source = _mapping(payload.get("source"), "source")
    context = {
        "payload_version": _escape_table(_text(payload.get("payload_version", "unknown"))),
        "source_repository": _escape_table(_text(source.get("repository", "unknown"))),
        "source_ref": _escape_table(_text(source.get("ref", "unknown"))),
        "source_sha": _escape_table(_text(source.get("sha", "unknown"))),
        "source_run_id": _escape_table(_text(source.get("run_id", "unknown"))),
        "generated_at": _escape_table(_text(payload.get("generated_at", "unknown"))),
        "status": _escape_table(_text(payload.get("status", "unknown")).upper()),
        "summary": _text(payload.get("summary", "No summary supplied.")),
        "metrics_table": _render_metrics(payload.get("metrics", [])),
        "artifacts_table": _render_artifacts(payload.get("artifacts", [])),
        "links_list": _render_links(payload.get("links", [])),
    }
    template = Path(template_path).read_text(encoding="utf-8")
    return _SafeFormatter().format(template, **context)


def write_report(
    payload_path: str | Path,
    output_path: str | Path,
    template_path: str | Path = DEFAULT_TEMPLATE,
) -> Path:
    """Render a payload file and write the Markdown report."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_report(load_payload(payload_path), template_path), encoding="utf-8")
    return output


def _render_metrics(metrics: Any) -> str:
    if not metrics:
        return "_No telemetry metrics were supplied._"
    if not isinstance(metrics, list):
        raise ReportRenderError("metrics must be an array")
    rows = ["| Metric | Value | Unit | Status |", "|---|---:|---|---|"]
    for metric in metrics:
        item = _mapping(metric, "metric")
        rows.append(
            "| {name} | {value} | {unit} | {status} |".format(
                name=_escape_table(_text(item.get("name", "unknown"))),
                value=_escape_table(_text(item.get("value", ""))),
                unit=_escape_table(_text(item.get("unit", ""))),
                status=_escape_table(_text(item.get("status", "unknown"))),
            )
        )
    return "\n".join(rows)


def _render_artifacts(artifacts: Any) -> str:
    if not artifacts:
        return "_No ABACUS artifacts were supplied._"
    if not isinstance(artifacts, list):
        raise ReportRenderError("artifacts must be an array")
    rows = ["| Artifact | Path | Type | Description |", "|---|---|---|---|"]
    for artifact in artifacts:
        item = _mapping(artifact, "artifact")
        rows.append(
        rows.append(
            "| {name} | {path} | {mime_type} | {description} |".format(
                name=_escape_table(_text(item.get("name", "unknown"))),
                path=_escape_table(_text(item.get("path", ""))),
                mime_type=_escape_table(_text(item.get("mime_type", ""))),
                description=_escape_table(_text(item.get("description", ""))),
            )
        )
        )
    return "\n".join(rows)


def _render_links(links: Any) -> str:
    if not links:
        return "_No links were supplied._"
    if not isinstance(links, list):
        raise ReportRenderError("links must be an array")
    rendered = []
    for link in links:
        item = _mapping(link, "link")
        label = _text(item.get("label", "link")).replace("[", r"\\[").replace("]", r"\\]")
        url = _text(item.get("url", "#")).replace(" ", "%20").replace("<", "%3C").replace(">", "%3E")
        rendered.append(f"- [{label}](<{url}>)")
    return "\n".join(rendered)


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ReportRenderError(f"{name} must be an object")
    return value


def _text(value: Any) -> str:
    return str(value).replace("\n", " ").strip()


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render ABACUS telemetry into a CODEX Markdown report")
    parser.add_argument("--input", required=True, help="Path to repository_dispatch client payload JSON")
    parser.add_argument("--output", required=True, help="Path to write the Markdown report")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="Markdown template path")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    output = write_report(args.input, args.output, args.template)
    print(f"Rendered ABACUS report: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
