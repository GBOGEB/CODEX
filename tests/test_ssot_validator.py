from pathlib import Path

from tools.validators.ssot_validator import (
    generate_report,
    load_schema,
    validate_document,
)


def test_load_schema_loads_mapping() -> None:
    schema = load_schema()

    assert schema["title"] == "MASTER Contract Governance Workbench SSOT"
    assert "ssot_version" in schema["required"]


def test_validate_document_accepts_current_ssot() -> None:
    report = validate_document()

    assert report["valid"] is True
    assert report["errors"] == []


def test_validate_document_reports_missing_required_fields(tmp_path: Path) -> None:
    schema = {
        "type": "object",
        "required": ["ssot_version", "governance"],
        "properties": {
            "ssot_version": {"type": "string"},
            "governance": {
                "type": "object",
                "required": ["rules"],
                "properties": {"rules": {"type": "array", "minItems": 1}},
            },
        },
    }

    report = validate_document(document={"governance": {"rules": []}}, schema=schema)

    assert report["valid"] is False
    assert {error["path"] for error in report["errors"]} == {
        "ssot_version",
        "governance/rules",
    }
    assert "Missing required field" in report["errors"][0]["message"]


def test_generate_report_writes_json_and_markdown(tmp_path: Path) -> None:
    report = validate_document(document={"name": "demo"}, schema={"type": "object"})
    outputs = generate_report(
        report,
        json_path=tmp_path / "validation_report.json",
        markdown_path=tmp_path / "validation_report.md",
    )

    assert outputs["json"].exists()
    assert outputs["markdown"].exists()
    assert "YAML SSOT Validation Report" in outputs["markdown"].read_text(
        encoding="utf-8"
    )
