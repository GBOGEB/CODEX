from scripts.analyze_missioncontrol_logs import analyze


def test_empty_logs_are_withheld() -> None:
    result = analyze([])
    assert result["status"] == "WITHHELD"
    assert result["first_red"] is None


def test_log_analysis_finds_first_red_and_recurrence() -> None:
    result = analyze([
        {"node_id": "repo_codex", "at": "2026-09-30T09:00:00Z", "status": "FAIL", "fingerprint": "STALE_PAGE"},
        {"node_id": "repo_codex", "at": "2026-09-30T09:02:00Z", "status": "SUCCESS", "fingerprint": "FIXED"},
        {"node_id": "repo_codex", "at": "2026-09-30T09:03:00Z", "status": "FAIL", "fingerprint": "STALE_PAGE"},
    ])
    assert result["status"] == "MEASURED"
    assert result["first_red"]["fingerprint"] == "STALE_PAGE"
    assert result["recurrences"][0] == {"fingerprint": "STALE_PAGE", "count": 2}
