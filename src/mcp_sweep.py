"""Alpha A6 MCP sweep integration contracts and runtime pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import enum
import json
from pathlib import Path
import re
import time
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import yaml

from .authenticator import GitHubAuthenticator
from .github_interface import GitHubInterface


REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
PARENT_REQUIREMENT_PATTERN = re.compile(r"(REQ-[A-Z0-9-]+|RTM-[A-Z0-9-]+)")
DEFAULT_OBSOLETE_MARKERS = (
    "obsolete",
    "legacy",
    "deprecated",
    "superseded",
    "wontfix",
    "cancelled",
    "canceled",
    "abandoned",
)
DEFAULT_NEAR_MISS_MARKERS = ("todo", "follow-up", "followup", "optimiz", "improv", "near-miss")


class TokenScope(enum.Enum):
    """Supported runtime token scopes for strict handshake enforcement."""

    GITHUB = "GITHUB_TOKEN"
    OPENAI = "OPENAI_API_TOKEN"
    GEMINI_PRO = "GEMINI_PRO_API_TOKEN"
    ABACUS = "ABACUS_API_TOKEN"


@dataclass
class SweepInputContract:
    """Strict input contract for MCP sweep runs."""

    repo: str
    since: Optional[str] = None
    until: Optional[str] = None
    pr_states: Tuple[str, ...] = ("closed",)
    branch_filters: Tuple[str, ...] = ()
    max_prs: int = 50
    aborted_sessions_path: Optional[str] = None
    required_token_scopes: Tuple[TokenScope, ...] = (TokenScope.GITHUB,)

    def validate(self) -> List[str]:
        issues: List[str] = []
        if not REPO_PATTERN.match(self.repo):
            issues.append("repo must use owner/repo format")
        if self.max_prs <= 0:
            issues.append("max_prs must be greater than zero")
        if any(state.lower() != "closed" for state in self.pr_states):
            issues.append("pr_states currently supports only 'closed'")
        if self.since and not _is_iso_timestamp(self.since):
            issues.append("since must be ISO-8601 when provided")
        if self.until and not _is_iso_timestamp(self.until):
            issues.append("until must be ISO-8601 when provided")
        if self.since and self.until and _parse_timestamp(self.since) > _parse_timestamp(self.until):
            issues.append("since must be before until")
        return issues


@dataclass(frozen=True)
class SweepFinding:
    """Normalized finding from MCP sweep analysis."""

    dedupe_key: str
    source: str
    source_ref: str
    suggestion: str
    confidence: float
    status: str
    provenance: Tuple[str, ...]
    discovered_at: str
    parent_requirement: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dedupe_key": self.dedupe_key,
            "source": self.source,
            "source_ref": self.source_ref,
            "suggestion": self.suggestion,
            "confidence": self.confidence,
            "status": self.status,
            "provenance": list(self.provenance),
            "discovered_at": self.discovered_at,
            "parent_requirement": self.parent_requirement,
        }


@dataclass
class SweepOutputContract:
    """Normalized output contract with explicit near-miss/obsolete partitions."""

    repo: str
    generated_at: str
    near_misses: List[SweepFinding] = field(default_factory=list)
    obsolete_items: List[SweepFinding] = field(default_factory=list)
    crawl_metrics: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        issues: List[str] = []
        if not REPO_PATTERN.match(self.repo):
            issues.append("output repo must use owner/repo format")
        for finding in [*self.near_misses, *self.obsolete_items]:
            if not 0.0 <= finding.confidence <= 1.0:
                issues.append(f"invalid confidence for {finding.dedupe_key}")
            if not finding.provenance:
                issues.append(f"missing provenance for {finding.dedupe_key}")
        return issues

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repo": self.repo,
            "generated_at": self.generated_at,
            "near_misses": [item.to_dict() for item in self.near_misses],
            "obsolete_items": [item.to_dict() for item in self.obsolete_items],
            "crawl_metrics": self.crawl_metrics,
        }

    def to_markdown(self) -> str:
        lines = [
            "## [MCP SWEEP PROTOCOL: COMPLETED]",
            "---",
            f"* Repository: `{self.repo}`",
            f"* Generated: `{self.generated_at}`",
            f"* PR pages scanned: `{self.crawl_metrics.get('pages_scanned', 0)}`",
            f"* Retry attempts: `{self.crawl_metrics.get('retries', 0)}`",
            f"* Authentication failures: `{self.crawl_metrics.get('auth_failures', 0)}`",
            "",
        ]
        for item in self.near_misses:
            lines.append(f"* [ ] **NEAR-MISS ESCALATED:** {item.suggestion}")
            lines.append(f"  - *Origin:* {item.source_ref}")
            lines.append(f"  - *Confidence:* {item.confidence:.2f}")
        lines.append("")
        lines.append(f"* [-] **OBSOLETE STATE WIPED:** Cleared {len(self.obsolete_items)} stale configuration tracks.")
        return "\n".join(lines)


class TokenBoundaryGuard:
    """Enforces explicit per-scope runtime handshake for token access."""

    def __init__(self) -> None:
        self._tokens: Dict[TokenScope, str] = {}

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
    """State persistence with TTL pruning and dedupe protection."""

    state_path: Path
    ttl_days: int = 30

    def load(self) -> Dict[str, str]:
        if not self.state_path.exists():
            return {}
        payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        return {str(k): str(v) for k, v in payload.items()}

    def save(self, payload: Dict[str, str]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def prune(self, now: datetime) -> Dict[str, str]:
        state = self.load()
        cutoff = now - timedelta(days=self.ttl_days)
        kept = {k: v for k, v in state.items() if _parse_timestamp(v) >= cutoff}
        self.save(kept)
        return kept

    def should_include(self, dedupe_key: str, now: datetime) -> bool:
        state = self.prune(now)
        return dedupe_key not in state

    def record(self, dedupe_key: str, now: datetime) -> None:
        state = self.prune(now)
        state[dedupe_key] = now.isoformat()
        self.save(state)


@dataclass
class LineageDeltaStore:
    """Append-only local RTM lineage ledger for near-miss promotions."""

    output_path: Path

    def append_near_misses(self, findings: Sequence[SweepFinding]) -> None:
        if not findings:
            return

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.output_path.exists():
            self.output_path.write_text(
                "\n".join(
                    [
                        "# Local RTM Delta Lineage",
                        "",
                        "| Delta ID | Parent Requirement | Suggestion | Source | Confidence | Timestamp |",
                        "|---|---|---|---|---:|---|",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

        with self.output_path.open("a", encoding="utf-8") as handle:
            for index, finding in enumerate(findings, start=1):
                delta_id = f"RTM-DELTA-{finding.discovered_at.replace(':', '').replace('-', '')}-{index:03d}"
                parent_requirement = finding.parent_requirement or "UNASSIGNED"
                handle.write(
                    f"| {delta_id} | {parent_requirement} | {finding.suggestion} | {finding.source_ref} "
                    f"| {finding.confidence:.2f} | {finding.discovered_at} |\n"
                )


@dataclass
class PullRequestCrawler:
    """Dedicated PR crawl service above GitHub interface/authenticator boundaries."""

    interface: GitHubInterface
    authenticator: GitHubAuthenticator
    max_retries: int = 3
    per_page: int = 30
    retry_sleep_seconds: float = 0.05

    def list_closed_pull_requests(
        self,
        owner: str,
        repo: str,
        *,
        since: Optional[str],
        until: Optional[str],
        branch_filters: Tuple[str, ...],
        max_prs: int,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        metrics = {"pages_scanned": 0, "retries": 0, "auth_failures": 0, "errors": []}
        token = self.authenticator.get_current_token()
        if not token:
            metrics["auth_failures"] += 1
            return [], metrics

        collected: List[Dict[str, Any]] = []
        page = 1
        while len(collected) < max_prs:
            metrics["pages_scanned"] += 1
            result, retries_used = self._request_with_retry(
                f"/repos/{owner}/{repo}/pulls",
                token,
                params={
                    "state": "closed",
                    "sort": "updated",
                    "direction": "desc",
                    "per_page": self.per_page,
                    "page": page,
                },
            )
            metrics["retries"] += retries_used

            status_code = result.get("status_code")
            if status_code in (401, 403):
                metrics["auth_failures"] += 1
                metrics["errors"].append(result.get("message", "authentication error"))
                break
            if not result.get("success"):
                metrics["errors"].append(result.get("message", "request failed"))
                break

            entries = result.get("data", [])
            if not isinstance(entries, list) or not entries:
                break

            for entry in entries:
                if self._is_pr_in_window(entry, since, until) and self._is_pr_on_target_branch(entry, branch_filters):
                    collected.append(entry)
                    if len(collected) >= max_prs:
                        break

            if len(entries) < self.per_page:
                break
            page += 1

        metrics["total_candidates"] = len(collected)
        return collected, metrics

    def get_pull_request_signals(self, owner: str, repo: str, number: int) -> Dict[str, Any]:
        token = self.authenticator.get_current_token()
        if not token:
            return {"number": number, "title": "", "labels": [], "files": [], "commits": [], "reviews": []}

        pr_response, _ = self._request_with_retry(f"/repos/{owner}/{repo}/pulls/{number}", token, params=None)
        base_data = pr_response.get("data", {}) if pr_response.get("success") else {}
        labels = [label.get("name", "") for label in base_data.get("labels", []) if isinstance(label, dict)]

        files = self._collect_paginated(f"/repos/{owner}/{repo}/pulls/{number}/files", token)
        commits = self._collect_paginated(f"/repos/{owner}/{repo}/pulls/{number}/commits", token)
        reviews = self._collect_paginated(f"/repos/{owner}/{repo}/pulls/{number}/reviews", token)

        return {
            "number": number,
            "title": base_data.get("title", ""),
            "labels": labels,
            "files": [item.get("filename", "") for item in files if isinstance(item, dict)],
            "commits": [item.get("commit", {}).get("message", "") for item in commits if isinstance(item, dict)],
            "reviews": [item.get("body", "") for item in reviews if isinstance(item, dict)],
            "closed_at": base_data.get("closed_at"),
            "html_url": base_data.get("html_url", f"https://github.com/{owner}/{repo}/pull/{number}"),
        }

    def _collect_paginated(self, path: str, token: str) -> List[Dict[str, Any]]:
        all_items: List[Dict[str, Any]] = []
        page = 1
        while True:
            result, _ = self._request_with_retry(
                path,
                token,
                params={"per_page": 100, "page": page},
            )
            if not result.get("success"):
                break
            data = result.get("data", [])
            if not isinstance(data, list) or not data:
                break
            all_items.extend(item for item in data if isinstance(item, dict))
            if len(data) < 100:
                break
            page += 1
        return all_items

    def _request_with_retry(
        self,
        path: str,
        token: str,
        params: Optional[Dict[str, Any]],
    ) -> Tuple[Dict[str, Any], int]:
        attempts = 0
        retries_used = 0
        while attempts < self.max_retries:
            attempts += 1
            response = self.interface.api_get(path, token=token, params=params)
            status_code = response.get("status_code")
            if response.get("success"):
                return response, retries_used
            if status_code not in (429, 500, 502, 503, 504):
                return response, retries_used
            retries_used += 1
            time.sleep(self.retry_sleep_seconds)
        return response, retries_used

    @staticmethod
    def _is_pr_in_window(entry: Dict[str, Any], since: Optional[str], until: Optional[str]) -> bool:
        closed_at_raw = entry.get("closed_at")
        if not closed_at_raw:
            return False
        closed_at = _parse_timestamp(closed_at_raw)
        if since and closed_at < _parse_timestamp(since):
            return False
        if until and closed_at > _parse_timestamp(until):
            return False
        return True

    @staticmethod
    def _is_pr_on_target_branch(entry: Dict[str, Any], branch_filters: Tuple[str, ...]) -> bool:
        if not branch_filters:
            return True
        base = entry.get("base", {})
        ref = base.get("ref") if isinstance(base, dict) else None
        return bool(ref and ref in branch_filters)


@dataclass
class MCPSweepEngine:
    """Bounded MCP sweep runtime pipeline with stage telemetry and lineage output."""

    crawler: PullRequestCrawler
    state_store: SweepStateStore
    lineage_store: LineageDeltaStore

    def run(self, contract: SweepInputContract, token_guard: TokenBoundaryGuard) -> SweepOutputContract:
        issues = contract.validate()
        if issues:
            raise ValueError(f"invalid sweep input contract: {issues}")

        for scope in contract.required_token_scopes:
            token_guard.get_token(scope)

        owner, repo = contract.repo.split("/", 1)
        now = datetime.now(timezone.utc)

        candidates, crawl_metrics = self.crawler.list_closed_pull_requests(
            owner,
            repo,
            since=contract.since,
            until=contract.until,
            branch_filters=contract.branch_filters,
            max_prs=contract.max_prs,
        )

        aborted_candidates = self._load_aborted_sessions(contract.aborted_sessions_path)

        near_misses: List[SweepFinding] = []
        obsolete_items: List[SweepFinding] = []

        for candidate in candidates:
            number = int(candidate.get("number", 0))
            if number <= 0:
                continue
            signal = self.crawler.get_pull_request_signals(owner, repo, number)
            finding = self._classify_signal(signal, source="pull_request", source_ref=f"PR-{number}", now=now)
            if not finding:
                continue
            if not self.state_store.should_include(finding.dedupe_key, now):
                continue
            self.state_store.record(finding.dedupe_key, now)
            if finding.status == "obsolete":
                obsolete_items.append(finding)
            else:
                near_misses.append(finding)

        for item in aborted_candidates:
            finding = self._classify_signal(
                item,
                source="aborted_session",
                source_ref=str(item.get("origin", "aborted-session")),
                now=now,
            )
            if not finding:
                continue
            if not self.state_store.should_include(finding.dedupe_key, now):
                continue
            self.state_store.record(finding.dedupe_key, now)
            if finding.status == "obsolete":
                obsolete_items.append(finding)
            else:
                near_misses.append(finding)

        output = SweepOutputContract(
            repo=contract.repo,
            generated_at=now.isoformat(),
            near_misses=near_misses,
            obsolete_items=obsolete_items,
            crawl_metrics=crawl_metrics,
        )
        output_issues = output.validate()
        if output_issues:
            raise ValueError(f"invalid sweep output contract: {output_issues}")

        self.lineage_store.append_near_misses(output.near_misses)
        return output

    @staticmethod
    def _load_aborted_sessions(path: Optional[str]) -> List[Dict[str, Any]]:
        if not path:
            return []
        source = Path(path)
        if not source.exists():
            return []
        payload = json.loads(source.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [entry for entry in payload if isinstance(entry, dict)]
        return []

    def _classify_signal(
        self,
        signal: Dict[str, Any],
        *,
        source: str,
        source_ref: str,
        now: datetime,
    ) -> Optional[SweepFinding]:
        suggestion = str(
            signal.get("suggestion")
            or signal.get("title")
            or signal.get("origin")
            or ""
        ).strip()
        if not suggestion:
            return None

        textual_parts = [
            suggestion,
            *[str(x) for x in signal.get("commits", [])],
            *[str(x) for x in signal.get("reviews", [])],
            *[str(x) for x in signal.get("labels", [])],
        ]
        body = " ".join(textual_parts).lower()
        parent_requirement = _extract_parent_requirement(" ".join(textual_parts))

        is_marked_obsolete = bool(signal.get("is_obsolete"))
        if not is_marked_obsolete:
            is_marked_obsolete = any(marker in body for marker in DEFAULT_OBSOLETE_MARKERS)

        if is_marked_obsolete:
            status = "obsolete"
            confidence = 0.92 if any(marker in body for marker in DEFAULT_OBSOLETE_MARKERS) else 0.75
        else:
            status = "near_miss"
            confidence = 0.84 if any(marker in body for marker in DEFAULT_NEAR_MISS_MARKERS) else 0.68

        provenance = [source_ref]
        for file_path in signal.get("files", [])[:5]:
            if file_path:
                provenance.append(f"file:{file_path}")
        if url := signal.get("html_url"):
            provenance.append(str(url))

        dedupe_key = f"{source}:{source_ref}:{suggestion.lower()}".replace(" ", "-")
        return SweepFinding(
            dedupe_key=dedupe_key,
            source=source,
            source_ref=source_ref,
            suggestion=suggestion,
            confidence=round(confidence, 2),
            status=status,
            provenance=tuple(provenance),
            discovered_at=now.isoformat(),
            parent_requirement=parent_requirement,
        )


def validate_governance_schema(payload: Dict[str, Any]) -> List[str]:
    """Validate Alpha A6 governance YAML shape for sweep runtime usage."""
    issues: List[str] = []

    runtime = payload.get("runtime")
    if not isinstance(runtime, dict):
        issues.append("runtime section is required")
    else:
        if not runtime.get("engine"):
            issues.append("runtime.engine is required")
        if not runtime.get("framework_version"):
            issues.append("runtime.framework_version is required")

    boundaries = payload.get("security_boundaries")
    if not isinstance(boundaries, dict):
        issues.append("security_boundaries section is required")
    else:
        federation = boundaries.get("federation", {})
        tokens = federation.get("allowed_tokens", [])
        required = {scope.value for scope in TokenScope}
        if not required.issubset(set(tokens)):
            issues.append("security_boundaries.federation.allowed_tokens must include all required runtime scopes")

    wire_links = payload.get("wire_links")
    if not isinstance(wire_links, dict):
        issues.append("wire_links section is required")
    else:
        targets = wire_links.get("target_repositories", [])
        if not isinstance(targets, list) or not targets:
            issues.append("wire_links.target_repositories must define at least one repository")

    return issues


def load_governance_config(config_path: Path) -> Dict[str, Any]:
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("governance config must be a mapping")
    issues = validate_governance_schema(payload)
    if issues:
        raise ValueError(f"invalid governance config: {issues}")
    return payload


def _is_iso_timestamp(value: str) -> bool:
    try:
        _parse_timestamp(value)
    except ValueError:
        return False
    return True


def _parse_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _extract_parent_requirement(text: str) -> Optional[str]:
    match = PARENT_REQUIREMENT_PATTERN.search(text)
    if not match:
        return None
    return match.group(1)

