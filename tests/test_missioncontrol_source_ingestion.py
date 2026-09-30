import json
from pathlib import Path

from scripts.ingest_missioncontrol_sources import collect_source, recover_stale


def test_fixture_ingestion_reads_declared_metadata(tmp_path: Path) -> None:
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
    assert result["default_branch"] == "main"


def test_stale_recovery_preserves_last_known_identity() -> None:
    current = [{"id": "abacus", "status": "ERROR", "observed_at": "now", "error": "timeout"}]
    previous = {"sources": [{"id": "abacus", "status": "FRESH", "repository": "GBOGEB/ABACUS", "head_sha": "abc"}]}
    recovered = recover_stale(current, previous)
    assert recovered[0]["status"] == "STALE_CACHE"
    assert recovered[0]["head_sha"] == "abc"
    assert recovered[0]["refresh_attempted_at"] == "now"
