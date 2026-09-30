import json
from pathlib import Path

from scripts.ingest_missioncontrol_sources import (
    collect_source,
    recover_stale,
    temporal_refresh_events,
)


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
    (tmp_path / "codex_repository.json").write_text(json.dumps({"default_branch": "main", "open_issues_count": 4}))
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
