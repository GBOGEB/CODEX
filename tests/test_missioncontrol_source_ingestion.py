import json
from pathlib import Path

import yaml

from scripts.ingest_missioncontrol_sources import (
    IDENTITY_BASIS,
    collect_source,
    recover_stale,
    refresh_identity,
    temporal_refresh_events,
)

ROOT = Path(__file__).resolve().parents[1]


def test_fixture_ingestion_reads_exact_head_and_declared_metadata(
    tmp_path: Path,
) -> None:
    (tmp_path / "codex_repository.json").write_text(
        json.dumps({"default_branch": "main", "open_issues_count": 4})
    )
    (tmp_path / "codex_head.json").write_text(
        json.dumps(
            {
                "sha": "abc123",
                "html_url": "https://github.com/GBOGEB/CODEX/commit/abc123",
            }
        )
    )
    source = {
        "id": "codex",
        "repository": "GBOGEB/CODEX",
        "authority_class": "LOCAL_AUTHORITATIVE",
        "role": "ORCHESTRATION_UI_GOVERNANCE",
        "ingest": ["repository"],
    }
    result = collect_source(source, token=None, fixture_dir=tmp_path)
    assert result["status"] == "FRESH"
    assert result["default_branch"] == "main"
    assert result["head_ref"] == "main"
    assert result["head_sha"] == "abc123"
    assert result["identity_status"] == "MEASURED"
    assert result["head_sha"] == "abc123"
    assert result["telemetry_status"] == "COMPLETE"


def test_stale_recovery_preserves_last_known_identity() -> None:
    current = [
        {
            "id": "abacus",
            "status": "ERROR",
            "observed_at": "now",
            "error": "timeout",
        }
    ]
    previous = {
        "sources": [
            {
                "id": "abacus",
                "status": "FRESH",
                "repository": "GBOGEB/ABACUS",
                "head_sha": "abc",
            }
        ]
    }
    recovered = recover_stale(current, previous)
    assert recovered[0]["status"] == "STALE_CACHE"
    assert recovered[0]["head_sha"] == "abc"
    assert recovered[0]["refresh_attempted_at"] == "now"


def test_temporal_events_append_only_on_source_change() -> None:
    previous = {
        "sources": [
            {
                "id": "abacus",
                "repository": "GBOGEB/ABACUS",
                "authority_class": "REMOTE_AUTHORITATIVE",
                "status": "FRESH",
                "head_sha": "old",
            }
        ]
    }
    current = {
        "generated_at": "2026-09-30T11:20:00+00:00",
        "sources": [
            {
                "id": "abacus",
                "repository": "GBOGEB/ABACUS",
                "authority_class": "REMOTE_AUTHORITATIVE",
                "status": "FRESH",
                "head_sha": "new",
            }
        ],
    }
    events = {
        "events": [
            {
                "id": "EV-0011",
                "at": "earlier",
                "type": "RECOVERY",
                "node_id": "current_next",
                "source_repo": "GBOGEB/CODEX",
                "source_sha": "base",
                "parent_event": None,
                "content_ref": "reentry",
                "summary": "baseline",
            }
        ]
    }
    updated = temporal_refresh_events(previous, current, events)
    assert len(events["events"]) == 1
    assert len(updated["events"]) == 2
    event = updated["events"][-1]
    assert event["id"] == "EV-0012"
    assert event["type"] == "EXTERNAL_RETURN"
    assert event["source_ref"] == "UNBOUND"
    assert event["source_sha"] == "new"
    assert event["acceptance_decision"] == "PROJECTION_ONLY_NO_ACCEPTANCE"
    assert event["authority_transfer"] is False


def test_optional_telemetry_failure_does_not_poison_exact_head(
    tmp_path: Path,
) -> None:
    (tmp_path / "codex_repository.json").write_text(
        json.dumps({"default_branch": "main", "open_issues_count": 4})
    )
    (tmp_path / "codex_head.json").write_text(json.dumps({"sha": "head-ok"}))
    source = {
        "id": "codex",
        "repository": "GBOGEB/CODEX",
        "authority_class": "LOCAL_AUTHORITATIVE",
        "role": "ORCHESTRATION_UI_GOVERNANCE",
        "ingest": ["repository", "issues"],
    }
    result = collect_source(source, token=None, fixture_dir=tmp_path)
    assert result["status"] == "FRESH"
    assert result["head_sha"] == "head-ok"
    assert result["telemetry_status"] == "PARTIAL"
    assert "issues" in result["telemetry_errors"]


def test_fixture_ingestion_withholds_identity_when_head_fixture_missing(tmp_path: Path) -> None:
    (tmp_path / "codex_repository.json").write_text(
        json.dumps({"default_branch": "main", "open_issues_count": 4})
    )
    source = {
        "id": "codex",
        "repository": "GBOGEB/CODEX",
        "authority_class": "LOCAL_AUTHORITATIVE",
        "role": "ORCHESTRATION_UI_GOVERNANCE",
        "ingest": ["repository"],
    }
    result = collect_source(source, token=None, fixture_dir=tmp_path)
    assert result["status"] == "FRESH"
    assert result["head_ref"] == "main"
    assert "head_sha" not in result
    assert result["identity_status"] == "WITHHELD_FIXTURE_HEAD_MISSING"


def test_temporal_event_records_loss_of_exact_identity() -> None:
    previous = {
        "sources": [
            {
                "id": "abacus",
                "repository": "GBOGEB/ABACUS",
                "authority_class": "REMOTE_AUTHORITATIVE",
                "status": "FRESH",
                "identity_status": "MEASURED",
                "head_sha": "old-head",
            }
        ]
    }
    current = {
        "generated_at": "2026-09-30T13:10:00+00:00",
        "sources": [
            {
                "id": "abacus",
                "repository": "GBOGEB/ABACUS",
                "authority_class": "REMOTE_AUTHORITATIVE",
                "status": "FRESH",
                "identity_status": "WITHHELD_HEAD_SHA_MISSING",
                "default_branch": "main",
            }
        ],
    }
    updated = temporal_refresh_events(previous, current, {"events": []})
    assert len(updated["events"]) == 1
    event = updated["events"][0]
    assert event["source_sha"] is None
    assert event["identity_status_before"] == "MEASURED"
    assert event["identity_status_after"] == "WITHHELD_HEAD_SHA_MISSING"
    assert "old-head -> UNAVAILABLE" in event["summary"]


def test_identity_refresh_keeps_curated_census_and_embeds_no_payload() -> None:
    previous = {
        "sources": [
            {
                "id": "abacus",
                "repository": "GBOGEB/ABACUS",
                "authority_class": "REMOTE_AUTHORITATIVE",
                "role": "EXECUTION_DOW",
                "status": "MEASURED_CHAT_CONNECTOR",
                "observed_at": "2026-10-02T13:57:52Z",
                "head_sha": "census-head",
                "census_head_sha": "census-head",
                "census_total": 3129,
                "W293": 0,
                "measurement_basis": "curated census at census-head",
            }
        ]
    }
    current = [
        {
            "id": "abacus",
            "repository": "GBOGEB/ABACUS",
            "authority_class": "REMOTE_AUTHORITATIVE",
            "role": "EXECUTION_DOW",
            "status": "FRESH",
            "observed_at": "2026-10-20T00:00:00+00:00",
            "default_branch": "main",
            "head_ref": "main",
            "head_sha": "live-head",
            "head_url": "https://github.com/GBOGEB/ABACUS/commit/live-head",
            "identity_status": "MEASURED",
            "pushed_at": "2026-10-19T23:00:00Z",
            "open_issue_count": 7,
            "data": {"repository": {"private": False}},
            "telemetry_errors": {},
            "telemetry_status": "COMPLETE",
            "topology": {"open_pulls": 3},
        }
    ]
    [record] = refresh_identity(current, previous)
    assert record["status"] == "FRESH"
    assert record["head_sha"] == "live-head"
    assert record["identity_status"] == "MEASURED"
    assert record["census_head_sha"] == "census-head"
    assert record["census_total"] == 3129
    assert record["W293"] == 0
    assert record["measurement_basis"] == IDENTITY_BASIS
    assert record["curated_measurement_basis"] == "curated census at census-head"
    for key in (
        "data",
        "telemetry_errors",
        "telemetry_status",
        "topology",
        "pushed_at",
        "open_issue_count",
    ):
        assert key not in record

    # A second refresh keeps the original curated basis, not the identity one.
    [again] = refresh_identity(current, {"sources": [record]})
    assert again["curated_measurement_basis"] == "curated census at census-head"


def test_identity_refresh_falls_back_to_stale_cache_on_read_error() -> None:
    previous = {
        "sources": [
            {
                "id": "cryoplant_project",
                "repository": "GBOGEB/cryoplant-project",
                "status": "MEASURED_CHAT_CONNECTOR",
                "head_sha": "last-known",
            }
        ]
    }
    current = [
        {
            "id": "cryoplant_project",
            "repository": "GBOGEB/cryoplant-project",
            "authority_class": "REMOTE_AUTHORITATIVE",
            "role": "ENGINEERING_TRUTH_QPS",
            "status": "ERROR",
            "observed_at": "now",
            "error": "HTTPError: HTTP Error 404: Not Found",
        }
    ]
    [record] = refresh_identity(current, previous)
    assert record["status"] == "STALE_CACHE"
    assert record["head_sha"] == "last-known"
    assert record["refresh_attempted_at"] == "now"


def test_committed_fallback_records_keep_curated_census_fields() -> None:
    status = json.loads(
        (ROOT / "mission_control" / "mycelium" / "source_status.json").read_text(
            encoding="utf-8"
        )
    )
    rows = {row["id"]: row for row in status["sources"]}
    abacus = rows["abacus"]
    for key in ("census_head_sha", "census_job", "census_pr", "census_total", "W293"):
        assert key in abacus
    for row in rows.values():
        assert "data" not in row
        assert row["status"] in {"FRESH", "STALE_CACHE", "MEASURED_CHAT_CONNECTOR"}


def test_pages_rebuilds_on_schedule_from_release_gated_main() -> None:
    workflow = yaml.safe_load(
        (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    )
    triggers = workflow.get("on", workflow.get(True))
    assert "workflow_run" in triggers
    assert triggers["schedule"] and "workflow_dispatch" in triggers
    jobs = workflow["jobs"]
    resolve = jobs["resolve"]
    assert "refs/heads/main" in resolve["if"]
    assert "github.event.workflow_run.conclusion == 'success'" in resolve["if"]
    script = resolve["steps"][0]["run"]
    gate_query = "runtime_release_gate.yml/runs?branch=main&event=push&status=success"
    assert gate_query in script
    assert jobs["build"]["needs"] == "resolve"
    assert jobs["build"]["steps"][0]["with"]["ref"] == (
        "${{ needs.resolve.outputs.source_sha }}"
    )
    assert set(jobs["deploy"]["needs"]) == {"resolve", "build"}
    raw = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    assert raw.count("github.event.workflow_run.head_sha") == 1
