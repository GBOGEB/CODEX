"""Shared MCP sweep contracts/services harvested from the A6 donor runtime.

W04/P3 moves capability beneath the canonical federation runtime without
retiring ``src.mcp_sweep`` until differential parity is proven.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import enum
import json
from pathlib import Path
import re
from typing import Any

REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")

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
        issues=[]
        if not REPO_PATTERN.match(self.repo): issues.append("repo must use owner/repo format")
        if self.max_prs <= 0: issues.append("max_prs must be greater than zero")
        if any(s.lower() != "closed" for s in self.pr_states): issues.append("pr_states currently supports only 'closed'")
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
        issues=[]
        if not REPO_PATTERN.match(self.repo): issues.append("output repo must use owner/repo format")
        for finding in [*self.near_misses,*self.obsolete_items]:
            if not 0.0 <= finding.confidence <= 1.0: issues.append(f"invalid confidence for {finding.dedupe_key}")
            if not finding.provenance: issues.append(f"missing provenance for {finding.dedupe_key}")
        return issues

class TokenBoundaryGuard:
    def __init__(self) -> None: self._tokens: dict[TokenScope,str]={}
    def handshake(self, scope: TokenScope, token: str) -> None:
        if not token: raise ValueError(f"token required for scope {scope.value}")
        self._tokens[scope]=token
    def get_token(self, scope: TokenScope) -> str:
        if scope not in self._tokens: raise PermissionError(f"scope {scope.value} has no explicit handshake")
        return self._tokens[scope]

@dataclass
class SweepStateStore:
    state_path: Path
    ttl_days: int = 30
    def load(self) -> dict[str,str]:
        if not self.state_path.exists(): return {}
        return {str(k):str(v) for k,v in json.loads(self.state_path.read_text(encoding="utf-8")).items()}
    def save(self,payload:dict[str,str])->None:
        self.state_path.parent.mkdir(parents=True,exist_ok=True)
        self.state_path.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
    def load_pruned(self,now:datetime)->dict[str,str]:
        cutoff=now-timedelta(days=self.ttl_days)
        return {k:v for k,v in self.load().items() if datetime.fromisoformat(v.replace("Z","+00:00")) >= cutoff}
    def should_include(self,key:str,now:datetime)->bool: return key not in self.load_pruned(now)
    def record(self,key:str,now:datetime)->None:
        state=self.load_pruned(now); state[key]=now.isoformat(); self.save(state)
