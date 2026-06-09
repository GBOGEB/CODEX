"""Shared traceability models for W002 governance validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid5, NAMESPACE_URL


class TraceStage(StrEnum):
    """Required C006 dependency trace stages in governance order."""

    REQUIREMENT = "Requirement"
    APPLICANT_RESPONSE = "Applicant Response"
    REVIEW = "Review"
    CHANGE_REQUEST = "Change Request"
    APPROVAL = "Approval"
    GENERATED_ARTIFACT = "Generated Artifact"


TRACE_STAGE_ORDER: tuple[TraceStage, ...] = (
    TraceStage.REQUIREMENT,
    TraceStage.APPLICANT_RESPONSE,
    TraceStage.REVIEW,
    TraceStage.CHANGE_REQUEST,
    TraceStage.APPROVAL,
    TraceStage.GENERATED_ARTIFACT,
)


class LineageStage(StrEnum):
    """Required C007 lineage stages in governance order."""

    ITT = "ITT"
    APPLICANT_PACKAGE = "Applicant Package"
    REVIEW = "Review"
    REVISION = "Revision"
    APPROVAL = "Approval"
    BASELINE = "Baseline"


LINEAGE_STAGE_ORDER: tuple[LineageStage, ...] = (
    LineageStage.ITT,
    LineageStage.APPLICANT_PACKAGE,
    LineageStage.REVIEW,
    LineageStage.REVISION,
    LineageStage.APPROVAL,
    LineageStage.BASELINE,
)


@dataclass(frozen=True)
class ValidationIssue:
    """Stable validation issue shape for JSON reports and tests."""

    code: str
    message: str
    node_id: str | None = None

    def as_dict(self) -> dict[str, str]:
        payload = {"code": self.code, "message": self.message}
        if self.node_id is not None:
            payload["node_id"] = self.node_id
        return payload


@dataclass(frozen=True)
class TraceNode:
    """Single dependency trace node with a UUID identifier."""

    id: str
    stage: TraceStage
    title: str
    parent: str | None = None
    source_path: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return {
            "id": self.id,
            "stage": self.stage.value,
            "title": self.title,
            "parent": self.parent,
            "source_path": self.source_path,
        }

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "TraceNode":
        return cls(
            id=str(data["id"]),
            stage=TraceStage(str(data["stage"])),
            title=str(data["title"]),
            parent=str(data["parent"]) if data.get("parent") else None,
            source_path=str(data["source_path"]) if data.get("source_path") else None,
        )


@dataclass(frozen=True)
class LineageNode:
    """Single lineage node retaining required governance timestamps and status."""

    id: str
    stage: LineageStage
    title: str
    created: str
    updated: str
    parent: str | None
    status: str

    def as_dict(self) -> dict[str, str | None]:
        return {
            "id": self.id,
            "stage": self.stage.value,
            "title": self.title,
            "created": self.created,
            "updated": self.updated,
            "parent": self.parent,
            "status": self.status,
        }

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "LineageNode":
        return cls(
            id=str(data["id"]),
            stage=LineageStage(str(data["stage"])),
            title=str(data["title"]),
            created=str(data["created"]),
            updated=str(data["updated"]),
            parent=str(data["parent"]) if data.get("parent") else None,
            status=str(data["status"]),
        )


def stable_uuid(name: str) -> str:
    """Return a deterministic UUID string for repository-seeded trace data."""
    return str(uuid5(NAMESPACE_URL, f"GBOGEB/ARTSTYLE-WIP/W002/{name}"))


def is_uuid(value: str) -> bool:
    """Return whether ``value`` is a syntactically valid UUID string."""
    try:
        UUID(value)
    except ValueError:
        return False
    return True


def utc_now() -> str:
    """Return a timezone-aware UTC timestamp for generated reports."""
    return datetime.now(timezone.utc).isoformat()
