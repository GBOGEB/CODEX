"""Validate SUPERPIPELINE render requests before CODEX rendering."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

PAYLOAD_VERSION = "1.0.0"
DISPATCH_EVENT_TYPE = "superpipeline.render_request.v1"
SUPPORTED_HUB_REPOSITORY = "GBOGEB/SUPERPIPELINE"
SUPPORTED_RENDERER = "abacus_technical_status_report"
_REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_STATUSES = {"success", "warning", "failure"}
_METRIC_STATUSES = _STATUSES | {"unknown"}


class SuperpipelinePayloadError(ValueError):
    """Raised when a SUPERPIPELINE request cannot be accepted by CODEX."""


def load_request(path: str | Path) -> dict[str, Any]:
    """Load and validate a SUPERPIPELINE render request JSON file."""

    request = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_request(request)
    return request


def validate_request(request: dict[str, Any]) -> None:
    """Validate the dispatch-critical render request contract.

    Validation is intentionally dependency-light so the receiver workflow can run
    before installing optional renderer tooling.
    """

    if not isinstance(request, dict):
        raise SuperpipelinePayloadError("request must be a JSON object")
    _require_keys(request, ("payload_version", "orchestration", "telemetry", "render"), "request")
    if request["payload_version"] != PAYLOAD_VERSION:
        raise SuperpipelinePayloadError(f"payload_version must be {PAYLOAD_VERSION}")

    orchestration = _object(request["orchestration"], "orchestration")
    _require_keys(
        orchestration,
        ("hub_repository", "source_repository", "source_event_type", "correlation_id", "dispatch_run_id"),
        "orchestration",
    )
    for key in ("hub_repository", "source_repository"):
        if not _REPOSITORY_RE.match(_string(orchestration.get(key), f"orchestration.{key}")):
            raise SuperpipelinePayloadError(f"orchestration.{key} must use owner/repo syntax")
    if orchestration["hub_repository"] != SUPPORTED_HUB_REPOSITORY:
        raise SuperpipelinePayloadError(f"orchestration.hub_repository must be {SUPPORTED_HUB_REPOSITORY}")
    for key in ("source_event_type", "correlation_id", "dispatch_run_id"):
        _string(orchestration.get(key), f"orchestration.{key}")

    telemetry = _object(request["telemetry"], "telemetry")
    validate_telemetry(telemetry)

    render = _object(request["render"], "render")
    _require_keys(render, ("renderer", "artifact_name"), "render")
    if render["renderer"] != SUPPORTED_RENDERER:
        raise SuperpipelinePayloadError(f"render.renderer must be {SUPPORTED_RENDERER}")
    artifact_name = _string(render.get("artifact_name"), "render.artifact_name")
    if not artifact_name.endswith(".md") or "/" in artifact_name or "\\" in artifact_name:
        raise SuperpipelinePayloadError("render.artifact_name must be a Markdown filename")


def validate_telemetry(telemetry: dict[str, Any]) -> None:
    """Validate the ABACUS telemetry subset needed by the CODEX renderer."""

    _require_keys(telemetry, ("payload_version", "source", "generated_at", "status", "summary", "metrics", "artifacts"), "telemetry")
    _string(telemetry.get("payload_version"), "telemetry.payload_version")
    _string(telemetry.get("generated_at"), "telemetry.generated_at")
    if telemetry.get("status") not in _STATUSES:
        raise SuperpipelinePayloadError("telemetry.status must be success, warning, or failure")
    _string(telemetry.get("summary"), "telemetry.summary")

    source = _object(telemetry["source"], "telemetry.source")
    _require_keys(source, ("repository", "ref", "sha", "run_id"), "telemetry.source")
    if not _REPOSITORY_RE.match(_string(source.get("repository"), "telemetry.source.repository")):
        raise SuperpipelinePayloadError("telemetry.source.repository must use owner/repo syntax")
    for key in ("ref", "sha", "run_id"):
        _string(source.get(key), f"telemetry.source.{key}")
    if len(source["sha"]) < 7:
        raise SuperpipelinePayloadError("telemetry.source.sha must be at least 7 characters")

    _validate_metrics(telemetry["metrics"])
    _validate_artifacts(telemetry["artifacts"])
    _validate_links(telemetry.get("links", []))


def extract_telemetry(request: dict[str, Any]) -> dict[str, Any]:
    """Return the renderer-ready telemetry payload from a validated request."""

    validate_request(request)
    return dict(request["telemetry"])


def artifact_name(request: dict[str, Any]) -> str:
    """Return the requested Markdown artifact filename from a validated request."""

    validate_request(request)
    return str(request["render"]["artifact_name"])


def _validate_metrics(metrics: Any) -> None:
    if not isinstance(metrics, list):
        raise SuperpipelinePayloadError("telemetry.metrics must be an array")
    for index, metric in enumerate(metrics):
        item = _object(metric, f"telemetry.metrics[{index}]")
        _require_keys(item, ("name", "value"), f"telemetry.metrics[{index}]")
        _string(item.get("name"), f"telemetry.metrics[{index}].name")
        if not isinstance(item.get("value"), (int, float, str, bool)):
            raise SuperpipelinePayloadError(f"telemetry.metrics[{index}].value must be scalar")
        if "unit" in item:
            _string(item.get("unit"), f"telemetry.metrics[{index}].unit", allow_empty=True)
        if item.get("status", "unknown") not in _METRIC_STATUSES:
            raise SuperpipelinePayloadError(f"telemetry.metrics[{index}].status is invalid")


def _validate_artifacts(artifacts: Any) -> None:
    if not isinstance(artifacts, list):
        raise SuperpipelinePayloadError("telemetry.artifacts must be an array")
    for index, artifact in enumerate(artifacts):
        item = _object(artifact, f"telemetry.artifacts[{index}]")
        for key in ("name", "path"):
            _string(item.get(key), f"telemetry.artifacts[{index}].{key}")
        for key in ("mime_type", "description"):
            if key in item:
                _string(item.get(key), f"telemetry.artifacts[{index}].{key}", allow_empty=True)


def _validate_links(links: Any) -> None:
    if not isinstance(links, list):
        raise SuperpipelinePayloadError("telemetry.links must be an array")
    for index, link in enumerate(links):
        item = _object(link, f"telemetry.links[{index}]")
        for key in ("label", "url"):
            _string(item.get(key), f"telemetry.links[{index}].{key}")


def _require_keys(value: dict[str, Any], keys: tuple[str, ...], path: str) -> None:
    missing = sorted(set(keys) - set(value))
    if missing:
        raise SuperpipelinePayloadError(f"{path} missing required field(s): {', '.join(missing)}")


def _object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SuperpipelinePayloadError(f"{path} must be an object")
    return value


def _string(value: Any, path: str, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value):
        raise SuperpipelinePayloadError(f"{path} must be a non-empty string")
    return value


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a SUPERPIPELINE render request for CODEX")
    parser.add_argument("--input", required=True, help="Path to the SUPERPIPELINE render request JSON")
    parser.add_argument("--telemetry-output", help="Optional path to write extracted telemetry JSON")
    parser.add_argument("--artifact-name-output", help="Optional path to write the requested artifact filename")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    request = load_request(args.input)
    if args.telemetry_output:
        Path(args.telemetry_output).write_text(json.dumps(extract_telemetry(request), indent=2) + "\n", encoding="utf-8")
    if args.artifact_name_output:
        Path(args.artifact_name_output).write_text(artifact_name(request) + "\n", encoding="utf-8")
    if not args.telemetry_output and not args.artifact_name_output:
        print(json.dumps(request, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
