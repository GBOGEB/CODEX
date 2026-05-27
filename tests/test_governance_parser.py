import json
from pathlib import Path

import pytest

from federation_runtime.engines.governance_parser import (
    extract_governance_block,
    run_header_compliance_audit,
    validate_governance_header,
)


SCHEMA_PATH = Path("federation_runtime/schema/governance_header.schema.json")


def _markdown(fields: dict[str, str] | None = None) -> str:
    metadata = {
        "PR-ID": "PR-007",
        "WAVE": "W003",
        "SPRINT": "S8-P1",
        "DOMAIN": "EXECUTION_GOVERNANCE_INFRASTRUCTURE",
        "TYPE": "GOVERNANCE",
        "CRITICALITY": "HIGH",
        "TOPOLOGY IMPACT": "YES",
        "SCHEMA MUTATION": "CONTROLLED",
    }
    if fields:
        metadata.update(fields)

    lines = ["## PR CLASSIFICATION", *[f"- {key}: {value}" for key, value in metadata.items()], "", "---"]
    return "\n".join(lines)


def test_extract_governance_block_returns_metadata() -> None:
    metadata = extract_governance_block(_markdown())

    assert metadata is not None
    assert metadata["PR-ID"] == "PR-007"
    assert metadata["TYPE"] == "GOVERNANCE"


def test_validate_governance_header_rejects_additional_properties() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    markdown = _markdown({"UNTRACKED": "VALUE"})

    with pytest.raises(ValueError, match="Additional properties are not allowed"):
        validate_governance_header(markdown, schema)


def test_validate_governance_header_rejects_controlled_schema_mutation_outside_governance() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    markdown = _markdown({"TYPE": "RUNTIME", "SCHEMA MUTATION": "CONTROLLED"})

    with pytest.raises(ValueError, match="Unauthorized schema mutation outside GOVERNANCE type"):
        validate_governance_header(markdown, schema)


def test_run_header_compliance_audit_accepts_valid_markdown_file(tmp_path) -> None:
    markdown_path = tmp_path / "governance.md"
    markdown_path.write_text(_markdown(), encoding="utf-8")

    run_header_compliance_audit(markdown_path=markdown_path, schema_path=SCHEMA_PATH, source="tmp governance file")
