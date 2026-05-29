import json
from pathlib import Path

from src.federation.mcp_sweep_engine import MCPSweepEngine
from src.github_interface import GitHubInterface


class FakeSweepEngine(MCPSweepEngine):
    def fetch_closed_pull_requests(self, owner: str, repo: str, per_page: int = 30):
        return [
            {
                "number": 1,
                "title": "Near-miss: improve thermal bridge",
                "body": "contains near-miss follow-up",
                "merged_at": "2026-05-27T00:00:00Z",
            },
            {
                "number": 2,
                "title": "Cancelled experiment",
                "body": "",
                "merged_at": None,
            },
        ]


def test_sweep_run_writes_outputs(tmp_path: Path):
    logs = tmp_path / "logs"
    logs.mkdir(parents=True)
    (logs / "abort-1.json").write_text(
        json.dumps({"state": "aborted", "suggestion": "recover topology delta"}),
        encoding="utf-8",
    )

    lineage = tmp_path / "lineage.yaml"
    lineage.write_text(
        "entries:\n  - unique_id: RTM-A6-OLD\n    status: stale\n    proto_need: drop old route\n",
        encoding="utf-8",
    )

    telemetry = tmp_path / "outputs" / "mcp.md"
    rtm = tmp_path / "traceability" / "RTM_LINEAGE_DELTA.md"

    engine = FakeSweepEngine(
        repo_path=tmp_path,
        github_interface=GitHubInterface(),
        github_token="token",
    )
    result = engine.run(
        owner="GBOGEB",
        repo="CODEX",
        session_log_dir=logs,
        lineage_path=lineage,
        telemetry_output_path=telemetry,
        rtm_delta_output_path=rtm,
    )

    assert result["proposed_count"] + result["active_count"] >= 2
    assert telemetry.exists()
    assert rtm.exists()
