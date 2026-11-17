#!/usr/bin/env python3
"""C-PATH: critical path, unlock levers and reverse pressure over an issue/PR/BD graph.

Read-only analysis. Input is a graph JSON (`codex.cpath.graph.v1`); output is a report
(`codex.cpath.report.v1`). An edge ``{"from": A, "to": B}`` means A must finish before B.

What it computes, and how far each number can be trusted:

* Kahn waves (safe execution order) and the cycle set Kahn cannot drain (deadlocks).
* CPM on the acyclic part: earliest/latest start, slack, and the critical path, using each
  node's ``effort_days + latency_days`` as its duration. Durations are class defaults unless
  a node gives its own, so the path is an ordering argument, not a forecast.
* Downstream cone (how much work a node blocks) and Brandes betweenness (chokepoints).
* Reverse pressure: goal weight flows backwards along edges with damping, so upstream items
  (BD-queue rows included) inherit the urgency of what they block.
* Levers: nodes sharing a ``lever`` (one owner session, one CI root...). For each lever, the
  nodes that become ready when it is done, per unit of effort (multiplier); for each pair,
  extra readiness beyond the two alone (synergy, produced by AND-joins).
* PCA (power iteration, descriptive only) and Bradley-Terry strengths from pairwise
  dominance on (pressure, cone, betweenness, -effort). With tens of nodes neither is
  inference; the report says so.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import re
from collections import defaultdict, deque
from pathlib import Path

GRAPH_SCHEMA = "codex.cpath.graph.v1"
REPORT_SCHEMA = "codex.cpath.report.v1"
CLASS_DEFAULTS = {  # (effort_days, latency_days) by closure class
    "near": (0.25, 0.5),
    "needs-evidence": (0.0, 2.0),
    "owner-decision": (0.1, 3.0),
    "active": (3.0, 1.0),
    "external": (1.0, 5.0),
    "gate": (0.25, 1.0),
    "pr": (0.25, 0.5),
    "bd": (1.0, 0.5),
    "time": (0.0, 2.0),
}
REF_RE = re.compile(
    r"\b(blocked by|depends on|requires|after|closes|fixes|resolves)\s+"
    r"(?:(?P<repo>[A-Za-z0-9_.-]+)\s*)?#(?P<num>\d+)",
    re.IGNORECASE,
)


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def load_graph(data: dict) -> tuple[dict, list[tuple[str, str]]]:
    _require(data.get("schema") == GRAPH_SCHEMA, f"expected schema {GRAPH_SCHEMA}")
    nodes: dict[str, dict] = {}
    for n in data["nodes"]:
        _require(n["id"] not in nodes, f"duplicate node {n['id']}")
        eff, lat = CLASS_DEFAULTS.get(n.get("closure") or n.get("kind"), (1.0, 1.0))
        nodes[n["id"]] = {"effort_days": eff, "latency_days": lat, "levers": [], **n}
    edges = []
    for e in data["edges"]:
        a, b = e["from"], e["to"]
        _require(a in nodes and b in nodes, f"edge to unknown node {a}->{b}")
        _require(a != b, f"self edge {a}")
        if (a, b) not in edges:
            edges.append((a, b))
    return nodes, edges


def _adjacency(nodes, edges):
    succ, pred = defaultdict(list), defaultdict(list)
    for a, b in edges:
        succ[a].append(b)
        pred[b].append(a)
    return succ, pred


def kahn(nodes, edges) -> tuple[list[list[str]], list[str]]:
    succ, _ = _adjacency(nodes, edges)
    indeg = {n: 0 for n in nodes}
    for _, b in edges:
        indeg[b] += 1
    waves, remaining = [], set(nodes)
    ready = sorted(n for n in nodes if indeg[n] == 0)
    while ready:
        waves.append(ready)
        nxt = []
        for n in ready:
            remaining.discard(n)
            for c in succ[n]:
                indeg[c] -= 1
                if indeg[c] == 0:
                    nxt.append(c)
        ready = sorted(nxt)
    return waves, sorted(remaining)


def cpm(nodes, edges, order: list[str]) -> dict:
    succ, pred = _adjacency(nodes, edges)
    inset = set(order)
    dur = {n: 0.0 if nodes[n].get("done") else nodes[n]["effort_days"] + nodes[n]["latency_days"]
           for n in order}
    es, ef = {}, {}
    for n in order:
        es[n] = max((ef[p] for p in pred[n] if p in inset), default=0.0)
        ef[n] = es[n] + dur[n]
    end = max(ef.values(), default=0.0)
    lf, ls = {}, {}
    for n in reversed(order):
        lf[n] = min((ls[s] for s in succ[n] if s in inset), default=end)
        ls[n] = lf[n] - dur[n]
    slack = {n: round(ls[n] - es[n], 6) for n in order}
    path = []
    if order:
        cur = max(order, key=lambda n: (ef[n], n))
        while cur is not None:
            path.append(cur)
            cands = [p for p in pred[cur] if p in inset and abs(ef[p] - es[cur]) < 1e-9]
            cur = max(cands, key=lambda p: (ef[p], p)) if cands else None
        path.reverse()
    return {"es": es, "ef": ef, "slack": slack, "duration_days": round(end, 3), "path": path}


def path_to(nodes, edges, order: list[str], target: str) -> dict:
    """Critical (longest-duration) chain ending at ``target``: the C-path for one goal."""
    _, pred = _adjacency(nodes, edges)
    c = cpm(nodes, edges, order)
    path, cur = [], target if target in c["ef"] else None
    while cur is not None:
        path.append(cur)
        cands = [p for p in pred[cur] if p in c["ef"] and abs(c["ef"][p] - c["es"][cur]) < 1e-9]
        cur = max(cands, key=lambda p: (c["ef"][p], p)) if cands else None
    return {"target": target, "days": round(c["ef"].get(target, 0.0), 3), "path": path[::-1]}


def cones(nodes, edges) -> dict[str, set[str]]:
    succ, _ = _adjacency(nodes, edges)
    out = {}
    for n in nodes:
        seen, q = set(), deque(succ[n])
        while q:
            c = q.popleft()
            if c not in seen:
                seen.add(c)
                q.extend(succ[c])
        out[n] = seen
    return out


def betweenness(nodes, edges) -> dict[str, float]:
    """Brandes, directed, unweighted; normalised by (n-1)(n-2)."""
    succ, _ = _adjacency(nodes, edges)
    bc = dict.fromkeys(nodes, 0.0)
    for s in nodes:
        stack, preds = [], defaultdict(list)
        sigma, dist = dict.fromkeys(nodes, 0.0), dict.fromkeys(nodes, -1)
        sigma[s], dist[s] = 1.0, 0
        q = deque([s])
        while q:
            v = q.popleft()
            stack.append(v)
            for w in succ[v]:
                if dist[w] < 0:
                    dist[w] = dist[v] + 1
                    q.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    preds[w].append(v)
        delta = dict.fromkeys(nodes, 0.0)
        while stack:
            w = stack.pop()
            for v in preds[w]:
                delta[v] += sigma[v] / sigma[w] * (1 + delta[w])
            if w != s:
                bc[w] += delta[w]
    n = len(nodes)
    scale = 1.0 / ((n - 1) * (n - 2)) if n > 2 else 1.0
    return {k: v * scale for k, v in bc.items()}


def reverse_pressure(nodes, edges, alpha: float = 0.85, iters: int = 200, mode: str = "and") -> dict[str, float]:
    """Goal weight flows backwards along prerequisite edges with damping ``alpha``.

    ``mode="and"`` (default): every edge is a hard prerequisite, so each blocker of a node
    inherits that node's full pressure: p[u] = g[u] + alpha * sum_{v in succ(u)} p[v].
    ``mode="share"``: PageRank-style, a node's pressure is split across its blockers
    (p[v] / |pred(v)|); use it when blockers are alternatives rather than all required.
    Goal weight g: a node's own ``goal_weight`` (default 1 for issues, 0 for gates, PRs,
    BD rows and time waits), so pressure enters only where outcomes are wanted. Done nodes
    pass no pressure upstream. Normalised to max 1.
    """
    _require(mode in ("and", "share"), f"unknown pressure mode {mode}")
    succ, pred = _adjacency(nodes, edges)
    g = {n: 0.0 if nodes[n].get("done") else
         float(nodes[n].get("goal_weight", 1.0 if nodes[n].get("kind") == "issue" else 0.0)) for n in nodes}
    live = {n: not nodes[n].get("done") for n in nodes}
    p = dict(g)
    for _ in range(iters):
        new = {u: g[u] + alpha * sum(p[v] / (len(pred[v]) if mode == "share" else 1)
                                     for v in succ[u] if live[v]) for u in nodes}
        done = max((abs(new[u] - p[u]) for u in nodes), default=0) < 1e-12
        p = new
        if done:
            break
    top = max(p.values(), default=0) or 1.0
    return {u: v / top for u, v in p.items()}


def _ready(nodes, pred, done: set[str]) -> set[str]:
    return {n for n in nodes if n not in done and all(p in done for p in pred[n])}


def levers(nodes, edges) -> dict:
    _, pred = _adjacency(nodes, edges)
    groups = defaultdict(set)
    for n, d in nodes.items():
        for lv in d.get("levers", []):
            groups[lv].add(n)
    base_done = {n for n, d in nodes.items() if d.get("done")}
    base = _ready(nodes, pred, base_done)

    def gain(members: set[str]) -> set[str]:
        return _ready(nodes, pred, base_done | members) - base - members

    rows = {}
    for lv, members in sorted(groups.items()):
        eff = sum(nodes[m]["effort_days"] for m in members) or 0.05
        unlocked = gain(members)
        rows[lv] = {"members": sorted(members), "effort_days": round(eff, 3),
                    "unlocks": sorted(unlocked), "multiplier": round(len(unlocked) / eff, 3)}
    syn = []
    for a, b in itertools.combinations(sorted(groups), 2):
        both = gain(groups[a] | groups[b])
        extra = both - set(rows[a]["unlocks"]) - set(rows[b]["unlocks"])
        if extra:
            syn.append({"levers": [a, b], "extra_unlocks": sorted(extra), "synergy": len(extra)})
    syn.sort(key=lambda r: (-r["synergy"], r["levers"]))
    return {"levers": rows, "synergy": syn}


def ancestors(nodes, edges, target: str) -> set[str]:
    _, pred = _adjacency(nodes, edges)
    seen, q = set(), deque(pred[target])
    while q:
        a = q.popleft()
        if a not in seen:
            seen.add(a)
            q.extend(pred[a])
    return seen


def lever_cover(nodes, edges, target: str) -> dict:
    """Greedy k-way lever set that makes ``target`` ready (AND-joins need several levers).

    Each step picks the lever that completes the most still-open ancestors of the target per
    effort-day. ``share`` is that lever's part of the target's open ancestry; ``residual``
    lists ancestors no lever covers (work outside any lever, i.e. a hidden blocker).
    """
    anc = {a for a in ancestors(nodes, edges, target) if not nodes[a].get("done")}
    groups = defaultdict(set)
    for n, d in nodes.items():
        for lv in d.get("levers", []):
            groups[lv].add(n)
    covered, steps = set(), []
    while True:
        best = None
        for lv, members in sorted(groups.items()):
            gain = (members & anc) - covered
            if not gain:
                continue
            eff = sum(nodes[m]["effort_days"] for m in gain) or 0.05
            key = (len(gain) / eff, len(gain), lv)
            if best is None or key > best[0]:
                best = (key, lv, gain, eff)
        if best is None:
            break
        _, lv, gain, eff = best
        covered |= gain
        steps.append({"lever": lv, "completes": len(gain), "effort_days": round(eff, 3),
                      "share": round(len(gain) / len(anc), 3) if anc else 0.0})
    residual = sorted(anc - covered)
    # Nodes in the ancestry that are not lever members still block until done themselves.
    return {"target": target, "open_ancestors": len(anc), "steps": steps,
            "residual": residual, "ready_after_cover": not residual}


def pca(matrix: list[list[float]], names: list[str], k: int = 3) -> dict:
    """Descriptive PCA via power iteration on the standardised covariance matrix."""
    n, m = len(matrix), len(names)
    if n < 3:
        return {"note": "too few nodes", "components": []}
    cols = list(zip(*matrix))
    z = []
    for c in cols:
        mu = sum(c) / n
        sd = math.sqrt(sum((x - mu) ** 2 for x in c) / (n - 1)) or 1.0
        z.append([(x - mu) / sd for x in c])
    cov = [[sum(z[i][r] * z[j][r] for r in range(n)) / (n - 1) for j in range(m)] for i in range(m)]
    total = sum(cov[i][i] for i in range(m)) or 1.0
    comps = []
    for _ in range(min(k, m)):
        v = [1.0 / math.sqrt(m)] * m
        lam = 0.0
        for _ in range(500):
            w = [sum(cov[i][j] * v[j] for j in range(m)) for i in range(m)]
            norm = math.sqrt(sum(x * x for x in w)) or 1.0
            v = [x / norm for x in w]
            lam = norm
        if lam < 1e-12:
            break
        comps.append({"explained": round(lam / total, 4),
                      "loadings": dict(sorted(((names[i], round(v[i], 3)) for i in range(m)),
                                              key=lambda t: -abs(t[1])))})
        cov = [[cov[i][j] - lam * v[i] * v[j] for j in range(m)] for i in range(m)]
    return {"note": "descriptive only; small n, no inference", "components": comps}


def bradley_terry(items: list[str], scores: dict[str, list[float]], iters: int = 500) -> dict[str, float]:
    """MM estimate from pairwise dominance: i beats j once per criterion where it scores higher."""
    wins = defaultdict(float)
    games = defaultdict(float)
    for i, j in itertools.combinations(items, 2):
        for a, b in zip(scores[i], scores[j]):
            if a == b:
                continue
            wins[i if a > b else j] += 1
            games[(i, j)] += 1
            games[(j, i)] += 1
    p = dict.fromkeys(items, 1.0)
    for _ in range(iters):
        new = {}
        for i in items:
            den = sum(games[(i, j)] / (p[i] + p[j]) for j in items if j != i and games[(i, j)])
            new[i] = (wins[i] + 0.1) / den if den else p[i]
        s = sum(new.values()) or 1.0
        p = {i: v * len(items) / s for i, v in new.items()}
    return p


def analyse(data: dict, alpha: float = 0.85, mode: str = "and") -> dict:
    nodes, edges = load_graph(data)
    waves, cycle = kahn(nodes, edges)
    order = [n for w in waves for n in w]
    c = cpm(nodes, edges, order)
    cone = cones(nodes, edges)
    bc = betweenness(nodes, edges)
    pr = reverse_pressure(nodes, edges, alpha, mode=mode)
    lv = levers(nodes, edges)
    feats = ["cone", "betweenness", "pressure", "slack", "effort", "age_days", "comments"]
    acyclic = [n for n in order]
    mat = [[len(cone[n]), bc[n], pr[n], c["slack"][n], nodes[n]["effort_days"],
            float(nodes[n].get("age_days", 0)), float(nodes[n].get("comments", 0))] for n in acyclic]
    open_items = [n for n in nodes if not nodes[n].get("done")]
    bt = bradley_terry(open_items, {n: [pr[n], len(cone[n]), bc[n], -nodes[n]["effort_days"]]
                                    for n in open_items})
    rows = []
    for n in nodes:
        d = nodes[n]
        rows.append({"id": n, "kind": d.get("kind"), "closure": d.get("closure"),
                     "title": d.get("title", ""), "actor": d.get("actor", ""),
                     "levers": d.get("levers", []), "wave": next((i for i, w in enumerate(waves) if n in w), None),
                     "slack_days": c["slack"].get(n), "critical": n in c["path"],
                     "cone": len(cone[n]), "betweenness": round(bc[n], 4),
                     "pressure": round(pr[n], 4), "bt_strength": round(bt.get(n, 0.0), 4)})
    rows.sort(key=lambda r: (-r["pressure"], -r["cone"], r["id"]))
    bd = [r for r in rows if r["kind"] == "bd"]
    goals = data.get("goals") or sorted(
        (x for x in order if not _adjacency(nodes, edges)[0][x]), key=lambda x: -c["ef"][x])[:5]
    return {"schema": REPORT_SCHEMA, "nodes": len(nodes), "edges": len(edges),
            "waves": waves, "cycle": cycle, "critical_path": c["path"],
            "critical_path_days": c["duration_days"], "ranking": rows,
            "goal_paths": [path_to(nodes, edges, order, g) for g in goals if g in nodes],
            "pressure_mode": mode,
            "bd_queue_by_pressure": sorted(
                ({"id": r["id"], "pressure": r["pressure"], "cone": r["cone"], "title": r["title"],
                  "effort_days": nodes[r["id"]]["effort_days"],
                  "pressure_per_day": round(r["pressure"] / (nodes[r["id"]]["effort_days"] or 0.05), 3)}
                 for r in bd if not nodes[r["id"]].get("done")),
                key=lambda b: (-b["pressure"], -b["pressure_per_day"], b["id"])),
            "lever_cover": [lever_cover(nodes, edges, g) for g in goals if g in nodes],
            "levers": lv["levers"], "synergy": lv["synergy"],
            "pca": pca(mat, feats), "caveats": [
                "Durations are class defaults unless a node sets them; the path orders work, it does not forecast dates.",
                "Edges marked evidence=INFERRED are reviewed judgements, not GitHub-declared links.",
                "PCA and Bradley-Terry are descriptive over tens of nodes; no inference."]}


def edges_from_text(source_id: str, text: str, default_repo: str) -> list[dict]:
    """Declared links in an issue/PR body: 'blocked by #N' -> N blocks source; 'closes #N' -> source blocks N."""
    out = []
    for m in REF_RE.finditer(text or ""):
        verb = m.group(1).lower()
        repo = m.group("repo") if m.group("repo") and "/" not in m.group("repo") else default_repo
        other = f"{repo}#{m.group('num')}"
        if other == source_id:
            continue
        if verb in ("closes", "fixes", "resolves"):
            out.append({"from": source_id, "to": other, "evidence": "DECLARED", "source": verb})
        else:
            out.append({"from": other, "to": source_id, "evidence": "DECLARED", "source": verb})
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--graph", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--alpha", type=float, default=0.85)
    ap.add_argument("--mode", choices=("and", "share"), default="and")
    args = ap.parse_args(argv)
    report = analyse(json.loads(args.graph.read_text(encoding="utf-8")), args.alpha, args.mode)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"nodes={report['nodes']} edges={report['edges']} waves={len(report['waves'])} "
          f"cycle={len(report['cycle'])} critical_path_days={report['critical_path_days']}")
    print("critical path: " + " -> ".join(report["critical_path"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
