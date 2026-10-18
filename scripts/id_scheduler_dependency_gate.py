"""W34 source-bound non-executing selection over CODEX Mycelium W33 task DAG.

This adapter reuses the existing work-conserving scheduler's value-density,
age and affinity policy; adds dependency-ready, path-disjoint and measured pool
admission. It does not submit work or grant worker, merge or owner authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from scripts.id_work_conserving_scheduler import Item, choose

SCHEMA = "missioncontrol.mycelium.w34.ready_pool_plan.v1"
W33 = "missioncontrol.mycelium.operational_dag.metrics.v1"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")
PATH = re.compile(r"[A-Za-z0-9_.\/-]+\Z")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(obj):
    return (json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True)
            +"\n").encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def path_normalize(p):
    need(type(p) is str and bool(PATH.fullmatch(p)) and
         not p.startswith("/") and all(bit not in ("",".","..")
                                       for bit in p.split("/")),
         "UNSAFE_CHANGED_PATH")
    return p.casefold()


def collide(path_a, path_b):
    return (path_a==path_b or path_a.startswith(path_b+"/")
            or path_b.startswith(path_a+"/"))


def validate(metrics, tasks, *, max_proposals=4):
    need(type(metrics) is dict and metrics.get("schema")==W33, "UNTRUSTED_W33_METRICS")
    need(metrics.get("admission")=="HOLD" and
         metrics.get("dispatch_enabled") is False and
         metrics.get("formal_root_closures") is None, "UNAUTHORIZED_UPSTREAM_PROMOTION")
    need(type(metrics.get("source_digest")) is str
         and SHA64.fullmatch(metrics["source_digest"]), "UNPINNED_UPSTREAM_DIGEST")
    sources=metrics.get("sources")
    need(type(sources) is dict and bool(sources), "UNKNOWN_SOURCE_HEADS")
    need(all(type(k) is str and k.startswith("GBOGEB/")
             and type(v) is str and SHA40.fullmatch(v) for k,v in sources.items()),
         "BAD_CURRENT_HEAD")
    need(type(metrics.get("task_instances")) is list and
         type(metrics.get("pools")) is list, "INCOMPLETE_TASK_OR_POOL_POPULATION")
    states={}
    for task in metrics["task_instances"]:
        tid=task.get("id")
        need(type(tid) is str and tid and tid not in states, "DUPLICATE_DAG_TASK")
        need(task.get("state") in
             {"READY_PROPOSED","WAITING_UPSTREAM_DERIVED","UPSTREAM_FAILED_DERIVED",
              "OWNER_HOLD","SUCCESS_NATIVE","FAILED_NATIVE","CANCELLED_NATIVE",
              "SKIPPED_NATIVE","QUEUED_NATIVE","RUNNING_NATIVE","PENDING_NATIVE",
              "REQUESTED_NATIVE","WAITING_NATIVE"}, "UNQUALIFIED_TASK_STATE")
        states[tid]=task
    pools={}
    for p in metrics["pools"]:
        name=p.get("id")
        need(type(name) is str and name and name not in pools, "DUPLICATE_POOL")
        observed=p.get("observed_slots")
        running=p.get("running_observed")
        state=p.get("capacity_state")
        need(state in {"UNKNOWN","OBSERVED_BOUND"}
             and type(running) is int and running>=0, "INVALID_POOL_OBSERVATION")
        if state=="UNKNOWN":
            need(observed is None and p.get("utilization_pct") is None,
                 "FABRICATED_CAPACITY_DENOMINATOR")
        else:
            need(type(observed) is int and observed>=0 and running<=observed,
                 "OVERCLAIMED_POOL_CAPACITY")
        pools[name]=p
    need(type(max_proposals) is int and 0<=max_proposals<=4, "UNBOUNDED_PROPOSAL_SIZE")
    need(type(tasks) is list and 0<len(tasks)<=100, "INVALID_REQUEST_POPULATION")
    ids=set()
    for request in tasks:
        identity=request.get("id")
        need(type(identity) is str and identity and identity not in ids,
             "DUPLICATE_PROPOSAL")
        ids.add(identity)
        need(request.get("task_id") in states and
             request.get("repo") in sources and
             request.get("pool") in pools, "UNKNOWN_NATIVE_OR_POOL_OWNER")
        need(request.get("repo")==states[request["task_id"]].get("owner") and
             request.get("pool")==states[request["task_id"]].get("pool"),
             "WRONG_TASK_OWNER_OR_POOL")
        need(type(request.get("head_sha")) is str
             and SHA40.fullmatch(request["head_sha"]), "UNPINNED_PROPOSAL_HEAD")
        need(request.get("action_class")=="STAGE_ONLY" and
             request.get("mutation_enabled") is False,
             "NON_STAGE_OR_REMOTE_MUTATION_REQUEST")
        paths=request.get("changed_paths")
        need(type(paths) is list and bool(paths), "MISSING_CHANGED_PATHS")
        keys=[path_normalize(x) for x in paths]
        need(len(set(keys))==len(keys), "DUPLICATE_CHANGED_PATH")
        need(type(request.get("age_s")) in (int,float)
             and request["age_s"]>=0 and
             type(request.get("est_remaining_s")) in (int,float)
             and request["est_remaining_s"]>0, "INVALID_AGE_OR_DURATION")
        for key in ("convergence_gain","stability_gain","unblock_gain"):
            need(type(request.get(key)) in (int,float)
                 and 0<=request[key]<=100, "UNBOUNDED_REWARD")
    return states,pools,sources


def stage(metrics, requests, *, max_proposals=4, completed_keys=None):
    states,pools,sources=validate(metrics,requests,max_proposals=max_proposals)
    completed_keys=set(completed_keys or [])
    need(all(type(k) is str and SHA64.fullmatch(k)
             for k in completed_keys), "INVALID_IDEMPOTENCY_LEDGER")

    status={}
    candidates=[]
    for req in requests:
        ident=req["id"]
        row=states[req["task_id"]]
        key=digest(canonical({
            "id":ident,"task_id":req["task_id"],"repo":req["repo"],
            "head_sha":req["head_sha"],"changed_paths":req["changed_paths"],
            "action_class":"STAGE_ONLY"}))
        if key in completed_keys:
            status[ident]=("DEFER_ALREADY_STAGED",key)
        elif req["head_sha"]!=sources[req["repo"]]:
            status[ident]=("DEFER_STALE_SOURCE_HEAD",key)
        elif row["state"]!="READY_PROPOSED":
            status[ident]=("DEFER_DEPENDENCY_"+row["state"],key)
        elif pools[req["pool"]]["capacity_state"]!="OBSERVED_BOUND":
            status[ident]=("DEFER_POOL_CAPACITY_UNKNOWN",key)
        elif pools[req["pool"]]["observed_slots"]<=pools[req["pool"]]["running_observed"]:
            status[ident]=("DEFER_POOL_FULL",key)
        else:
            item=Item(id=ident,state="QUEUED",age_s=req["age_s"],
                      est_remaining_s=req["est_remaining_s"],
                      convergence_gain=req["convergence_gain"],
                      stability_gain=req["stability_gain"],
                      unblock_gain=req["unblock_gain"],
                      setup_affinity=req.get("setup_affinity","default"),
                      max_queue_s=req.get("max_queue_s",300.0))
            candidates.append(item)
            status[ident]=("ELIGIBLE_READ_ONLY",key)

    ordered=choose(candidates,len(candidates))
    known={x["id"]:x for x in requests}
    available={name:(max(0,p["observed_slots"]-p["running_observed"])
                     if p["capacity_state"]=="OBSERVED_BOUND" else 0)
               for name,p in pools.items()}
    accepted=[]
    locks=[]
    for item in ordered:
        req=known[item.id]
        ident=item.id
        if len(accepted)>=max_proposals:
            status[ident]=("DEFER_PULSE_BUDGET",status[ident][1])
            continue
        if available[req["pool"]]<=0:
            status[ident]=("DEFER_POOL_RESERVED_BY_OTHER_PROPOSAL",status[ident][1])
            continue
        paths=[path_normalize(x) for x in req["changed_paths"]]
        collision=any(owner==req["repo"] and
                      any(collide(x,y) for x in paths for y in old)
                      for owner,old in locks)
        if collision:
            status[ident]=("DEFER_CHANGED_PATH_LOCK",status[ident][1])
            continue
        available[req["pool"]]-=1
        locks.append((req["repo"],paths))
        accepted.append(ident)
        status[ident]=("STAGED_NOT_DISPATCHED",status[ident][1])

    rows=[]
    for req in requests:
        decision,key=status[req["id"]]
        rows.append({
            "id":req["id"],"task_id":req["task_id"],"pool":req["pool"],
            "source_head":req["head_sha"],"idempotency_key":key,
            "decision":decision,"native_job_launch":None,
            "changed_paths":req["changed_paths"],
            "next_action":("REAUTHORIZE_THROUGH_CODEX_OWNER_GATEWAY"
                           if decision=="STAGED_NOT_DISPATCHED" else
                           "REFRESH_OR_WAIT_FOR_INDEPENDENT_ELIGIBILITY")})
    return {
        "schema":SCHEMA,"source_digest":metrics["source_digest"],
        "candidate_population":len(requests),"eligible_before_pool_and_locks":
            len(candidates),"staged_proposals":len(accepted),
        "staged_ids":accepted,"decisions":rows,
        "pool_capacity_remaining_after_proposals":available,
        "all_proposals_are_non_executing":True,
        "owner_acceptance":None,"merge_admission":"HOLD",
        "dispatch_enabled":False,"authority_transfer":False,
        "formal_root_closures":None,"cross_repo_worker_launches":0,
        "selected_output_not_engineering_credit":True
    }


def receipt(report, out, *, candidate_head, run_id=None, attempt=None):
    need(type(candidate_head) is str and SHA40.fullmatch(candidate_head),
         "CANDIDATE_HEAD_NOT_EXACT")
    need((run_id is None and attempt is None) or
         (type(run_id) is int and run_id>0 and type(attempt) is int and attempt>0),
         "PARTIAL_EXACT_RUN")
    need(report.get("merge_admission")=="HOLD" and
         report.get("dispatch_enabled") is False and
         report.get("cross_repo_worker_launches")==0, "RESULT_AUTHORITY_PROMOTION")
    out.mkdir(parents=True,exist_ok=True)
    raw=canonical(report)
    (out/"W34_READY_PLAN.json").write_bytes(raw)
    m={"schema":"missioncontrol.mycelium.w34.ready_pool.receipt.v1",
       "candidate_head":candidate_head,"run_id":run_id,"attempt":attempt,
       "upstream_source_digest":report["source_digest"],
       "admission":"HOLD","dispatch_enabled":False,
       "sha256":{"W34_READY_PLAN.json":digest(raw)}}
    (out/"W34_SHA256.json").write_bytes(canonical(m))
    return m


def verify(out,head):
    m=json.loads((out/"W34_SHA256.json").read_bytes())
    need(m.get("candidate_head")==head and m.get("admission")=="HOLD" and
         m.get("dispatch_enabled") is False, "RECEIPT_AUTHORITY")
    need(set(m.get("sha256",{}))=={"W34_READY_PLAN.json"}, "INCOMPLETE_RECEIPT")
    raw=(out/"W34_READY_PLAN.json").read_bytes()
    need(digest(raw)==m["sha256"]["W34_READY_PLAN.json"],"RECEIPT_HASH_DRIFT")
    report=json.loads(raw)
    need(report.get("merge_admission")=="HOLD" and
         report.get("source_digest")==m.get("upstream_source_digest") and
         report.get("cross_repo_worker_launches")==0, "FORGED_RESULT_AUTHORITY")
    return m


def source_bound_metrics(metrics_file, receipt_file, producer_head):
    """Reject fabricated W33 populations before generating any stage proposal."""
    need(type(producer_head) is str and SHA40.fullmatch(producer_head),
         "UNPINNED_PRODUCER_HEAD")
    need(metrics_file.is_file() and receipt_file.is_file()
         and not metrics_file.is_symlink() and not receipt_file.is_symlink(),
         "MISSING_OR_UNSAFE_UPSTREAM_RECEIPT")
    raw=metrics_file.read_bytes()
    met=json.loads(raw)
    meta=json.loads(receipt_file.read_bytes())
    need(meta.get("schema")=="missioncontrol.mycelium.operational_dag.receipt.v1"
         and meta.get("candidate_head")==producer_head
         and meta.get("admission")=="HOLD" and
         meta.get("dispatch_enabled") is False and
         meta.get("authority_transfer") is False,
         "FORGED_UPSTREAM_RECEIPT")
    need(type(meta.get("files")) is dict and
         meta["files"].get("W33_TASK_METRICS.json")==digest(raw)
         and meta.get("source_digest")==met.get("source_digest"),
         "UPSTREAM_BYTES_OR_SOURCE_MISMATCH")
    need(met.get("schema")==W33 and met.get("admission")=="HOLD",
         "UPSTREAM_METRICS_SCHEMA_OR_AUTHORITY")
    return met


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--metrics",type=Path,required=True)
    p.add_argument("--producer-receipt",type=Path,required=True)
    p.add_argument("--producer-head",required=True)
    p.add_argument("--requests",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--head",required=True)
    p.add_argument("--run-id",type=int)
    p.add_argument("--attempt",type=int)
    p.add_argument("--verify-only",action="store_true")
    a=p.parse_args()
    if not a.verify_only:
        met=source_bound_metrics(a.metrics,a.producer_receipt,a.producer_head)
        req=json.loads(a.requests.read_text(encoding="utf-8"))
        receipt(stage(met,req),a.out,candidate_head=a.head,
                run_id=a.run_id,attempt=a.attempt)
    print(json.dumps(verify(a.out,a.head),sort_keys=True))


if __name__=="__main__":
    main()
