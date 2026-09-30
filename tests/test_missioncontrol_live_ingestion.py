import json
from pathlib import Path

from scripts.ingest_missioncontrol_sources import (
    collect_source,
    derive_federation_events,
    recover_stale,
)


def _source():
    return {
        "id": "example",
        "repository": "GBOGEB/example",
        "authority_class": "REMOTE_AUTHORITATIVE",
        "role": "TEST",
        "branch": "main",
        "ingest": ["repository", "head"],
        "freshness_minutes": 60,
    }


def test_collect_source_binds_exact_head_from_fixture(tmp_path: Path) -> None:
    (tmp_path / "example_repository.json").write_text(
        json.dumps({"default_branch": "main", "pushed_at": "2026-09-30T10:00:00Z", "open_issues_count": 3}),
        encoding="utf-8",
    )
    (tmp_path / "example_head.json").write_text(
        json.dumps({"commit": {"sha": "a" * 40, "html_url": "https://github.com/GBOGEB/example/commit/" + "a" * 40}}),
        encoding="utf-8",
    )
    result = collect_source(
        _source(),
        token=None,
        fixture_dir=tmp_path,
        observed_at="2026-09-30T11:00:00Z",
    )
    assert result["status"] == "FRESH"
    assert result["freshness_status"] == "FRESH"
    assert result["head_sha"] == "a" * 40
    assert result["branch"] == "main"


def test_recover_stale_preserves_last_identity() -> None:
    previous = {
        "sources": [
            {
                "id": "example",
                "repository": "GBOGEB/example",
                "head_sha": "b" * 40,
                "observed_at": "2026-09-30T10:00:00Z",
                "status": "FRESH",
            }
        ]
    }
    current = [
        {
            "id": "example",
            "repository": "GBOGEB/example",
            "status": "ERROR",
            "freshness_status": "ERROR",
            "observed_at": "2026-09-30T11:00:00Z",
            "freshness_minutes": 60,
            "error": "network unavailable",
        }
    ]
    recovered = recover_stale(current, previous)
    assert recovered[0]["status"] == "STALE_CACHE"
    assert recovered[0]["freshness_status"] == "STALE"
    assert recovered[0]["head_sha"] == "b" * 40
    assert recovered[0]["refresh_attempted_at"] == "2026-09-30T11:00:00Z"


def test_temporal_events_record_head_advance_without_authority_transfer() -> None:
    previous = {
        "sources": [
            {
                "id": "example",
                "head_sha": "a" * 40,
            }
        ]
    }
    sources = [
        {
            "id": "example",
            "repository": "GBOGEB/example",
            "branch": "main",
            "head_sha": "b" * 40,
            "authority_class": "REMOTE_AUTHORITATIVE",
            "status": "FRESH",
            "freshness_status": "FRESH",
        }
    ]
    events = derive_federation_events(
        sources=sources,
        previous=previous,
        existing={"events": []},
        observed_at="2026-09-30T11:00:00Z",
    )
    assert events["append_only"] is True
    event = events["events"][0]
    assert event["type"] == "FEDERATION_HEAD_ADVANCED"
    assert event["previous_sha"] == "a" * 40
    assert event["source_sha"] == "b" * 40
    assert event["authority_transfer"] is False
