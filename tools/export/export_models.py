"""Canonical governance runtime model for W003A exports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tools.traceability.trace_models import stable_uuid

RUNTIME_SCHEMA_VERSION = "0.1"
GOVERNANCE_RUNTIME_ID = stable_uuid("export/governance-runtime")


@dataclass(frozen=True)
class RuntimeSource:
    """Source reference retained by the canonical governance runtime."""

    key: str
    path: str
    kind: str

    def as_dict(self) -> dict[str, str]:
        return {"key": self.key, "path": self.path, "kind": self.kind}


@dataclass(frozen=True)
class RuntimeLink:
    """Parent-child link retained from trace or lineage source models."""

    source: str
    target: str
    relationship: str

    def as_dict(self) -> dict[str, str]:
        return {
            "source": self.source,
            "target": self.target,
            "relationship": self.relationship,
        }


@dataclass(frozen=True)
class ValidationSummary:
    """Volatility-stripped validation summary for deterministic exports."""

    key: str
    status: str
    error_count: int
    report_path: str
    errors: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "status": self.status,
            "error_count": self.error_count,
            "report_path": self.report_path,
            "errors": list(self.errors),
        }


def strip_runtime_volatility(report: dict[str, Any]) -> dict[str, Any]:
    """Remove run-specific fields from validation report payloads."""
    return {key: value for key, value in report.items() if key != "checked_at"}


def ordered_links(nodes: list[dict[str, Any]], relationship: str) -> list[dict[str, str]]:
    """Return parent-child links in the already deterministic node order."""
    return [
        RuntimeLink(source=str(node["parent"]), target=str(node["id"]), relationship=relationship).as_dict()
        for node in nodes
        if node.get("parent")
    ]


def sort_nodes(nodes: list[dict[str, Any]], model_order: list[str]) -> list[dict[str, Any]]:
    """Return nodes sorted by model stage order and UUID for stable exports."""
    stage_index = {stage: index for index, stage in enumerate(model_order)}
    return sorted(nodes, key=lambda node: (stage_index.get(str(node.get("stage")), 999), str(node.get("id"))))
