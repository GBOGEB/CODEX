"""Validate the governance runtime export against the W003B runtime contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_SCHEMA_PATH = Path("schemas/governance_runtime.schema.yaml")
DEFAULT_DOCUMENT_PATH = Path("generated/governance_runtime.json")
DEFAULT_JSON_REPORT_PATH = Path("generated/runtime_validation.json")
DEFAULT_MARKDOWN_REPORT_PATH = Path("generated/runtime_validation.md")


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        payload = yaml.safe_load(stream)
    if not isinstance(payload, dict):
        raise TypeError(f"YAML schema must be a mapping: {path}")
    return payload


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"JSON document must be an object: {path}")
    return payload


def _format_path(path_parts: object) -> str:
    parts = list(path_parts)  # type: ignore[arg-type]
    return "/".join(str(part) for part in parts) if parts else "<root>"


def load_schema(schema_path: Path | str = DEFAULT_SCHEMA_PATH) -> dict[str, Any]:
    """Load and self-check the governance runtime schema."""
    schema = _load_yaml(Path(schema_path))
    Draft202012Validator.check_schema(schema)
    return schema


def _schema_errors(payload: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, str]]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        {
            "code": "schema_validation",
            "path": _format_path(error.path),
            "message": error.message,
        }
        for error in sorted(validator.iter_errors(payload), key=lambda item: (list(item.path), item.message))
    ]


def _reference_errors_for_section(
    payload: dict[str, Any],
    section_key: str,
    link_relationship: str,
) -> list[dict[str, str]]:
    section = payload.get(section_key, {})
    if not isinstance(section, dict):
        return []
    nodes = section.get("nodes", [])
    if not isinstance(nodes, list):
        return []
    node_ids = {node.get("id") for node in nodes if isinstance(node, dict) and isinstance(node.get("id"), str)}
    errors: list[dict[str, str]] = []

    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            continue
        parent = node.get("parent")
        if parent is not None and parent not in node_ids:
            errors.append(
                {
                    "code": "broken_reference",
                    "path": f"{section_key}/nodes/{index}/parent",
                    "message": f"Parent reference does not resolve inside {section_key}: {parent}",
                }
            )

    links = section.get("links", [])
    if isinstance(links, list):
        for index, link in enumerate(links):
            if not isinstance(link, dict):
                continue
            source = link.get("source")
            target = link.get("target")
            relationship = link.get("relationship")
            if relationship == link_relationship and source not in node_ids:
                errors.append(
                    {
                        "code": "broken_reference",
                        "path": f"{section_key}/links/{index}/source",
                        "message": f"Link source does not resolve inside {section_key}: {source}",
                    }
                )
            if relationship == link_relationship and target not in node_ids:
                errors.append(
                    {
                        "code": "broken_reference",
                        "path": f"{section_key}/links/{index}/target",
                        "message": f"Link target does not resolve inside {section_key}: {target}",
                    }
                )

    traversal = section.get("traversal", [])
    if isinstance(traversal, list):
        for index, node_id in enumerate(traversal):
            if isinstance(node_id, str) and node_id not in node_ids:
                errors.append(
                    {
                        "code": "broken_reference",
                        "path": f"{section_key}/traversal/{index}",
                        "message": f"Traversal reference does not resolve inside {section_key}: {node_id}",
                    }
                )
    return errors


def validate_payload(payload: dict[str, Any], schema: dict[str, Any] | None = None) -> list[dict[str, str]]:
    """Validate a governance runtime payload and return normalized issues."""
    loaded_schema = schema if schema is not None else load_schema()
    errors = _schema_errors(payload, loaded_schema)
    errors.extend(_reference_errors_for_section(payload, "dependency_trace", "depends_on_parent"))
    errors.extend(_reference_errors_for_section(payload, "lineage_trace", "lineage_parent"))
    return errors


def validate_runtime_document(
    document_path: Path | str = DEFAULT_DOCUMENT_PATH,
    schema_path: Path | str = DEFAULT_SCHEMA_PATH,
) -> dict[str, Any]:
    """Validate a governance runtime JSON export against schema and references."""
    schema = load_schema(schema_path)
    payload = _load_json(Path(document_path))
    errors = validate_payload(payload, schema)
    return {
        "status": "pass" if not errors else "fail",
        "schema_path": str(schema_path),
        "document_path": str(document_path),
        "error_count": len(errors),
        "errors": errors,
    }


def _render_markdown(result: dict[str, Any]) -> str:
    status = "PASS" if result["status"] == "pass" else "FAIL"
    lines = [
        "# Governance Runtime Contract Validation",
        "",
        f"- Status: **{status}**",
        f"- Schema: `{result['schema_path']}`",
        f"- Document: `{result['document_path']}`",
        f"- Error count: `{result['error_count']}`",
        "",
    ]
    if result["errors"]:
        lines.extend(["## Errors", ""])
        for error in result["errors"]:
            lines.append(f"- `{error['code']}` at `{error['path']}`: {error['message']}")
    else:
        lines.append("No runtime contract validation errors detected.")
    lines.append("")
    return "\n".join(lines)


def write_reports(
    result: dict[str, Any],
    json_report_path: Path | str = DEFAULT_JSON_REPORT_PATH,
    markdown_report_path: Path | str = DEFAULT_MARKDOWN_REPORT_PATH,
) -> dict[str, Path]:
    """Write JSON and Markdown governance runtime contract reports."""
    json_path = Path(json_report_path)
    markdown_path = Path(markdown_report_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(_render_markdown(result), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument("--document", type=Path, default=DEFAULT_DOCUMENT_PATH)
    parser.add_argument("--json-report", type=Path, default=DEFAULT_JSON_REPORT_PATH)
    parser.add_argument("--markdown-report", type=Path, default=DEFAULT_MARKDOWN_REPORT_PATH)
    args = parser.parse_args()

    result = validate_runtime_document(args.document, args.schema)
    write_reports(result, args.json_report, args.markdown_report)
    if result["status"] == "fail":
        print(f"Governance runtime contract validation failed with {result['error_count']} error(s).")
        for error in result["errors"]:
            print(f"- {error['code']} at {error['path']}: {error['message']}")
        return 1
    print("Governance runtime contract validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
