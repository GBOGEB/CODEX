"""Validate the MASTER Contract Governance Workbench YAML SSOT.

The validator resolves its default authoritative document/schema through the
CODEX authority resolver, then writes machine-readable plus Markdown reports
for CI and local handover review. Explicit CLI paths remain supported.
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

from codex.ssot_resolver import resolve_ssot


def _default_authority_paths() -> tuple[Path, Path]:
    node = resolve_ssot("CODEX_MASTER_CONTRACT", require_local=True)
    if "path" not in node or "schema" not in node:
        raise RuntimeError("CODEX_MASTER_CONTRACT must declare both path and schema")
    return Path(node["schema"]), Path(node["path"])


DEFAULT_SCHEMA_PATH, DEFAULT_DOCUMENT_PATH = _default_authority_paths()
DEFAULT_JSON_REPORT_PATH = Path("generated/validation_report.json")
DEFAULT_MARKDOWN_REPORT_PATH = Path("generated/validation_report.md")


@dataclass(frozen=True)
class ValidationIssue:
    """Normalized validation issue for stable reports and test assertions."""

    path: str
    message: str
    validator: str

    def as_dict(self) -> dict[str, str]:
        return {"path": self.path, "message": self.message, "validator": self.validator}


def _load_yaml_file(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")
    with path.open(encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    if data is None:
        raise ValueError(f"YAML file is empty: {path}")
    return data


def load_schema(schema_path: Path | str = DEFAULT_SCHEMA_PATH) -> dict[str, Any]:
    path = Path(schema_path)
    schema = _load_yaml_file(path)
    if not isinstance(schema, dict):
        raise TypeError(f"Schema must be a YAML mapping/object: {path}")
    Draft202012Validator.check_schema(schema)
    return schema


def _format_error_path(error: ValidationError) -> str:
    if not error.path:
        return "<root>"
    return "/".join(str(part) for part in error.path)


def validate_document(
    document_path: Path | str = DEFAULT_DOCUMENT_PATH,
    schema: dict[str, Any] | None = None,
    schema_path: Path | str = DEFAULT_SCHEMA_PATH,
) -> dict[str, Any]:
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
    parser.add_argument("--document", "--ssot", dest="document", type=Path, default=DEFAULT_DOCUMENT_PATH)
    parser.add_argument("--json-report", type=Path, default=DEFAULT_JSON_REPORT_PATH)
    parser.add_argument("--markdown-report", type=Path, default=DEFAULT_MARKDOWN_REPORT_PATH)
    args = parser.parse_args()

    try:
        schema = load_schema(args.schema)
        result = validate_document(args.document, schema=schema, schema_path=args.schema)
    except Exception as exc:
        result = {
            "status": "fail",
            "schema_path": str(args.schema),
            "document_path": str(args.document),
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "error_count": 1,
            "errors": [{"path": "<loader>", "message": str(exc), "validator": exc.__class__.__name__}],
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
