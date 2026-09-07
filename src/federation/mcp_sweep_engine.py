from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import yaml

from src.github_interface import GitHubInterface
from src.federation.mcp_sweep_services import (
    AppendOnlyLineageStore,
    PullRequestCrawler,
    SweepInputContract,
    SweepStateStore,
    TokenBoundaryGuard,
    TokenScope,
)


@dataclass(frozen=True)
class SweepItem:
    unique_id: str
    origin: str
    proto_need: str
    status: str
    implementation_path: str
    verification_method: str
    parent_requirement: str = "REQ-FEDERATION-A6"


class MCPSweepEngine:
    """Canonical MCP sweep runtime with donor-equivalent crawl controls."""

    def __init__(self, repo_path: str | Path, github_interface: GitHubInterface, github_token: str,
                 near_miss_keywords: list[str] | None = None, stale_status_values: set[str] | None = None):
        self.repo_path = Path(repo_path)
        self.github_interface = github_interface
        self.github_token = github_token
        self.near_miss_keywords = [i.lower() for i in (near_miss_keywords or ["near-miss", "todo", "follow-up"])]
        self.stale_status_values = {i.lower() for i in (stale_status_values or {"stale", "obsolete", "cancelled"})}
        self.token_guard = TokenBoundaryGuard()
        if github_token:
            self.token_guard.handshake(TokenScope.GITHUB, github_token)

    def validate_contract(self, repo: str, max_prs: int = 50, since: str | None = None,
                          until: str | None = None, branch_filters: tuple[str, ...] = ()) -> list[str]:
        return SweepInputContract(repo=repo, max_prs=max_prs, since=since, until=until, branch_filters=branch_filters).validate()

    def fetch_closed_pull_requests(self, owner: str, repo: str, per_page: int = 30, *,
                                   since: str | None = None, until: str | None = None,
                                   branch_filters: tuple[str, ...] = (), max_prs: int = 50
                                   ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        if not self.github_token:
            return [], {"pages_scanned": 0, "retries": 0, "auth_failures": 0, "errors": [], "total_candidates": 0}
        crawler = PullRequestCrawler(self.github_interface, self.token_guard.get_token(TokenScope.GITHUB), per_page=per_page)
        return crawler.list_closed_pull_requests(owner, repo, since=since, until=until,
                                                 branch_filters=branch_filters, max_prs=max_prs)

    def _fetch_for_run(self, owner: str, repo: str, *, since: str | None, until: str | None,
                       branch_filters: tuple[str, ...], max_prs: int
                       ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Normalize legacy list-returning overrides and the enriched P4 crawler contract."""
        enriched = any((since, until, branch_filters, max_prs != 50))
        if enriched:
            fetched = self.fetch_closed_pull_requests(owner, repo, since=since, until=until,
                                                       branch_filters=branch_filters, max_prs=max_prs)
        else:
            fetched = self.fetch_closed_pull_requests(owner, repo)
        if isinstance(fetched, tuple):
            return fetched
        return fetched, {"pages_scanned": 0, "retries": 0, "auth_failures": 0,
                         "errors": [], "total_candidates": len(fetched)}

    def extract_from_pull_requests(self, pulls: list[dict[str, Any]]) -> tuple[list[SweepItem], list[SweepItem]]:
        proposed: list[SweepItem] = []
        pruned: list[SweepItem] = []
        for pull in pulls:
            number = pull.get("number")
            title = str(pull.get("title", ""))
            body = str(pull.get("body", ""))
            merged_at = pull.get("merged_at")
            text = f"{title}\n{body}".lower()
            if any(k in text for k in self.near_miss_keywords):
                proposed.append(SweepItem(f"RTM-A6-PR-{number}", f"{'merged:' if merged_at else 'PR-'}{number}", title,
                                          "proposed", "federation-wire-link", "Review merged PR summary and telemetry"))
            elif not merged_at:
                pruned.append(SweepItem(f"RTM-A6-PR-{number}", f"PR-{number}", f"Closed without merge: {title}",
                                        "pruned", "n/a", "Closed PR state verified"))
        return proposed, pruned

    def scan_aborted_sessions(self, session_log_dir: str | Path) -> list[SweepItem]:
        findings: list[SweepItem] = []
        log_dir = Path(session_log_dir)
        if not log_dir.exists():
            return findings
        for path in sorted(log_dir.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            if str(payload.get("state", "")).lower() == "aborted":
                findings.append(SweepItem(f"RTM-A6-ABORT-{path.stem}", f"aborted:{path.name}",
                                          str(payload.get("suggestion", path.stem)), "proposed",
                                          "agent-runtime-followup", "Replay aborted session output"))
        return findings

    def scan_stale_lineage(self, lineage_path: str | Path) -> list[SweepItem]:
        result: list[SweepItem] = []
        target = Path(lineage_path)
        if not target.exists():
            return result
        for item in (yaml.safe_load(target.read_text(encoding="utf-8")) or {}).get("entries", []):
            if str(item.get("status", "")).lower() in self.stale_status_values:
                result.append(SweepItem(str(item.get("unique_id", "RTM-A6-UNKNOWN")), str(item.get("origin", "lineage")),
                                        str(item.get("proto_need", "stale lineage marker")), "pruned", "lineage-pruning",
                                        "Stale marker classification", str(item.get("parent_requirement", "REQ-FEDERATION-A6"))))
        return result

    @staticmethod
    def _escape_markdown_table_cell(text: str) -> str:
        return text.replace("|", "\\|").replace("\n", " ").replace("\r", "")

    @staticmethod
    def write_rtm_delta(entries: list[SweepItem], output_path: str | Path) -> Path:
        path = Path(output_path)
        store = AppendOnlyLineageStore(path)
        store.append_rows([{
            "unique_id": item.unique_id,
            "parent_requirement": item.parent_requirement,
            "proto_need": MCPSweepEngine._escape_markdown_table_cell(item.proto_need),
            "implementation_path": MCPSweepEngine._escape_markdown_table_cell(item.implementation_path),
            "verification_method": MCPSweepEngine._escape_markdown_table_cell(item.verification_method),
            "status": item.status,
        } for item in entries])
        return path

    @staticmethod
    def write_markdown_telemetry(proposed: list[SweepItem], pruned: list[SweepItem], active: list[SweepItem],
                                 output_path: str | Path, metrics: dict[str, Any] | None = None) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        metrics = metrics or {}
        lines = ["## [MCP SWEEP PROTOCOL: COMPLETED]", f"*Generated:* {datetime.now(timezone.utc).isoformat()}", "---",
                 f"- Proposed near-misses: {len(proposed)}", f"- Pruned stale/obsolete: {len(pruned)}",
                 f"- Promoted active deltas: {len(active)}", f"- PR pages scanned: {metrics.get('pages_scanned', 0)}",
                 f"- Retry attempts: {metrics.get('retries', 0)}", ""]
        for label, items in (("NEAR-MISS ESCALATED", proposed), ("ACTIVE DELTA", active), ("OBSOLETE STATE WIPED", pruned)):
            for item in items:
                lines.append(f"* **{label}:** {self_text(item.proto_need)} ({self_text(item.origin)})")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def run(self, owner: str, repo: str, session_log_dir: str | Path, lineage_path: str | Path,
            telemetry_output_path: str | Path, rtm_delta_output_path: str | Path, *,
            since: str | None = None, until: str | None = None, branch_filters: tuple[str, ...] = (),
            max_prs: int = 50, state_path: str | Path | None = None) -> dict[str, Any]:
        issues = self.validate_contract(f"{owner}/{repo}", max_prs, since, until, branch_filters)
        if issues:
            raise ValueError("; ".join(issues))
        pulls, metrics = self._fetch_for_run(owner, repo, since=since, until=until,
                                             branch_filters=branch_filters, max_prs=max_prs)
        proposed_pr, pruned_pr = self.extract_from_pull_requests(pulls)
        proposed = proposed_pr + self.scan_aborted_sessions(session_log_dir)
        pruned = pruned_pr + self.scan_stale_lineage(lineage_path)
        active = [i for i in proposed if i.origin.lower().startswith("merged:")]
        proposed = [i for i in proposed if i not in active]
        if state_path:
            store = SweepStateStore(Path(state_path))
            now = datetime.now(timezone.utc)
            proposed = [i for i in proposed if store.should_include(i.unique_id, now)]
            active = [i for i in active if store.should_include(i.unique_id, now)]
            for item in proposed + active:
                store.record(item.unique_id, now)
        self.write_markdown_telemetry(proposed, pruned, active, telemetry_output_path, metrics)
        self.write_rtm_delta(proposed + active, rtm_delta_output_path)
        return {"proposed_count": len(proposed), "pruned_count": len(pruned), "active_count": len(active),
                "crawl_metrics": metrics, "telemetry_output": str(telemetry_output_path),
                "rtm_delta_output": str(rtm_delta_output_path)}


def self_text(value: str) -> str:
    return MCPSweepEngine._escape_markdown_table_cell(value)
