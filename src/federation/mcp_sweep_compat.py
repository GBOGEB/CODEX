"""Compatibility API for the pre-W04 MCP sweep contract surface.

This module is explicitly NON-AUTHORITATIVE. Runtime authority remains
``src.federation.mcp_sweep_engine.MCPSweepEngine``. The adapter preserves the
public ``src.mcp_sweep`` contract while consumers migrate to the canonical
federation runtime/services.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

import yaml

from src.authenticator import GitHubAuthenticator
from src.github_interface import GitHubInterface
from src.federation.mcp_sweep_services import (
    PullRequestCrawler as CanonicalCrawler,
    SweepFinding,
    SweepStateStore as CanonicalStateStore,
    TokenBoundaryGuard,
    TokenScope,
    parse_timestamp,
)

REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
PARENT_REQUIREMENT_PATTERN = re.compile(r"(REQ-[A-Z0-9-]+|RTM-[A-Z0-9-]+)")
DEFAULT_OBSOLETE_MARKERS = ("obsolete", "legacy", "deprecated", "superseded", "wontfix", "cancelled", "canceled", "abandoned")
DEFAULT_NEAR_MISS_MARKERS = ("todo", "follow-up", "followup", "optimiz", "improv", "near-miss")


@dataclass
class SweepInputContract:
    repo: str
    since: str | None = None
    until: str | None = None
    pr_states: tuple[str, ...] = ("closed",)
    branch_filters: tuple[str, ...] = ()
    max_prs: int = 50
    aborted_sessions_path: str | None = None
    required_token_scopes: tuple[TokenScope, ...] = (TokenScope.GITHUB,)

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not REPO_PATTERN.match(self.repo): issues.append("repo must use owner/repo format")
        if self.max_prs <= 0: issues.append("max_prs must be greater than zero")
        if any(state.lower() != "closed" for state in self.pr_states): issues.append("pr_states currently supports only 'closed'")
        try: since = parse_timestamp(self.since) if self.since else None
        except ValueError: issues.append("since must be ISO-8601 when provided"); since = None
        try: until = parse_timestamp(self.until) if self.until else None
        except ValueError: issues.append("until must be ISO-8601 when provided"); until = None
        if since and until and since > until: issues.append("since must be before until")
        return issues


@dataclass
class SweepOutputContract:
    repo: str
    generated_at: str
    near_misses: list[SweepFinding] = field(default_factory=list)
    obsolete_items: list[SweepFinding] = field(default_factory=list)
    crawl_metrics: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> list[str]:
        issues=[]
        if not REPO_PATTERN.match(self.repo): issues.append("output repo must use owner/repo format")
        for finding in [*self.near_misses,*self.obsolete_items]:
            if not 0.0 <= finding.confidence <= 1.0: issues.append(f"invalid confidence for {finding.dedupe_key}")
            if not finding.provenance: issues.append(f"missing provenance for {finding.dedupe_key}")
        return issues


class SweepStateStore(CanonicalStateStore):
    def prune(self, now: datetime) -> dict[str, str]:
        kept = self.load_pruned(now); self.save(kept); return kept


@dataclass
class LineageDeltaStore:
    output_path: Path
    def append_near_misses(self, findings: list[SweepFinding]) -> None:
        if not findings: return
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.output_path.exists():
            self.output_path.write_text("# Local RTM Delta Lineage\n\n| Delta ID | Parent Requirement | Suggestion | Source | Confidence | Timestamp |\n|---|---|---|---|---:|---|\n", encoding="utf-8")
        existing=self.output_path.read_text(encoding="utf-8")
        with self.output_path.open("a",encoding="utf-8") as handle:
            for index,finding in enumerate(findings,start=1):
                marker=f"| {finding.dedupe_key} |"
                if marker in existing: continue
                delta_id=f"RTM-DELTA-{finding.discovered_at.replace(':','').replace('-','')}-{index:03d}"
                handle.write(f"| {delta_id} | {finding.parent_requirement or 'UNASSIGNED'} | {finding.suggestion} | {finding.source_ref} | {finding.confidence:.2f} | {finding.discovered_at} |\n")


@dataclass
class PullRequestCrawler:
    interface: GitHubInterface
    authenticator: GitHubAuthenticator
    max_retries: int = 3
    per_page: int = 30
    retry_sleep_seconds: float = 0.05

    def _canonical(self) -> CanonicalCrawler:
        return CanonicalCrawler(self.interface, self.authenticator.get_current_token() or "", self.max_retries, self.per_page, self.retry_sleep_seconds)

    def list_closed_pull_requests(self, owner:str, repo:str, *, since:str|None, until:str|None, branch_filters:tuple[str,...], max_prs:int):
        token=self.authenticator.get_current_token()
        if not token: return [], {"pages_scanned":0,"retries":0,"auth_failures":1,"errors":[],"total_candidates":0}
        return self._canonical().list_closed_pull_requests(owner,repo,since=since,until=until,branch_filters=branch_filters,max_prs=max_prs)

    def get_pull_request_signals(self, owner:str, repo:str, number:int) -> dict[str,Any]:
        token=self.authenticator.get_current_token()
        if not token: return {"number":number,"title":"","labels":[],"files":[],"commits":[],"reviews":[]}
        base=self.interface.api_get(f"/repos/{owner}/{repo}/pulls/{number}",token=token,params=None)
        data=base.get("data",{}) if base.get("success") else {}
        def collect(suffix:str):
            result=self.interface.api_get(f"/repos/{owner}/{repo}/pulls/{number}/{suffix}",token=token,params={"per_page":100,"page":1})
            return result.get("data",[]) if result.get("success") and isinstance(result.get("data"),list) else []
        labels=[x.get("name","") for x in data.get("labels",[]) if isinstance(x,dict)]
        files=collect("files"); commits=collect("commits"); reviews=collect("reviews")
        return {"number":number,"title":data.get("title",""),"labels":labels,"files":[x.get("filename","") for x in files if isinstance(x,dict)],"commits":[x.get("commit",{}).get("message","") for x in commits if isinstance(x,dict)],"reviews":[x.get("body","") for x in reviews if isinstance(x,dict)],"closed_at":data.get("closed_at"),"html_url":data.get("html_url",f"https://github.com/{owner}/{repo}/pull/{number}")}


@dataclass
class MCPSweepEngine:
    """Compatibility adapter; not MCP runtime authority."""
    crawler: Any
    state_store: SweepStateStore
    lineage_store: LineageDeltaStore

    def run(self, contract:SweepInputContract, token_guard:TokenBoundaryGuard) -> SweepOutputContract:
        issues=contract.validate()
        if issues: raise ValueError(f"invalid sweep input contract: {issues}")
        for scope in contract.required_token_scopes: token_guard.get_token(scope)
        owner,repo=contract.repo.split("/",1); now=datetime.now(timezone.utc)
        candidates,metrics=self.crawler.list_closed_pull_requests(owner,repo,since=contract.since,until=contract.until,branch_filters=contract.branch_filters,max_prs=contract.max_prs)
        aborted=self._load_aborted_sessions(contract.aborted_sessions_path)
        near=[]; obsolete=[]; state=self.state_store.load_pruned(now) if self.state_store.state_path.exists() else {}
        for candidate in candidates:
            number=int(candidate.get("number",0))
            if number<=0: continue
            finding=self._classify_signal(self.crawler.get_pull_request_signals(owner,repo,number),source="pull_request",source_ref=f"PR-{number}",now=now)
            if finding and finding.dedupe_key not in state:
                state[finding.dedupe_key]=now.isoformat(); (obsolete if finding.status=="obsolete" else near).append(finding)
        for item in aborted:
            finding=self._classify_signal(item,source="aborted_session",source_ref=str(item.get("origin","aborted-session")),now=now)
            if finding and finding.dedupe_key not in state:
                state[finding.dedupe_key]=now.isoformat(); (obsolete if finding.status=="obsolete" else near).append(finding)
        if self.state_store.state_path.exists() or state: self.state_store.save(state)
        output=SweepOutputContract(contract.repo,now.isoformat(),near,obsolete,metrics)
        if output.validate(): raise ValueError(f"invalid sweep output contract: {output.validate()}")
        self.lineage_store.append_near_misses(output.near_misses); return output

    @staticmethod
    def _load_aborted_sessions(path:str|None) -> list[dict[str,Any]]:
        if not path or not Path(path).exists(): return []
        payload=json.loads(Path(path).read_text(encoding="utf-8")); return [x for x in payload if isinstance(x,dict)] if isinstance(payload,list) else []

    @staticmethod
    def _classify_signal(signal:dict[str,Any],*,source:str,source_ref:str,now:datetime) -> SweepFinding|None:
        suggestion=str(signal.get("suggestion") or signal.get("title") or signal.get("origin") or "").strip()
        if not suggestion: return None
        parts=[suggestion,*[str(x) for x in signal.get("commits",[])],*[str(x) for x in signal.get("reviews",[])],*[str(x) for x in signal.get("labels",[])]]
        body=" ".join(parts).lower(); match=PARENT_REQUIREMENT_PATTERN.search(" ".join(parts)); parent=match.group(1) if match else None
        obsolete=bool(signal.get("is_obsolete")) or any(m in body for m in DEFAULT_OBSOLETE_MARKERS)
        status="obsolete" if obsolete else "near_miss"; confidence=0.92 if obsolete else (0.84 if any(m in body for m in DEFAULT_NEAR_MISS_MARKERS) else 0.68)
        provenance=[source_ref,*[f"file:{p}" for p in signal.get("files",[])[:5] if p]]
        if signal.get("html_url"): provenance.append(str(signal["html_url"]))
        key=f"{source}:{source_ref}:{suggestion.lower()}".replace(" ","-")
        return SweepFinding(key,source,source_ref,suggestion,round(confidence,2),status,tuple(provenance),now.isoformat(),parent)


def validate_governance_schema(payload:dict[str,Any]) -> list[str]:
    issues=[]; runtime=payload.get("runtime")
    if not isinstance(runtime,dict): issues.append("runtime section is required")
    else:
        if not runtime.get("engine"): issues.append("runtime.engine is required")
        if not runtime.get("framework_version"): issues.append("runtime.framework_version is required")
    boundaries=payload.get("security_boundaries")
    if not isinstance(boundaries,dict): issues.append("security_boundaries section is required")
    else:
        tokens=boundaries.get("federation",{}).get("allowed_tokens",[]); required={s.value for s in TokenScope}
        if not required.issubset(set(tokens)): issues.append("security_boundaries.federation.allowed_tokens must include all required runtime scopes")
    wire=payload.get("wire_links")
    if not isinstance(wire,dict): issues.append("wire_links section is required")
    elif not isinstance(wire.get("target_repositories",[]),list) or not wire.get("target_repositories"): issues.append("wire_links.target_repositories must define at least one repository")
    return issues


def load_governance_config(config_path:Path) -> dict[str,Any]:
    payload=yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(payload,dict): raise ValueError("governance config must be a mapping")
    issues=validate_governance_schema(payload)
    if issues: raise ValueError(f"invalid governance config: {issues}")
    return payload
