from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.federation.mcp_sweep_engine import MCPSweepEngine
from src.federation.mcp_sweep_services import PullRequestCrawler, SweepInputContract


class FakeInterface:
    api_url = "https://api.github.test"

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def api_get(self, path, token=None, params=None):
        self.calls.append((path, token, params))
        return self.responses.pop(0)

    def get_api_headers(self, token):
        return {"Authorization": f"Bearer {token}"}


def pr(number, closed_at, base="main", merged_at=None, title="todo parity", body=""):
    return {"number": number, "closed_at": closed_at, "merged_at": merged_at, "title": title, "body": body,
            "base": {"ref": base}}


def test_contract_rejects_bad_dates_and_inverted_window():
    assert "since must be ISO-8601 when provided" in SweepInputContract(repo="GBOGEB/CODEX", since="bad").validate()
    assert "since must be before until" in SweepInputContract(
        repo="GBOGEB/CODEX", since="2026-09-08T00:00:00Z", until="2026-09-07T00:00:00Z").validate()


def test_crawler_filters_date_branch_and_paginates():
    page1 = [pr(1, "2026-09-07T10:00:00Z"), pr(2, "2026-09-06T10:00:00Z"),
             pr(3, "2026-09-07T11:00:00Z", base="dev")]
    page2 = [pr(4, "2026-09-07T12:00:00Z")]
    interface = FakeInterface([
        {"success": True, "status_code": 200, "data": page1},
        {"success": True, "status_code": 200, "data": page2},
    ])
    crawler = PullRequestCrawler(interface, "token", per_page=3)
    pulls, metrics = crawler.list_closed_pull_requests(
        "GBOGEB", "CODEX", since="2026-09-07T00:00:00Z", branch_filters=("main",), max_prs=10)
    assert [item["number"] for item in pulls] == [1, 4]
    assert metrics["pages_scanned"] == 2


def test_transient_retry_is_counted():
    interface = FakeInterface([
        {"success": False, "status_code": 503, "message": "busy"},
        {"success": True, "status_code": 200, "data": []},
    ])
    crawler = PullRequestCrawler(interface, "token", retry_sleep_seconds=0)
    pulls, metrics = crawler.list_closed_pull_requests("GBOGEB", "CODEX")
    assert pulls == []
    assert metrics["retries"] == 1


def test_append_only_lineage_and_idempotence(tmp_path: Path):
    interface = FakeInterface([{"success": True, "status_code": 200, "data": [
        pr(7, "2026-09-07T12:00:00Z", merged_at="2026-09-07T12:01:00Z")]}])
    engine = MCPSweepEngine(tmp_path, interface, "token")
    kwargs = dict(owner="GBOGEB", repo="CODEX", session_log_dir=tmp_path / "sessions",
                  lineage_path=tmp_path / "lineage.yaml", telemetry_output_path=tmp_path / "telemetry.md",
                  rtm_delta_output_path=tmp_path / "rtm.md", state_path=tmp_path / "state.json")
    first = engine.run(**kwargs)
    assert first["active_count"] == 1
    first_rtm = (tmp_path / "rtm.md").read_text()

    interface.responses.append({"success": True, "status_code": 200, "data": [
        pr(7, "2026-09-07T12:00:00Z", merged_at="2026-09-07T12:01:00Z")]})
    second = engine.run(**kwargs)
    assert second["active_count"] == 0
    assert (tmp_path / "rtm.md").read_text() == first_rtm


def test_adversarial_auth_failure_fails_closed(tmp_path: Path):
    interface = FakeInterface([{"success": False, "status_code": 401, "message": "bad token"}])
    engine = MCPSweepEngine(tmp_path, interface, "token")
    result = engine.run("GBOGEB", "CODEX", tmp_path / "sessions", tmp_path / "lineage.yaml",
                        tmp_path / "telemetry.md", tmp_path / "rtm.md")
    assert result["crawl_metrics"]["auth_failures"] == 1
    assert result["active_count"] == result["proposed_count"] == 0
