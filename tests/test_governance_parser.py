import json
from pathlib import Path

from federation_runtime.engines.governance_parser import extract_governance_block, validate_metadata


def _load_schema() -> dict:
    schema_path = Path("federation_runtime/schema/governance_header.schema.json")
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _valid_metadata() -> dict[str, str]:
    return {
        "PR-ID": "PR-007",
        "WAVE": "W003",
        "SPRINT": "S8-P1",
        "DOMAIN": "EXECUTION_GOVERNANCE_INFRASTRUCTURE",
        "TYPE": "GOVERNANCE",
        "CRITICALITY": "HIGH",
        "TOPOLOGY IMPACT": "YES",
        "SCHEMA MUTATION": "CONTROLLED",
    }


def test_extract_governance_block_reads_pr_classification() -> None:
    markdown = """
## PR CLASSIFICATION
- PR-ID: PR-007
- WAVE: W003
- SPRINT: S8-P1
- DOMAIN: EXECUTION_GOVERNANCE_INFRASTRUCTURE
- TYPE: GOVERNANCE
- CRITICALITY: HIGH
- TOPOLOGY IMPACT: YES
- SCHEMA MUTATION: CONTROLLED

---
"""
    metadata = extract_governance_block(markdown)
    assert metadata is not None
    assert metadata["PR-ID"] == "PR-007"
    assert metadata["TYPE"] == "GOVERNANCE"


def test_validate_metadata_accepts_valid_governance_header() -> None:
    valid, errors = validate_metadata(_valid_metadata(), _load_schema())
    assert valid is True
    assert errors == []


def test_validate_metadata_rejects_unknown_key_when_additional_properties_false() -> None:
    metadata = _valid_metadata() | {"EXTRA": "VALUE"}
    valid, errors = validate_metadata(metadata, _load_schema())
    assert valid is False
    assert "Unknown key not allowed by schema: EXTRA" in errors


def test_validate_metadata_rejects_pattern_and_enum_and_const_mismatch() -> None:
    metadata = _valid_metadata() | {
        "PR-ID": "PR-7",
        "DOMAIN": "WRONG_DOMAIN",
        "CRITICALITY": "SEVERE",
    }
    valid, errors = validate_metadata(metadata, _load_schema())
    assert valid is False
    assert any(error.startswith("Pattern mismatch for PR-ID:") for error in errors)
    assert any(error.startswith("Const mismatch for DOMAIN:") for error in errors)
    assert any(error.startswith("Enum mismatch for CRITICALITY:") for error in errors)


def test_validate_metadata_rejects_schema_mutation_outside_governance_type() -> None:
    metadata = _valid_metadata() | {
        "TYPE": "RUNTIME",
        "SCHEMA MUTATION": "YES",
    }
    valid, errors = validate_metadata(metadata, _load_schema())
    assert valid is False
    assert "Unauthorized schema mutation outside GOVERNANCE type" in errors
