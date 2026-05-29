from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import requests
import yaml

from src.github_interface import GitHubInterface


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
    """Ingests closed PRs, aborted sessions, and stale lineage markers.
    
    TODO: Wave A6 — CI integration needed
    - Task A6.3.1.1: Create scripts/run_mcp_sweep.py CI script
    - Task A6.3.1.2: Wire into .github/workflows/ci.yml (post-test, pre-publish)
    - Task A6.3.1.3: Publish RTM delta to GitHub Pages
    - See: MANIFEST/A6_FEDERATION_TODO_ROADMAP.md § Phase A6.3
    
    TODO: Wave A7 — Orchestration integration
    - Task A7.1.1.3: Connect to federation_lane_orchestrator.py
    - Task A7.2.1.1: MCP sweep telemetry dashboard visualization
    - See: MANIFEST/A6_FEDERATION_TODO_ROADMAP.md § Phase A7.2
    """

    def __init__(
        self,
        repo_path: str | Path,
        github_interface: GitHubInterface,
        github_token: str,
        near_miss_keywords: list[str] | None = None,
        stale_status_values: set[str] | None = None,
    ):
        self.repo_path = Path(repo_path)
        self.github_interface = github_interface
        self.github_token = github_token
        self.near_miss_keywords = [item.lower() for item in (near_miss_keywords or ["near-miss", "todo", "follow-up"])]
        self.stale_status_values = {item.lower() for item in (stale_status_values or {"stale", "obsolete", "cancelled"})}

    def _headers(self) -> dict[str, str]:
        return self.github_interface.get_api_headers(self.github_token)

    def fetch_closed_pull_requests(self, owner: str, repo: str, per_page: int = 30) -> list[dict[str, Any]]:
        url = f"{self.github_interface.api_url}/repos/{owner}/{repo}/pulls?state=closed&per_page={per_page}"
        response = requests.get(url, headers=self._headers(), timeout=20)
        response.raise_for_status()
        return list(response.json())

    def fetch_pull_diff_summary(self, owner: str, repo: str, pull_number: int) -> dict[str, Any]:
        url = f"{self.github_interface.api_url}/repos/{owner}/{repo}/pulls/{pull_number}"
        response = requests.get(url, headers=self._headers(), timeout=20)
        response.raise_for_status()
        payload = response.json()
        return {
            "number": pull_number,
            "title": payload.get("title", ""),
            "additions": payload.get("additions", 0),
            "deletions": payload.get("deletions", 0),
            "changed_files": payload.get("changed_files", 0),
            "merged_at": payload.get("merged_at"),
        }

    def extract_from_pull_requests(self, pulls: list[dict[str, Any]]) -> tuple[list[SweepItem], list[SweepItem]]:
        proposed: list[SweepItem] = []
        pruned: list[SweepItem] = []

        for pull in pulls:
            number = pull.get("number")
            title = str(pull.get("title", ""))
            body = str(pull.get("body", ""))
            merged_at = pull.get("merged_at")
            text = f"{title}\n{body}".lower()
            contains_near_miss = any(key in text for key in self.near_miss_keywords)

            if contains_near_miss:
                # Mark merged PRs in origin field so they can be detected as active
                origin_prefix = "merged:" if merged_at else "PR-"
                proposed.append(
                    SweepItem(
                        unique_id=f"RTM-A6-PR-{number}",
                        origin=f"{origin_prefix}{number}",
                        proto_need=title,
                        status="proposed",
                        implementation_path="federation-wire-link",
                        verification_method="Review merged PR summary and telemetry",
                    )
                )
            elif not merged_at:
                pruned.append(
                    SweepItem(
                        unique_id=f"RTM-A6-PR-{number}",
                        origin=f"PR-{number}",
                        proto_need=f"Closed without merge: {title}",
                        status="pruned",
                        implementation_path="n/a",
                        verification_method="Closed PR state verified",
                    )
                )
        return proposed, pruned

    def scan_aborted_sessions(self, session_log_dir: str | Path) -> list[SweepItem]:
        findings: list[SweepItem] = []
        log_dir = Path(session_log_dir)
        if not log_dir.exists():
            return findings

        for path in sorted(log_dir.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            state = str(payload.get("state", "")).lower()
            if state != "aborted":
                continue
            suggestion = str(payload.get("suggestion", path.stem))
            findings.append(
                SweepItem(
                    unique_id=f"RTM-A6-ABORT-{path.stem}",
                    origin=f"aborted:{path.name}",
                    proto_need=suggestion,
                    status="proposed",
                    implementation_path="agent-runtime-followup",
                    verification_method="Replay aborted session output",
                )
            )
        return findings

    def scan_stale_lineage(self, lineage_path: str | Path) -> list[SweepItem]:
        result: list[SweepItem] = []
        target = Path(lineage_path)
        if not target.exists():
            return result

        payload = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
        for item in payload.get("entries", []):
            status = str(item.get("status", "")).lower()
            if status in self.stale_status_values:
                result.append(
                    SweepItem(
                        unique_id=str(item.get("unique_id", "RTM-A6-UNKNOWN")),
                        origin=str(item.get("origin", "lineage")),
                        proto_need=str(item.get("proto_need", "stale lineage marker")),
                        status="pruned",
                        implementation_path="lineage-pruning",
                        verification_method="Stale marker classification",
                        parent_requirement=str(item.get("parent_requirement", "REQ-FEDERATION-A6")),
                    )
                )
        return result

    @staticmethod
    def _escape_markdown_table_cell(text: str) -> str:
        """Escape pipe and newline characters to prevent Markdown table injection."""
        return text.replace("|", "\\|").replace("\n", " ").replace("\r", "")
    
    @staticmethod
    def write_rtm_delta(entries: list[SweepItem], output_path: str | Path) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Local Requirements Traceability Matrix (RTM) Lineage Delta",
            "",
            "| Unique ID | Parent Requirement | Proto-Need | Implementation Path | Verification Method | Status |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for item in entries:
            # Escape all user-controlled fields to prevent Markdown injection
            unique_id = MCPSweepEngine._escape_markdown_table_cell(item.unique_id)
            parent_req = MCPSweepEngine._escape_markdown_table_cell(item.parent_requirement)
            proto_need = MCPSweepEngine._escape_markdown_table_cell(item.proto_need)
            impl_path = MCPSweepEngine._escape_markdown_table_cell(item.implementation_path)
            verif_method = MCPSweepEngine._escape_markdown_table_cell(item.verification_method)
            status = item.status.upper()
            
            lines.append(
                f"| **{unique_id}** | {parent_req} | {proto_need} | {impl_path} | {verif_method} | `[{status}]` |"
            )
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    @staticmethod
    def write_markdown_telemetry(
        proposed: list[SweepItem],
        pruned: list[SweepItem],
        active: list[SweepItem],
        output_path: str | Path,
    ) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc).isoformat()
        lines = [
            "## [MCP SWEEP PROTOCOL: COMPLETED]",
            f"*Generated:* {now}",
            "---",
            f"- Proposed near-misses: {len(proposed)}",
            f"- Pruned stale/obsolete: {len(pruned)}",
            f"- Promoted active deltas: {len(active)}",
            "",
        ]
        for item in proposed:
            # Escape user-controlled fields to prevent injection
            proto_need = MCPSweepEngine._escape_markdown_table_cell(item.proto_need)
            origin = MCPSweepEngine._escape_markdown_table_cell(item.origin)
            lines.append(f"* [ ] **NEAR-MISS ESCALATED:** {proto_need} ({origin})")
        for item in active:
            proto_need = MCPSweepEngine._escape_markdown_table_cell(item.proto_need)
            origin = MCPSweepEngine._escape_markdown_table_cell(item.origin)
            lines.append(f"* [x] **ACTIVE DELTA:** {proto_need} ({origin})")
        for item in pruned:
            proto_need = MCPSweepEngine._escape_markdown_table_cell(item.proto_need)
            origin = MCPSweepEngine._escape_markdown_table_cell(item.origin)
            lines.append(f"* [-] **OBSOLETE STATE WIPED:** {proto_need} ({origin})")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def run(
        self,
        owner: str,
        repo: str,
        session_log_dir: str | Path,
        lineage_path: str | Path,
        telemetry_output_path: str | Path,
        rtm_delta_output_path: str | Path,
    ) -> dict[str, Any]:
        pulls = self.fetch_closed_pull_requests(owner, repo)
        proposed_from_pr, pruned_from_pr = self.extract_from_pull_requests(pulls)
        proposed_from_sessions = self.scan_aborted_sessions(session_log_dir)
        pruned_from_lineage = self.scan_stale_lineage(lineage_path)

        proposed = proposed_from_pr + proposed_from_sessions
        pruned = pruned_from_pr + pruned_from_lineage

        active = [item for item in proposed if item.origin.lower().startswith("merged:")]
        proposed = [item for item in proposed if item not in active]

        self.write_markdown_telemetry(proposed, pruned, active, telemetry_output_path)
        self.write_rtm_delta(proposed + active, rtm_delta_output_path)

        return {
            "proposed_count": len(proposed),
            "pruned_count": len(pruned),
            "active_count": len(active),
            "telemetry_output": str(telemetry_output_path),
            "rtm_delta_output": str(rtm_delta_output_path),
        }
