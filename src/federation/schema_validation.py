from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


TYPE_MAP = {
    "str": str,
    "bool": bool,
    "list": list,
    "mapping": dict,
}


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _validate_mapping(data: dict[str, Any], schema: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    required = schema.get("required", [])
    for key in required:
        if key not in data:
            errors.append(f"{path}.{key} is required")

    properties = schema.get("properties", {})
    for key, constraints in properties.items():
        if key not in data:
            continue
        value = data[key]
        expected_name = constraints.get("type")
        if expected_name:
            expected_type = TYPE_MAP.get(expected_name)
            if expected_type and not isinstance(value, expected_type):
                errors.append(
                    f"{path}.{key} expected {expected_name}, got {type(value).__name__}"
                )
                continue
        if isinstance(value, dict):
            nested_required = constraints.get("required", [])
            for nested_key in nested_required:
                if nested_key not in value:
                    errors.append(f"{path}.{key}.{nested_key} is required")
    return errors


def validate_repository_ssot(repo_root: Path) -> list[str]:
    governance_path = repo_root / "_config" / "governance.yml"
    schema_root = repo_root / "governance" / "schemas"

    if not governance_path.exists():
        return [f"Missing governance config: {governance_path}"]

    governance = _load_yaml(governance_path)
    errors: list[str] = []

    schema_targets = {
        "identity_boundaries": schema_root / "identity_boundaries.schema.yaml",
        "binary_sources": schema_root / "binary_source_registry.schema.yaml",
        "mcp_sweep": schema_root / "sweep_classification.schema.yaml",
    }

    for section, schema_path in schema_targets.items():
        if not schema_path.exists():
            errors.append(f"Missing schema file: {schema_path}")
            continue
        schema = _load_yaml(schema_path)
        section_data = governance.get(section)
        if not isinstance(section_data, dict):
            errors.append(f"governance section '{section}' must be a mapping")
            continue
        errors.extend(_validate_mapping(section_data, schema, section))

    # RTM schema validates entries produced by sweep output.
    rtm_schema_path = schema_root / "rtm_lineage_delta.schema.yaml"
    if not rtm_schema_path.exists():
        errors.append(f"Missing schema file: {rtm_schema_path}")
    else:
        schema = _load_yaml(rtm_schema_path)
        sample_entry = {
            "unique_id": "RTM-A6-001",
            "parent_requirement": "REQ-FEDERATION-A6",
            "proto_need": "Sample",
            "implementation_path": "sample-path",
            "verification_method": "sample-check",
            "status": "PROPOSED",
        }
        errors.extend(_validate_mapping(sample_entry, schema, "rtm_lineage_delta"))

    return errors
