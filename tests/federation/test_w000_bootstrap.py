import json
from pathlib import Path

import pytest

from codex.bridges.superpipeline_payload import (
    DISPATCH_EVENT_TYPE,
    SuperpipelinePayloadError,
    artifact_name,
    extract_telemetry,
    validate_request,
)
from codex.renderers.abacus_report import render_report, write_report


def sample_telemetry() -> dict:
    return {
        "payload_version": "1.0.0",
        "source": {
            "repository": "GBOGEB/ABACUS",
            "ref": "refs/heads/wave/W000-superpipeline-hub",
            "sha": "1234567890abcdef",
            "run_id": "42",
        },
        "generated_at": "2026-05-28T00:00:00Z",
        "status": "success",
        "summary": "ABACUS calculation engine completed a dispatchable telemetry cycle.",
        "metrics": [
            {"name": "cycle_efficiency", "value": 0.91, "unit": "ratio", "status": "success"},
            {"name": "dispatch_ready", "value": True, "unit": "boolean", "status": "success"},
        ],
        "artifacts": [
            {
                "name": "telemetry_snapshot",
                "path": "outputs/telemetry.json",
                "mime_type": "application/json",
                "description": "Structured ABACUS telemetry snapshot.",
            }
        ],
        "links": [{"label": "ABACUS run", "url": "https://github.com/GBOGEB/ABACUS/actions/runs/42"}],
    }


def sample_request() -> dict:
    return {
        "payload_version": "1.0.0",
        "orchestration": {
            "hub_repository": "GBOGEB/SUPERPIPELINE",
            "source_repository": "GBOGEB/ABACUS",
            "source_event_type": "abacus.telemetry.v1",
            "correlation_id": "w000-a-42",
            "dispatch_run_id": "9001",
        },
        "telemetry": sample_telemetry(),
        "render": {
            "renderer": "abacus_technical_status_report",
            "artifact_name": "abacus_technical_status_report.md",
        },
    }


def test_superpipeline_request_validates_and_exposes_renderer_inputs() -> None:
    request = sample_request()

    validate_request(request)

    assert DISPATCH_EVENT_TYPE == "superpipeline.render_request.v1"
    assert extract_telemetry(request) == request["telemetry"]
    assert artifact_name(request) == "abacus_technical_status_report.md"


def test_superpipeline_request_rejects_non_hub_dispatcher() -> None:
    request = sample_request()
    request["orchestration"]["hub_repository"] = "GBOGEB/ABACUS"

    with pytest.raises(SuperpipelinePayloadError, match="hub_repository"):
        validate_request(request)


def test_superpipeline_request_rejects_malformed_source_context() -> None:
    request = sample_request()
    request["telemetry"]["source"]["sha"] = "123"

    with pytest.raises(SuperpipelinePayloadError, match="telemetry.source.sha"):
        validate_request(request)


def test_superpipeline_request_rejects_path_traversal_artifact_name() -> None:
    request = sample_request()
    request["render"]["artifact_name"] = "../report.md"

    with pytest.raises(SuperpipelinePayloadError, match="artifact_name"):
        validate_request(request)


def test_renderer_generates_markdown_report_from_unwrapped_telemetry() -> None:
    markdown = render_report(extract_telemetry(sample_request()))

    assert "# ABACUS Technical Status Report" in markdown
    assert "GBOGEB/ABACUS" in markdown
    assert "cycle_efficiency" in markdown
    assert "outputs/telemetry.json" in markdown


def test_renderer_writes_markdown_artifact(tmp_path: Path) -> None:
    payload_path = tmp_path / "telemetry.json"
    output_path = tmp_path / "report.md"
    payload_path.write_text(json.dumps(extract_telemetry(sample_request())), encoding="utf-8")

    result = write_report(payload_path, output_path)

    assert result == output_path
    assert output_path.read_text(encoding="utf-8").startswith("# ABACUS Technical Status Report")
