"""Validate YAML single-source-of-truth documents against a YAML schema.

The validator intentionally implements the small JSON Schema subset used by the
W001 governance schema so it can run in a minimal CI environment after installing
only repository dependencies. It checks required fields, basic types, enum
values, array item schemas, and minItems constraints, then writes JSON and
Markdown reports.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

DEFAULT_SCHEMA_PATH = Path("schemas/master_contract_ssot.schema.yaml")
DEFAULT_DOCUMENT_PATH = Path("ssot/master_contract_ssot_v0_2.yaml")
DEFAULT_JSON_REPORT_PATH = Path("generated/validation_report.json")
DEFAULT_MARKDOWN_REPORT_PATH = Path("generated/validation_report.md")


@dataclass(frozen=True)
class ValidationMessage:
    """A single validation finding with a stable path and clear message."""

    path: str
    message: str


def _load_yaml(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def load_schema(schema_path: str | Path = DEFAULT_SCHEMA_PATH) -> dict[str, Any]:
    """Load the YAML SSOT schema from disk."""

    schema = _load_yaml(Path(schema_path))
    if not isinstance(schema, dict):
        raise ValueError(f"Schema must be a YAML mapping: {schema_path}")
    return schema


def _load_document(document_path: str | Path) -> dict[str, Any]:
    document = _load_yaml(Path(document_path))
    if not isinstance(document, dict):
        raise ValueError(f"Document must be a YAML mapping: {document_path}")
    return document


def _schema_types(schema: dict[str, Any]) -> tuple[str, ...]:
    schema_type = schema.get("type")
    if isinstance(schema_type, list):
        return tuple(str(item) for item in schema_type)
    if isinstance(schema_type, str):
        return (schema_type,)
    return ()


def _matches_type(value: Any, schema_type: str) -> bool:
    if schema_type == "object":
        return isinstance(value, dict)
    if schema_type == "array":
        return isinstance(value, list)
    if schema_type == "string":
        return isinstance(value, str)
    if schema_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if schema_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if schema_type == "boolean":
        return isinstance(value, bool)
    if schema_type == "null":
        return value is None
    return True


def _path_join(parent: str, child: str) -> str:
    return f"{parent}/{child}" if parent else child


def _validate_node(
    value: Any, schema: dict[str, Any], path: str
) -> list[ValidationMessage]:
    errors: list[ValidationMessage] = []
    schema_types = _schema_types(schema)
    if schema_types and not any(
        _matches_type(value, schema_type) for schema_type in schema_types
    ):
        expected = " or ".join(schema_types)
        actual = type(value).__name__
        errors.append(
            ValidationMessage(path or "<root>", f"Expected {expected}, got {actual}")
        )
        return errors

    enum_values = schema.get("enum")
    if enum_values is not None and value not in enum_values:
        errors.append(
            ValidationMessage(
                path or "<root>",
                f"Value {value!r} is not one of: {', '.join(repr(item) for item in enum_values)}",
            )
        )

    if isinstance(value, dict):
        required = schema.get("required", [])
        for field in required:
            if field not in value:
                errors.append(
                    ValidationMessage(
                        _path_join(path, str(field)),
                        f"Missing required field {field!r}",
                    )
                )
        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for field, child_schema in properties.items():
                if field in value and isinstance(child_schema, dict):
                    errors.extend(
                        _validate_node(
                            value[field], child_schema, _path_join(path, str(field))
                        )
                    )

    if isinstance(value, list):
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(value) < min_items:
            errors.append(
                ValidationMessage(
                    path or "<root>",
                    f"Expected at least {min_items} item(s), got {len(value)}",
                )
            )
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(
                    _validate_node(item, item_schema, _path_join(path, str(index)))
                )

    return errors


def validate_document(
    document: dict[str, Any] | None = None,
    schema: dict[str, Any] | None = None,
    *,
    document_path: str | Path = DEFAULT_DOCUMENT_PATH,
    schema_path: str | Path = DEFAULT_SCHEMA_PATH,
) -> dict[str, Any]:
    """Validate a YAML SSOT document and return a serializable report."""

    loaded_schema = schema if schema is not None else load_schema(schema_path)
    loaded_document = (
        document if document is not None else _load_document(document_path)
    )
    errors = _validate_node(loaded_document, loaded_schema, "")
    return {
        "schema_path": str(schema_path),
        "document_path": str(document_path),
        "valid": not errors,
        "error_count": len(errors),
        "errors": [asdict(error) for error in errors],
        "checked_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def _report_to_markdown(report: dict[str, Any]) -> str:
    status = "PASS" if report["valid"] else "FAIL"
    lines = [
        "# YAML SSOT Validation Report",
        "",
        f"- Status: **{status}**",
        f"- Schema: `{report['schema_path']}`",
        f"- Document: `{report['document_path']}`",
        f"- Checked at: `{report['checked_at']}`",
        f"- Error count: **{report['error_count']}**",
        "",
    ]
    if report["errors"]:
        lines.append("## Errors")
        lines.append("")
        for error in report["errors"]:
            lines.append(f"- `{error['path']}`: {error['message']}")
        lines.append("")
    else:
        lines.append("No validation errors found.")
        lines.append("")
    return "\n".join(lines)


def generate_report(
    report: dict[str, Any],
    json_path: str | Path = DEFAULT_JSON_REPORT_PATH,
    markdown_path: str | Path = DEFAULT_MARKDOWN_REPORT_PATH,
) -> dict[str, Path]:
    """Write JSON and Markdown validation reports."""

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
    parser = argparse.ArgumentParser(description="Validate the MASTER YAML SSOT")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument(
        "--document",
        "--ssot",
        dest="document",
        type=Path,
        default=DEFAULT_DOCUMENT_PATH,
    )
    parser.add_argument("--json-report", type=Path, default=DEFAULT_JSON_REPORT_PATH)
    parser.add_argument(
        "--markdown-report", type=Path, default=DEFAULT_MARKDOWN_REPORT_PATH
    )
    args = parser.parse_args(argv)

    report = validate_document(document_path=args.document, schema_path=args.schema)
    outputs = generate_report(report, args.json_report, args.markdown_report)
    if report["valid"]:
        print(f"YAML SSOT validation passed: {outputs['json']} {outputs['markdown']}")
        return 0
    print(f"YAML SSOT validation failed with {report['error_count']} error(s):")
    for error in report["errors"]:
        print(f"- {error['path']}: {error['message']}")
    print(f"Reports written: {outputs['json']} {outputs['markdown']}")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
