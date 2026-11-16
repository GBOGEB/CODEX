#!/usr/bin/env python3
"""Federation PR dependency DAG: Kahn order, critical path, reverse pressure.

Read-only and recommendation-only (3P3 W59: recommendations are not authority).

Pipeline
  1. census     open PRs (+ BD-queue issues) -> nodes with a verdict and effort
  2. edges      Depends-on / kit pin / shared files / human gates / BD binding
  3. Kahn       priority-aware topological order; leftovers are deadlock cycles
  4. CPM        forward/backward pass -> slack; zero-slack chain = critical path
  5. pressure   BT priority propagated backwards: R(v) = p(v) + lam * sum R(succ)
  6. leverage   score = R(v) * (1 + |descendants|) / effort  ("unlock per hour")
  7. pilot      apply unblocking vectors alone and in pairs; synergy =
                gain(A+B) - gain(A) - gain(B)  (> 0 = multiplying effect)

Usage
  python scripts/ci/federation_pr_dag.py collect --repo GBOGEB/CODEX --repo GBOGEB/ABACUS \
      --bd-queue controls/BD_QUEUE_CURRENT.md --out census.json
  python scripts/ci/federation_pr_dag.py analyze census.json \
      [--bt-scores scores.json] --json-out dag.json --md-out dag.md
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import subprocess  # nosec B404
import sys
from datetime import UTC, datetime
from pathlib import Path

# Remaining effort in hours by census verdict (estimates; override with --effort).
EFFORT = {
    "READY": 0.1,
    "REQ_PENDING": 1.0,
    "BEHIND": 1.0,
    "THREADS": 0.5,  # + THREAD_COST per unresolved thread
    "CONFLICT": 1.5,
    "REQ_RED": 3.0,
    "DRAFT": 4.0,
    "NEEDS_APPROVAL": 0.2,
    "BD_ISSUE": 0.5,
}
THREAD_COST = 0.25
HUMAN_WAIT = 8.0  # a gate waits for the owner: approve runs, tick a checklist
LAMBDA = 0.6  # reverse-pressure decay per hop

GENERATED = re.compile(
    r"^(docs/data/|mission_control/|MIP/kit/KIT_MANIFEST\.json$|"
    r"ci/governance/workflow_policy\.json$|docs/ci/WORKFLOW_RATIONALIZATION\.md$)"
)
DEP_RE = re.compile(
    r"(?im)^[\s>*-]*(?:depends[- ]on|blocked[- ]by|merge after|stacked on)\s*:?\s*"
    r"((?:[\w.-]+/[\w.-]+)?#\d+(?:\s*,\s*(?:[\w.-]+/[\w.-]+)?#\d+)*)"
)
REF_RE = re.compile(r"(?:([\w.-]+/[\w.-]+))?#(\d+)")
CLOSES_RE = re.compile(r"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)")
KIT_PRODUCER = "MIP/kit/KIT_MANIFEST.json"
KIT_CONSUMER = ".github/workflows/mip-n2-self-index.yml"


# --------------------------------------------------------------------- census
def node_id(repo: str, number: int, kind: str = "#") -> str:
    return f"{repo.split('/')[-1]}{kind}{number}"


def default_priority(title: str, verdict: str) -> float:
    t = title.lower()
    if re.search(r"security|bandit|codeql|cve|vuln|secret", t):
        return 0.8
    if re.search(r"^(fix|ci|mip kit)|\bfix\b|kit", t):
        return 0.6
    if re.search(r"^(docs|chore)|refresh|metrics|inventory", t):
        return 0.3
    return 0.5


def effort_for(node: dict) -> float:
    base = EFFORT.get(node["verdict"], 1.0)
    if node["verdict"] == "THREADS":
        base += THREAD_COST * int(node.get("unresolved", 0))
    return base


def parse_bd_queue(text: str, repo: str) -> list[dict]:
    rows = re.findall(r"^\|\s*(\d+)\s*\|\s*#(\d+)\s+([^|]+)\|\s*([A-Z_]+)\s*\|", text, re.MULTILINE)
    n = max(len(rows), 1)
    return [
        {
            "id": node_id(repo, int(num), "!"),
            "repo": repo,
            "number": int(num),
            "title": title.strip(),
            "kind": "issue",
            "verdict": "BD_ISSUE",
            # EXTERNAL_GATE waits on the owner; PARENT_CONTROL is not executable work.
            "effort": HUMAN_WAIT if state == "EXTERNAL_GATE" else EFFORT["BD_ISSUE"],
            "actionable": state not in ("PARENT_CONTROL",),
            "bd_state": state,
            "priority": round(1.0 - (int(rank) - 1) / n, 4),
            "files": [],
            "body": "",
        }
        for rank, num, title, state in rows
    ]


# ---------------------------------------------------------------------- edges
def build_graph(census: dict) -> tuple[dict, list[dict]]:
    nodes = {n["id"]: dict(n) for n in census["nodes"]}
    edges: list[dict] = []

    def add(u: str, v: str, kind: str, soft: bool = False) -> None:
        if u != v and u in nodes and v in nodes:
            edges.append({"from": u, "to": v, "kind": kind, "soft": soft})

    prs = [n for n in nodes.values() if n.get("kind", "pr") == "pr"]
    for n in prs:
        body = n.get("body") or ""
        for group in DEP_RE.findall(body):
            for repo, num in REF_RE.findall(group):
                add(node_id(repo or n["repo"], int(num)), n["id"], "depends_on")
        for num in CLOSES_RE.findall(body):
            add(n["id"], node_id(n["repo"], int(num), "!"), "closes_bd")
        if n.get("verdict") == "NEEDS_APPROVAL":
            g = f"GATE:{n['id']}:approve-runs"
            nodes[g] = _gate(g, n["repo"], "approve held workflow runs")
            add(g, n["id"], "human_gate")
        if n.get("owner_checklist"):
            g = f"GATE:{n['id']}:owner-checklist"
            nodes[g] = _gate(g, n["repo"], "owner merge checklist")
            add(g, n["id"], "human_gate")

    producers = [n for n in prs if KIT_PRODUCER in n.get("files", []) and n["repo"].endswith("CODEX")]
    consumers = [n for n in prs if KIT_CONSUMER in n.get("files", []) and not n["repo"].endswith("CODEX")]
    for p, c in itertools.product(producers, consumers):
        add(p["id"], c["id"], "kit_pin")

    # Shared files inside one repo: the cheaper (then older) PR goes first.
    by_repo: dict[str, list[dict]] = {}
    for n in prs:
        by_repo.setdefault(n["repo"], []).append(n)
    for group in by_repo.values():
        for a, b in itertools.combinations(group, 2):
            shared = set(a.get("files", [])) & set(b.get("files", []))
            if not shared:
                continue
            first, second = sorted((a, b), key=lambda x: (effort_for(x), x["number"]))
            generated_only = all(GENERATED.match(f) for f in shared)
            edges.append(
                {
                    "from": first["id"],
                    "to": second["id"],
                    "kind": "shared_generated" if generated_only else "shared_files",
                    "soft": True,
                    "files": sorted(shared)[:5],
                    "shared": len(shared),
                }
            )
    for n in nodes.values():
        n.setdefault("effort", effort_for(n) if not n["id"].startswith("GATE:") else HUMAN_WAIT)
        n.setdefault("priority", default_priority(n.get("title", ""), n.get("verdict", "")))
    return nodes, edges


def _gate(gid: str, repo: str, title: str) -> dict:
    return {"id": gid, "repo": repo, "kind": "gate", "title": title, "verdict": "HUMAN_GATE",
            "effort": HUMAN_WAIT, "priority": 0.0, "files": []}


# ----------------------------------------------------------------- algorithms
def kahn(nodes: dict, edges: list[dict]) -> tuple[list[str], list[str]]:
    """Priority-aware Kahn: among ready nodes, take the highest priority first.

    Returns (order, cycle_nodes). Nodes left with in-degree > 0 sit on or behind
    a cycle: a deadlock where PRs wait on each other.
    """
    indeg = {v: 0 for v in nodes}
    succ: dict[str, list[str]] = {v: [] for v in nodes}
    for e in edges:
        indeg[e["to"]] += 1
        succ[e["from"]].append(e["to"])
    ready = sorted((v for v in nodes if indeg[v] == 0), key=lambda v: (-nodes[v]["priority"], v))
    order: list[str] = []
    while ready:
        v = ready.pop(0)
        order.append(v)
        for w in succ[v]:
            indeg[w] -= 1
            if indeg[w] == 0:
                ready.append(w)
        ready.sort(key=lambda x: (-nodes[x]["priority"], x))
    return order, sorted(v for v in nodes if indeg[v] > 0)


def break_cycles(nodes: dict, edges: list[dict]) -> tuple[list[dict], list[dict]]:
    """Drop soft edges inside cycles until the graph is acyclic (hard ones last)."""
    kept = list(edges)
    dropped: list[dict] = []
    while True:
        _, stuck = kahn(nodes, kept)
        if not stuck:
            return kept, dropped
        stuck_set = set(stuck)
        inside = [e for e in kept if e["from"] in stuck_set and e["to"] in stuck_set]
        victim = next((e for e in inside if e["soft"]), inside[0])
        kept.remove(victim)
        dropped.append(victim)


def cpm(nodes: dict, edges: list[dict], order: list[str]) -> dict:
    preds: dict[str, list[str]] = {v: [] for v in nodes}
    succ: dict[str, list[str]] = {v: [] for v in nodes}
    for e in edges:
        preds[e["to"]].append(e["from"])
        succ[e["from"]].append(e["to"])
    es, ef = {}, {}
    for v in order:
        es[v] = max((ef[p] for p in preds[v]), default=0.0)
        ef[v] = es[v] + nodes[v]["effort"]
    makespan = max(ef.values(), default=0.0)
    lf, ls = {}, {}
    for v in reversed(order):
        lf[v] = min((ls[s] for s in succ[v]), default=makespan)
        ls[v] = lf[v] - nodes[v]["effort"]
    slack = {v: round(ls[v] - es[v], 6) + 0.0 for v in order}
    # Walk the zero-slack chain from the earliest critical start.
    path: list[str] = []
    cur = min((v for v in order if slack[v] == 0 and not preds[v]),
              key=lambda v: (-ef[v], v), default=None)
    while cur is not None:
        path.append(cur)
        nxt = [s for s in succ[cur] if slack[s] == 0 and abs(es[s] - ef[cur]) < 1e-9]
        cur = min(nxt, key=lambda v: v) if nxt else None
    return {"es": es, "ef": ef, "ls": ls, "lf": lf, "slack": slack,
            "makespan": round(makespan, 3), "critical_path": path}


def reverse_pressure(nodes: dict, edges: list[dict], order: list[str], lam: float = LAMBDA) -> dict:
    succ: dict[str, list[str]] = {v: [] for v in nodes}
    for e in edges:
        succ[e["from"]].append(e["to"])
    r: dict[str, float] = {}
    desc: dict[str, set[str]] = {}
    for v in reversed(order):
        r[v] = nodes[v]["priority"] + lam * sum(r[s] for s in succ[v])
        desc[v] = set(succ[v]).union(*(desc[s] for s in succ[v])) if succ[v] else set()
    out = {}
    for v in order:
        lev = 1 + len(desc[v])
        out[v] = {"pressure": round(r[v], 4), "leverage": lev,
                  "unlock_per_hour": round(r[v] * lev / max(nodes[v]["effort"], 0.1), 4),
                  "descendants": sorted(desc[v])}
    return out


def ready_now(nodes: dict, edges: list[dict]) -> int:
    blocked = {e["to"] for e in edges}
    return sum(1 for v, n in nodes.items()
               if v not in blocked and n.get("verdict") in ("READY", "REQ_PENDING"))


# ---------------------------------------------------------------- vector pilot
def _v_approve(nodes, edges):
    gates = {v for v, n in nodes.items() if v.endswith(":approve-runs")}
    nodes = {v: n for v, n in nodes.items() if v not in gates}
    edges = [e for e in edges if e["from"] not in gates]
    for n in nodes.values():
        if n.get("verdict") == "NEEDS_APPROVAL":
            n["verdict"], n["effort"] = "REQ_PENDING", EFFORT["REQ_PENDING"]
    return nodes, edges


def _v_threads(nodes, edges):
    for n in nodes.values():
        if n.get("verdict") == "THREADS":
            n["verdict"], n["effort"] = "READY", 0.5  # autofix agent: fix, push, resolve
    return nodes, edges


def _v_merge_queue(nodes, edges):
    for n in nodes.values():
        if n.get("verdict") in ("BEHIND", "REQ_PENDING"):
            n["effort"] = 0.3  # queue rebuilds and tests; no human update-branch loop
    return nodes, edges


def _v_regen_on_main(nodes, edges):
    return nodes, [e for e in edges if e["kind"] != "shared_generated"]


def _v_auto_rebase(nodes, edges):
    for n in nodes.values():
        if n.get("verdict") == "CONFLICT":
            n["verdict"], n["effort"] = "REQ_PENDING", 0.5
    return nodes, edges


VECTORS = {
    "approve_bot_runs": _v_approve,
    "thread_autofix": _v_threads,
    "merge_queue": _v_merge_queue,
    "regen_on_main": _v_regen_on_main,
    "auto_rebase": _v_auto_rebase,
}


def _measure(nodes, edges) -> dict:
    acyclic, _ = break_cycles(nodes, edges)
    order, _ = kahn(nodes, acyclic)
    c = cpm(nodes, acyclic, order)
    return {"makespan": c["makespan"], "ready_now": ready_now(nodes, acyclic),
            "total_effort": round(sum(n["effort"] for n in nodes.values()), 3)}


def _apply(names, nodes, edges):
    nodes = {v: dict(n) for v, n in nodes.items()}
    edges = [dict(e) for e in edges]
    for name in names:
        nodes, edges = VECTORS[name](nodes, edges)
    return _measure(nodes, edges)


def pilot(nodes: dict, edges: list[dict]) -> dict:
    base = _measure(nodes, edges)

    def gain(m):  # hours of makespan saved, plus total hours saved
        return {"makespan_saved": round(base["makespan"] - m["makespan"], 3),
                "effort_saved": round(base["total_effort"] - m["total_effort"], 3),
                "ready_gained": m["ready_now"] - base["ready_now"]}

    single = {k: gain(_apply([k], nodes, edges)) for k in VECTORS}
    pairs = []
    for a, b in itertools.combinations(VECTORS, 2):
        g = gain(_apply([a, b], nodes, edges))
        syn = round(g["makespan_saved"] - single[a]["makespan_saved"] - single[b]["makespan_saved"], 3)
        syn_ready = g["ready_gained"] - single[a]["ready_gained"] - single[b]["ready_gained"]
        pairs.append({"vectors": [a, b], **g, "synergy_makespan": syn, "synergy_ready": syn_ready,
                      "effect": "multiplying" if syn > 1e-9 or syn_ready > 0
                      else ("overlapping" if syn < -1e-9 or syn_ready < 0 else "additive")})
    pairs.sort(key=lambda p: (-p["synergy_makespan"], -p["synergy_ready"], -p["makespan_saved"]))
    every = gain(_apply(list(VECTORS), nodes, edges))
    return {"baseline": base, "single": single, "pairs": pairs, "all_vectors": every}


# -------------------------------------------------------------------- analyze
def analyze(census: dict, bt_scores: dict | None = None) -> dict:
    nodes, edges = build_graph(census)
    for k, v in (bt_scores or {}).items():
        if k in nodes:
            nodes[k]["priority"] = float(v)
    _, raw_cycles = kahn(nodes, edges)
    acyclic, dropped = break_cycles(nodes, edges)
    order, _ = kahn(nodes, acyclic)
    c = cpm(nodes, acyclic, order)
    rp = reverse_pressure(nodes, acyclic, order)
    ranking = sorted((v for v in order if nodes[v].get("actionable", True)),
                     key=lambda v: (-rp[v]["unlock_per_hour"], v))
    report = {
        "schema": "federation_pr_dag/v1",
        "observed_at": census.get("observed_at"),
        "repos": census.get("repos", []),
        "recommendations_are_not_authority": True,
        "counts": {"nodes": len(nodes), "edges": len(edges),
                   "gates": sum(1 for v in nodes if v.startswith("GATE:"))},
        "deadlock_nodes": raw_cycles,
        "dropped_edges": dropped,
        "kahn_order": order,
        "makespan_hours": c["makespan"],
        "critical_path": c["critical_path"],
        "nodes": {v: {"title": nodes[v].get("title", ""), "verdict": nodes[v].get("verdict"),
                      "effort": nodes[v]["effort"], "priority": nodes[v]["priority"],
                      "slack": c["slack"][v], **rp[v]} for v in order},
        "edges": acyclic,
        "ranking": ranking,
        "pilot": pilot(nodes, edges),
    }
    payload = json.dumps(report, sort_keys=True, separators=(",", ":")).encode()
    report["payload_sha256"] = hashlib.sha256(payload).hexdigest()
    return report


def to_markdown(rep: dict, top: int = 12) -> str:
    n = rep["nodes"]
    lines = [f"# Federation PR DAG — {rep['observed_at']}", "",
             "Recommendation-only (3P3 W59). Effort figures are estimates by census verdict.", "",
             (f"- Nodes {rep['counts']['nodes']} (gates {rep['counts']['gates']}), "
              f"edges {rep['counts']['edges']}, makespan **{rep['makespan_hours']} h**"),
             f"- Deadlocks: {', '.join(rep['deadlock_nodes']) or 'none'}", "",
             "## Critical path (zero slack)", ""]
    lines += [f"{i}. `{v}` {n[v]['verdict']} {n[v]['effort']} h: {n[v]['title'][:70]}"
              for i, v in enumerate(rep["critical_path"], 1)]
    lines += ["", "## Unlock ranking (reverse pressure x leverage / effort)", "",
              "| # | Node | Verdict | Effort h | Pressure | Unblocks | Score | Slack |",
              "|--:|---|---|--:|--:|--:|--:|--:|"]
    for i, v in enumerate(rep["ranking"][:top], 1):
        x = n[v]
        lines.append(f"| {i} | `{v}` | {x['verdict']} | {x['effort']} | {x['pressure']} | "
                     f"{x['leverage'] - 1} | {x['unlock_per_hour']} | {x['slack']} |")
    p = rep["pilot"]
    lines += ["", "## Pilot: unblocking vectors", "",
              (f"Baseline makespan {p['baseline']['makespan']} h, ready now {p['baseline']['ready_now']}, "
               f"total effort {p['baseline']['total_effort']} h."), "",
              "| Vector | Makespan saved h | Effort saved h | Ready gained |", "|---|--:|--:|--:|"]
    lines += [f"| {k} | {g['makespan_saved']} | {g['effort_saved']} | {g['ready_gained']} |"
              for k, g in p["single"].items()]
    lines += ["", "| Pair | Saved h | Synergy h | Synergy ready | Effect |", "|---|--:|--:|--:|---|"]
    lines += [f"| {' + '.join(q['vectors'])} | {q['makespan_saved']} | {q['synergy_makespan']} | "
              f"{q['synergy_ready']} | {q['effect']} |" for q in p["pairs"]]
    a = p["all_vectors"]
    lines += ["", (f"All vectors together: makespan saved {a['makespan_saved']} h, "
                   f"effort saved {a['effort_saved']} h, ready gained {a['ready_gained']}."), "",
              f"payload_sha256 `{rep['payload_sha256']}`", ""]
    return "\n".join(lines)


# -------------------------------------------------------------------- collect
def _gh(path: str) -> object:
    out = subprocess.run(["gh", "api", path], check=True, capture_output=True, text=True)  # nosec B603 B607 - fixed gh argv, no shell
    return json.loads(out.stdout)


def collect(repos: list[str], bd_queue: Path | None) -> dict:
    nodes = []
    for repo in repos:
        rules = _gh(f"repos/{repo}/rules/branches/main")
        req = sorted({c["context"] for r in rules if r["type"] == "required_status_checks"
                      for c in r["parameters"]["required_status_checks"]})
        strict = any(r["parameters"].get("strict_required_status_checks_policy")
                     for r in rules if r["type"] == "required_status_checks")
        for pr in _gh(f"repos/{repo}/pulls?state=open&per_page=100"):
            num = pr["number"]
            d = _gh(f"repos/{repo}/pulls/{num}")
            sha = d["head"]["sha"]
            runs = []
            for page in range(1, 6):
                chunk = _gh(f"repos/{repo}/commits/{sha}/check-runs?per_page=100&page={page}")["check_runs"]
                if not chunk:
                    break
                runs += chunk
            latest = {r["name"]: r for r in runs}
            red = [c for c in req if c in latest and latest[c]["status"] == "completed"
                   and latest[c]["conclusion"] not in ("success", "neutral", "skipped")]
            pend = [c for c in req if c not in latest or latest[c]["status"] != "completed"]
            held = _gh(f"repos/{repo}/actions/runs?head_sha={sha}&status=action_required&per_page=1")["total_count"]
            threads = _gh(f"repos/{repo}/pulls/{num}/ccr/review_threads")
            unresolved = sum(1 for t in threads if not t.get("resolved"))
            files = [f["filename"] for f in _gh(f"repos/{repo}/pulls/{num}/files?per_page=100")]
            ms = d["mergeable_state"]
            body = d.get("body") or ""
            if d["draft"]:
                verdict = "DRAFT"
            elif held and pend:  # held runs matter only while a required check is missing
                verdict = "NEEDS_APPROVAL"
            elif ms == "dirty":
                verdict = "CONFLICT"
            elif ms == "behind" and strict:
                verdict = "BEHIND"
            elif red:
                verdict = "REQ_RED"
            elif pend:
                verdict = "REQ_PENDING"
            elif unresolved:
                verdict = "THREADS"
            else:
                verdict = "READY"
            nodes.append({
                "id": node_id(repo, num), "repo": repo, "number": num, "kind": "pr",
                "title": d["title"], "verdict": verdict, "mergeable_state": ms,
                "required_red": red, "required_pending": pend, "held_runs": held,
                "unresolved": unresolved, "files": files, "body": body,
                "owner_checklist": bool(re.search(r"(?im)^\s*- \[ \].*(owner|merge gate|approv)", body)),
                "user": d["user"]["login"], "created_at": d["created_at"],
            })
    if bd_queue and bd_queue.exists():
        nodes += parse_bd_queue(bd_queue.read_text(encoding="utf-8"), "GBOGEB/CODEX")
    return {"schema": "federation_pr_census/v1", "repos": repos, "nodes": nodes,
            "observed_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ")}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--repo", action="append", required=True)
    c.add_argument("--bd-queue", type=Path)
    c.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("analyze")
    a.add_argument("census", type=Path)
    a.add_argument("--bt-scores", type=Path, help="JSON {node_id: priority 0..1} from the PCA/BT engine")
    a.add_argument("--json-out", type=Path)
    a.add_argument("--md-out", type=Path)
    args = ap.parse_args(argv)
    if args.cmd == "collect":
        census = collect(args.repo, args.bd_queue)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(census, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        print(f"census: {len(census['nodes'])} nodes -> {args.out}")
        return 0
    census = json.loads(args.census.read_text(encoding="utf-8"))
    bt = json.loads(args.bt_scores.read_text(encoding="utf-8")) if args.bt_scores else None
    rep = analyze(census, bt)
    for path, text in ((args.json_out, json.dumps(rep, indent=1, sort_keys=True) + "\n"),
                       (args.md_out, to_markdown(rep))):
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
    print(f"makespan {rep['makespan_hours']} h; critical path {' -> '.join(rep['critical_path'])}")
    print(f"top unlock: {', '.join(rep['ranking'][:5])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
