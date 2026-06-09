"""Validate dependency trace reports against the W003B contract schema."""

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

DEFAULT_SCHEMA_PATH = Path("schemas/dependency_trace.schema.yaml")
DEFAULT_DOCUMENT_PATH = Path("generated/trace_matrix.json")
DEFAULT_JSON_REPORT_PATH = Path("generated/dependency_trace_validation.json")


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
    """Load and self-check the dependency trace schema."""
    schema = _load_yaml(Path(schema_path))
    Draft202012Validator.check_schema(schema)
    return schema


def validate_payload(payload: dict[str, Any], schema: dict[str, Any] | None = None) -> list[dict[str, str]]:
    """Validate a dependency trace payload and return normalized issues."""
    loaded_schema = schema if schema is not None else load_schema()
    validator = Draft202012Validator(loaded_schema, format_checker=FormatChecker())
    errors = [
        {
            "code": "schema_validation",
            "path": _format_path(error.path),
            "message": error.message,
        }
        for error in sorted(validator.iter_errors(payload), key=lambda item: (list(item.path), item.message))
    ]

    nodes = payload.get("nodes", [])
    if isinstance(nodes, list):
        node_ids = [node.get("id") for node in nodes if isinstance(node, dict)]
        node_id_set = set(node_id for node_id in node_ids if isinstance(node_id, str))
        for node_id in sorted(node_id for node_id in node_id_set if node_ids.count(node_id) > 1):
            errors.append(
                {"code": "duplicate_trace_id", "path": "nodes", "message": f"Duplicate trace node ID: {node_id}"}
            )
        for index, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            parent = node.get("parent")
            if parent is not None and parent not in node_id_set:
                errors.append(
                    {
                        "code": "broken_reference",
                        "path": f"nodes/{index}/parent",
                        "message": f"Parent reference does not resolve to a dependency trace node: {parent}",
                    }
                )
        if payload.get("node_count") != len(nodes):
            errors.append(
                {
                    "code": "node_count_mismatch",
                    "path": "node_count",
                    "message": f"node_count is {payload.get('node_count')} but {len(nodes)} node(s) were found.",
                }
            )
    return errors


def validate_dependency_trace_document(
    document_path: Path | str = DEFAULT_DOCUMENT_PATH,
    schema_path: Path | str = DEFAULT_SCHEMA_PATH,
) -> dict[str, Any]:
    """Validate a dependency trace JSON report against schema and references."""
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


def write_report(result: dict[str, Any], report_path: Path | str = DEFAULT_JSON_REPORT_PATH) -> Path:
    """Write the dependency trace contract validation report."""
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument("--document", type=Path, default=DEFAULT_DOCUMENT_PATH)
    parser.add_argument("--json-report", type=Path, default=DEFAULT_JSON_REPORT_PATH)
    args = parser.parse_args()

    result = validate_dependency_trace_document(args.document, args.schema)
    write_report(result, args.json_report)
    if result["status"] == "fail":
        print(f"Dependency trace contract validation failed with {result['error_count']} error(s).")
        for error in result["errors"]:
            print(f"- {error['code']} at {error['path']}: {error['message']}")
        return 1
    print("Dependency trace contract validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
