"""Build the Method Atlas v3 from the seed and the local federation checkouts.

Reads tools/method_atlas/method_atlas_seed.yaml and the tracked files (git
index) of every declared repository, then writes:

    docs/method_atlas/method_atlas.json   source-derived atlas (canonical)
    docs/method_atlas/index.html          dashboard projection of that JSON
    docs/method_atlas/method_atlas.mmd    Mermaid DAG of the functional blocks

    python tools/method_atlas/build_method_atlas.py --check   # exit 1 on drift, writes nothing
    python tools/method_atlas/build_method_atlas.py --write
    python tools/method_atlas/build_method_atlas.py --write --repo HUB=../mission-control
    python tools/method_atlas/build_method_atlas.py --check --run-checks   # also run each block's `check:`

Identity is recorded twice: commit SHA (which commit) and git object IDs
(which content): the HEAD tree OID per checkout and the blob OID per declared
input/output. Equal tree OIDs mean identical content even when SHAs differ.

No network, no dispatch, no promotion. Broker figures are a static model from
workflow YAML and seed parameters, never an observed queue. --run-checks
results go to a separate receipt, never into the canonical atlas.
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
import shlex
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from health import build_health  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SEED = ROOT / "tools/method_atlas/method_atlas_seed.yaml"
OUT_DIR = ROOT / "docs/method_atlas"
OUT_PREFIX = "docs/method_atlas/"
TEMPLATE = Path(__file__).with_name("method_atlas_template.html")
CHECKS_OUT = ROOT / "artifacts/method_atlas/checks.json"

TEXT_EXT = {".md", ".yaml", ".yml", ".json", ".jsonl", ".py", ".html", ".js", ".csv", ".txt", ".mmd", ".toml", ".ps1", ".sh"}
PARSEABLE = {".json", ".jsonl", ".yaml", ".yml", ".csv"}
MAX_BYTES = 1_500_000
DEFAULT_TIMEOUT_MIN = 360
STAGGER_STEP_MIN = 5


# ---------------------------------------------------------------- repositories and object IDs

def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout


def repo_identity(spec: dict, path: Path) -> dict:
    info = {"id": spec["id"], "remote": spec.get("remote"), "role": spec.get("role"),
            "path": spec["path"], "present": path.is_dir()}
    if not info["present"]:
        return info
    info["head"] = git(path, "rev-parse", "HEAD").strip()
    info["tree"] = git(path, "rev-parse", "HEAD^{tree}").strip()
    info["branch"] = git(path, "branch", "--show-current").strip() or None
    status = [line for line in git(path, "status", "--porcelain", "--untracked-files=no").splitlines() if line]
    info["dirty_tracked"] = len(status)
    return info


def blob_index(path: Path) -> dict[str, str]:
    """Index blob OIDs of every tracked file (`git ls-files -s`): path -> OID."""
    out = {}
    for rec in git(path, "ls-files", "-s", "-z").split("\0"):
        if rec:
            meta, rel = rec.split("\t", 1)
            out[rel] = meta.split()[1]
    return out


def worktree_modified(path: Path) -> set[str]:
    """Tracked paths whose working-tree content differs from the index (filters/EOL applied by git)."""
    return {p for p in git(path, "diff", "--name-only", "-z").split("\0") if p}


def last_change(path: Path, rel: str) -> dict | None:
    out = git(path, "log", "-1", "--format=%H %ct", "--", rel).strip()
    if not out:
        return None
    sha, ts = out.split()
    return {"commit": sha, "ts": int(ts)}


def git_blob_oid(data: bytes) -> str:
    """Git's SHA-1 blob object ID for raw bytes (used when no index is available)."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


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
                found = [m.group(0) for m in rx.finditer(text)]
                if found or rx.search(rel):
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
    src = (seed.get("monikers") or {}).get("source")
    if not src or src["repo"] not in roots:
        return []
    path = roots[src["repo"]] / src["path"]
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    keep = ("id", "label", "type", "use", "not")
    return [{k: e.get(k) for k in keep} for e in data.get("entries", [])]


# ---------------------------------------------------------------- functional blocks, I/O, DAG

def parse_check(path: Path) -> str:
    ext = path.suffix.lower()
    if ext not in PARSEABLE:
        return "NA"
    try:
        text = path.read_text(encoding="utf-8")
        if ext == ".json":
            json.loads(text)
        elif ext == ".jsonl":
            for line in text.splitlines():
                if line.strip():
                    json.loads(line)
        elif ext in (".yaml", ".yml"):
            yaml.safe_load(text)
        else:
            list(csv.reader(io.StringIO(text)))
        return "OK"
    except (OSError, ValueError, yaml.YAMLError, csv.Error, UnicodeDecodeError):
        return "FAIL"


def check_io(item: dict, root: Path, oids: dict[str, str], modified: set[str], history) -> dict:
    kind = item.get("kind", "file")
    res = {"path": item["path"], "kind": kind}
    if kind in ("runtime", "external"):
        res["status"] = "RUNTIME" if kind == "runtime" else "EXTERNAL"
        return res
    if kind == "glob":
        n = sum(1 for p in oids if fnmatch.fnmatch(p, item["path"]))
        res["matches"] = n
        res["status"] = "OK" if n else "MISSING"
        return res
    path = root / item["path"]
    if item["path"] in oids:
        res["status"] = "OK"
        res["oid"] = oids[item["path"]]
        res["worktree"] = "MODIFIED" if item["path"] in modified else "CLEAN"
        if history:
            change = history(item["path"])
            if change:
                res["last_commit"], res["changed_ts"] = change["commit"], change["ts"]
    elif path.exists():
        res["status"] = "UNTRACKED"
    else:
        res["status"] = "MISSING"
    if res["status"] in ("OK", "UNTRACKED"):
        res["parse"] = parse_check(path)
    return res


def block_verdict(present: bool, entry_ok: bool, ins: list, outs: list, freshness: bool) -> str:
    if not present:
        return "REPO_ABSENT"
    if not entry_ok:
        return "ENTRY_MISSING"
    if any(i["status"] == "MISSING" for i in ins):
        return "INPUT_MISSING"
    if any(i.get("parse") == "FAIL" for i in ins):
        return "INPUT_UNPARSEABLE"
    if not outs:
        return "NO_DECLARED_OUTPUT"
    if any(o["status"] == "MISSING" for o in outs):
        return "OUTPUT_MISSING"
    if any(o.get("parse") == "FAIL" for o in outs):
        return "OUTPUT_UNPARSEABLE"
    if all(o["status"] in ("RUNTIME", "EXTERNAL") for o in outs):
        return "RUNTIME_ONLY"
    if freshness:
        in_ts = [i["changed_ts"] for i in ins if "changed_ts" in i]
        out_ts = [o["changed_ts"] for o in outs if "changed_ts" in o]
        if in_ts and out_ts and max(in_ts) > min(out_ts):
            return "STALE_OUTPUT"
    return "IO_OK"


def build_blocks(seed: dict, repos: dict, oids: dict, roots: dict, modified: dict, history: dict) -> dict:
    stages = [s["id"] for s in seed["spine"]]
    blocks = []
    for b in seed["blocks"]:
        rid = b["repo"]
        present = repos.get(rid, {}).get("present", False)
        root = roots.get(rid, ROOT)
        o = oids.get(rid, {})
        mod = modified.get(rid, set())
        # The atlas's own block is never freshness-checked: committing it would change its own inputs.
        self_block = rid == seed["host_repo"] and any(x["path"].startswith(OUT_PREFIX) for x in b.get("outputs", []))
        hist = None if self_block else history.get(rid)
        entry_ok = present and b["entry"] in o
        entry_text = read_text(root / b["entry"]) if entry_ok else None
        ins = [check_io(i, root, o, mod, hist) for i in b.get("inputs", [])] if present else []
        outs = [check_io(x, root, o, mod, hist) for x in b.get("outputs", [])] if present else []
        for item in ins + outs:
            item["referenced_by_entry"] = bool(entry_text and Path(item["path"]).name in entry_text)
        assert b["stage"] in stages, f"{b['id']}: unknown stage {b['stage']}"
        verdict = block_verdict(present, entry_ok, ins, outs, freshness=not self_block)
        if rid == seed["host_repo"]:
            # Host commit SHAs/times move when this atlas is committed; keep them out of the output.
            for item in ins + outs:
                item.pop("last_commit", None)
                item.pop("changed_ts", None)
        blocks.append({**{k: b.get(k) for k in ("id", "name", "repo", "stage", "lanes", "entry", "need",
                                                  "supplier", "customer", "check")},
                       "entry_exists": entry_ok, "entry_oid": o.get(b["entry"]),
                       "inputs": ins, "outputs": outs, "verdict": verdict,
                       "worktree_modified": sorted(x["path"] for x in ins + outs if x.get("worktree") == "MODIFIED"),
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
            outs = {x["path"] for x in a["outputs"] if x["kind"] == "file"}
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
        rows.append({"block": b["id"], "stage": b["stage"], "lanes": b["lanes"], "supplier": b["supplier"],
                     "input": [i["path"] for i in b["inputs"]], "process": b["need"],
                     "output": [o["path"] for o in b["outputs"]], "customer": b["customer"]})
    return rows


def build_spline(seed: dict, blocks: list[dict]) -> list[dict]:
    """Lane x SPINE-stage matrix: which lanes have a functional block at each stage."""
    rows = []
    for lane in [{"id": "CORE"}] + seed["lanes"]:
        cells = {}
        for s in seed["spine"]:
            cells[s["id"]] = [b["id"] for b in blocks if b["stage"] == s["id"] and
                              ((lane["id"] == "CORE" and not b["lanes"]) or lane["id"] in (b["lanes"] or []))]
        rows.append({"lane": lane["id"], "cells": cells})
    return rows


def build_mirrors(seed: dict, repos: dict, oids: dict, base: Path) -> list[dict]:
    """Compare other checkouts of a declared repo by commit SHA, tree OID and blob OIDs."""
    out = []
    for m in seed.get("mirrors") or []:
        path = Path(m["path"]) if Path(m["path"]).is_absolute() else (base / m["path"]).resolve()
        entry = {"id": m["id"], "of": m["of"], "path": m["path"], "note": m.get("note"), "present": path.is_dir()}
        primary = repos.get(m["of"], {})
        if entry["present"] and primary.get("present"):
            ident = repo_identity({"id": m["id"], "path": m["path"]}, path)
            mirror_oids = blob_index(path)
            prim = oids.get(m["of"], {})
            differing = sorted(p for p in prim.keys() & mirror_oids.keys() if prim[p] != mirror_oids[p])
            entry.update({
                "head": ident["head"], "tree": ident["tree"], "branch": ident["branch"],
                "dirty_tracked": ident["dirty_tracked"],
                "same_commit": ident["head"] == primary.get("head"),
                "same_tree": ident["tree"] == primary.get("tree"),
                "files_only_primary": len(prim.keys() - mirror_oids.keys()),
                "files_only_mirror": len(mirror_oids.keys() - prim.keys()),
                "files_differing": len(differing),
                "files_identical": len(prim.keys() & mirror_oids.keys()) - len(differing),
                "differing_sample": differing[:20],
            })
        out.append(entry)
    return out


# ---------------------------------------------------------------- cron model

def expand_field(field: str, lo: int, hi: int) -> list[int]:
    values = set()
    for part in field.split(","):
        step = 1
        if "/" in part:
            part, s = part.split("/", 1)
            step = int(s)
        if part in ("*", "?", ""):
            a, b = lo, hi
        elif "-" in part:
            a, b = (int(x) for x in part.split("-", 1))
        else:
            a = int(part)
            b = hi if step > 1 else a
        values.update(range(a, b + 1, step))
    return sorted(v for v in values if lo <= v <= hi)


def cron_runs_by_hour(expr: str) -> dict[int, int]:
    """Runs per UTC hour on a day the cron fires."""
    parts = expr.split()
    if len(parts) < 5:
        return {}
    try:
        minutes = expand_field(parts[0], 0, 59)
        hours = expand_field(parts[1], 0, 23)
    except ValueError:
        return {}
    return {h: len(minutes) for h in hours}


def cron_minutes(expr: str) -> list[tuple[int, int]]:
    """(hour, minute) firing times on a day the cron fires."""
    parts = expr.split()
    if len(parts) < 5:
        return []
    try:
        return [(h, m) for h in expand_field(parts[1], 0, 23) for m in expand_field(parts[0], 0, 59)]
    except ValueError:
        return []


def cron_day_fraction(expr: str) -> float:
    """Share of days on which the cron fires (1.0 = every day). Cron ORs day-of-month and weekday."""
    parts = expr.split()
    if len(parts) < 5:
        return 0.0
    dom, mon, dow = parts[2], parts[3], parts[4]
    try:
        mon_frac = 1.0 if mon in ("*", "?") else len(expand_field(mon, 1, 12)) / 12
        dom_frac = 1.0 if dom in ("*", "?") else min(len(expand_field(dom, 1, 31)) / 30.44, 1.0)
        dow_frac = 1.0 if dow in ("*", "?") else len({d % 7 for d in expand_field(dow, 0, 7)}) / 7
    except ValueError:
        return 1.0
    if dom not in ("*", "?") and dow not in ("*", "?"):
        day = min(dom_frac + dow_frac, 1.0)
    else:
        day = dom_frac * dow_frac
    return round(day * mon_frac, 4)


def movable_cron(expr: str) -> bool:
    """A cron with one explicit minute and explicit hour(s) can be re-timed by changing its minute."""
    parts = expr.split()
    return len(parts) >= 5 and parts[0].isdigit() and not any(c in parts[1] for c in "*/")


def stagger_plan(entries: list[dict], slots: int) -> dict:
    """Greedy re-timing of movable crons so no single minute starts more job slots than runners.

    entries: {repo, file, name, cron, job_slots}. Load is the worst day (every cron fires).
    """
    load = Counter()
    for e in entries:
        for hm in cron_minutes(e["cron"]):
            load[hm] += e["job_slots"]
    before = max(load.values() or [0])
    moves = []
    for hm, _ in sorted(load.items(), key=lambda kv: (-kv[1], kv[0])):
        if load[hm] <= slots:
            continue
        at = [e for e in entries if hm in cron_minutes(e["cron"])]
        here = sorted([e for e in at if movable_cron(e["cron"])], key=lambda e: (-e["job_slots"], e["repo"], e["file"]))
        # Biggest first; one cron keeps the slot only if no fixed (*/N) cron already anchors it.
        candidates = here if len(here) < len(at) else here[1:]
        for e in candidates:
            if load[hm] <= slots:
                break
            parts = e["cron"].split()
            hours = expand_field(parts[1], 0, 23)
            cur = int(parts[0])
            options = [m for m in range(0, 60, STAGGER_STEP_MIN) if m != cur]
            best = min(options, key=lambda m: (max(load[(h, m)] for h in hours), abs(m - cur), m))
            if max(load[(h, best)] for h in hours) + e["job_slots"] >= load[hm]:
                continue
            for h in hours:
                load[(h, cur)] -= e["job_slots"]
                load[(h, best)] += e["job_slots"]
            new = " ".join([str(best)] + parts[1:])
            moves.append({"repo": e["repo"], "file": e["file"], "name": e["name"], "from": e["cron"],
                          "to": new, "job_slots": e["job_slots"]})
            e["cron"] = new
    return {"peak_minute_slots_before": before, "peak_minute_slots_after": max(load.values() or [0]),
            "moves": moves}


# ---------------------------------------------------------------- workflow orchestration

def matrix_size(strategy) -> tuple[int, bool]:
    if not isinstance(strategy, dict):
        return 1, False
    m = strategy.get("matrix")
    if m is None:
        return 1, False
    if not isinstance(m, dict):
        return 1, True
    size, dynamic, axes = 1, False, 0
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
        if "self-hosted" in json.dumps(job.get("runs-on")):
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


def build_orchestration(seed: dict, files: dict, roots: dict, file_lanes: dict) -> dict:
    workflows = []
    for rid, paths in files.items():
        for rel in paths:
            if re.fullmatch(r"\.github/workflows/[^/]+\.ya?ml", rel):
                text = read_text(roots[rid] / rel)
                if text is not None:
                    w = parse_workflow(rid, rel, text)
                    w["lanes"] = file_lanes.get((rid, rel), [])
                    workflows.append(w)
    ok = [w for w in workflows if "error" not in w]
    broker = seed["broker"]
    slots = broker["runner_slots"]["value"]

    # Cron contributors: one row per (workflow, cron).
    cron_entries = []
    for w in ok:
        for c in w["crons"]:
            cron_entries.append({"repo": w["repo"], "file": w["file"], "name": w["name"], "cron": c,
                                 "job_slots": w["job_slots"], "day_fraction": cron_day_fraction(c),
                                 "lanes": w["lanes"]})
    worst, daily, avg = Counter(), Counter(), Counter()
    by_hour = defaultdict(list)
    minute_load = Counter()
    minute_who = defaultdict(list)
    for e in cron_entries:
        for h, n in cron_runs_by_hour(e["cron"]).items():
            s = n * e["job_slots"]
            worst[h] += s
            avg[h] += s * e["day_fraction"]
            if e["day_fraction"] >= 1.0:
                daily[h] += s
            by_hour[h].append({**e, "runs": n, "slots_in_hour": s})
        for hm in cron_minutes(e["cron"]):
            minute_load[hm] += e["job_slots"]
            minute_who[hm].append(e)
    peak_hour = max(range(24), key=lambda h: (worst[h], -h)) if worst else 0
    peak_minutes = []
    for (h, m), v in sorted(minute_load.items(), key=lambda kv: (-kv[1], kv[0]))[:8]:
        peak_minutes.append({"time": f"{h:02d}:{m:02d}", "job_slots": v, "over_slots": v > slots,
                             "contributors": sorted(({"repo": e["repo"], "name": e["name"], "file": e["file"],
                                                      "cron": e["cron"], "job_slots": e["job_slots"],
                                                      "day_fraction": e["day_fraction"]} for e in minute_who[(h, m)]),
                                                    key=lambda c: (-c["job_slots"], c["repo"], c["file"]))})
    peak_minute_slots = peak_minutes[0]["job_slots"] if peak_minutes else 0
    stagger = stagger_plan([dict(e) for e in cron_entries], slots)

    per_repo = {}
    for rid in files:
        ws = [w for w in ok if w["repo"] == rid]
        pr_ws = [w for w in ws if "pull_request" in w["path_filtered"] or "pull_request_target" in w["path_filtered"]]
        push_ws = [w for w in ws if "push" in w["path_filtered"]]
        broad_pr = [w for w in pr_ws if not any(w["path_filtered"].get(e) for e in ("pull_request", "pull_request_target"))]
        flood = [w for w in ws if w["path_filtered"] and not w["concurrency_group"]]
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
        }

    chains = []
    for w in ok:
        for up in w["upstream_workflows"]:
            src = [x for x in ok if x["repo"] == w["repo"] and x["name"] == up]
            chains.append({"repo": w["repo"], "upstream": up, "downstream": w["name"],
                           "upstream_file": src[0]["file"] if src else None})

    burst = broker["burst_prs"]["value"]
    n = max(len(per_repo), 1)
    avg_min = sum(r["pr_jobs_min"] for r in per_repo.values()) / n
    avg_max = sum(r["pr_jobs_max"] for r in per_repo.values()) / n
    peak_time = peak_minutes[0]["time"] if peak_minutes else "00:00"
    scenarios = []
    for rid, r in sorted(per_repo.items()):
        # jobs = always-triggered (no paths filter); jobs_max = every workflow's path filter matches.
        scenarios.append(scenario(f"One PR to {rid}", r["pr_jobs_min"], slots, broker, r["pr_jobs_max"]))
        scenarios.append(scenario(f"One push to {rid} default branch", r["push_jobs_min"], slots, broker, r["push_jobs_max"]))
    scenarios.append(scenario(f"Peak cron minute {peak_time} UTC (all repos start together)", peak_minute_slots, slots, broker))
    scenarios.append(scenario(f"Burst: {burst} PRs + peak cron minute", round(burst * avg_min) + peak_minute_slots, slots,
                              broker, round(burst * avg_max) + peak_minute_slots))
    if stagger["moves"]:
        scenarios.append(scenario(f"Peak cron minute after staggering ({len(stagger['moves'])} moves)",
                                  stagger["peak_minute_slots_after"], slots, broker))

    orchestrators = []
    for o in seed.get("orchestrators", []):
        root = roots.get(o["repo"])
        entry = {**{k: o[k] for k in ("id", "repo", "path", "type", "policy")},
                 "exists": bool(root and (root / o["path"]).exists())}
        if o.get("queue_dirs") and root and o["repo"] in files:
            entry["queue_depth"] = {k: len([p for p in files[o["repo"]] if p.startswith(v.rstrip("/") + "/")])
                                    for k, v in o["queue_dirs"].items()}
        if o["type"] == "measured-baseline" and entry["exists"]:
            entry["baseline"] = json.loads((root / o["path"]).read_text(encoding="utf-8")).get("baseline")
        orchestrators.append(entry)

    return {
        "workflows": sorted(workflows, key=lambda w: (w["repo"], w["file"])),
        "per_repo": per_repo,
        "cron": {
            "slots_by_hour_worst_day": {str(h): worst[h] for h in range(24)},
            "slots_by_hour_every_day": {str(h): daily[h] for h in range(24)},
            "slots_by_hour_average_day": {str(h): round(avg[h], 1) for h in range(24)},
            "peak_hour_utc": peak_hour,
            "peak_minutes": peak_minutes,
            "contributors_by_hour": {str(h): sorted(by_hour[h], key=lambda e: (-e["slots_in_hour"], e["repo"], e["file"]))
                                     for h in range(24)},
            "stagger": stagger,
        },
        "workflow_run_chains": sorted(chains, key=lambda c: (c["repo"], c["upstream"], c["downstream"])),
        "orchestrators": orchestrators,
        "broker": {"parameters": {k: broker[k] for k in ("runner_slots", "burst_prs", "default_job_minutes")},
                   "modes": broker["modes"], "scenarios": scenarios,
                   "recommendations": recommendations(per_repo, peak_minutes, stagger, slots)},
    }


def scenario(label: str, jobs: int, slots: int, broker: dict, jobs_max: int | None = None) -> dict:
    ratio = jobs / slots if slots else math.inf
    mode = next(m["id"] for m in broker["modes"] if m["max_ratio"] is None or ratio < m["max_ratio"])
    waves = math.ceil(jobs / slots) if slots else None
    return {"label": label, "jobs": jobs, "jobs_max": jobs if jobs_max is None else jobs_max,
            "runner_slots": slots, "ratio": round(ratio, 2),
            "queue_depth": max(0, jobs - slots), "drain_waves": waves,
            "drain_minutes_est": (waves or 0) * broker["default_job_minutes"]["value"], "mode": mode}


def recommendations(per_repo: dict, peak_minutes: list, stagger: dict, slots: int) -> list[str]:
    recs = []
    for rid, r in sorted(per_repo.items()):
        if r["flood_risk_workflows"]:
            recs.append(f"{rid}: {len(r['flood_risk_workflows'])} push/PR workflows have no concurrency group; "
                        "add `concurrency: {group: <workflow>-${{ github.ref }}, cancel-in-progress: true}` "
                        "so superseded runs stop queueing.")
        if r["broad_pr_workflows"]:
            recs.append(f"{rid}: {len(r['broad_pr_workflows'])} PR workflows run on every PR (no paths filter); "
                        "add path filters to specialist ones (see the runner-fanout baseline).")
    over = [p for p in peak_minutes if p["over_slots"]]
    if over:
        recs.append(f"{len(over)} cron minute(s) start more job slots than the {slots} runners "
                    f"(worst {over[0]['time']} UTC: {over[0]['job_slots']}).")
    if stagger["moves"]:
        recs.append(f"Staggering {len(stagger['moves'])} cron(s) to other minutes cuts the peak start load from "
                    f"{stagger['peak_minute_slots_before']} to {stagger['peak_minute_slots_after']} job slots "
                    "(see the stagger plan).")
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


def build_ledger(seed: dict, files: dict, roots: dict, file_lanes: dict, oids: dict) -> dict:
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
            entries.append({"repo": rid, "path": rel, "oid": oids.get(rid, {}).get(rel), "theme": theme,
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
        out.append(f'<g class="node v-{b["verdict"]}" data-block="{html.escape(b["id"])}" '
                   f'data-lanes="{" ".join(b["lanes"] or [])}" tabindex="0" role="button">'
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


# ---------------------------------------------------------------- opt-in block checks

def run_checks(atlas: dict, roots: dict, timeout_s: int = 600) -> dict:
    """Run each block's declared `check:` from its repo root. Results never enter the canonical atlas."""
    results = []
    for b in atlas["dag"]["blocks"]:
        cmd = b.get("check")
        if not cmd or b["verdict"] == "REPO_ABSENT":
            continue
        argv = shlex.split(cmd)
        if argv and argv[0] in ("python", "python3"):
            argv[0] = sys.executable
        start = time.monotonic()
        try:
            proc = subprocess.run(argv, cwd=roots[b["repo"]], capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=timeout_s)
            status = "PASS" if proc.returncode == 0 else "FAIL"
            code, tail = proc.returncode, (proc.stdout + proc.stderr).strip().splitlines()[-5:]
        except subprocess.TimeoutExpired:
            status, code, tail = "TIMEOUT", None, []
        results.append({"block": b["id"], "repo": b["repo"], "check": cmd, "status": status, "exit_code": code,
                        "seconds": round(time.monotonic() - start, 1), "tail": tail})
    return {"schema": "codex.method_atlas.checks.v1", "atlas_digest": atlas["digest"],
            "summary": dict(sorted(Counter(r["status"] for r in results).items())), "results": results}


# ---------------------------------------------------------------- main

def build(seed_path: Path = SEED, overrides: dict | None = None) -> tuple[dict, dict, dict]:
    seed = yaml.safe_load(seed_path.read_text(encoding="utf-8"))
    assert seed["schema"] == "codex.method_atlas.seed.v3"
    base = seed_path.resolve().parents[2]
    roots, repos, files, oids, modified, history = {}, {}, {}, {}, {}, {}
    for spec in seed["repos"]:
        path = Path((overrides or {}).get(spec["id"], spec["path"]))
        path = path if path.is_absolute() else (base / path).resolve()
        roots[spec["id"]] = path
        host = spec["id"] == seed["host_repo"]
        repos[spec["id"]] = repo_identity(spec, path)
        if host:
            # The host's own HEAD/tree/dirty state changes with every commit of this atlas; omit it.
            for key in ("head", "tree", "branch", "dirty_tracked"):
                repos[spec["id"]].pop(key, None)
            repos[spec["id"]]["host"] = True
        if repos[spec["id"]]["present"]:
            index = blob_index(path)
            if host:
                index = {p: o for p, o in index.items() if not p.startswith(OUT_PREFIX)}
            oids[spec["id"]] = index
            files[spec["id"]] = sorted(index)
            modified[spec["id"]] = worktree_modified(path)
            history[spec["id"]] = (lambda p: (lambda rel: last_change(p, rel)))(path)
            repos[spec["id"]]["tracked_files"] = len(index)
    taxonomy, file_lanes = build_taxonomy(seed, repos, files, roots)
    dag = build_blocks(seed, repos, oids, roots, modified, history)
    atlas = {
        "schema": "codex.method_atlas.v3",
        "authority": {"read_only": True, "network": False, "dispatch": False, "merge_admission": "HOLD",
                      "identity": "COMMIT_SHA_PLUS_GIT_OBJECT_IDS",
                      "broker_model": "STATIC_UPPER_BOUND_FROM_WORKFLOW_YAML"},
        "repos": [repos[s["id"]] for s in seed["repos"]],
        "mirrors": build_mirrors(seed, repos, oids, base),
        "spine": seed["spine"],
        "taxonomy": taxonomy,
        "dag": dag,
        "sipoc": build_sipoc(seed, dag["blocks"]),
        "spline": build_spline(seed, dag["blocks"]),
        "orchestration": build_orchestration(seed, files, roots, file_lanes),
        "ledger": build_ledger(seed, files, roots, file_lanes, oids),
        "health": build_health(seed, files, roots),
        "conflict_playbook": seed.get("conflicts", {}),
    }
    atlas["digest"] = hashlib.sha256(json.dumps(atlas, sort_keys=True, separators=(",", ":"),
                                                ensure_ascii=True).encode()).hexdigest()
    return atlas, seed, roots


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
    ap.add_argument("--run-checks", action="store_true", help="also run each block's declared `check:` command")
    ap.add_argument("--checks-out", type=Path, default=CHECKS_OUT, help="receipt path for --run-checks")
    args = ap.parse_args(argv)
    overrides = dict(r.split("=", 1) for r in args.repo)
    atlas, seed, roots = build(SEED, overrides)
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
    report = {"mode": "CHECK" if args.check else "WRITE", "result": "PASS" if not drift or args.write else "HOLD",
              "drift": drift, "digest": atlas["digest"], "blocks": atlas["dag"]["verdicts"],
              "workflows": len(atlas["orchestration"]["workflows"])}
    failed_checks = False
    if args.run_checks:
        receipt = run_checks(atlas, roots)
        args.checks_out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.checks_out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(receipt, indent=1) + "\n")
        report["checks"] = receipt["summary"]
        report["checks_receipt"] = str(args.checks_out)
        failed_checks = any(r["status"] != "PASS" for r in receipt["results"])
    print(json.dumps(report, indent=1))
    return 1 if (args.check and drift) or failed_checks else 0


if __name__ == "__main__":
    sys.exit(main())
