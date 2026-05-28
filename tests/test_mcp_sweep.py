"""Unit tests for Alpha A6 MCP sweep integration contracts and pipeline."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import pytest

from src.authenticator import GitHubAuthenticator
from src.github_interface import GitHubInterface
from src.mcp_sweep import (
    LineageDeltaStore,
    MCPSweepEngine,
    PullRequestCrawler,
    SweepInputContract,
    SweepStateStore,
    TokenBoundaryGuard,
    TokenScope,
    load_governance_config,
    validate_governance_schema,
)


class StubInterface:
    """Simple stub that returns pre-seeded responses for api_get calls."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def api_get(self, path, token=None, params=None, timeout=10):
        self.calls.append({"path": path, "token": token, "params": params, "timeout": timeout})
        return self.responses.pop(0)


def test_sweep_input_contract_validation_rejects_bad_repo():
    contract = SweepInputContract(repo="bad_repo")
    issues = contract.validate()
    assert any("owner/repo" in issue for issue in issues)


def test_token_boundary_guard_requires_explicit_handshake():
    guard = TokenBoundaryGuard()
    with pytest.raises(PermissionError):
        guard.get_token(TokenScope.GITHUB)

    guard.handshake(TokenScope.GITHUB, "gh-token")
    assert guard.get_token(TokenScope.GITHUB) == "gh-token"


def test_validate_and_load_governance_schema():
    repo_root = Path(__file__).resolve().parents[1]
    config_path = repo_root / "_config/governance.yml"
    payload = load_governance_config(config_path)
    assert payload["runtime"]["engine"] == "Alpha A6"
    assert validate_governance_schema(payload) == []


def test_github_interface_api_get_reports_http_error(monkeypatch):
    class FakeResponse:
        status_code = 500
        headers = {"x-test": "1"}
        text = "server error"

        def json(self):
            return {"message": "server error"}

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr("src.github_interface.requests.get", fake_get)
    interface = GitHubInterface()
    result = interface.api_get("/repos/a/b")
    assert result["success"] is False
    assert result["status_code"] == 500
    assert result["error"] == "HTTP 500"


def test_pull_request_crawler_paginates_filters_and_retries():
    responses = [
        {"success": False, "status_code": 500, "message": "retry", "error": "HTTP 500"},
        {
            "success": True,
            "status_code": 200,
            "data": [
                {
                    "number": 10,
                    "closed_at": "2026-05-10T00:00:00+00:00",
                    "base": {"ref": "main"},
                }
            ],
        },
    ]
    interface = StubInterface(responses)
    auth = GitHubAuthenticator()
    auth._token_cache["current"] = {"token": "tkn", "expires_at": None}
    crawler = PullRequestCrawler(interface=interface, authenticator=auth, retry_sleep_seconds=0.0)

    prs, metrics = crawler.list_closed_pull_requests(
        "GBOGEB",
        "CODEX",
        since="2026-05-01T00:00:00+00:00",
        until="2026-05-20T00:00:00+00:00",
        branch_filters=("main",),
        max_prs=10,
    )

    assert len(prs) == 1
    assert prs[0]["number"] == 10
    assert metrics["retries"] == 1
    assert metrics["pages_scanned"] == 1


def test_mcp_sweep_engine_generates_lineage_and_is_idempotent(tmp_path):
    class StubCrawler:
        def list_closed_pull_requests(self, *args, **kwargs):
            return [
                {
                    "number": 11,
                    "closed_at": "2026-05-11T00:00:00+00:00",
                    "base": {"ref": "main"},
                }
            ], {"pages_scanned": 1, "retries": 0, "auth_failures": 0}

        def get_pull_request_signals(self, owner, repo, number):
            return {
                "number": number,
                "title": "Optimize compressor staging REQ-MINERVA-CORE",
                "labels": ["enhancement"],
                "files": ["src/runtime/engine.py"],
                "commits": ["follow-up optimization"],
                "reviews": ["Looks good; TODO tighten thresholds"],
                "html_url": f"https://github.com/{owner}/{repo}/pull/{number}",
            }

    aborted = tmp_path / "aborted.json"
    aborted.write_text(
        json.dumps(
            [
                {
                    "origin": "Cancelled-Agent-Session-0526",
                    "suggestion": "Legacy Plotly web server interface",
                    "is_obsolete": True,
                }
            ]
        ),
        encoding="utf-8",
    )

    state_store = SweepStateStore(tmp_path / "state.json", ttl_days=90)
    lineage_store = LineageDeltaStore(tmp_path / "lineage.md")
    engine = MCPSweepEngine(crawler=StubCrawler(), state_store=state_store, lineage_store=lineage_store)

    contract = SweepInputContract(
        repo="GBOGEB/CODEX",
        since="2026-05-01T00:00:00+00:00",
        until="2026-05-20T00:00:00+00:00",
        branch_filters=("main",),
        aborted_sessions_path=str(aborted),
    )
    guard = TokenBoundaryGuard()
    guard.handshake(TokenScope.GITHUB, "gh")

    first = engine.run(contract, guard)
    assert len(first.near_misses) == 1
    assert first.near_misses[0].parent_requirement == "REQ-MINERVA-CORE"
    assert len(first.obsolete_items) == 1
    assert first.crawl_metrics["pages_scanned"] == 1
    assert "RTM-DELTA-" in lineage_store.output_path.read_text(encoding="utf-8")

    second = engine.run(contract, guard)
    assert len(second.near_misses) == 0
    assert len(second.obsolete_items) == 0


def test_state_store_prunes_old_entries(tmp_path):
    store = SweepStateStore(tmp_path / "state.json", ttl_days=1)
    now = datetime.now(timezone.utc)
    stale = (now - timedelta(days=2)).isoformat()
    fresh = now.isoformat()
    store.save({"old": stale, "new": fresh})
    remaining = store.prune(now)
    assert "old" not in remaining
    assert "new" in remaining


def test_mcp_sweep_engine_prunes_state_once_per_run(tmp_path):
    class StubCrawler:
        def list_closed_pull_requests(self, *args, **kwargs):
            return [
                {
                    "number": 11,
                    "closed_at": "2026-05-11T00:00:00+00:00",
                    "base": {"ref": "main"},
                }
            ], {"pages_scanned": 1, "retries": 0, "auth_failures": 0}

        def get_pull_request_signals(self, owner, repo, number):
            return {
                "number": number,
                "title": "Optimize compressor staging REQ-MINERVA-CORE",
                "labels": ["enhancement"],
                "files": ["src/runtime/engine.py"],
                "commits": ["follow-up optimization"],
                "reviews": ["Looks good; TODO tighten thresholds"],
                "html_url": f"https://github.com/{owner}/{repo}/pull/{number}",
            }

    class CountingStateStore(SweepStateStore):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.load_pruned_calls = 0
            self.save_calls = 0

        def load_pruned(self, now):
            self.load_pruned_calls += 1
            return super().load_pruned(now)

        def save(self, payload):
            self.save_calls += 1
            super().save(payload)

    now = datetime.now(timezone.utc)
    state_path = tmp_path / "state.json"
    state_path.write_text(
        json.dumps({"stale": (now - timedelta(days=2)).isoformat()}),
        encoding="utf-8",
    )
    store = CountingStateStore(state_path, ttl_days=1)
    lineage_store = LineageDeltaStore(tmp_path / "lineage.md")
    engine = MCPSweepEngine(crawler=StubCrawler(), state_store=store, lineage_store=lineage_store)

    contract = SweepInputContract(
        repo="GBOGEB/CODEX",
        since="2026-05-01T00:00:00+00:00",
        until="2026-05-20T00:00:00+00:00",
        branch_filters=("main",),
    )
    guard = TokenBoundaryGuard()
    guard.handshake(TokenScope.GITHUB, "gh")

    output = engine.run(contract, guard)

    assert len(output.near_misses) == 1
    assert store.load_pruned_calls == 1
    assert store.save_calls == 1
