from __future__ import annotations

import json
from pathlib import Path

import yaml

from tools.export.export_registry import EXPORT_FORMATS, registry_entries
from tools.export.governance_export import build_governance_runtime, generate_governance_runtime


def test_export_registry_includes_renderer_placeholders() -> None:
    entries = registry_entries()

    assert EXPORT_FORMATS == ["json", "yaml", "markdown", "excel", "html"]
    assert entries[-2:] == [
        {"format": "excel", "status": "placeholder"},
        {"format": "html", "status": "placeholder"},
    ]


def test_governance_runtime_aggregates_canonical_sections() -> None:
    runtime = build_governance_runtime()

    assert runtime["schema_version"] == "0.1"
    assert runtime["runtime_id"]
    assert set(runtime) == {
        "schema_version",
        "runtime_id",
        "export_registry",
        "sources",
        "ssot",
        "master_input",
        "dependency_trace",
        "lineage_trace",
        "validation_reports",
    }
    assert [report["key"] for report in runtime["validation_reports"]] == [
        "dependency_trace",
        "lineage",
        "master_input",
        "ssot",
    ]


def test_governance_runtime_preserves_trace_and_lineage_links() -> None:
    runtime = build_governance_runtime()

    dependency_nodes = runtime["dependency_trace"]["nodes"]
    dependency_links = runtime["dependency_trace"]["links"]
    lineage_nodes = runtime["lineage_trace"]["nodes"]
    lineage_links = runtime["lineage_trace"]["links"]

    assert len(dependency_nodes) == 6
    assert len(dependency_links) == 5
    assert {link["target"] for link in dependency_links}.issubset({node["id"] for node in dependency_nodes})
    assert len(lineage_nodes) == 6
    assert len(lineage_links) == 5
    assert runtime["lineage_trace"]["traversal"] == [node["id"] for node in lineage_nodes]


def test_governance_runtime_is_deterministic() -> None:
    first = build_governance_runtime()
    second = build_governance_runtime()

    assert first == second


def test_generate_governance_runtime_writes_json_yaml_and_markdown(tmp_path: Path) -> None:
    json_path = tmp_path / "governance_runtime.json"
    yaml_path = tmp_path / "governance_runtime.yaml"
    markdown_path = tmp_path / "governance_runtime.md"

    runtime, paths = generate_governance_runtime(json_path, yaml_path, markdown_path)

    assert paths == {"json": json_path, "yaml": yaml_path, "markdown": markdown_path}
    assert json.loads(json_path.read_text(encoding="utf-8")) == runtime
    assert yaml.safe_load(yaml_path.read_text(encoding="utf-8")) == runtime
    assert "Governance Runtime Export" in markdown_path.read_text(encoding="utf-8")
