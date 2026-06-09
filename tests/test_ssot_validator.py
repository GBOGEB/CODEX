from __future__ import annotations

import json
from pathlib import Path

import yaml

from tools.validators.ssot_validator import generate_report, load_schema, validate_document


def test_load_schema_loads_required_fields() -> None:
    schema = load_schema()

    assert schema["title"] == "MASTER Contract Governance Workbench SSOT"
    assert "governance" in schema["required"]
    assert "repositories" in schema["properties"]


def test_validate_document_passes_for_current_ssot() -> None:
    schema = load_schema()

    result = validate_document(schema=schema)

    assert result["status"] == "pass"
    assert result["error_count"] == 0
    assert result["errors"] == []


def test_validate_document_reports_missing_required_fields(tmp_path: Path) -> None:
    invalid_document = tmp_path / "invalid.yaml"
    invalid_document.write_text(yaml.safe_dump({"ssot_version": "0.2"}), encoding="utf-8")

    result = validate_document(invalid_document)

    assert result["status"] == "fail"
    messages = [error["message"] for error in result["errors"]]
    assert any("'governance' is a required property" in message for message in messages)
    assert any("'lifecycle' is a required property" in message for message in messages)


def test_generate_report_writes_json_and_markdown(tmp_path: Path) -> None:
    result = validate_document()
    json_report = tmp_path / "validation_report.json"
    markdown_report = tmp_path / "validation_report.md"

    paths = generate_report(result, json_report, markdown_report)

    assert paths["json"] == json_report
    assert paths["markdown"] == markdown_report
    assert json.loads(json_report.read_text(encoding="utf-8"))["status"] == "pass"
    assert "MASTER SSOT Validation Report" in markdown_report.read_text(encoding="utf-8")
