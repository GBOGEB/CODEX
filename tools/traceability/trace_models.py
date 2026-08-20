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
        try:
            node_id = data.get("id")
            if not node_id:
                raise ValueError("Missing required field: id")
            stage_value = data.get("stage")
            if not stage_value:
                raise ValueError("Missing required field: stage")
            title_value = data.get("title")
            if not title_value:
                raise ValueError("Missing required field: title")
            
            return cls(
                id=str(node_id),
                stage=TraceStage(str(stage_value)),
                title=str(title_value),
                parent=str(data["parent"]) if data.get("parent") else None,
                source_path=str(data["source_path"]) if data.get("source_path") else None,
            )
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(f"Failed to parse TraceNode from mapping: {e}") from e


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
        try:
            node_id = data.get("id")
            if not node_id:
                raise ValueError("Missing required field: id")
            stage_value = data.get("stage")
            if not stage_value:
                raise ValueError("Missing required field: stage")
            title_value = data.get("title")
            if not title_value:
                raise ValueError("Missing required field: title")
            created_value = data.get("created")
            if not created_value:
                raise ValueError("Missing required field: created")
            updated_value = data.get("updated")
            if not updated_value:
                raise ValueError("Missing required field: updated")
            status_value = data.get("status")
            if not status_value:
                raise ValueError("Missing required field: status")
            
            return cls(
                id=str(node_id),
                stage=LineageStage(str(stage_value)),
                title=str(title_value),
                created=str(created_value),
                updated=str(updated_value),
                parent=str(data["parent"]) if data.get("parent") else None,
                status=str(status_value),
            )
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(f"Failed to parse LineageNode from mapping: {e}") from e


def stable_uuid(name: str) -> str:
    """Return a deterministic UUID string for repository-seeded trace data."""
    return str(uuid5(NAMESPACE_URL, f"GBOGEB/CODEX/W002/{name}"))


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
