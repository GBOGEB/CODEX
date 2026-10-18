"""CODE PURPLE MIP operational DAG observer: frozen, read-only, no dispatch.

Task outcome (observed) and dependency inhibition (derived) never conflate.
Pools are declared capacity, not inferred from GitHub job successes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path

SCHEMA = "codepurple.mycelium.operational-dag.v1"
STATES = {"queued", "in_progress", "completed"}
TERMINAL = {"success", "failure", "cancelled", "skipped", "timed_out"}
DEFERRED = {"AWAITING_APPROVAL", "AWAITING_ARTIFACT", "AWAITING_EXTERNAL_OWNER"}
SHA = __import__("re").compile(r"^[0-9a-f]{40}$")


def demand(ok, label):
    if not ok:
        raise ValueError(label)


def stamp(x):
    if x is None:
        return None
    demand(type(x) is str, "INVALID_TIMESTAMP")
    dt = datetime.fromisoformat(x.replace("Z", "+00:00"))
    demand(dt.utcoffset() is not None, "NAIVE_TIMESTAMP")
    return dt


def nearest_rank(rows, p):
    if not rows:
        return None
    return round(sorted(rows)[math.ceil(len(rows)*p)-1], 3)


def measure(data):
    demand(type(data) is dict and data.get("schema") == SCHEMA, "SCHEMA")
    demand(data.get("mutation_enabled") is False and data.get("admission") == "HOLD"
           and data.get("dispatch_authorized") is False, "AUTHORITY_PROMOTION")
    tasks = data.get("tasks")
    pools = data.get("pools")
    demand(type(tasks) is list and len(tasks) > 0 and type(pools) is list, "EMPTY_POPULATION")
    poolmap = {}
    for pool in pools:
        label = pool.get("name")
        size = pool.get("slots")
        demand(type(label) is str and label and label not in poolmap and
               type(size) is int and size >= 0, "POOL_INVALID")
        poolmap[label] = size
    ids = set()
    native = set()
    byid = {}
    for t in tasks:
        name = t.get("id")
        demand(type(name) is str and name and name not in ids, "DUPLICATE_ID")
        ids.add(name)
        byid[name] = t
        demand(t.get("state") in STATES or t.get("state") == "deferred", "INVALID_STATE")
        demand(type(t.get("head_sha")) is str and SHA.fullmatch(t["head_sha"]), "UNPINNED_HEAD")
        demand(type(t.get("owner")) is str and t["owner"], "OWNER_MISSING")
        demand(type(t.get("depends_on")) is list and
               len(set(t["depends_on"])) == len(t["depends_on"]), "BAD_DEPENDENCIES")
        demand(t.get("pool") in poolmap, "UNKNOWN_POOL")
        status = t["state"]
        conclusion = t.get("conclusion")
        demand((status == "completed" and conclusion in TERMINAL) or
               (status != "completed" and conclusion is None), "PREMATURE_OUTCOME")
        if status == "deferred":
            demand(t.get("defer_reason") in DEFERRED and
                   t.get("started_at") is None, "FALSE_DEFER")
        else:
            demand(t.get("defer_reason") is None, "FALSE_DEFER_REASON")
        if t.get("run_id") is not None or t.get("job_id") is not None:
            k = (t.get("repo"), t.get("run_id"), t.get("attempt"), t.get("job_id"))
            demand(type(k[0]) is str and all(type(x) is int and x > 0 for x in k[1:]),
                   "NATIVE_ID_INCOMPLETE")
            demand(k not in native, "NATIVE_ID_REPLAY")
            native.add(k)
        for key in ("created_at", "started_at", "completed_at"):
            stamp(t.get(key))
        if status != "completed":
            demand(t.get("completed_at") is None, "NONTERMINAL_END")
        demand(t.get("evidence_verified") in (True, False, None), "EVIDENCE_CLASS")
        if t.get("evidence_verified") is True:
            demand(status == "completed" and conclusion == "success"
                   and t.get("job_id") is not None, "FORGED_PROOF")
    children = defaultdict(set)
    for t in tasks:
        for dependency in t["depends_on"]:
            demand(dependency in ids and dependency != t["id"], "DANGLING_DEPENDENCY")
            children[dependency].add(t["id"])
    pending = {x: len(byid[x]["depends_on"]) for x in ids}
    layers, ready = [], sorted(x for x in ids if pending[x] == 0)
    seen = set()
    while ready:
        layers.append(ready)
        nxt = set()
        for x in ready:
            seen.add(x)
            for c in children[x]:
                pending[c] -= 1
                if pending[c] == 0:
                    nxt.add(c)
        ready = sorted(nxt)
    demand(len(seen) == len(ids), "EXECUTABLE_CYCLE")
    queue, runtime = [], []
    derived = {}
    poolstate = {p: {"slots": n, "running": 0, "queued": 0, "deferred": 0}
                 for p, n in poolmap.items()}
    roots = {}
    for x in sorted(ids):
        t = byid[x]
        state = t["state"]
        p = poolstate[t["pool"]]
        if state == "in_progress":
            p["running"] += 1
        elif state == "queued":
            p["queued"] += 1
        elif state == "deferred":
            p["deferred"] += 1
        failed_ancestors = set()
        walk = list(t["depends_on"])
        scanned = set()
        while walk:
            y = walk.pop()
            if y in scanned:
                continue
            scanned.add(y)
            if byid[y].get("conclusion") in {"failure", "timed_out"}:
                failed_ancestors.add(y)
            walk.extend(byid[y]["depends_on"])
        derived[x] = {"native_state": state, "native_conclusion": t.get("conclusion"),
                      "blocked_by": sorted(failed_ancestors),
                      "derived_upstream_failed": bool(failed_ancestors) and
                      state in {"queued", "deferred"},
                      "source_ref": t.get("source_ref")}
        if t.get("conclusion") in {"failure", "timed_out"}:
            roots[x] = {"direct_dependents": len(children[x]),
                        "blocked_descendants": 0, "all_descendants": 0}
        created, started, ended = (stamp(t.get(k)) for k in
                                    ("created_at", "started_at", "completed_at"))
        if created and started:
            delta = (started-created).total_seconds()
            demand(delta >= 0, "NEGATIVE_QUEUE")
            queue.append(delta)
        if started and ended:
            delta = (ended-started).total_seconds()
            demand(delta >= 0, "NEGATIVE_RUNTIME")
            runtime.append(delta)
    for root in roots:
        downstream, stack = set(), list(children[root])
        while stack:
            node = stack.pop()
            if node in downstream:
                continue
            downstream.add(node)
            stack.extend(children[node])
        roots[root]["all_descendants"] = len(downstream)
        roots[root]["blocked_descendants"] = sum(
            bool(derived[node]["derived_upstream_failed"]) for node in downstream)
    demand(all(p["running"] <= p["slots"] for p in poolstate.values()),
           "OBSERVED_POOL_OVERSUBSCRIPTION")
    for p in poolstate.values():
        p["utilization"] = round(p["running"]/p["slots"], 4) if p["slots"] else None
    completed = [t for t in tasks if t["state"] == "completed"]
    verified = sum(t["evidence_verified"] is True for t in completed)
    return {"schema": "codepurple.mycelium.operational-metrics.v1",
            "source_digest": hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest(),
            "tasks": len(tasks), "nodes": len(ids),
            "dependency_edges": sum(len(t["depends_on"]) for t in tasks),
            "dag_layers": len(layers), "layers": layers,
            "native_instances": len(native), "completed": len(completed),
            "native_failed": sum(t["conclusion"] in {"failure", "timed_out"} for t in completed),
            "verified_native_proofs": verified,
            "proof_yield": round(verified/len(completed), 4) if completed else None,
            "queue_p95_seconds": nearest_rank(queue, 0.95),
            "runtime_p95_seconds": nearest_rank(runtime, 0.95),
            "queue_sample_n": len(queue), "runtime_sample_n": len(runtime),
            "pool": poolstate, "task_states": derived, "root_pressure": roots,
            "distinct_primary_failure_instances": len(roots),
            "union_blocked_instances": sum(row["derived_upstream_failed"] for row in derived.values()),
            "engineering_acceptance": None, "dispatches": 0,
            "merge_admission": "HOLD", "authority_transfer": False}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    result = measure(json.loads(a.input.read_text(encoding="utf-8")))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n", encoding="utf-8")

if __name__ == "__main__":
    main()
