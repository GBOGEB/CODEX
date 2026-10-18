"""W36 federated read-only GitHub census; no dispatch, writes, or private-QPS access.

The resulting ZIP artifact is an OBSERVED snapshot. Only owner-side exact run/job/
attempt plus independent security/review can establish admission; source-read
metadata is not a formal acceptance or worker-execution receipt.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SOURCE = "codepurple.federated.dov.v1"
REPOS = ("GBOGEB/ABACUS", "GBOGEB/CODEX")
SHA = re.compile(r"[0-9a-f]{40}\Z")
ACTIVE = {"queued", "in_progress", "pending", "requested", "waiting"}
TERMINAL = {"success", "failure", "cancelled", "skipped", "timed_out",
            "neutral", "action_required", "startup_failure", "stale"}
MAX_PAGES = 3


def require(condition, text):
    if not condition:
        raise ValueError(text)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)+"\n").encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def validate_source(snapshot):
    require(snapshot.get("schema") == SOURCE, "SOURCE_SCHEMA")
    g = snapshot.get("governance", {})
    require(g.get("merge_admission") == "HOLD"
            and g.get("remote_dispatch") is False
            and g.get("root_closures") is None
            and g.get("security_waiver") is False,
            "AUTHORITY_PROMOTION")
    repos = snapshot.get("repos", [])
    require(len(repos) == 3 and
            {r["repo"] for r in repos} == set(REPOS)|{"GBOGEB/cryoplant-project"},
            "THREE_OWNER_REPOS")
    require(next(r for r in repos if r["repo"] == "GBOGEB/cryoplant-project")
            ["visibility"] == "private", "PRIVATE_QPS_BOUNDARY")
    require(len(snapshot.get("axes", [])) == 5, "NONCOMPENSATING_FIVE_AXES")
    return True


def request_json(url):
    headers = {"User-Agent": "code-purple-w36-read-only-census",
               "Accept": "application/vnd.github+json"}
    # No credentials for cross-repository or private assets. Use public API only.
    request = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(request, timeout=12) as response:
        return json.load(response)


def read_public(repo, fetch=request_json, pages=MAX_PAGES):
    require(repo in REPOS and type(pages) is int and 1 <= pages <= MAX_PAGES,
            "OWNER_OR_PAGE_BOUNDARY")
    endpoint = "https://api.github.com/repos/"+repo
    branch = fetch(endpoint+"/branches/main")
    head = branch.get("commit", {}).get("sha")
    require(type(head) is str and SHA.fullmatch(head), "CURRENT_MAIN_UNPINNED")
    items = {}
    total = None
    for page in range(1, pages+1):
        result = fetch(endpoint+"/actions/runs?head_sha="+head+
                       "&per_page=100&page="+str(page))
        n = result.get("total_count")
        require(type(n) is int and n >= 0, "MISSING_RUN_POPULATION")
        if total is not None:
            require(total == n, "UNSTABLE_PAGINATION_POPULATION")
        total = n
        rows = result.get("workflow_runs")
        require(type(rows) is list and len(rows) <= 100, "INVALID_RUN_PAGE")
        for r in rows:
            require(type(r.get("id")) is int and r["id"] > 0
                    and type(r.get("run_attempt")) is int and r["run_attempt"] > 0,
                    "INVALID_RUN_ID")
            require(r.get("head_sha") == head, "WRONG_SOURCE_HEAD")
            status, outcome = r.get("status"), r.get("conclusion")
            require((status in ACTIVE and outcome is None) or
                    (status == "completed" and outcome in TERMINAL),
                    "INVALID_TERMINAL_CREDIT")
            key = r["id"]
            other = items.get(key)
            minimal = {"id": key, "attempt": r["run_attempt"],
                       "workflow": r.get("name"), "status": status,
                       "conclusion": outcome, "head_sha": head}
            if other is not None and other["attempt"] == minimal["attempt"]:
                require(other == minimal, "DUPLICATE_ID_CONFLICT")
            elif other is None or other["attempt"] < minimal["attempt"]:
                items[key] = minimal
        if len(rows) < 100 or len(items) >= total:
            break
    observed = len(items)
    require(total >= observed, "CENSUS_OVERCOUNT")
    queued = sum(r["status"] == "queued" for r in items.values())
    not_terminal = sum(r["status"] in ACTIVE for r in items.values())
    return {"repo": repo, "source_sha": head, "reported_total": total,
            "returned_distinct_runs": observed, "unknown_tail": total-observed,
            "complete": observed == total,
            "queued_observed": queued, "nonterminal_observed": not_terminal,
            "nonterminal_fraction_observed":
                round(not_terminal/observed, 6) if observed else None,
            "workflows_observed": len({r["workflow"] for r in items.values()}),
            "pr_feedback_gate_observed":
                sum(r["workflow"] == "PR Feedback Gate Evaluator" for r in items.values()),
            "runs": sorted(items.values(), key=lambda r: (-r["id"], -r["attempt"])),
            "evidence_class": "API_READBACK_PARTIAL_IF_UNKNOWN_TAIL"}


def build(snapshot, fetch=request_json, pages=MAX_PAGES):
    validate_source(snapshot)
    result = {"schema":"codepurple.federated.live-readback.v1",
              "observed_utc":datetime.now(timezone.utc).isoformat(),
              "source_digest":digest(canonical(snapshot)),
              "governance":{"merge_admission":"HOLD","remote_dispatch":False,
                            "root_closures":None,"formal_security_credit":None},
              "population":"PUBLIC_REPO_HEAD_SNAPSHOT_WITH_PAGINATION_BOUND",
              "repositories":[]}
    for repo in REPOS:
        try:
            result["repositories"].append(read_public(repo, fetch, pages))
        except (ValueError, urllib.error.URLError, TimeoutError, OSError) as e:
            result["repositories"].append({
                "repo":repo, "source_sha":None,"complete":False,
                "reported_total":None,"unknown_tail":None,
                "error_type":type(e).__name__,"evidence_class":"UNAVAILABLE_NOT_ZERO"})
    result["repositories"].append({"repo":"GBOGEB/cryoplant-project",
                                   "evidence_class":"PRIVATE_OWNER_DEFER",
                                   "source_sha":None,"complete":False,
                                   "remote_access_attempted":False})
    return result


def emit(snapshot, output, *, head, run_id=None, attempt=None, fetch=request_json):
    require(type(head) is str and SHA.fullmatch(head), "CANDIDATE_HEAD_INVALID")
    for number in (run_id, attempt):
        require(number is None or type(number) is int and number > 0,
                "BAD_RUN_ATTEMPT")
    output.mkdir(parents=True,exist_ok=True)
    blob = canonical(build(snapshot, fetch))
    (output/"W36_LIVE_READBACK.json").write_bytes(blob)
    receipt = {"schema":"codepurple.federated.sha256.v1",
               "candidate_head":head,"run_id":run_id,"attempt":attempt,
               "admission":"HOLD","mutation_enabled":False,
               "files":{"W36_LIVE_READBACK.json":digest(blob)}}
    (output/"W36_SHA256.json").write_bytes(canonical(receipt))
    return receipt


def verify(output, head):
    receipt=json.loads((output/"W36_SHA256.json").read_bytes())
    require(receipt.get("candidate_head")==head
            and receipt.get("admission")=="HOLD"
            and receipt.get("mutation_enabled") is False,"RECEIPT_AUTHORITY")
    require(set(receipt.get("files",{}))=={"W36_LIVE_READBACK.json"},
            "MANIFEST_COMPLETENESS")
    actual=(output/"W36_LIVE_READBACK.json").read_bytes()
    require(receipt["files"]["W36_LIVE_READBACK.json"]==digest(actual),
            "RECEIPT_HASH_DRIFT")
    data=json.loads(actual)
    require(data["governance"]["merge_admission"]=="HOLD"
            and data["governance"]["remote_dispatch"] is False,
            "FALSE_PROMOTION")
    return receipt


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--snapshot",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--head",required=True)
    p.add_argument("--run-id",type=int)
    p.add_argument("--attempt",type=int)
    p.add_argument("--verify-only",action="store_true")
    a=p.parse_args()
    if not a.verify_only:
        snapshot=json.loads(a.snapshot.read_text(encoding="utf-8"))
        emit(snapshot,a.out,head=a.head,run_id=a.run_id,attempt=a.attempt)
    print(json.dumps(verify(a.out,a.head),sort_keys=True))


if __name__=="__main__":
    main()
