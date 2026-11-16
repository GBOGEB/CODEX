"""CODE PURPLE mid-wave census: evidence-only, resumable, never merge authority."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "code-purple.midwave-testflight.v1"
STAGES = ("preflight", "focused_tests", "integrated_ci", "security", "review")
PREFERRED = (
    "CODEX", "ABACUS", "cryogenic-compliance", "DOCX_RTM_Automation",
    "Q_engineering_tools", "cryo_leak_rate_dashboard",
    "cryogenic-accelerator-workspace", "gg_MATH", "GEMINI",
    "GBOGEB-PROGRAM-COOL", "pipeline-automation-hub",
)
BOT_LOGINS = {"chatgpt-codex-connector", "github-actions", "dependabot", "github-advanced-security"}
ISSUE_MARKER = "<!-- code-purple-midwave-receipt-v1 "
KEYWORD_GROUPS = {
    "security": ("security", "vulnerab", "cve-", "ghsa-", "secret", "injection", "osv"),
    "coverage": ("coverage", "uncovered", "branch", "line rate"),
    "code": ("code", "test", "lint", "ruff", "bug", "regress", "refactor", "assert"),
}


def stable_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def is_bot(login: str) -> bool:
    identity = login.lower()
    return identity.endswith("[bot]") or identity in BOT_LOGINS


def classify_comment(text: str) -> str:
    clean = text.lower()
    for group, patterns in KEYWORD_GROUPS.items():
        if any(p in clean for p in patterns):
            return group
    return "review_other"


def normalize_comment(item: dict, category: str, repo: str, pr: int, source_sha: str) -> dict | None:
    author = (item.get("user") or {}).get("login", "")
    if not is_bot(author):
        return None
    body = item.get("body") or ""
    if not body.strip():
        return None
    key = str(item.get("id") or item.get("node_id") or "")
    if not key:
        return None
    return {
        "id": f"{repo}#{pr}:{category}:{key}",
        "repo": repo, "pr": pr, "source_sha_at_census": source_sha,
        "author": author, "kind": classify_comment(body),
        "comment_url": item.get("html_url"),
        "updated_at": item.get("updated_at") or item.get("submitted_at"),
        "fingerprint": stable_hash({"id": key, "body": body, "updated": item.get("updated_at")}),
        "disposition": "REVIEW_REQUIRED_NOT_APPROVAL",
    }


def compact_prior(
    comments: list[dict],
    prior: dict | None,
    head_sha: str,
    root_id: str,
    scanned: set[str] | None = None,
) -> dict:
    """Keep completed work in history, but never credit stale-head proof."""
    prior = prior or {}
    history = list(prior.get("history", []))[-8:]
    last_sha = prior.get("source_sha")
    if last_sha and last_sha != head_sha:
        history.append({
            "source_sha": last_sha, "gates": prior.get("gates", {}),
            "comment_fingerprint_digest": stable_hash(prior.get("comment_fingerprints", [])),
            "bot_comment_count": len(prior.get("comment_fingerprints", [])),
        })
    seen = set(prior.get("comment_fingerprints", []))
    latest = {x["id"]: x for x in comments}
    new = [x for x in latest.values() if x["fingerprint"] not in seen]
    # Only fingerprints still open are carried forward: the marker stays bounded
    # by the live set instead of growing (and arbitrarily truncating) forever.
    current = sorted({x["fingerprint"] for x in latest.values()})
    prior_open = prior.get("open_ids")
    # IDs are "<repo>#<pr>:<category>:<key>". Only a PR that was scanned this
    # run can prove a finding resolved; findings on PRs outside the sample stay
    # open and are carried forward. scanned=None keeps the old "all scanned" rule.
    def in_scope(fid: str) -> bool:
        return scanned is None or fid.split(":", 1)[0] in scanned

    if isinstance(prior_open, list):
        resolved = sorted(i for i in set(prior_open) - set(latest) if in_scope(i))
        carried = sorted(i for i in set(prior_open) - set(latest) if not in_scope(i))
    else:
        resolved, carried = [], []
    return {
        "root_id": root_id,
        "source_sha": head_sha,
        "history": history[-8:],
        "comment_fingerprints": current,
        "open_ids": sorted(set(latest) | set(carried)),
        "carried_unscanned_ids": carried,
        "new_bot_comments": new,
        "resolved_ids": resolved,
        "prior_open_count": len(prior_open) if isinstance(prior_open, list) else None,
        # A legacy receipt (fingerprints, no open_ids) must still emit the first
        # delta marker so later runs have open_ids to diff against.
        "legacy_migration": prior_open is None and bool(prior.get("comment_fingerprints")),
        "same_head": bool(last_sha == head_sha),
        "authority_transfer": False,
    }


def render_delta_comment(state: dict, prior_observed_at: str | None) -> str:
    """Delta-only checkpoint: what changed since the last receipt, plus totals."""
    new, resolved = state["new_bot_comments"], state["resolved_ids"]
    total = len(state["open_ids"])
    before = state.get("prior_open_count")
    since = f" since {prior_observed_at}" if prior_observed_at else ""
    lines = [
        "CODE PURPLE mid-wave bot-review delta: **HOLD / independent disposition required**.",
        f"**Delta{since}: +{len(new)} new, -{len(resolved)} resolved | "
        f"open now: {total}" + (f" (was {before})" if before is not None else " (first delta receipt)") + "**",
        f"Head: `{(state['source_sha'] or 'UNKNOWN')[:12]}`",
    ]
    if new:
        lines.append("\nNew:")
        lines += [f"- {r['repo']} #{r['pr']} ({r['kind']}): {r['comment_url'] or r['id']}" for r in new[:12]]
        if len(new) > 12:
            lines.append(f"- ... +{len(new) - 12} more (see run artifact)")
    if resolved:
        lines.append("\nNo longer present:")
        lines += [f"- {rid}" for rid in resolved[:12]]
        if len(resolved) > 12:
            lines.append(f"- ... +{len(resolved) - 12} more")
    return "\n".join(lines)


def find_latest_checkpoint(client: GitHubRead, repo: str, issue: int, max_pages: int = 30) -> dict | None:
    """Scan every page: the newest receipt is on the last page, not the first."""
    latest = None
    for page in range(1, max_pages + 1):
        try:
            batch = client.get(f"/repos/{repo}/issues/{issue}/comments?per_page=100&page={page}")
        except (urllib.error.HTTPError, TypeError):
            break
        if not isinstance(batch, list):
            break
        for comment in batch:
            parsed = parse_checkpoint_comment(comment.get("body", "") or "")
            if parsed:
                latest = dict(parsed, _observed_at=comment.get("created_at"))
        if len(batch) < 100:
            break
    return latest


def gate_census(checks: list[dict], source_sha: str) -> dict:
    counts = {"success": 0, "failure": 0, "skipped": 0, "cancelled": 0, "pending": 0}
    for item in checks:
        if item.get("head_sha") not in (None, source_sha):
            continue
        label = item.get("conclusion") or "pending"
        if label not in counts:
            label = "pending"
        counts[label] += 1
    executed = counts["success"] + counts["failure"]
    return {
        "counts": counts, "executed": executed,
        "pass_fraction": {"numerator": counts["success"], "denominator": executed},
        "all_required_green": None,
        "note": "Not an admission decision; skipped/cancelled/pending are never passed.",
    }


def latest_checkpoint(gates: dict) -> dict:
    # A new head can preserve work history, never stale executed-test credit.
    ordered = [key for key in STAGES if gates.get(key) is True]
    return {
        "completed": ordered,
        "numerator": len(ordered), "denominator": len(STAGES),
        "next": next((k for k in STAGES if gates.get(k) is not True), "admission_hold"),
        "admission": "HOLD",
    }


class GitHubRead:
    def __init__(self, token: str = "") -> None:
        self.token = token
    def get(self, path: str) -> object:
        request = urllib.request.Request(
            "https://api.github.com" + path,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "code-purple-midwave-testflight",
                **({"Authorization": f"Bearer {self.token}"} if self.token else {}),
            },
        )
        with urllib.request.urlopen(request, timeout=16) as response:
            return json.load(response)
    def post_issue_comment(self, repo: str, issue: int, body: str) -> None:
        if not self.token:
            raise ValueError("Token required to post a checkpoint")
        request = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/issues/{issue}/comments",
            data=json.dumps({"body": body}).encode(),
            method="POST",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "code-purple-midwave-testflight",
            },
        )
        with urllib.request.urlopen(request, timeout=16) as response:
            if response.status != 201:
                raise RuntimeError("Checkpoint was not created")


def probe_repo(client: GitHubRead, repo: dict) -> dict:
    name = repo["full_name"]
    branch = repo.get("default_branch") or "main"
    entry = {
        "repo": name, "default_branch": branch,
        "fork": bool(repo.get("fork")), "archived": bool(repo.get("archived")),
        "main_sha": None, "protected": None,
        "ci": "UNKNOWN", "recent_runs": {}, "tool_config": {},
        "local_runner_status": "UNKNOWN_REQUIRES_RUNNER_ADMIN_OR_HOST_PROOF",
        "debugger_session": "UNKNOWN_REQUIRES_SESSION_RECEIPT",
    }
    try:
        b = client.get(f"/repos/{name}/branches/{urllib.parse.quote(branch, safe='')}")
        entry["main_sha"] = b["commit"]["sha"]
        entry["protected"] = b.get("protected")
    except (urllib.error.HTTPError, KeyError, TypeError) as exc:
        entry["branch_error"] = type(exc).__name__
        return entry
    try:
        runs = client.get(f"/repos/{name}/actions/runs?branch={urllib.parse.quote(branch)}&per_page=30")["workflow_runs"]
        counts = {}
        for run in runs:
            outcome = run.get("conclusion") or run.get("status") or "UNKNOWN"
            counts[outcome] = counts.get(outcome, 0) + 1
        entry["ci"] = "OBSERVED"
        entry["recent_runs"] = {"n": len(runs), "outcomes": counts}
    except (urllib.error.HTTPError, KeyError, TypeError) as exc:
        entry["ci_error"] = type(exc).__name__
    try:
        listing = client.get(f"/repos/{name}/contents/.github/workflows?ref={entry['main_sha']}")
        if isinstance(listing, list):
            filenames = [i["name"].lower() for i in listing if i.get("type") == "file"]
            for key, terms in {
                "bandit": ("bandit",), "rhel": ("rhel", "ubi"),
                "lldb": ("lldb",), "mip": ("mip",),
                "coverage": ("coverage",), "testflight": ("testflight", "testpilot"),
                "security": ("security", "codeql", "osv"),
            }.items():
                entry["tool_config"][key] = any(any(word in name for word in terms) for name in filenames)
            entry["workflow_count"] = len(filenames)
    except (urllib.error.HTTPError, KeyError, TypeError):
        entry["tool_config_status"] = "UNKNOWN"
    try:
        client.get(f"/repos/{name}/contents/.pre-commit-config.yaml?ref={entry['main_sha']}")
        entry["tool_config"]["pre_commit"] = True
    except urllib.error.HTTPError as exc:
        entry["tool_config"]["pre_commit"] = False if exc.code == 404 else None
    return entry


def bot_comments_for_pr(client: GitHubRead, repo: str, pr: dict) -> list[dict]:
    n = pr["number"]
    sha = pr["head"]["sha"]
    comments = []
    for typ, endpoint in (
        ("discussion", f"/repos/{repo}/issues/{n}/comments?per_page=100"),
        ("inline", f"/repos/{repo}/pulls/{n}/comments?per_page=100"),
        ("review", f"/repos/{repo}/pulls/{n}/reviews?per_page=100"),
    ):
        try:
            for item in client.get(endpoint):
                normalized = normalize_comment(item, typ, repo, n, sha)
                if normalized:
                    comments.append(normalized)
        except (urllib.error.HTTPError, TypeError):
            continue
    return comments


def parse_checkpoint_comment(body: str) -> dict | None:
    pos = body.find(ISSUE_MARKER)
    if pos < 0:
        return None
    end = body.find(" -->", pos)
    if end < 0:
        return None
    try:
        doc = json.loads(body[pos + len(ISSUE_MARKER):end])
    except json.JSONDecodeError:
        return None
    return doc if isinstance(doc, dict) and doc.get("schema") == SCHEMA else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", default="GBOGEB")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--out", type=Path, default=Path("outputs/midwave/testflight.json"))
    parser.add_argument("--post-on-new-bot-findings", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.limit <= 25 or not re.fullmatch(r"[a-zA-Z0-9-]+", args.owner):
        parser.error("owner must be a login and limit must be 1..25")
    client = GitHubRead(os.getenv("GITHUB_TOKEN", ""))
    all_repos = []
    for page in range(1, 5):
        page_repos = client.get(f"/users/{args.owner}/repos?per_page=100&page={page}&type=owner")
        all_repos.extend(page_repos)
        if len(page_repos) < 100:
            break
    accessible = [r for r in all_repos if (r.get("owner") or {}).get("login", "").lower() == args.owner.lower()]
    ordered = sorted(accessible, key=lambda x: (
        PREFERRED.index(x["name"]) if x["name"] in PREFERRED else 999,
        x["name"].lower(),
    ))
    studied = [probe_repo(client, r) for r in ordered[:args.limit]]
    monitored = [r for r in studied if r["repo"] in (f"{args.owner}/CODEX", f"{args.owner}/ABACUS")]
    bot_comments = []
    scanned: set[str] = set()
    for item in monitored:
        try:
            prs = client.get(f"/repos/{item['repo']}/pulls?state=open&per_page=10")
            for pr in prs[:5]:
                bot_comments.extend(bot_comments_for_pr(client, item["repo"], pr))
                scanned.add(f"{item['repo']}#{pr['number']}")
        except (urllib.error.HTTPError, TypeError):
            pass
    owner_issue = f"{args.owner}/CODEX"
    previous = find_latest_checkpoint(client, owner_issue, 1037)
    prior_observed_at = (previous or {}).pop("_observed_at", None)
    head = next((r["main_sha"] for r in monitored if r["repo"] == owner_issue), None)
    state = compact_prior(bot_comments, previous, head or "UNKNOWN", "CODE_PURPLE_ORG_TESTFLIGHT", scanned)
    snapshot = {
        "schema": SCHEMA, "observed_at": datetime.now(timezone.utc).isoformat(),
        "authority_transfer": False, "merge_allowed": False,
        "repository_census": {
            "owner": args.owner, "accessible_count": len(accessible),
            "deep_sample_count": len(studied), "not_deep_inspected": len(accessible) - len(studied),
            "sampling_rule": "fixed priority then alphabetical; nonselected status UNKNOWN",
        },
        "repositories": studied,
        "bot_review_census": {
            "count": len(bot_comments),
            "new_since_last_checkpoint": len(state["new_bot_comments"]),
            "resolved_since_last_checkpoint": len(state["resolved_ids"]),
            "comments": bot_comments,
            "open_findings_require_review": True,
        },
        "continuation": state,
        "progress": latest_checkpoint((previous or {}).get("gates", {}) if state["same_head"] else {}),
        "unknowns": ["actual_local_runner_inventory", "active_lldb_sessions",
                     "accepted_security_review", "comparable_broad_coverage"],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(snapshot, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    changed = bool(state["new_bot_comments"] or state["resolved_ids"] or state["legacy_migration"])
    if args.post_on_new_bot_findings and changed:
        # No arbitrary comment body is reposted, only safe evidence links/identities.
        event = {
            "schema": SCHEMA, "root_id": state["root_id"],
            "source_sha": state["source_sha"],
            "comment_fingerprints": state["comment_fingerprints"],
            "open_ids": state["open_ids"],
            "history": state["history"], "gates": {},
        }
        body = render_delta_comment(state, prior_observed_at)
        body += "\n" + ISSUE_MARKER + json.dumps(event, sort_keys=True, separators=(",", ":")) + " -->"
        client.post_issue_comment(owner_issue, 1037, body)
    print(f"Mid-wave testflight: {len(accessible)} repos, {len(studied)} probed, "
          f"{len(bot_comments)} bot review receipts; authority=HOLD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
