"""Build and validate ABACUS telemetry payloads for CODEX dispatch."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PAYLOAD_VERSION = "1.0.0"
DISPATCH_EVENT_TYPE = "abacus.telemetry.v1"
_REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_STATUSES = {"success", "warning", "failure"}
_METRIC_STATUSES = _STATUSES | {"unknown"}


class PayloadValidationError(ValueError):
    """Raised when an ABACUS telemetry payload is not dispatch-safe."""


@dataclass(frozen=True)
class SourceContext:
    """GitHub source context for a telemetry payload."""

    repository: str
    ref: str
    sha: str
    run_id: str

    def to_dict(self) -> dict[str, str]:
        return {
            "repository": self.repository,
            "ref": self.ref,
            "sha": self.sha,
            "run_id": self.run_id,
        }


@dataclass(frozen=True)
class TelemetryMetric:
    """Single ABACUS telemetry metric."""

    name: str
    value: int | float | str | bool
    unit: str = ""
    status: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "status": self.status,
        }


@dataclass(frozen=True)
class TelemetryArtifact:
    """Artifact reference emitted by ABACUS."""

    name: str
    path: str
    mime_type: str = "application/octet-stream"
    description: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "path": self.path,
            "mime_type": self.mime_type,
            "description": self.description,
        }


@dataclass(frozen=True)
class TelemetryPayload:
    """Versioned payload sent from ABACUS to CODEX."""

    source: SourceContext
    status: str
    summary: str
    metrics: list[TelemetryMetric] = field(default_factory=list)
    artifacts: list[TelemetryArtifact] = field(default_factory=list)
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    links: list[dict[str, str]] = field(default_factory=list)
    payload_version: str = PAYLOAD_VERSION

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "payload_version": self.payload_version,
            "source": self.source.to_dict(),
            "generated_at": self.generated_at,
            "status": self.status,
            "summary": self.summary,
            "metrics": [metric.to_dict() for metric in self.metrics],
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "links": self.links,
        }
        validate_payload(payload)
        return payload


def load_payload(path: str | Path) -> dict[str, Any]:
    """Load a telemetry payload from JSON and validate it."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_payload(payload)
    return payload


def validate_payload(payload: dict[str, Any]) -> None:
    """Validate the dispatch-critical subset of telemetry.schema.json.

    The bridge intentionally uses standard-library checks so the dispatch workflow
    has no dependency installation step before repository_dispatch.
    """

    if not isinstance(payload, dict):
        raise PayloadValidationError("payload must be a JSON object")

    required = {"payload_version", "source", "generated_at", "status", "summary", "metrics", "artifacts"}
    missing = sorted(required - set(payload))
    if missing:
        raise PayloadValidationError(f"missing required field(s): {', '.join(missing)}")

    if payload["payload_version"] != PAYLOAD_VERSION:
        raise PayloadValidationError(f"payload_version must be {PAYLOAD_VERSION}")

    source = payload["source"]
    if not isinstance(source, dict):
        raise PayloadValidationError("source must be an object")
    for key in ("repository", "ref", "sha", "run_id"):
        if not isinstance(source.get(key), str) or not source[key]:
            raise PayloadValidationError(f"source.{key} must be a non-empty string")
    if not _REPOSITORY_RE.match(source["repository"]):
        raise PayloadValidationError("source.repository must use owner/repo syntax")
    if len(source["sha"]) < 7:
        raise PayloadValidationError("source.sha must be at least 7 characters")

    if not isinstance(payload["generated_at"], str) or not payload["generated_at"]:
        raise PayloadValidationError("generated_at must be a non-empty string")
    if payload["status"] not in _STATUSES:
        raise PayloadValidationError("status must be success, warning, or failure")
    if not isinstance(payload["summary"], str) or not payload["summary"]:
        raise PayloadValidationError("summary must be a non-empty string")

    _validate_metrics(payload["metrics"])
    _validate_artifacts(payload["artifacts"])
    _validate_links(payload.get("links", []))


def build_repository_dispatch_payload(
    telemetry_payload: dict[str, Any],
    event_type: str = DISPATCH_EVENT_TYPE,
) -> dict[str, Any]:
    """Wrap telemetry in GitHub repository_dispatch request shape."""

    validate_payload(telemetry_payload)
    return {"event_type": event_type, "client_payload": telemetry_payload}


def _validate_metrics(metrics: Any) -> None:
    if not isinstance(metrics, list):
        raise PayloadValidationError("metrics must be an array")
    for index, metric in enumerate(metrics):
        if not isinstance(metric, dict):
            raise PayloadValidationError(f"metrics[{index}] must be an object")
        if not isinstance(metric.get("name"), str) or not metric["name"]:
            raise PayloadValidationError(f"metrics[{index}].name must be a non-empty string")
        if "value" not in metric or not isinstance(metric["value"], (int, float, str, bool)):
            raise PayloadValidationError(f"metrics[{index}].value must be scalar telemetry")
        if "unit" in metric and not isinstance(metric["unit"], str):
            raise PayloadValidationError(f"metrics[{index}].unit must be a string")
        if metric.get("status", "unknown") not in _METRIC_STATUSES:
            raise PayloadValidationError(f"metrics[{index}].status is invalid")


def _validate_artifacts(artifacts: Any) -> None:
    if not isinstance(artifacts, list):
        raise PayloadValidationError("artifacts must be an array")
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            raise PayloadValidationError(f"artifacts[{index}] must be an object")
        for key in ("name", "path"):
            if not isinstance(artifact.get(key), str) or not artifact[key]:
                raise PayloadValidationError(f"artifacts[{index}].{key} must be a non-empty string")
        for key in ("mime_type", "description"):
            if key in artifact and not isinstance(artifact[key], str):
                raise PayloadValidationError(f"artifacts[{index}].{key} must be a string")


def _validate_links(links: Any) -> None:
    if not isinstance(links, list):
        raise PayloadValidationError("links must be an array")
    for index, link in enumerate(links):
        if not isinstance(link, dict):
            raise PayloadValidationError(f"links[{index}] must be an object")
        for key in ("label", "url"):
            if not isinstance(link.get(key), str) or not link[key]:
                raise PayloadValidationError(f"links[{index}].{key} must be a non-empty string")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and wrap ABACUS telemetry for CODEX dispatch")
    parser.add_argument("--input", required=True, help="Path to an ABACUS telemetry JSON payload")
    parser.add_argument("--output", help="Optional path for repository_dispatch JSON body")
    parser.add_argument("--event-type", default=DISPATCH_EVENT_TYPE, help="GitHub repository_dispatch event type")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    payload = load_payload(args.input)
    dispatch_body = build_repository_dispatch_payload(payload, event_type=args.event_type)
    if args.output:
        Path(args.output).write_text(json.dumps(dispatch_body, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(dispatch_body, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
