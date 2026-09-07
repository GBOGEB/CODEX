from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import requests
import yaml

from src.github_interface import GitHubInterface
from src.federation.mcp_sweep_services import SweepInputContract, SweepOutputContract, TokenBoundaryGuard, TokenScope, SweepStateStore

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
    """Canonical MCP sweep runtime.

    W04/P3 consumes the shared contract/token/state service layer harvested
    from ``src.mcp_sweep``. The donor orchestration remains intact until
    differential representative/adversarial parity is proven.
    """
    def __init__(self,repo_path:str|Path,github_interface:GitHubInterface,github_token:str,near_miss_keywords:list[str]|None=None,stale_status_values:set[str]|None=None):
        self.repo_path=Path(repo_path); self.github_interface=github_interface; self.github_token=github_token
        self.near_miss_keywords=[i.lower() for i in (near_miss_keywords or ["near-miss","todo","follow-up"])]
        self.stale_status_values={i.lower() for i in (stale_status_values or {"stale","obsolete","cancelled"})}
        self.token_guard=TokenBoundaryGuard(); self.token_guard.handshake(TokenScope.GITHUB,github_token)

    def validate_contract(self,repo:str,max_prs:int=50)->list[str]: return SweepInputContract(repo=repo,max_prs=max_prs).validate()
    def _headers(self)->dict[str,str]: return self.github_interface.get_api_headers(self.token_guard.get_token(TokenScope.GITHUB))
    def fetch_closed_pull_requests(self,owner:str,repo:str,per_page:int=30)->list[dict[str,Any]]:
        response=requests.get(f"{self.github_interface.api_url}/repos/{owner}/{repo}/pulls?state=closed&per_page={per_page}",headers=self._headers(),timeout=20); response.raise_for_status(); return list(response.json())
    def extract_from_pull_requests(self,pulls:list[dict[str,Any]])->tuple[list[SweepItem],list[SweepItem]]:
        proposed=[]; pruned=[]
        for pull in pulls:
            number=pull.get("number"); title=str(pull.get("title","")); body=str(pull.get("body","")); merged_at=pull.get("merged_at"); text=f"{title}\n{body}".lower()
            if any(k in text for k in self.near_miss_keywords):
                proposed.append(SweepItem(f"RTM-A6-PR-{number}",f"{'merged:' if merged_at else 'PR-'}{number}",title,"proposed","federation-wire-link","Review merged PR summary and telemetry"))
            elif not merged_at:
                pruned.append(SweepItem(f"RTM-A6-PR-{number}",f"PR-{number}",f"Closed without merge: {title}","pruned","n/a","Closed PR state verified"))
        return proposed,pruned
    def scan_aborted_sessions(self,session_log_dir:str|Path)->list[SweepItem]:
        findings=[]; log_dir=Path(session_log_dir)
        if not log_dir.exists(): return findings
        for path in sorted(log_dir.glob("*.json")):
            payload=json.loads(path.read_text(encoding="utf-8"))
            if str(payload.get("state","")).lower()=="aborted": findings.append(SweepItem(f"RTM-A6-ABORT-{path.stem}",f"aborted:{path.name}",str(payload.get("suggestion",path.stem)),"proposed","agent-runtime-followup","Replay aborted session output"))
        return findings
    def scan_stale_lineage(self,lineage_path:str|Path)->list[SweepItem]:
        result=[]; target=Path(lineage_path)
        if not target.exists(): return result
        for item in (yaml.safe_load(target.read_text(encoding="utf-8")) or {}).get("entries",[]):
            if str(item.get("status","")).lower() in self.stale_status_values: result.append(SweepItem(str(item.get("unique_id","RTM-A6-UNKNOWN")),str(item.get("origin","lineage")),str(item.get("proto_need","stale lineage marker")),"pruned","lineage-pruning","Stale marker classification",str(item.get("parent_requirement","REQ-FEDERATION-A6"))))
        return result
    @staticmethod
    def _escape_markdown_table_cell(text:str)->str: return text.replace("|","\\|").replace("\n"," ").replace("\r","")
    @staticmethod
    def write_rtm_delta(entries:list[SweepItem],output_path:str|Path)->Path:
        path=Path(output_path); path.parent.mkdir(parents=True,exist_ok=True); lines=["# Local Requirements Traceability Matrix (RTM) Lineage Delta","","| Unique ID | Parent Requirement | Proto-Need | Implementation Path | Verification Method | Status |","| :--- | :--- | :--- | :--- | :--- | :--- |"]
        for i in entries: lines.append(f"| **{MCPSweepEngine._escape_markdown_table_cell(i.unique_id)}** | {MCPSweepEngine._escape_markdown_table_cell(i.parent_requirement)} | {MCPSweepEngine._escape_markdown_table_cell(i.proto_need)} | {MCPSweepEngine._escape_markdown_table_cell(i.implementation_path)} | {MCPSweepEngine._escape_markdown_table_cell(i.verification_method)} | `[{i.status.upper()}]` |")
        path.write_text("\n".join(lines)+"\n",encoding="utf-8"); return path
    @staticmethod
    def write_markdown_telemetry(proposed:list[SweepItem],pruned:list[SweepItem],active:list[SweepItem],output_path:str|Path)->Path:
        path=Path(output_path); path.parent.mkdir(parents=True,exist_ok=True); lines=["## [MCP SWEEP PROTOCOL: COMPLETED]",f"*Generated:* {datetime.now(timezone.utc).isoformat()}","---",f"- Proposed near-misses: {len(proposed)}",f"- Pruned stale/obsolete: {len(pruned)}",f"- Promoted active deltas: {len(active)}",""]
        for label,items in (("NEAR-MISS ESCALATED",proposed),("ACTIVE DELTA",active),("OBSOLETE STATE WIPED",pruned)):
            for i in items: lines.append(f"* **{label}:** {MCPSweepEngine._escape_markdown_table_cell(i.proto_need)} ({MCPSweepEngine._escape_markdown_table_cell(i.origin)})")
        path.write_text("\n".join(lines)+"\n",encoding="utf-8"); return path
    def run(self,owner:str,repo:str,session_log_dir:str|Path,lineage_path:str|Path,telemetry_output_path:str|Path,rtm_delta_output_path:str|Path)->dict[str,Any]:
        issues=self.validate_contract(f"{owner}/{repo}")
        if issues: raise ValueError("; ".join(issues))
        pulls=self.fetch_closed_pull_requests(owner,repo); proposed_pr,pruned_pr=self.extract_from_pull_requests(pulls); proposed=proposed_pr+self.scan_aborted_sessions(session_log_dir); pruned=pruned_pr+self.scan_stale_lineage(lineage_path); active=[i for i in proposed if i.origin.lower().startswith("merged:")]; proposed=[i for i in proposed if i not in active]
        self.write_markdown_telemetry(proposed,pruned,active,telemetry_output_path); self.write_rtm_delta(proposed+active,rtm_delta_output_path)
        return {"proposed_count":len(proposed),"pruned_count":len(pruned),"active_count":len(active),"telemetry_output":str(telemetry_output_path),"rtm_delta_output":str(rtm_delta_output_path)}
