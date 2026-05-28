import json
from pathlib import Path

import pytest

from abacus.bridges.codex_payload import (
    DISPATCH_EVENT_TYPE,
    PayloadValidationError,
    build_repository_dispatch_payload,
    validate_payload,
)
from codex.renderers.abacus_report import render_report, write_report


def sample_payload() -> dict:
    return {
        "payload_version": "1.0.0",
        "source": {
            "repository": "GBOGEB/ABACUS",
            "ref": "refs/heads/wave/W000-federation-bootstrap",
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


def test_payload_validates_and_wraps_for_repository_dispatch() -> None:
    payload = sample_payload()

    validate_payload(payload)
    dispatch = build_repository_dispatch_payload(payload)

    assert dispatch["event_type"] == DISPATCH_EVENT_TYPE
    assert dispatch["client_payload"] == payload


def test_payload_validation_rejects_missing_source_context() -> None:
    payload = sample_payload()
    del payload["source"]["sha"]

    with pytest.raises(PayloadValidationError, match="source.sha"):
        validate_payload(payload)


def test_renderer_generates_markdown_report() -> None:
    markdown = render_report(sample_payload())

    assert "# ABACUS Technical Status Report" in markdown
    assert "GBOGEB/ABACUS" in markdown
    assert "cycle_efficiency" in markdown
    assert "outputs/telemetry.json" in markdown


def test_renderer_writes_markdown_artifact(tmp_path: Path) -> None:
    payload_path = tmp_path / "payload.json"
    output_path = tmp_path / "report.md"
    payload_path.write_text(json.dumps(sample_payload()), encoding="utf-8")

    result = write_report(payload_path, output_path)

    assert result == output_path
    assert output_path.read_text(encoding="utf-8").startswith("# ABACUS Technical Status Report")
