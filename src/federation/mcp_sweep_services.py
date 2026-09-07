"""Canonical MCP sweep contracts and shared runtime services.

W04/P4 completes the donor-capability migration needed before the legacy
``src.mcp_sweep`` orchestration shell can be reduced to a compatibility facade.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import enum
import json
from pathlib import Path
import re
import time
from typing import Any

REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
TRANSIENT_STATUS = {429, 500, 502, 503, 504}


def parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


class TokenScope(enum.Enum):
    GITHUB = "GITHUB_TOKEN"
    OPENAI = "OPENAI_API_TOKEN"
    GEMINI_PRO = "GEMINI_PRO_API_TOKEN"
    ABACUS = "ABACUS_API_TOKEN"


@dataclass
class SweepInputContract:
    repo: str
    since: str | None = None
    until: str | None = None
    pr_states: tuple[str, ...] = ("closed",)
    branch_filters: tuple[str, ...] = ()
    max_prs: int = 50
    required_token_scopes: tuple[TokenScope, ...] = (TokenScope.GITHUB,)

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not REPO_PATTERN.match(self.repo):
            issues.append("repo must use owner/repo format")
        if self.max_prs <= 0:
            issues.append("max_prs must be greater than zero")
        if any(s.lower() != "closed" for s in self.pr_states):
            issues.append("pr_states currently supports only 'closed'")
        try:
            since = parse_timestamp(self.since) if self.since else None
        except ValueError:
            issues.append("since must be ISO-8601 when provided")
            since = None
        try:
            until = parse_timestamp(self.until) if self.until else None
        except ValueError:
            issues.append("until must be ISO-8601 when provided")
            until = None
        if since and until and since > until:
            issues.append("since must be before until")
        return issues


@dataclass(frozen=True)
class SweepFinding:
    dedupe_key: str
    source: str
    source_ref: str
    suggestion: str
    confidence: float
    status: str
    provenance: tuple[str, ...]
    discovered_at: str
    parent_requirement: str | None = None


@dataclass
class SweepOutputContract:
    repo: str
    generated_at: str
    near_misses: list[SweepFinding] = field(default_factory=list)
    obsolete_items: list[SweepFinding] = field(default_factory=list)
    crawl_metrics: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not REPO_PATTERN.match(self.repo):
            issues.append("output repo must use owner/repo format")
        for finding in [*self.near_misses, *self.obsolete_items]:
            if not 0.0 <= finding.confidence <= 1.0:
                issues.append(f"invalid confidence for {finding.dedupe_key}")
            if not finding.provenance:
                issues.append(f"missing provenance for {finding.dedupe_key}")
        return issues


class TokenBoundaryGuard:
    def __init__(self) -> None:
        self._tokens: dict[TokenScope, str] = {}

    def handshake(self, scope: TokenScope, token: str) -> None:
        if not token:
            raise ValueError(f"token required for scope {scope.value}")
        self._tokens[scope] = token

    def get_token(self, scope: TokenScope) -> str:
        if scope not in self._tokens:
            raise PermissionError(f"scope {scope.value} has no explicit handshake")
        return self._tokens[scope]


@dataclass
class SweepStateStore:
    state_path: Path
    ttl_days: int = 30

    def load(self) -> dict[str, str]:
        if not self.state_path.exists():
            return {}
        return {str(k): str(v) for k, v in json.loads(self.state_path.read_text(encoding="utf-8")).items()}

    def save(self, payload: dict[str, str]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def load_pruned(self, now: datetime) -> dict[str, str]:
        cutoff = now - timedelta(days=self.ttl_days)
        return {k: v for k, v in self.load().items() if parse_timestamp(v) >= cutoff}

    def should_include(self, key: str, now: datetime) -> bool:
        return key not in self.load_pruned(now)

    def record(self, key: str, now: datetime) -> None:
        state = self.load_pruned(now)
        state[key] = now.isoformat()
        self.save(state)


@dataclass
class PullRequestCrawler:
    """Paginated, filtered, retry-aware GitHub PR crawler."""

    interface: Any
    token: str
    max_retries: int = 3
    per_page: int = 30
    retry_sleep_seconds: float = 0.05

    def _request(self, path: str, params: dict[str, Any] | None) -> tuple[dict[str, Any], int]:
        retries = 0
        response: dict[str, Any] = {}
        for attempt in range(self.max_retries):
            response = self.interface.api_get(path, token=self.token, params=params)
            if response.get("success"):
                return response, retries
            if response.get("status_code") not in TRANSIENT_STATUS:
                return response, retries
            if attempt + 1 < self.max_retries:
                retries += 1
                time.sleep(self.retry_sleep_seconds)
        return response, retries

    def list_closed_pull_requests(
        self,
        owner: str,
        repo: str,
        *,
        since: str | None = None,
        until: str | None = None,
        branch_filters: tuple[str, ...] = (),
        max_prs: int = 50,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        metrics: dict[str, Any] = {"pages_scanned": 0, "retries": 0, "auth_failures": 0, "errors": []}
        collected: list[dict[str, Any]] = []
        page = 1
        while len(collected) < max_prs:
            metrics["pages_scanned"] += 1
            response, retries = self._request(
                f"/repos/{owner}/{repo}/pulls",
                {"state": "closed", "sort": "updated", "direction": "desc", "per_page": self.per_page, "page": page},
            )
            metrics["retries"] += retries
            status = response.get("status_code")
            if status in (401, 403):
                metrics["auth_failures"] += 1
            if not response.get("success"):
                metrics["errors"].append(response.get("message", "request failed"))
                break
            entries = response.get("data", [])
            if not isinstance(entries, list) or not entries:
                break
            for entry in entries:
                closed_raw = entry.get("closed_at")
                if not closed_raw:
                    continue
                closed_at = parse_timestamp(closed_raw)
                if since and closed_at < parse_timestamp(since):
                    continue
                if until and closed_at > parse_timestamp(until):
                    continue
                if branch_filters:
                    base = entry.get("base", {})
                    if not isinstance(base, dict) or base.get("ref") not in branch_filters:
                        continue
                collected.append(entry)
                if len(collected) >= max_prs:
                    break
            if len(entries) < self.per_page:
                break
            page += 1
        metrics["total_candidates"] = len(collected)
        return collected, metrics


@dataclass
class AppendOnlyLineageStore:
    """Append-only RTM writer that preserves the pre-W04 outward table contract."""

    output_path: Path

    def append_rows(self, rows: list[dict[str, str]]) -> None:
        if not rows:
            return
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.output_path.exists():
            self.output_path.write_text(
                "# Local Requirements Traceability Matrix (RTM) Lineage Delta\n\n"
                "| Unique ID | Parent Requirement | Proto-Need | Implementation Path | Verification Method | Status |\n"
                "| :--- | :--- | :--- | :--- | :--- | :--- |\n",
                encoding="utf-8",
            )
        existing = self.output_path.read_text(encoding="utf-8")
        seen = {row["unique_id"] for row in rows if f"**{row['unique_id']}**" in existing}
        with self.output_path.open("a", encoding="utf-8") as handle:
            for row in rows:
                uid = row["unique_id"]
                if uid in seen:
                    continue
                handle.write(
                    f"| **{uid}** | {row['parent_requirement']} | {row['proto_need']} | "
                    f"{row['implementation_path']} | {row['verification_method']} | `[{row['status'].upper()}]` |\n"
                )
                seen.add(uid)
