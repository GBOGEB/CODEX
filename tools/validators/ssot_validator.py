"""Validate the MASTER Contract Governance Workbench YAML SSOT.

The validator loads a JSON Schema expressed as YAML, validates a YAML SSOT
against it, and writes machine-readable plus Markdown reports for CI and local
handover review.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

DEFAULT_SCHEMA_PATH = Path("schemas/master_contract_ssot.schema.yaml")
DEFAULT_DOCUMENT_PATH = Path("ssot/master_contract_ssot_v0_2.yaml")
DEFAULT_JSON_REPORT_PATH = Path("generated/validation_report.json")
DEFAULT_MARKDOWN_REPORT_PATH = Path("generated/validation_report.md")


@dataclass(frozen=True)
class ValidationIssue:
    """Normalized validation issue for stable reports and test assertions."""

    path: str
    message: str
    validator: str

    def as_dict(self) -> dict[str, str]:
        """Return a JSON-serializable representation of the issue."""
        return {
            "path": self.path,
            "message": self.message,
            "validator": self.validator,
        }


def _load_yaml_file(path: Path) -> Any:
    """Load YAML from ``path`` and raise a clear error if it is missing or empty."""
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    with path.open(encoding="utf-8") as stream:
        data = yaml.safe_load(stream)

    if data is None:
        raise ValueError(f"YAML file is empty: {path}")

    return data


def load_schema(schema_path: Path | str = DEFAULT_SCHEMA_PATH) -> dict[str, Any]:
    """Load the JSON Schema YAML used to validate the MASTER SSOT."""
    path = Path(schema_path)
    schema = _load_yaml_file(path)
    if not isinstance(schema, dict):
        raise TypeError(f"Schema must be a YAML mapping/object: {path}")

    Draft202012Validator.check_schema(schema)
    return schema


def _format_error_path(error: ValidationError) -> str:
    """Format a jsonschema error path for concise human-readable output."""
    if not error.path:
        return "<root>"
    return "/".join(str(part) for part in error.path)


def validate_document(
    document_path: Path | str = DEFAULT_DOCUMENT_PATH,
    schema: dict[str, Any] | None = None,
    schema_path: Path | str = DEFAULT_SCHEMA_PATH,
) -> dict[str, Any]:
    """Validate a YAML SSOT document and return a structured result.

    Args:
        document_path: Path to the YAML SSOT document.
        schema: Optional pre-loaded schema. When omitted, ``schema_path`` is
            loaded via :func:`load_schema`.
        schema_path: Schema path used when ``schema`` is not provided.
    """
    resolved_document_path = Path(document_path)
    resolved_schema_path = Path(schema_path)
    loaded_schema = schema if schema is not None else load_schema(resolved_schema_path)
    document = _load_yaml_file(resolved_document_path)

    validator = Draft202012Validator(loaded_schema)
    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: (list(error.path), error.message),
    )
    issues = [
        ValidationIssue(
            path=_format_error_path(error),
            message=error.message,
            validator=error.validator,
        )
        for error in errors
    ]

    return {
        "status": "pass" if not issues else "fail",
        "schema_path": str(resolved_schema_path),
        "document_path": str(resolved_document_path),
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "error_count": len(issues),
        "errors": [issue.as_dict() for issue in issues],
    }


def _render_markdown(report: dict[str, Any]) -> str:
    """Render a validation report as Markdown."""
    status = "PASS" if report["status"] == "pass" else "FAIL"
    lines = [
        "# MASTER SSOT Validation Report",
        "",
        f"- Status: **{status}**",
        f"- Document: `{report['document_path']}`",
        f"- Schema: `{report['schema_path']}`",
        f"- Checked at: `{report['checked_at']}`",
        f"- Error count: `{report['error_count']}`",
        "",
    ]

    if report["errors"]:
        lines.extend(["## Errors", ""])
        for error in report["errors"]:
            lines.append(
                f"- `{error['path']}`: {error['message']} "
                f"(validator: `{error['validator']}`)"
            )
    else:
        lines.append("No schema validation errors detected.")

    lines.append("")
    return "\n".join(lines)


def generate_report(
    result: dict[str, Any],
    json_report_path: Path | str = DEFAULT_JSON_REPORT_PATH,
    markdown_report_path: Path | str = DEFAULT_MARKDOWN_REPORT_PATH,
) -> dict[str, Path]:
    """Write JSON and Markdown reports for a validation result."""
    json_path = Path(json_report_path)
    markdown_path = Path(markdown_report_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)

    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(_render_markdown(result), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}


def main() -> int:
    """CLI entrypoint. Returns non-zero when validation fails."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument("--document", "--ssot", dest="document", type=Path, default=DEFAULT_DOCUMENT_PATH)
    parser.add_argument("--json-report", type=Path, default=DEFAULT_JSON_REPORT_PATH)
    parser.add_argument("--markdown-report", type=Path, default=DEFAULT_MARKDOWN_REPORT_PATH)
    args = parser.parse_args()

    try:
        schema = load_schema(args.schema)
        result = validate_document(args.document, schema=schema, schema_path=args.schema)
    except Exception as exc:  # CLI boundary: convert loader/schema errors to reports.
        result = {
            "status": "fail",
            "schema_path": str(args.schema),
            "document_path": str(args.document),
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "error_count": 1,
            "errors": [
                {
                    "path": "<loader>",
                    "message": str(exc),
                    "validator": exc.__class__.__name__,
                }
            ],
        }

    generate_report(result, args.json_report, args.markdown_report)
    if result["status"] == "fail":
        print(f"SSOT validation failed with {result['error_count']} error(s).")
        for error in result["errors"]:
            print(f"- {error['path']}: {error['message']}")
        return 1

    print(f"SSOT validation passed for {args.document}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
