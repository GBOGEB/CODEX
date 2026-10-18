"""CODE PURPLE W33 operational task-instance DAG: read-only, exact-source bound.

Unlike the reference Mycelium graph, this projection only places SUCCESS-
required edges in its executable DAG. Historical jobs and owner gates are
not native dispatch permission, nor engineering/admission credit.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

SCHEMA = "missioncontrol.mycelium.operational_dag.snapshot.v1"
SHA = re.compile(r"[0-9a-f]{40}\Z")
LEVELS = {"NATIVE_JOB_METADATA", "NATIVE_LOG_VERIFIED", "DECLARED_ONLY"}
NATIVE_STATES = {"queued", "in_progress", "completed", "waiting", "pending", "requested"}
TERMINAL = {"success", "failure", "cancelled", "timed_out", "skipped"}
DERIVED_STATES = {"pending", "owner_hold"}
REQUIRES = "REQUIRES_SUCCESS"
EDGE_TYPES = {REQUIRES, "REFERENCES"}
AXES = ("source_coverage", "adversarial_penetration", "cross_module_integration",
        "platform_runner_reach", "causal_defect_detection")
SIPOC = [
    ("source_coverage", "ABACUS B0", "exact source/head and eligible lines",
     "join matched JUnit/coverage", "source proof or UNKNOWN", "source reviewer"),
    ("adversarial_penetration", "negative-test owner", "fault-oracle identities",
     "run reverse and fail-closed tests", "effective detection numerator", "MIP"),
    ("cross_module_integration", "source + receiver", "two sided run/attempt/hash",
     "validate owner return", "authenticated pair or DEFER", "QPS owner"),
    ("platform_runner_reach", "GitHub/runner", "OS/Python/job instances",
     "measure queue, pool and runtime", "native cell receipts", "CI owner"),
    ("causal_defect_detection", "BD/root owner", "native log first-reds",
     "fingerprint and propagate block", "candidate root/impact, no closure", "REX"),
]


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def serial(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
            + "\n").encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def instant(value):
    if value is None:
        return None
    need(type(value) is str and value, "INVALID_TIME")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("INVALID_TIME") from exc
    need(dt.tzinfo is not None and dt.utcoffset() is not None, "NON_UTC_AWARE_TIME")
    return dt


def percentile(values, q):
    return (round(sorted(values)[math.ceil(len(values) * q) - 1], 3)
            if values else None)


def validate(data):
    need(type(data) is dict and data.get("schema") == SCHEMA, "SCHEMA")
    need(data.get("population") == "SELECTED_OBSERVATIONS_NOT_FLEET",
         "POPULATION_OVERCLAIM")
    instant(data.get("capture_utc"))
    gov = data.get("governance", {})
    need(gov.get("merge_admission") == "HOLD" and
         gov.get("dispatch_enabled") is False and
         gov.get("authority_transfer") is False and
         gov.get("root_closure_credit") == 0, "UNAUTHORIZED_PROMOTION")
    sources = data.get("sources")
    need(type(sources) is dict and bool(sources), "MISSING_SOURCES")
    for repo, sha in sources.items():
        need(type(repo) is str and repo.startswith("GBOGEB/") and
             type(sha) is str and SHA.fullmatch(sha), "INVALID_HEAD")
    pools = data.get("pools")
    need(type(pools) is list and bool(pools), "MISSING_POOLS")
    ps = set()
    for pool in pools:
        pid = pool.get("id")
        need(type(pid) is str and pid and pid not in ps, "DUPLICATE_POOL")
        ps.add(pid)
        cap = pool.get("observed_slots")
        need(cap is None or (type(cap) is int and cap >= 0), "INVALID_CAPACITY")
        if cap is not None:
            # Native task/run metadata does NOT prove runner pool slot inventory.
            # Require a separate bound pool inventory receipt, never a guess.
            need(pool.get("capacity_evidence") == "NATIVE_POOL_INVENTORY_VERIFIED"
                 and str(pool.get("source_ref", "")).startswith("https://github.com/")
                 and type(pool.get("receipt_sha256")) is str
                 and re.fullmatch(r"[0-9a-f]{64}", pool["receipt_sha256"]),
                 "UNVERIFIED_CAPACITY")
        else:
            need(pool.get("capacity_evidence") is None, "FAKE_CAPACITY_SOURCE")
    tasks = data.get("tasks")
    need(type(tasks) is list and len(tasks) > 0, "MISSING_TASKS")
    ids, native_ids = set(), set()
    for item in tasks:
        tid = item.get("id")
        need(type(tid) is str and tid and tid not in ids, "DUPLICATE_TASK")
        ids.add(tid)
        need(item.get("owner") in sources and item.get("pool") in ps and
             item.get("axis") in AXES and
             str(item.get("source_ref", "")).startswith("https://github.com/"),
             "INVALID_TASK_OWNER_OR_PROVENANCE")
        need(type(item.get("logical_key")) is str and item["logical_key"],
             "MISSING_LOGICAL_IDENTITY")
        kind = item.get("kind")
        need(kind in {"NATIVE", "DERIVED"}, "UNTYPED_TASK")
        state = item.get("status")
        if kind == "NATIVE":
            need(state in NATIVE_STATES, "BAD_NATIVE_STATE")
            n = item.get("native")
            need(type(n) is dict and all(type(n.get(k)) is int and n[k] > 0
                 for k in ("run_id", "attempt", "job_id")) and
                 type(n.get("head_sha")) is str and SHA.fullmatch(n["head_sha"]),
                 "MISSING_NATIVE_IDENTITY")
            key = (item["owner"], n["run_id"], n["attempt"], n["job_id"])
            need(key not in native_ids, "DUPLICATE_NATIVE_INSTANCE")
            native_ids.add(key)
            conclusion = item.get("conclusion")
            need((state == "completed" and conclusion in TERMINAL) or
                 (state != "completed" and conclusion is None),
                 "UNTRUSTWORTHY_OUTCOME")
            need(item.get("evidence_level") in
                 {"NATIVE_JOB_METADATA", "NATIVE_LOG_VERIFIED"}, "FAKE_NATIVE")
            if item.get("first_red_signature") is not None:
                need(state == "completed" and conclusion in ("failure", "timed_out")
                     and item["evidence_level"] == "NATIVE_LOG_VERIFIED" and
                     type(item["first_red_signature"]) is str and
                     bool(item["first_red_signature"]), "FAKE_ROOT_FINGERPRINT")
            times = [instant(item.get(k)) for k in
                     ("created_at", "started_at", "completed_at")]
            if times[0] and times[1]:
                need(times[0] <= times[1], "NEGATIVE_QUEUE_TIME")
            if times[1] and times[2]:
                need(state == "completed" and times[1] <= times[2],
                     "NEGATIVE_RUN_TIME")
            need(not times[2] or state == "completed", "PREMATURE_COMPLETION_TIME")
        else:
            need(state in DERIVED_STATES and item.get("native") is None and
                 item.get("conclusion") is None and
                 item.get("first_red_signature") is None and
                 item.get("evidence_level") == "DECLARED_ONLY",
                 "FAKE_DERIVED_EXECUTION")
    edges = data.get("edges")
    need(type(edges) is list, "MISSING_EDGES")
    seen = set()
    adj, inbound = defaultdict(set), defaultdict(set)
    for edge in edges:
        u, v = edge.get("from"), edge.get("to")
        kind = edge.get("kind")
        need(u in ids and v in ids and u != v and kind in EDGE_TYPES and
             str(edge.get("source_ref", "")).startswith("https://github.com/"),
             "DANGLING_OR_UNTYPED_EDGE")
        key = (u, v, kind)
        need(key not in seen, "DUPLICATE_EDGE")
        seen.add(key)
        if kind == REQUIRES:
            adj[u].add(v)
            inbound[v].add(u)
    degree = {tid:len(inbound[tid]) for tid in ids}
    left = set(ids)
    layers = []
    while left:
        ready = sorted(t for t in left if degree[t] == 0)
        need(bool(ready), "EXECUTABLE_DAG_CYCLE")
        layers.append(ready)
        for node in ready:
            left.remove(node)
            for child in adj[node]:
                degree[child] -= 1
    return layers, adj, inbound


def project(data):
    layers, adj, inbound = validate(data)
    byid = {x["id"]:x for x in data["tasks"]}
    status = {}
    blockers = {}
    for layer in layers:
        for tid in layer:
            task = byid[tid]
            if task["kind"] == "NATIVE":
                st = task["status"]
                if st == "completed":
                    state = {"success":"SUCCESS_NATIVE", "failure":"FAILED_NATIVE",
                             "timed_out":"FAILED_NATIVE", "cancelled":"CANCELLED_NATIVE",
                             "skipped":"SKIPPED_NATIVE"}[task["conclusion"]]
                else:
                    state = {"queued":"QUEUED_NATIVE", "in_progress":"RUNNING_NATIVE",
                             "pending":"PENDING_NATIVE", "requested":"REQUESTED_NATIVE",
                             "waiting":"WAITING_NATIVE"}[st]
                status[tid] = state
                blockers[tid] = [tid] if state == "FAILED_NATIVE" else []
            elif task["status"] == "owner_hold":
                status[tid] = "OWNER_HOLD"
                blockers[tid] = []
            else:
                parent_states = [status[x] for x in inbound[tid]]
                upstream = set()
                for parent in inbound[tid]:
                    upstream.update(blockers[parent])
                blockers[tid] = sorted(upstream)
                if upstream:
                    status[tid] = "UPSTREAM_FAILED_DERIVED"
                elif not parent_states or all(x=="SUCCESS_NATIVE" for x in parent_states):
                    # This is a proposal, not a launch. A derived task never becomes SUCCESS.
                    status[tid] = "READY_PROPOSED"
                else:
                    status[tid] = "WAITING_UPSTREAM_DERIVED"
    rows=[]
    queue_delays, service_times = [], []
    for item in data["tasks"]:
        tid=item["id"]
        n=item.get("native") or {}
        t0,t1,t2=[instant(item.get(k)) for k in
                  ("created_at", "started_at", "completed_at")]
        if t0 and t1:
            queue_delays.append((t1-t0).total_seconds())
        if t1 and t2:
            service_times.append((t2-t1).total_seconds())
        rows.append({"id":tid,"logical_key":item["logical_key"],
                     "owner":item["owner"],"pool":item["pool"],"axis":item["axis"],
                     "state":status[tid],"observed_state":item["status"],
                     "kind":item["kind"],"first_red_signature":item.get("first_red_signature"),
                     "blocked_by":blockers[tid] if item["kind"]=="DERIVED" else [],
                     "source_ref":item["source_ref"],"native":n or None,
                     "is_current_owner_head":(n.get("head_sha")==data["sources"][item["owner"]]
                                              if n else None),
                     "evidence_level":item["evidence_level"]})
    roots={}
    for item in data["tasks"]:
        tid=item["id"]
        if status[tid] != "FAILED_NATIVE":
            continue
        if item.get("first_red_signature"):
            key="verified:"+item["first_red_signature"]
            confidence="NATIVE_LOG_VERIFIED_FINGERPRINT_NOT_CAUSAL_CLOSURE"
        else:
            key="unclassified:"+item["owner"]+":"+str(item["native"]["job_id"])
            confidence="SEPARATE_UNCLASSIFIED_FAILURE"
        root=roots.setdefault(key,{"kind":confidence,"primary_instances":[],
                                   "blocked_descendants":set()})
        root["primary_instances"].append(tid)
        root["blocked_descendants"].update(row["id"] for row in rows
                                            if row["state"]=="UPSTREAM_FAILED_DERIVED"
                                            and tid in row["blocked_by"])
    rootrows=[]
    for fingerprint, data_root in sorted(roots.items()):
        rootrows.append({"fingerprint":fingerprint,"evidence":data_root["kind"],
                         "failure_manifestations":len(data_root["primary_instances"]),
                         "primary_ids":sorted(data_root["primary_instances"]),
                         "unique_downstream_blocked":len(data_root["blocked_descendants"]),
                         "blocked_ids":sorted(data_root["blocked_descendants"]),
                         "formal_causal_root_closed":None})
    poolrows=[]
    for pool in data["pools"]:
        rows_here=[r for r in rows if r["pool"]==pool["id"]]
        running=sum(r["state"]=="RUNNING_NATIVE" for r in rows_here)
        cap=pool["observed_slots"]
        poolrows.append({"id":pool["id"],"observed_slots":cap,
                         "running_observed":running,
                         "queued_observed":sum(r["state"]=="QUEUED_NATIVE" for r in rows_here),
                         "ready_proposals":sum(r["state"]=="READY_PROPOSED" for r in rows_here),
                         "utilization_pct":round(100*running/cap,2) if cap else None,
                         "capacity_state":"UNKNOWN" if cap is None else "OBSERVED_BOUND"})
    counts=Counter(r["state"] for r in rows)
    unique_blocked={r["id"] for r in rows if r["state"]=="UPSTREAM_FAILED_DERIVED"}
    report={
        "schema":"missioncontrol.mycelium.operational_dag.metrics.v1",
        "capture_utc":data["capture_utc"],"population":data["population"],
        "source_digest":digest(serial(data)),"sources":data["sources"],
        "graph":{"nodes":len(rows),"edges":len(data["edges"]),
                 "executable_edges":sum(e["kind"]==REQUIRES for e in data["edges"]),
                 "layers":len(layers)},
        "counts":dict(sorted(counts.items())),
        "terminal_native":sum(r["state"] in
                              {"SUCCESS_NATIVE","FAILED_NATIVE","CANCELLED_NATIVE",
                               "SKIPPED_NATIVE"} for r in rows),
        "native_failed_instances":sum(r["state"]=="FAILED_NATIVE" for r in rows),
        "primary_failure_fingerprint_candidates":len(rootrows),
        "downstream_unique_blocked":len(unique_blocked),
        "root_amplification_per_failed_instance":
            (round(len(unique_blocked)/sum(r["state"]=="FAILED_NATIVE" for r in rows),4)
             if any(r["state"]=="FAILED_NATIVE" for r in rows) else None),
        "queue_p95_s":percentile(queue_delays,.95),
        "queue_sample_n":len(queue_delays),
        "execution_p95_s":percentile(service_times,.95),
        "runtime_sample_n":len(service_times),
        "root_candidates":rootrows,"pools":poolrows,
        "task_instances":rows,
        "metric_targets":{
            "state_provenance": {"measured":len(rows),"eligible":len(rows)},
            "no_false_green":True,"no_duplicate_instances":True,
            "five_axes":list(AXES),"source_coverage":None,
            "adversarial_penetration":None,"cross_module_integration":None,
            "platform_runner_reach":None,"causal_defect_detection":None},
        "stability":{"comparable_epochs":1,
                     "stable":False,
                     "six_sigma_qualified":False,
                     "next_wave":"REQUIRE_NEW_EXACT_SOURCE_OBSERVATION"},
        "admission":"HOLD","dispatch_enabled":False,"formal_root_closures":None
    }
    return report, layers


def compare(previous,current):
    validate(previous)
    validate(current)
    a={x["logical_key"]:x for x in previous["tasks"]}
    b={x["logical_key"]:x for x in current["tasks"]}
    aligned=set(a)==set(b) and previous["population"]==current["population"]
    before=project(previous)[0]
    after=project(current)[0]
    return {"schema":"missioncontrol.mycelium.operational_dag.delta.v1",
            "same_logical_population":aligned,
            "exact_source_heads_equal":previous["sources"]==current["sources"],
            "prior_capture":previous["capture_utc"],
            "current_capture":current["capture_utc"],
            "native_failed_delta":after["native_failed_instances"]-before["native_failed_instances"]
                                  if aligned else None,
            "downstream_blocked_delta":after["downstream_unique_blocked"]-before["downstream_unique_blocked"]
                                        if aligned else None,
            "coverage_gain_eligible":None,
            "owner_admission": "HOLD",
            "evidence_note":"STATUS_TREND_ONLY_NOT_MATCHED_COVERAGE_OR_ROOT_CLOSURE"}


def viewer(report, layers, data):
    """Create a real edge-connected, local-only task-instance DAG review surface.

    Node/link identity is immutable source data; no in-browser scheduler,
    network fetch, token, gateway, or status/authority changes are implemented.
    """
    payload=json.dumps({"report":report,"layers":layers,"edges":data["edges"]},
                       separators=(",",":"),ensure_ascii=True).replace("<","\\u003c")
    return """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CODE PURPLE · W33 Operational Mycelium DAG</title>
<style>
:root{color-scheme:dark;font:14px/1.45 system-ui,sans-serif;background:#0d1625;color:#eef5ff}
*{box-sizing:border-box}body{margin:0}header{padding:16px 22px;background:#152239;
border-bottom:1px solid #344b68}h1{font-size:22px;margin:0}
small,.dim{color:#b8c8da}.bar{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}
.tile{flex:1 1 140px;background:#1c2d46;border:1px solid #3b526d;
border-radius:9px;padding:11px}.tile b{font-size:23px;display:block}
main{display:grid;grid-template-columns:minmax(320px,1.25fr) minmax(290px,1fr);
gap:12px;padding:12px}.panel{border:1px solid #344b68;border-radius:10px;
min-width:0;background:#15243b;padding:12px}
h2{font-size:16px;margin:2px 0 8px}
.note{font-size:12px;color:#b8c8da;margin:8px 0 10px}
.legend{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:11px;color:#b8c8da}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:4px}
.viewport{height:505px;max-height:58vh;min-height:330px;overflow:auto;
border:1px solid #344b68;border-radius:8px;position:relative;
background-color:#101c2e;
background-image:radial-gradient(#37516e 0.65px,transparent 0.65px);
background-size:13px 13px}
.canvas{position:relative;width:max-content;min-width:100%;min-height:100%}
.layer-grid{display:grid;grid-auto-flow:column;grid-auto-columns:191px;gap:66px;
position:relative;z-index:2;padding:18px 42px 38px}
.layer{display:flex;flex-direction:column;gap:10px}
.svg-edges{position:absolute;inset:0;z-index:1;pointer-events:none;overflow:visible}
.node{width:191px;min-height:53px;padding:7px 9px;display:flex;
flex-direction:column;align-items:flex-start;gap:2px;text-align:left;
border:1px solid #66829e;border-left:5px solid #8297ac;border-radius:6px;
background:#213451;color:#f0f6ff;cursor:pointer;font:inherit;overflow-wrap:anywhere}
.node strong{font-weight:650;font-size:12px}
.node small{font-size:10px;letter-spacing:.02em}
.node:focus-visible{outline:2px solid white}
.node[aria-pressed=true]{outline:2px solid #ffdc83;box-shadow:0 0 0 4px #f8d07130}
.node.dimmed{opacity:.42}
.SUCCESS_NATIVE{border-left-color:#47c986}.FAILED_NATIVE{border-left-color:#ff6d73}
.UPSTREAM_FAILED_DERIVED{border-left-color:#f4ab55}.READY_PROPOSED{border-left-color:#5dd6e0}
.OWNER_HOLD{border-left-color:#c8a0fd}.RUNNING_NATIVE{border-left-color:#7cb8ff}
p{margin:8px 0 10px}label{display:block;color:#c4d2e0;margin-bottom:5px}
select{width:100%;background:#0c1b2e;border:1px solid #58738f;color:#fff;
padding:8px;border-radius:6px}
table{width:100%;border-collapse:collapse;font-size:12px}
th,td{border-bottom:1px solid #354c67;text-align:left;padding:8px 6px}
th{color:#cce0f7}td{overflow-wrap:anywhere}tr{cursor:pointer}
tbody tr:hover{background:#273d58}.scroll{overflow:auto;max-height:460px}
a{color:#93d6ff}#detail{font-size:12px;overflow-wrap:anywhere;
min-height:95px;display:grid;gap:5px}
footer{padding:12px 22px;color:#bdccdf}
@media(max-width:860px){main{grid-template-columns:1fr}.viewport{height:380px;max-height:none}}
</style></head><body>
<header><h1>CODE PURPLE · Operational Mycelium</h1>
<small>W33 | EXACT-HEAD SELECTED SNAPSHOT | MERGE ADMISSION HOLD | NO DISPATCH</small>
<section class="bar" id="cards"></section></header>
<main><section class="panel"><h2>Operational DAG · state and evidence ancestry</h2>
<div class="legend">
<span><i class="dot" style="background:#47c986"></i>Executed success</span>
<span><i class="dot" style="background:#ff6d73"></i>Primary failure</span>
<span><i class="dot" style="background:#f4ab55"></i>Upstream blocked (derived)</span>
<span><i class="dot" style="background:#5dd6e0"></i>Ready proposal</span>
<span><i class="dot" style="background:#c8a0fd"></i>Owner hold</span>
</div><p class="note">Solid lines require predecessor success; dashed lines are lineage references. Scroll to inspect independent branches.</p>
<div id="graph" class="viewport" aria-label="Scrollable, connected operational DAG">
<div id="canvas" class="canvas"><svg id="edgePaths" class="svg-edges" aria-hidden="true"></svg>
<div id="layerGrid" class="layer-grid"></div></div></div>
<p class="dim note">Select a node to illuminate its incoming/outgoing edges. Orange descendants do not count as additional causal roots.</p>
</section><section class="panel"><h2>Task instances · source-bound readback</h2>
<div class="bar">
<div style="flex:1 1 140px"><label for="state">State</label><select id="state"><option value="">All states</option></select></div>
<div style="flex:1 1 130px"><label for="pool">Pool</label><select id="pool"><option value="">All pools</option></select></div>
</div>
<div class="scroll"><table><thead><tr><th>Task</th><th>State</th><th>Pool</th><th>Provenance</th></tr></thead>
<tbody id="tasks"></tbody></table></div>
<h2>Selected task · first-red lineage</h2><div id="detail" aria-live="polite">Select a graph node or table row to inspect native identity, blocked roots and source URL.</div>
</section></main>
<footer>Read-only source evidence. Queue P95, runner slots, acceptance and coverage remain UNKNOWN until measured by independently bound native receipts.</footer>
<script id="snapshot" type="application/json">"""+payload+"""</script>
<script>
"use strict";
const D=JSON.parse(document.getElementById("snapshot").textContent);
const rows=D.report.task_instances;
const byId=new Map(rows.map(t=>[t.id,t]));
const byElement=new Map();
const edgeElements=[];
const ns="http://www.w3.org/2000/svg";
function el(tag,classname,text){
 const n=document.createElement(tag);
 if(classname)n.className=classname;
 if(text!==undefined)n.textContent=String(text);
 return n;
}
const kpis=[["Task nodes",D.report.graph.nodes],["Typed edges",D.report.graph.edges],
 ["Primary failures",D.report.native_failed_instances],
 ["Downstream blocked",D.report.downstream_unique_blocked],
 ["Queue P95 (s)",D.report.queue_p95_s??"UNKNOWN"],
 ["Runtime P95 (s)",D.report.execution_p95_s??"UNKNOWN"]];
for(const [name,value] of kpis){
 const tile=el("div","tile"),number=el("b","",value);
 tile.append(number,el("small","",name));document.getElementById("cards").append(tile);
}
const grid=document.getElementById("layerGrid");
for(let i=0;i<D.layers.length;i++){
 const col=el("div","layer");
 for(const id of D.layers[i]){
  const item=byId.get(id);
  const btn=el("button","node "+item.state);
  btn.type="button";btn.dataset.id=id;btn.setAttribute("aria-pressed","false");
  btn.title=id+" — "+item.state;
  btn.append(el("strong","",id),el("small","",item.state.replaceAll("_"," ")));
  btn.addEventListener("click",()=>select(item));
  byElement.set(id,btn);col.append(btn);
 }
 grid.append(col);
}
const canvas=document.getElementById("canvas"),svg=document.getElementById("edgePaths");
function drawEdges(){
 const frame=canvas.getBoundingClientRect();
 const width=canvas.scrollWidth,height=canvas.scrollHeight;
 svg.setAttribute("width",width);svg.setAttribute("height",height);
 svg.setAttribute("viewBox","0 0 "+width+" "+height);
 svg.replaceChildren();edgeElements.length=0;
 for(const link of D.edges){
  const a=byElement.get(link.from),b=byElement.get(link.to);
  if(!a||!b)continue;
  const ra=a.getBoundingClientRect(),rb=b.getBoundingClientRect();
  const right=ra.right-frame.left,left=rb.left-frame.left;
  const y1=ra.top-frame.top+ra.height/2,y2=rb.top-frame.top+rb.height/2;
  const bend=Math.max(30,Math.abs(left-right)*.43);
  const p=document.createElementNS(ns,"path");
  p.setAttribute("d","M"+right+" "+y1+" C"+(right+bend)+" "+y1+" "+(left-bend)+" "+y2+" "+left+" "+y2);
  p.setAttribute("fill","none");p.setAttribute("stroke-width","1.7");
  p.setAttribute("stroke-linecap","round");
  p.setAttribute("stroke",link.kind==="REFERENCES"?"#7d92b2":
    byId.get(link.from).state==="FAILED_NATIVE"?"#ff747a":"#69accd");
  if(link.kind==="REFERENCES")p.setAttribute("stroke-dasharray","5 5");
  p.setAttribute("opacity",".7");
  svg.append(p);edgeElements.push({link,path:p});
 }
}
function select(row){
 const near=new Set([row.id]);
 for(const e of D.edges){
  if(e.from===row.id)near.add(e.to);
  if(e.to===row.id)near.add(e.from);
 }
 for(const [id,n] of byElement){
  n.setAttribute("aria-pressed",String(id===row.id));
  n.classList.toggle("dimmed",!near.has(id));
 }
 for(const e of edgeElements){
  const connected=e.link.from===row.id||e.link.to===row.id;
  e.path.setAttribute("opacity",connected?"1":".12");
  e.path.setAttribute("stroke-width",connected?"3.1":"1.2");
 }
 const box=document.getElementById("detail");box.replaceChildren();
 box.append(el("strong","",row.id),el("div","",row.state+" · "+row.evidence_level),
            el("div","",row.native?
              "GitHub run "+row.native.run_id+" / attempt "+row.native.attempt+" / job "+row.native.job_id:
              "Declared dependency / owner action only"),
            el("div","",row.blocked_by.length?
              "Blocked by native first-red task(s): "+row.blocked_by.join(", "):
              "No verified upstream failure for this task"),
            el("div","",row.is_current_owner_head===null?
              "No native source head":("Matches selected owner main: "+row.is_current_owner_head)));
 const url=el("a","","Open native/source evidence");
 url.href=row.source_ref;url.rel="noopener noreferrer";url.target="_blank";
 box.append(url);
}
const state=document.getElementById("state"),pool=document.getElementById("pool");
for(const value of [...new Set(rows.map(r=>r.state))].sort()){
 const op=el("option","",value);op.value=value;state.append(op);
}
for(const value of [...new Set(rows.map(r=>r.pool))].sort()){
 const op=el("option","",value);op.value=value;pool.append(op);
}
function refresh(){
 const body=document.getElementById("tasks");body.replaceChildren();
 for(const row of rows){
  if((state.value&&row.state!==state.value)||(pool.value&&row.pool!==pool.value))continue;
  const tr=el("tr");
  for(const v of [row.id,row.state,row.pool,row.evidence_level])tr.append(el("td","",v));
  tr.tabIndex=0;tr.addEventListener("click",()=>select(row));
  tr.addEventListener("keydown",e=>{if(e.key==="Enter")select(row)});
  body.append(tr);
 }
}
state.addEventListener("change",refresh);pool.addEventListener("change",refresh);
refresh();
requestAnimationFrame(drawEdges);
window.addEventListener("resize",drawEdges);
</script></body></html>
"""



def sipoc(data):
    validate(data)
    return {"schema":"missioncontrol.mycelium.operational_dag.sipoc.v1",
            "rows":[dict(zip(("axis","supplier","input","process","output","consumer"),x))
                    for x in SIPOC],"admission":"HOLD"}


def build(data, out, head, run_id=None, attempt=None, previous=None):
    need(type(head) is str and SHA.fullmatch(head), "CANDIDATE_SHA_REQUIRED")
    need((run_id is None and attempt is None) or
         (type(run_id) is int and run_id > 0 and
          type(attempt) is int and attempt > 0), "PARTIAL_NATIVE_RUN_BINDING")
    m,layers=project(data)
    out.mkdir(parents=True,exist_ok=True)
    files={"W33_TASK_DAG.json":serial({"schema":"missioncontrol.mycelium.operational_dag.graph.v1",
              "layers":layers,"edges":data["edges"],"source_digest":m["source_digest"]}),
           "W33_TASK_METRICS.json":serial(m),
           "W33_SIPOC.json":serial(sipoc(data)),
           "W33_TASK_VIEWER.html":viewer(m,layers,data).encode("utf-8")}
    if previous is not None:
        files["W33_TEMPORAL_DELTA.json"]=serial(compare(previous,data))
    for name,raw in files.items():
        (out/name).write_bytes(raw)
    receipt={"schema":"missioncontrol.mycelium.operational_dag.receipt.v1",
             "candidate_head":head,"run_id":run_id,"attempt":attempt,
             "source_digest":m["source_digest"],"admission":"HOLD",
             "dispatch_enabled":False,"authority_transfer":False,
             "evidence_class":"SELECTED_READ_ONLY_NATIVE_METADATA_PROJECTION",
             "files":{name:digest(raw) for name,raw in sorted(files.items())}}
    (out/"W33_SHA256.json").write_bytes(serial(receipt))
    return receipt


def verify(out, head):
    meta=json.loads((out/"W33_SHA256.json").read_bytes())
    need(meta.get("candidate_head")==head and meta.get("admission")=="HOLD" and
         meta.get("dispatch_enabled") is False and
         meta.get("authority_transfer") is False,"FALSE_RECEIPT_AUTHORITY")
    base={"W33_TASK_DAG.json","W33_TASK_METRICS.json",
          "W33_SIPOC.json","W33_TASK_VIEWER.html"}
    need(set(meta.get("files",{})) in (base,base|{"W33_TEMPORAL_DELTA.json"}),
         "RECEIPT_FILE_POPULATION")
    for name,sha in meta["files"].items():
        need((out/name).is_file() and digest((out/name).read_bytes())==sha,
             "RECEIPT_HASH_DRIFT:"+name)
    metric=json.loads((out/"W33_TASK_METRICS.json").read_bytes())
    need(metric["admission"]=="HOLD" and
         metric["source_digest"]==meta["source_digest"],"METRIC_AUTHORITY_DRIFT")
    return meta


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--head",required=True)
    p.add_argument("--run-id",type=int)
    p.add_argument("--attempt",type=int)
    p.add_argument("--previous",type=Path)
    p.add_argument("--verify-only",action="store_true")
    a=p.parse_args()
    if not a.verify_only:
        data=json.loads(a.input.read_text(encoding="utf-8"))
        prior=json.loads(a.previous.read_text(encoding="utf-8")) if a.previous else None
        build(data,a.out,a.head,a.run_id,a.attempt,previous=prior)
    print(json.dumps(verify(a.out,a.head),sort_keys=True))


if __name__ == "__main__":
    main()
