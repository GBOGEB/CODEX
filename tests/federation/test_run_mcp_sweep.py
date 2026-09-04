from __future__ import annotations

import json
from pathlib import Path

import yaml

from src.federation.mcp_sweep_engine import MCPSweepEngine
from src.github_interface import GitHubInterface


def test_mcp_sweep_pipeline_classifies_and_emits_outputs(tmp_path, monkeypatch):
    engine = MCPSweepEngine(
        repo_path=tmp_path,
        github_interface=GitHubInterface(),
        github_token="test-token",
    )

    pulls = [
        {
            "number": 101,
            "title": "near-miss follow-up | runtime",
            "body": "TODO: retain escaped newline\nwithout a second row",
            "merged_at": "2026-09-04T00:00:00Z",
        },
        {
            "number": 102,
            "title": "closed experiment",
            "body": "no promoted work",
            "merged_at": None,
        },
    ]
    monkeypatch.setattr(engine, "fetch_closed_pull_requests", lambda owner, repo: pulls)

    session_dir = tmp_path / "sessions"
    session_dir.mkdir()
    (session_dir / "aborted.json").write_text(
        json.dumps({"state": "aborted", "suggestion": "follow-up aborted worker"}),
        encoding="utf-8",
    )

    lineage = tmp_path / "lineage.yaml"
    lineage.write_text(
        yaml.safe_dump(
            {
                "entries": [
                    {
                        "unique_id": "RTM-A6-STALE-1",
                        "origin": "old-lane",
                        "proto_need": "obsolete worker",
                        "status": "stale",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    telemetry = tmp_path / "out" / "sweep_telemetry.md"
    rtm_delta = tmp_path / "out" / "rtm_delta.md"
    result = engine.run(
        owner="GBOGEB",
        repo="CODEX",
        session_log_dir=session_dir,
        lineage_path=lineage,
        telemetry_output_path=telemetry,
        rtm_delta_output_path=rtm_delta,
    )

    assert result["active_count"] == 1
    assert result["proposed_count"] == 1
    assert result["pruned_count"] == 2
    assert telemetry.is_file()
    assert rtm_delta.is_file()

    text = rtm_delta.read_text(encoding="utf-8")
    assert "near-miss follow-up \\| runtime" in text
    assert "merged:101" not in text  # origin is telemetry, not an RTM table column
    assert "RTM-A6-PR-101" in text


def test_mcp_sweep_is_public_metadata_only_by_construction(tmp_path, monkeypatch):
    engine = MCPSweepEngine(
        repo_path=tmp_path,
        github_interface=GitHubInterface(),
        github_token="",
    )
    monkeypatch.setattr(engine, "fetch_closed_pull_requests", lambda owner, repo: [])

    result = engine.run(
        owner="GBOGEB",
        repo="CODEX",
        session_log_dir=tmp_path / "missing-sessions",
        lineage_path=tmp_path / "missing-lineage.yaml",
        telemetry_output_path=tmp_path / "out" / "telemetry.md",
        rtm_delta_output_path=tmp_path / "out" / "delta.md",
    )
    assert result["proposed_count"] == 0
    assert result["pruned_count"] == 0
    assert result["active_count"] == 0
