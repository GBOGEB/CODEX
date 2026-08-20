"""Generate the renderer-independent W003A governance runtime export.

The runtime aggregates the SSOT, MASTER_input validation state, dependency
trace, lineage trace, and validation report summaries into one canonical model.
Excel and HTML rendering are intentionally not implemented in W003A.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.export.export_models import (  # noqa: E402
    GOVERNANCE_RUNTIME_ID,
    RUNTIME_SCHEMA_VERSION,
    RuntimeSource,
    ValidationSummary,
    ordered_links,
    sort_nodes,
    strip_runtime_volatility,
)
from tools.export.export_registry import EXPORT_OUTPUTS, registry_entries  # noqa: E402
from tools.traceability.dependency_engine import (  # noqa: E402
    DEFAULT_TRACE_INPUT_PATH,
    load_trace_nodes,
    validate_trace_nodes,
)
from tools.traceability.lineage_engine import (  # noqa: E402
    DEFAULT_LINEAGE_INPUT_PATH,
    load_lineage_nodes,
    validate_lineage_nodes,
)
from tools.validators.master_input_validator import (  # noqa: E402
    DEFAULT_INPUT_ROOT,
    DEFAULT_JSON_REPORT_PATH as MASTER_INPUT_REPORT_PATH,
    validate_master_input,
)
from tools.validators.ssot_validator import (  # noqa: E402
    DEFAULT_DOCUMENT_PATH,
    DEFAULT_JSON_REPORT_PATH as SSOT_REPORT_PATH,
    DEFAULT_SCHEMA_PATH,
    load_schema,
    validate_document,
)

TRACE_REPORT_PATH = Path("generated/trace_matrix.json")
LINEAGE_REPORT_PATH = Path("generated/lineage.json")


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        payload = yaml.safe_load(stream)
    if not isinstance(payload, dict):
        raise TypeError(f"YAML document must be a mapping: {path}")
    return payload


def _source_entries() -> list[dict[str, str]]:
    sources = [
        RuntimeSource("ssot", str(DEFAULT_DOCUMENT_PATH), "yaml"),
        RuntimeSource("ssot_schema", str(DEFAULT_SCHEMA_PATH), "yaml_schema"),
        RuntimeSource("master_input", str(DEFAULT_INPUT_ROOT), "directory"),
        RuntimeSource("dependency_trace", str(DEFAULT_TRACE_INPUT_PATH), "json_or_seeded_model"),
        RuntimeSource("lineage_trace", str(DEFAULT_LINEAGE_INPUT_PATH), "json_or_seeded_model"),
        RuntimeSource("ssot_validation_report", str(SSOT_REPORT_PATH), "json_report"),
        RuntimeSource("master_input_validation_report", str(MASTER_INPUT_REPORT_PATH), "json_report"),
        RuntimeSource("dependency_trace_report", str(TRACE_REPORT_PATH), "json_report"),
        RuntimeSource("lineage_report", str(LINEAGE_REPORT_PATH), "json_report"),
    ]
    return [source.as_dict() for source in sorted(sources, key=lambda source: source.key)]


def _validation_summary(
    key: str,
    report_path: Path,
    report: dict[str, Any],
) -> dict[str, Any]:
    errors = tuple(report.get("errors", []))
    return ValidationSummary(
        key=key,
        status=str(report.get("status", "unknown")),
        error_count=int(report.get("error_count", len(errors))),
        report_path=str(report_path),
        errors=errors,
    ).as_dict()


def _dependency_section(trace_report: dict[str, Any]) -> dict[str, Any]:
    model = [str(stage) for stage in trace_report["model"]]
    nodes = sort_nodes(list(trace_report["nodes"]), model)
    return {
        "model": model,
        "nodes": nodes,
        "links": ordered_links(nodes, "depends_on_parent"),
        "status": trace_report["status"],
    }


def _lineage_section(lineage_report: dict[str, Any]) -> dict[str, Any]:
    model = [str(stage) for stage in lineage_report["model"]]
    nodes = sort_nodes(list(lineage_report["nodes"]), model)
    return {
        "model": model,
        "nodes": nodes,
        "links": ordered_links(nodes, "lineage_parent"),
        "traversal": list(lineage_report["traversal"]),
        "status": lineage_report["status"],
    }


def build_governance_runtime() -> dict[str, Any]:
    """Build one canonical, renderer-independent governance runtime model."""
    schema = load_schema(DEFAULT_SCHEMA_PATH)
    ssot_validation = validate_document(DEFAULT_DOCUMENT_PATH, schema=schema, schema_path=DEFAULT_SCHEMA_PATH)
    master_input_validation = validate_master_input(DEFAULT_INPUT_ROOT)
    trace_report = validate_trace_nodes(load_trace_nodes(DEFAULT_TRACE_INPUT_PATH))
    lineage_report = validate_lineage_nodes(load_lineage_nodes(DEFAULT_LINEAGE_INPUT_PATH))
    ssot_document = _load_yaml(DEFAULT_DOCUMENT_PATH)

    validation_reports = [
        _validation_summary("dependency_trace", TRACE_REPORT_PATH, trace_report),
        _validation_summary("lineage", LINEAGE_REPORT_PATH, lineage_report),
        _validation_summary("master_input", MASTER_INPUT_REPORT_PATH, master_input_validation),
        _validation_summary("ssot", SSOT_REPORT_PATH, ssot_validation),
    ]

    runtime = {
        "schema_version": RUNTIME_SCHEMA_VERSION,
        "runtime_id": GOVERNANCE_RUNTIME_ID,
        "export_registry": registry_entries(),
        "sources": _source_entries(),
        "ssot": {
            "document_path": str(DEFAULT_DOCUMENT_PATH),
            "schema_path": str(DEFAULT_SCHEMA_PATH),
            "document": ssot_document,
            "validation": strip_runtime_volatility(ssot_validation),
        },
        "master_input": {
            "root": str(DEFAULT_INPUT_ROOT),
            "validation": strip_runtime_volatility(master_input_validation),
        },
        "dependency_trace": _dependency_section(trace_report),
        "lineage_trace": _lineage_section(lineage_report),
        "validation_reports": sorted(validation_reports, key=lambda item: item["key"]),
    }
    return runtime


def _render_markdown(runtime: dict[str, Any]) -> str:
    lines = [
        "# Governance Runtime Export",
        "",
        f"- Schema version: `{runtime['schema_version']}`",
        f"- Runtime ID: `{runtime['runtime_id']}`",
        "",
        "## Export Registry",
        "",
        "| Format | Status |",
        "| --- | --- |",
    ]
    for entry in runtime["export_registry"]:
        lines.append(f"| {entry['format']} | {entry['status']} |")

    lines.extend([
        "",
        "## Validation Reports",
        "",
        "| Key | Status | Error Count | Report |",
        "| --- | --- | ---: | --- |",
    ])
    for report in runtime["validation_reports"]:
        lines.append(
            f"| {report['key']} | {report['status']} | {report['error_count']} | `{report['report_path']}` |"
        )

    lines.extend([
        "",
        "## Dependency Trace Model",
        "",
        " → ".join(runtime["dependency_trace"]["model"]),
        "",
        f"- Nodes: `{len(runtime['dependency_trace']['nodes'])}`",
        f"- Links: `{len(runtime['dependency_trace']['links'])}`",
        f"- Status: `{runtime['dependency_trace']['status']}`",
        "",
        "## Lineage Trace Model",
        "",
        " → ".join(runtime["lineage_trace"]["model"]),
        "",
        f"- Nodes: `{len(runtime['lineage_trace']['nodes'])}`",
        f"- Links: `{len(runtime['lineage_trace']['links'])}`",
        f"- Status: `{runtime['lineage_trace']['status']}`",
        "",
    ])
    return "\n".join(lines)


def write_governance_runtime(
    runtime: dict[str, Any],
    json_path: Path | str = EXPORT_OUTPUTS["json"],
    yaml_path: Path | str = EXPORT_OUTPUTS["yaml"],
    markdown_path: Path | str = EXPORT_OUTPUTS["markdown"],
) -> dict[str, Path]:
    """Write canonical governance runtime outputs in implemented formats."""
    output_paths = {
        "json": Path(json_path),
        "yaml": Path(yaml_path),
        "markdown": Path(markdown_path),
    }
    for path in output_paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)

    output_paths["json"].write_text(
        json.dumps(runtime, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    output_paths["yaml"].write_text(
        yaml.safe_dump(runtime, sort_keys=True, allow_unicode=True),
        encoding="utf-8",
    )
    output_paths["markdown"].write_text(_render_markdown(runtime), encoding="utf-8")
    return output_paths


def generate_governance_runtime(
    json_path: Path | str = EXPORT_OUTPUTS["json"],
    yaml_path: Path | str = EXPORT_OUTPUTS["yaml"],
    markdown_path: Path | str = EXPORT_OUTPUTS["markdown"],
) -> tuple[dict[str, Any], dict[str, Path]]:
    """Build and write the governance runtime in all implemented formats."""
    runtime = build_governance_runtime()
    paths = write_governance_runtime(runtime, json_path, yaml_path, markdown_path)
    return runtime, paths


def main() -> int:
    """CLI entrypoint. Returns non-zero if any aggregated validation failed."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path, default=EXPORT_OUTPUTS["json"])
    parser.add_argument("--yaml-output", type=Path, default=EXPORT_OUTPUTS["yaml"])
    parser.add_argument("--markdown-output", type=Path, default=EXPORT_OUTPUTS["markdown"])
    args = parser.parse_args()

    runtime, paths = generate_governance_runtime(args.json_output, args.yaml_output, args.markdown_output)
    failures = [report for report in runtime["validation_reports"] if report["status"] != "pass"]
    print("Governance runtime exported:")
    for export_format, path in paths.items():
        print(f"- {export_format}: {path}")

    if failures:
        print(f"Governance runtime validation failed with {len(failures)} failing report(s).")
        for report in failures:
            print(f"- {report['key']}: {report['error_count']} error(s)")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
