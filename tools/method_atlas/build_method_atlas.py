"""Build the Method Atlas v3 from the seed and the local federation checkouts.

Reads tools/method_atlas/method_atlas_seed.yaml and the tracked files (git
ls-files) of every declared repository, then writes:

    docs/method_atlas/method_atlas.json   source-derived atlas (canonical)
    docs/method_atlas/index.html          dashboard projection of that JSON
    docs/method_atlas/method_atlas.mmd    Mermaid DAG of the functional blocks

    python tools/method_atlas/build_method_atlas.py --check   # exit 1 on drift, writes nothing
    python tools/method_atlas/build_method_atlas.py --write
    python tools/method_atlas/build_method_atlas.py --write --repo HUB=../mission-control

No network, no dispatch, no promotion. Broker figures are a static model from
workflow YAML and seed parameters, never an observed queue.
"""
from __future__ import annotations

import argparse
import csv
import fnmatch
import hashlib
import html
import io
import json
import math
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SEED = ROOT / "tools/method_atlas/method_atlas_seed.yaml"
OUT_DIR = ROOT / "docs/method_atlas"
TEMPLATE = Path(__file__).with_name("method_atlas_template.html")

TEXT_EXT = {".md", ".yaml", ".yml", ".json", ".jsonl", ".py", ".html", ".js", ".csv", ".txt", ".mmd", ".toml", ".ps1", ".sh"}
MAX_BYTES = 1_500_000
DEFAULT_TIMEOUT_MIN = 360


# ---------------------------------------------------------------- repositories

def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout


def repo_identity(spec: dict, path: Path) -> dict:
    info = {"id": spec["id"], "remote": spec.get("remote"), "role": spec.get("role"),
            "path": spec["path"], "present": path.is_dir()}
    if not info["present"]:
        return info
    info["head"] = git(path, "rev-parse", "HEAD").strip()
    info["branch"] = git(path, "branch", "--show-current").strip() or None
    status = [line for line in git(path, "status", "--porcelain", "--untracked-files=no").splitlines() if line]
    info["dirty_tracked"] = len(status)
    return info


def tracked_files(path: Path) -> list[str]:
    return sorted(p for p in git(path, "ls-files", "-z").split("\0") if p)


def read_text(path: Path) -> str | None:
    try:
        if path.suffix.lower() not in TEXT_EXT or path.stat().st_size > MAX_BYTES:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


# ---------------------------------------------------------------- taxonomy

def build_taxonomy(seed: dict, repos: dict, files: dict, roots: dict) -> tuple[dict, dict]:
    lanes = seed["lanes"]
    patterns = {lane["id"]: re.compile(lane["pattern"], re.I) for lane in lanes}
    monikers = load_monikers(seed, roots)
    mon_re = None
    if monikers:
        alt = "|".join(re.escape(m["id"]) for m in sorted(monikers, key=lambda m: -len(m["id"])))
        mon_re = re.compile(r"(?<![A-Za-z0-9_])(" + alt + r")(?![A-Za-z0-9_])")

    spellings = {lane["id"]: Counter() for lane in lanes}
    lane_files = {lane["id"]: Counter() for lane in lanes}
    cooccur = Counter()
    file_lanes: dict[tuple[str, str], list[str]] = {}
    moniker_files = Counter()

    for rid, paths in files.items():
        for rel in paths:
            text = read_text(roots[rid] / rel)
            if text is None:
                continue
            hit = []
            for lid, rx in patterns.items():
                found = rx.findall(text) if rx.groups == 0 else [m.group(0) for m in rx.finditer(text)]
                path_hit = rx.search(rel)
                if found or path_hit:
                    hit.append(lid)
                    lane_files[lid][rid] += 1
                    spellings[lid].update(found)
            if hit:
                file_lanes[(rid, rel)] = hit
                for i, a in enumerate(hit):
                    for b in hit[i + 1:]:
                        cooccur[f"{a}+{b}"] += 1
            if mon_re:
                moniker_files.update(set(mon_re.findall(text)))

    out_lanes = []
    for lane in lanes:
        lid = lane["id"]
        canon = set(lane.get("canonical_spellings", []))
        variants = [{"spelling": s, "count": n, "canonical": s in canon,
                     "normalize_to": None if s in canon else lane["display"]}
                    for s, n in sorted(spellings[lid].items(), key=lambda kv: (-kv[1], kv[0]))]
        src = lane["source"]
        src_ok = repos.get(src["repo"], {}).get("present") and (roots[src["repo"]] / src["path"]).is_file()
        out_lanes.append({
            **{k: lane[k] for k in ("id", "display", "tag", "color", "meaning", "not")},
            "source": {**src, "exists": bool(src_ok)},
            "files_by_repo": dict(sorted(lane_files[lid].items())),
            "files_total": sum(lane_files[lid].values()),
            "variants": variants[:25],
            "variant_count": len(variants),
            "nonstandard_mentions": sum(v["count"] for v in variants if not v["canonical"]),
        })
    taxonomy = {
        "lanes": out_lanes,
        "combinations": [{"pair": k, "files": v} for k, v in sorted(cooccur.items(), key=lambda kv: (-kv[1], kv[0]))],
        "monikers": [{**m, "files": moniker_files.get(m["id"], 0)} for m in monikers],
    }
    return taxonomy, file_lanes


def load_monikers(seed: dict, roots: dict) -> list[dict]:
    src = seed.get("monikers", {}).get("source")
    if not src or src["repo"] not in roots:
        return []
    path = roots[src["repo"]] / src["path"]
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    keep = ("id", "label", "type", "use", "not")
    return [{k: e.get(k) for k in keep} for e in data.get("entries", [])]


# ---------------------------------------------------------------- functional blocks, I/O, DAG

def check_io(item: dict, root: Path, tracked: set[str]) -> dict:
    kind = item.get("kind", "file")
    res = {"path": item["path"], "kind": kind}
    if kind in ("runtime", "external"):
        res["status"] = "RUNTIME" if kind == "runtime" else "EXTERNAL"
        return res
    if kind == "glob":
        n = sum(1 for p in tracked if fnmatch.fnmatch(p, item["path"]))
        res["matches"] = n
        res["status"] = "OK" if n else "MISSING"
        return res
    if item["path"] in tracked:
        res["status"] = "OK"
    elif (root / item["path"]).exists():
        res["status"] = "UNTRACKED"
    else:
        res["status"] = "MISSING"
    return res


def build_blocks(seed: dict, repos: dict, files: dict, roots: dict) -> dict:
    tracked = {rid: set(paths) for rid, paths in files.items()}
    stages = [s["id"] for s in seed["spine"]]
    blocks = []
    for b in seed["blocks"]:
        rid = b["repo"]
        present = repos.get(rid, {}).get("present", False)
        root = roots.get(rid, ROOT)
        t = tracked.get(rid, set())
        entry_ok = present and b["entry"] in t
        entry_text = read_text(root / b["entry"]) if entry_ok else None
        ins = [check_io(i, root, t) for i in b.get("inputs", [])] if present else []
        outs = [check_io(o, root, t) for o in b.get("outputs", [])] if present else []
        for item in ins + outs:
            name = Path(item["path"]).name
            item["referenced_by_entry"] = bool(entry_text and name in entry_text)
        assert b["stage"] in stages, f"{b['id']}: unknown stage {b['stage']}"
        if not present:
            verdict = "REPO_ABSENT"
        elif not entry_ok:
            verdict = "ENTRY_MISSING"
        elif any(i["status"] == "MISSING" for i in ins):
            verdict = "INPUT_MISSING"
        elif not outs:
            verdict = "NO_DECLARED_OUTPUT"
        elif any(o["status"] == "MISSING" for o in outs):
            verdict = "OUTPUT_MISSING"
        elif all(o["status"] in ("RUNTIME", "EXTERNAL") for o in outs):
            verdict = "RUNTIME_ONLY"
        else:
            verdict = "IO_OK"
        blocks.append({**{k: b.get(k) for k in ("id", "name", "repo", "stage", "lanes", "entry", "need",
                                                  "supplier", "customer")},
                       "entry_exists": entry_ok, "inputs": ins, "outputs": outs, "verdict": verdict,
                       "consumes_all_outputs": bool(b.get("consumes_all_outputs"))})

    # Derived edges: an output path of A equal to an input path of B in the same repo.
    edges = []
    for a in blocks:
        for b in blocks:
            if a is b:
                continue
            if b["consumes_all_outputs"] and a["outputs"]:
                edges.append({"source": a["id"], "target": b["id"], "via": "atlas census", "derived": "consumes_all"})
                continue
            if a["repo"] != b["repo"]:
                continue
            outs = {o["path"] for o in a["outputs"] if o["kind"] == "file"}
            for i in b["inputs"]:
                hit = i["path"] in outs or (i["kind"] == "glob" and any(fnmatch.fnmatch(p, i["path"]) for p in outs))
                if hit:
                    edges.append({"source": a["id"], "target": b["id"], "via": i["path"], "derived": "io_match"})
    order = topo_order([b["id"] for b in blocks], edges)
    level = {}
    for n in order:
        level[n] = max([level[e["source"]] + 1 for e in edges if e["target"] == n] or [0])
    for b in blocks:
        b["level"] = level[b["id"]]
    return {"blocks": blocks, "edges": edges, "topological_order": order,
            "verdicts": dict(sorted(Counter(b["verdict"] for b in blocks).items()))}


def topo_order(nodes: list[str], edges: list[dict]) -> list[str]:
    indeg = {n: 0 for n in nodes}
    adj = defaultdict(list)
    for e in edges:
        adj[e["source"]].append(e["target"])
        indeg[e["target"]] += 1
    ready = sorted(n for n, d in indeg.items() if d == 0)
    order = []
    while ready:
        n = ready.pop(0)
        order.append(n)
        for m in sorted(adj[n]):
            indeg[m] -= 1
            if indeg[m] == 0:
                ready.append(m)
        ready.sort()
    if len(order) != len(nodes):
        raise ValueError("functional block DAG has a cycle")
    return order


def build_sipoc(seed: dict, blocks: list[dict]) -> list[dict]:
    stage_rank = {s["id"]: i for i, s in enumerate(seed["spine"])}
    rows = []
    for b in sorted(blocks, key=lambda b: (stage_rank[b["stage"]], b["id"])):
        rows.append({"block": b["id"], "stage": b["stage"], "supplier": b["supplier"],
                     "input": [i["path"] for i in b["inputs"]], "process": b["need"],
                     "output": [o["path"] for o in b["outputs"]], "customer": b["customer"]})
    return rows


def build_spline(seed: dict, blocks: list[dict]) -> list[dict]:
    """Lane x SPINE-stage matrix: which lanes have a functional block at each stage."""
    rows = []
    for lane in [{"id": "CORE"}] + seed["lanes"]:
        cells = {}
        for s in seed["spine"]:
            ids = [b["id"] for b in blocks if b["stage"] == s["id"] and
                   ((lane["id"] == "CORE" and not b["lanes"]) or lane["id"] in (b["lanes"] or []))]
            cells[s["id"]] = ids
        rows.append({"lane": lane["id"], "cells": cells})
    return rows


# ---------------------------------------------------------------- workflow orchestration

def expand_field(field: str, lo: int, hi: int) -> list[int]:
    values = set()
    for part in field.split(","):
        step = 1
        if "/" in part:
            part, s = part.split("/", 1)
            step = int(s)
        if part in ("*", ""):
            a, b = lo, hi
        elif "-" in part:
            a, b = (int(x) for x in part.split("-", 1))
        else:
            a = int(part)
            b = hi if step > 1 else a
        values.update(range(a, b + 1, step))
    return sorted(v for v in values if lo <= v <= hi)


def cron_runs_by_hour(expr: str) -> dict[int, int]:
    """Runs per UTC hour on a day the cron fires (day/month/weekday fields ignored: upper bound)."""
    parts = expr.split()
    if len(parts) < 5:
        return {}
    try:
        minutes = expand_field(parts[0], 0, 59)
        hours = expand_field(parts[1], 0, 23)
    except ValueError:
        return {}
    return {h: len(minutes) for h in hours}


def matrix_size(strategy) -> tuple[int, bool]:
    if not isinstance(strategy, dict):
        return 1, False
    m = strategy.get("matrix")
    if m is None:
        return 1, False
    if not isinstance(m, dict):
        return 1, True
    size, dynamic = 1, False
    axes = 0
    for k, v in m.items():
        if k in ("include", "exclude"):
            continue
        if isinstance(v, list):
            size *= max(len(v), 1)
            axes += 1
        else:
            dynamic = True
    inc = m.get("include")
    if isinstance(inc, list):
        size = size + len(inc) if axes else max(len(inc), 1)
    exc = m.get("exclude")
    if isinstance(exc, list) and axes:
        size = max(size - len(exc), 1)
    return size, dynamic


def longest_needs_chain(jobs: dict) -> int:
    memo: dict[str, int] = {}

    def depth(j, seen=()):
        if j in memo:
            return memo[j]
        if j in seen:
            return 0
        needs = (jobs.get(j) or {}).get("needs") or []
        if isinstance(needs, str):
            needs = [needs]
        d = 1 + max([depth(n, seen + (j,)) for n in needs if n in jobs] or [0])
        memo[j] = d
        return d

    return max([depth(j) for j in jobs] or [0])


def parse_workflow(rid: str, rel: str, text: str) -> dict:
    try:
        doc = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        return {"repo": rid, "file": rel, "error": f"YAML: {str(exc).splitlines()[0]}"}
    if not isinstance(doc, dict):
        return {"repo": rid, "file": rel, "error": "not a mapping"}
    on = doc.get("on", doc.get(True))
    if isinstance(on, str):
        on = {on: None}
    elif isinstance(on, list):
        on = {k: None for k in on}
    elif not isinstance(on, dict):
        on = {}
    triggers = sorted(str(k) for k in on)
    crons = [c.get("cron") for c in (on.get("schedule") or []) if isinstance(c, dict) and c.get("cron")]
    filtered = {}
    for ev in ("push", "pull_request", "pull_request_target"):
        cfg = on.get(ev)
        if ev in on:
            filtered[ev] = isinstance(cfg, dict) and any(k in cfg for k in ("paths", "paths-ignore"))
    wr = on.get("workflow_run") or {}
    upstream = wr.get("workflows", []) if isinstance(wr, dict) else []
    conc = doc.get("concurrency")
    if isinstance(conc, str):
        conc = {"group": conc}
    jobs = doc.get("jobs") or {}
    if not isinstance(jobs, dict):
        jobs = {}
    slots, dynamic, timeouts, self_hosted, max_parallel = 0, False, [], False, None
    for job in jobs.values():
        job = job or {}
        size, dyn = matrix_size(job.get("strategy"))
        mp = (job.get("strategy") or {}).get("max-parallel") if isinstance(job.get("strategy"), dict) else None
        if isinstance(mp, int):
            max_parallel = mp
            size = min(size, mp)
        slots += size
        dynamic |= dyn
        t = job.get("timeout-minutes")
        timeouts.append(t if isinstance(t, (int, float)) else DEFAULT_TIMEOUT_MIN)
        ro = job.get("runs-on")
        if "self-hosted" in json.dumps(ro):
            self_hosted = True
    dispatch_out = bool(re.search(r"repository-dispatch|/dispatches\b|gh workflow run|createWorkflowDispatch", text))
    return {
        "repo": rid, "file": rel, "name": str(doc.get("name") or Path(rel).stem),
        "triggers": triggers, "crons": crons, "path_filtered": filtered,
        "upstream_workflows": [str(u) for u in upstream],
        "concurrency_group": bool(conc and conc.get("group")),
        "cancel_in_progress": bool(conc and conc.get("cancel-in-progress") is True),
        "jobs": len(jobs), "job_slots": slots, "dynamic_matrix": dynamic, "max_parallel": max_parallel,
        "needs_depth": longest_needs_chain(jobs), "max_timeout_min": max(timeouts or [0]),
        "self_hosted": self_hosted, "dispatches_out": dispatch_out,
    }


def build_orchestration(seed: dict, repos: dict, files: dict, roots: dict) -> dict:
    workflows = []
    for rid, paths in files.items():
        for rel in paths:
            if re.fullmatch(r"\.github/workflows/[^/]+\.ya?ml", rel):
                text = read_text(roots[rid] / rel)
                if text is not None:
                    workflows.append(parse_workflow(rid, rel, text))
    ok = [w for w in workflows if "error" not in w]
    broker = seed["broker"]
    slots = broker["runner_slots"]["value"]

    per_repo = {}
    cron_hours_total = Counter()
    for rid in files:
        ws = [w for w in ok if w["repo"] == rid]
        hours = Counter()
        hour_slots = Counter()
        for w in ws:
            for c in w["crons"]:
                for h, n in cron_runs_by_hour(c).items():
                    hours[h] += n
                    hour_slots[h] += n * w["job_slots"]
        cron_hours_total.update(hour_slots)
        pr_ws = [w for w in ws if "pull_request" in w["path_filtered"] or "pull_request_target" in w["path_filtered"]]
        push_ws = [w for w in ws if "push" in w["path_filtered"]]
        broad_pr = [w for w in pr_ws if not any(w["path_filtered"].get(e) for e in ("pull_request", "pull_request_target"))]
        flood = [w for w in ws if (w["path_filtered"]) and not w["concurrency_group"]]
        per_repo[rid] = {
            "workflows": len(ws),
            "parse_errors": len([w for w in workflows if w["repo"] == rid and "error" in w]),
            "by_trigger": dict(sorted(Counter(t for w in ws for t in w["triggers"]).items())),
            "scheduled": len([w for w in ws if w["crons"]]),
            "with_concurrency": len([w for w in ws if w["concurrency_group"]]),
            "cancel_in_progress": len([w for w in ws if w["cancel_in_progress"]]),
            "dispatch_senders": len([w for w in ws if w["dispatches_out"]]),
            "self_hosted": len([w for w in ws if w["self_hosted"]]),
            "pr_jobs_min": sum(w["job_slots"] for w in broad_pr),
            "pr_jobs_max": sum(w["job_slots"] for w in pr_ws),
            "push_jobs_min": sum(w["job_slots"] for w in push_ws if not w["path_filtered"]["push"]),
            "push_jobs_max": sum(w["job_slots"] for w in push_ws),
            "broad_pr_workflows": sorted(w["file"] for w in broad_pr),
            "flood_risk_workflows": sorted(w["file"] for w in flood),
            "cron_runs_by_hour": {str(h): hours[h] for h in range(24)},
            "cron_job_slots_by_hour": {str(h): hour_slots[h] for h in range(24)},
        }

    # workflow_run chains (by workflow name within a repo)
    chains = []
    for w in ok:
        for up in w["upstream_workflows"]:
            src = [x for x in ok if x["repo"] == w["repo"] and x["name"] == up]
            chains.append({"repo": w["repo"], "upstream": up, "downstream": w["name"],
                           "upstream_file": src[0]["file"] if src else None})

    # Broker scenarios (static upper bounds)
    peak_hour = max(range(24), key=lambda h: (cron_hours_total[h], -h)) if cron_hours_total else 0
    burst = broker["burst_prs"]["value"]
    n = max(len(per_repo), 1)
    avg_min = sum(r["pr_jobs_min"] for r in per_repo.values()) / n
    avg_max = sum(r["pr_jobs_max"] for r in per_repo.values()) / n
    cron_peak = cron_hours_total[peak_hour]
    scenarios = []
    for rid, r in sorted(per_repo.items()):
        # jobs = always-triggered (no paths filter); jobs_max = every PR workflow's filter matches.
        scenarios.append(scenario(f"One PR to {rid}", r["pr_jobs_min"], slots, broker, r["pr_jobs_max"]))
        scenarios.append(scenario(f"One push to {rid} default branch", r["push_jobs_min"], slots, broker, r["push_jobs_max"]))
    scenarios.append(scenario(f"Peak cron hour {peak_hour:02d}:00 UTC (all repos)", cron_peak, slots, broker))
    scenarios.append(scenario(f"Burst: {burst} PRs + peak cron hour", round(burst * avg_min) + cron_peak, slots, broker,
                              round(burst * avg_max) + cron_peak))

    orchestrators = []
    for o in seed.get("orchestrators", []):
        root = roots.get(o["repo"])
        entry = {**{k: o[k] for k in ("id", "repo", "path", "type", "policy")},
                 "exists": bool(root and (root / o["path"]).exists())}
        if o.get("queue_dirs") and root:
            entry["queue_depth"] = {k: len([p for p in files[o["repo"]] if p.startswith(v.rstrip("/") + "/")])
                                    for k, v in o["queue_dirs"].items()}
        if o["type"] == "measured-baseline" and entry["exists"]:
            data = json.loads((root / o["path"]).read_text(encoding="utf-8"))
            entry["baseline"] = data.get("baseline")
        orchestrators.append(entry)

    return {
        "workflows": sorted(workflows, key=lambda w: (w["repo"], w["file"])),
        "per_repo": per_repo,
        "cron_job_slots_by_hour_all": {str(h): cron_hours_total[h] for h in range(24)},
        "peak_hour_utc": peak_hour,
        "workflow_run_chains": sorted(chains, key=lambda c: (c["repo"], c["upstream"], c["downstream"])),
        "orchestrators": orchestrators,
        "broker": {"parameters": {k: broker[k] for k in ("runner_slots", "burst_prs", "default_job_minutes")},
                   "modes": broker["modes"], "scenarios": scenarios,
                   "recommendations": recommendations(per_repo, cron_hours_total, peak_hour, slots)},
    }


def scenario(label: str, jobs: int, slots: int, broker: dict, jobs_max: int | None = None) -> dict:
    ratio = jobs / slots if slots else math.inf
    mode = next(m["id"] for m in broker["modes"] if m["max_ratio"] is None or ratio < m["max_ratio"])
    waves = math.ceil(jobs / slots) if slots else None
    return {"label": label, "jobs": jobs, "jobs_max": jobs if jobs_max is None else jobs_max,
            "runner_slots": slots, "ratio": round(ratio, 2),
            "queue_depth": max(0, jobs - slots), "drain_waves": waves,
            "drain_minutes_est": (waves or 0) * broker["default_job_minutes"]["value"], "mode": mode}


def recommendations(per_repo: dict, hours: Counter, peak: int, slots: int) -> list[str]:
    recs = []
    for rid, r in sorted(per_repo.items()):
        if r["flood_risk_workflows"]:
            recs.append(f"{rid}: {len(r['flood_risk_workflows'])} push/PR workflows have no concurrency group; "
                        "add `concurrency: {group: <workflow>-${{ github.ref }}, cancel-in-progress: true}` "
                        "so superseded runs stop queueing.")
        if r["broad_pr_workflows"]:
            recs.append(f"{rid}: {len(r['broad_pr_workflows'])} PR workflows run on every PR (no paths filter); "
                        "add path filters to specialist ones (see the runner-fanout baseline).")
    if hours and hours[peak] > slots:
        recs.append(f"Cron peak at {peak:02d}:00 UTC enqueues {hours[peak]} job slots vs {slots} runners; "
                    "stagger schedules across off-peak hours.")
    return recs


# ---------------------------------------------------------------- burndown ledger

COUNT_KEYS = ("total", "open", "closed", "remaining", "done", "resolved", "roots", "manifestations", "open_roots", "closed_roots")


def extract_counts(obj) -> dict:
    found = {}

    def scan(d, depth):
        if not isinstance(d, dict) or depth > 2:
            return
        for k, v in d.items():
            lk = str(k).lower()
            if lk in COUNT_KEYS and isinstance(v, (int, float)) and not isinstance(v, bool) and lk not in found:
                found[lk] = v
            elif isinstance(v, dict) and lk in ("summary", "totals", "counts", "metrics", "status", "snapshot", "record", "burndown"):
                scan(v, depth + 1)

    scan(obj, 0)
    return found


def build_ledger(seed: dict, files: dict, roots: dict, file_lanes: dict) -> dict:
    cfg = seed["burndown"]
    rx = re.compile(cfg["path_pattern"], re.I)
    entries = []
    for rid, paths in files.items():
        for rel in paths:
            ext = Path(rel).suffix.lower()
            if ext not in (".json", ".yaml", ".yml", ".csv", ".jsonl") or not rx.search(rel):
                continue
            if rel.startswith((".github/", "tests/")) or "/tests/" in rel:
                continue
            tokens = set(re.split(r"[^a-z0-9]+", rel.lower()))
            theme = next((t["id"] for t in cfg["themes"] if tokens & {str(k).lower() for k in t["keywords"]}), "OTHER")
            counts, rows = {}, None
            text = read_text(roots[rid] / rel)
            if text is not None:
                try:
                    if ext == ".json":
                        counts = extract_counts(json.loads(text))
                    elif ext in (".yaml", ".yml"):
                        counts = extract_counts(yaml.safe_load(text))
                    elif ext == ".csv":
                        rows = max(len(list(csv.reader(io.StringIO(text)))) - 1, 0)
                    else:
                        rows = len([l for l in text.splitlines() if l.strip()])
                except (ValueError, yaml.YAMLError):
                    counts = {"parse_error": 1}
            entries.append({"repo": rid, "path": rel, "theme": theme,
                            "lanes": file_lanes.get((rid, rel), []), "counts": counts, "rows": rows})
    entries.sort(key=lambda e: (e["theme"], e["repo"], e["path"]))
    themes = []
    for t in cfg["themes"] + [{"id": "OTHER", "label": "Other"}]:
        es = [e for e in entries if e["theme"] == t["id"]]
        themes.append({"id": t["id"], "label": t["label"], "files": len(es),
                       "with_counts": len([e for e in es if e["counts"] or e["rows"]]),
                       "by_lane": dict(sorted(Counter(l for e in es for l in (e["lanes"] or ["CORE"])).items()))})
    return {"themes": themes, "entries": entries}


# ---------------------------------------------------------------- projections

def mermaid(atlas: dict, seed: dict) -> str:
    lines = ["flowchart LR", "%% Method Atlas v3: functional blocks by SPINE stage. Generated; do not edit."]
    for s in seed["spine"]:
        ids = [b for b in atlas["dag"]["blocks"] if b["stage"] == s["id"]]
        if not ids:
            continue
        lines.append(f'  subgraph {s["id"]}["{s["label"]}"]')
        for b in ids:
            lines.append(f'    {mid(b["id"])}["{b["name"]}<br/>{b["verdict"]}"]')
        lines.append("  end")
    for e in atlas["dag"]["edges"]:
        arrow = "-.->" if e["derived"] == "consumes_all" else "-->"
        lines.append(f'  {mid(e["source"])} {arrow} {mid(e["target"])}')
    for lane in seed["lanes"]:
        lines.append(f'  classDef {lane["id"]} stroke:{lane["color"]},stroke-width:3px')
        members = [mid(b["id"]) for b in atlas["dag"]["blocks"] if b["lanes"] and b["lanes"][0] == lane["id"]]
        if members:
            lines.append(f'  class {",".join(members)} {lane["id"]}')
    return "\n".join(lines) + "\n"


def mid(block_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", block_id)


def dag_svg(atlas: dict, seed: dict) -> str:
    blocks = atlas["dag"]["blocks"]
    stage_ix = {s["id"]: i for i, s in enumerate(seed["spine"])}
    colors = {l["id"]: l["color"] for l in seed["lanes"]}
    cols = defaultdict(list)
    for b in sorted(blocks, key=lambda b: b["id"]):
        cols[stage_ix[b["stage"]]].append(b)
    w, h, gx, gy, top = 150, 46, 26, 16, 34
    pos = {}
    for c, bs in cols.items():
        for r, b in enumerate(bs):
            pos[b["id"]] = (12 + c * (w + gx), top + r * (h + gy))
    width = 12 + len(seed["spine"]) * (w + gx)
    height = top + max(len(v) for v in cols.values()) * (h + gy) + 10
    out = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Functional block DAG by SPINE stage" class="dag">',
           '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
           '<path d="M0,0 L10,5 L0,10 z" class="arrowhead"/></marker></defs>']
    for i, s in enumerate(seed["spine"]):
        out.append(f'<text x="{12 + i * (w + gx) + w / 2}" y="18" class="stage" text-anchor="middle">{html.escape(s["label"])}</text>')
    for e in atlas["dag"]["edges"]:
        (x1, y1), (x2, y2) = pos[e["source"]], pos[e["target"]]
        cls = "edge dashed" if e["derived"] == "consumes_all" else "edge"
        out.append(f'<path class="{cls}" d="M{x1 + w},{y1 + h / 2} C{x1 + w + 40},{y1 + h / 2} {x2 - 40},{y2 + h / 2} {x2},{y2 + h / 2}" marker-end="url(#arr)"/>')
    for b in blocks:
        x, y = pos[b["id"]]
        stroke = colors.get((b["lanes"] or [None])[0], "var(--muted)")
        out.append(f'<g class="node v-{b["verdict"]}" data-block="{html.escape(b["id"])}" tabindex="0">'
                   f'<title>{html.escape(b["name"])}: {b["verdict"]}</title>'
                   f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" style="stroke:{stroke}"/>'
                   f'<text x="{x + 8}" y="{y + 19}" class="nid">{html.escape(b["id"])}</text>'
                   f'<text x="{x + 8}" y="{y + 36}" class="nv">{html.escape(b["verdict"])}</text></g>')
    out.append("</svg>")
    return "".join(out)


def render_html(atlas: dict, seed: dict) -> str:
    template = TEMPLATE.read_text(encoding="utf-8")
    payload = json.dumps(atlas, sort_keys=True, separators=(",", ":"), ensure_ascii=True).replace("</", "<\\/")
    return (template.replace("{{ATLAS_JSON}}", payload)
            .replace("{{DIGEST}}", atlas["digest"])
            .replace("{{DAG_SVG}}", dag_svg(atlas, seed)))


# ---------------------------------------------------------------- main

def build(seed_path: Path = SEED, overrides: dict | None = None) -> tuple[dict, dict]:
    seed = yaml.safe_load(seed_path.read_text(encoding="utf-8"))
    assert seed["schema"] == "codex.method_atlas.seed.v3"
    base = seed_path.resolve().parents[2]
    roots, repos, files = {}, {}, {}
    for spec in seed["repos"]:
        path = Path((overrides or {}).get(spec["id"], spec["path"]))
        path = path if path.is_absolute() else (base / path).resolve()
        roots[spec["id"]] = path
        host = spec["id"] == seed["host_repo"]
        repos[spec["id"]] = repo_identity(spec, path)
        if host:
            # The host's own HEAD/dirty state changes with every commit of this atlas; omit it.
            for key in ("head", "branch", "dirty_tracked"):
                repos[spec["id"]].pop(key, None)
            repos[spec["id"]]["host"] = True
        if repos[spec["id"]]["present"]:
            tracked = tracked_files(path)
            if host:
                prefix = str(OUT_DIR.relative_to(ROOT)).replace("\\", "/") + "/"
                tracked = [p for p in tracked if not p.startswith(prefix)]
            files[spec["id"]] = tracked
            repos[spec["id"]]["tracked_files"] = len(files[spec["id"]])
    taxonomy, file_lanes = build_taxonomy(seed, repos, files, roots)
    dag = build_blocks(seed, repos, files, roots)
    atlas = {
        "schema": "codex.method_atlas.v3",
        "authority": {"read_only": True, "network": False, "dispatch": False, "merge_admission": "HOLD",
                      "broker_model": "STATIC_UPPER_BOUND_FROM_WORKFLOW_YAML"},
        "repos": [repos[s["id"]] for s in seed["repos"]],
        "spine": seed["spine"],
        "taxonomy": taxonomy,
        "dag": dag,
        "sipoc": build_sipoc(seed, dag["blocks"]),
        "spline": build_spline(seed, dag["blocks"]),
        "orchestration": build_orchestration(seed, repos, files, roots),
        "ledger": build_ledger(seed, files, roots, file_lanes),
    }
    atlas["digest"] = hashlib.sha256(json.dumps(atlas, sort_keys=True, separators=(",", ":"),
                                                ensure_ascii=True).encode()).hexdigest()
    return atlas, seed


def outputs(atlas: dict, seed: dict, out_dir: Path = OUT_DIR) -> dict[Path, str]:
    return {out_dir / "method_atlas.json": json.dumps(atlas, indent=1, sort_keys=True, ensure_ascii=True) + "\n",
            out_dir / "index.html": render_html(atlas, seed),
            out_dir / "method_atlas.mmd": mermaid(atlas, seed)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    ap.add_argument("--repo", action="append", default=[], metavar="ID=PATH")
    args = ap.parse_args(argv)
    overrides = dict(r.split("=", 1) for r in args.repo)
    atlas, seed = build(SEED, overrides)
    expected = outputs(atlas, seed)
    drift = []
    for path, content in expected.items():
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != content:
            drift.append(str(path.relative_to(ROOT)).replace("\\", "/"))
            if args.write:
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(content)
    result = "PASS" if not drift or args.write else "HOLD"
    print(json.dumps({"mode": "CHECK" if args.check else "WRITE", "result": result, "drift": drift,
                      "digest": atlas["digest"], "blocks": atlas["dag"]["verdicts"],
                      "workflows": len(atlas["orchestration"]["workflows"])}, indent=1))
    return 1 if args.check and drift else 0


if __name__ == "__main__":
    sys.exit(main())
