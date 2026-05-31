"""Tests for federation/runtime_registry runtime evidence files."""
from __future__ import annotations

import json
from pathlib import Path


EXPECTED_FILES = (
    "abacus_runtime.json",
    "artstyle_runtime.json",
    "qplant_runtime.json",
    "codex_runtime.json",
)
REQUIRED_FIELDS = {
    "repo",
    "runtime_exists",
    "runtime_validated",
    "deployment_exists",
    "last_execution",
    "last_validation",
    "last_deployment",
    "truth_score",
}


def test_runtime_registry_files_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    registry_dir = root / "federation" / "runtime_registry"
    for filename in EXPECTED_FILES:
        assert (registry_dir / filename).exists(), f"Missing runtime registry file: {filename}"


def test_runtime_registry_files_have_required_fields() -> None:
    root = Path(__file__).resolve().parents[1]
    registry_dir = root / "federation" / "runtime_registry"
    for filename in EXPECTED_FILES:
        payload = json.loads((registry_dir / filename).read_text(encoding="utf-8"))
        assert REQUIRED_FIELDS.issubset(payload.keys()), f"Missing fields in {filename}"
