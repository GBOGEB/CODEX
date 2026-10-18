"""W30 read-only five-lane MYCELIUM fan-in / SIPOC / dependency SPINE.

A reproducible selected-native-evidence overlay; no remote dispatch, admissions,
security waivers, private QPS content or inferred causal closures.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

SCHEMA = "codepurple.mycelium.w30.parallel-fanin.v1"
KINDS = {"ORIGIN", "CANDIDATE", "TEST", "RUNNER", "RECEIPT", "CONSUMER",
         "GATE", "JOB", "FANIN"}
EDGES = {"TRACES_TO", "REQUIRES", "FAN_IN", "GATE_HOLD", "OBSERVED"}
EXECUTABLE = {"TRACES_TO", "REQUIRES", "FAN_IN", "GATE_HOLD", "OBSERVED"}
SHA = re.compile(r"[0-9a-f]{40}\Z")
PATH = re.compile(r"[A-Za-z0-9_.\/-]+\Z")
AXES = ("source_coverage", "adversarial_penetration",
        "cross_module_integration", "platform_runner_reach",
        "causal_defect_detection")
STAGE = {"SETUP": 0, "COMPARATOR_PREFLIGHT": 1,
         "BASELINE_COVERAGE": 2, "MATCHED_COMPARATOR": 3, "FULL_RECEIPT": 4}
SIPOC = (
    ("source_coverage", "ABACUS canonical B0", "Matched source/branch denominator",
     "Pin source and instrumenter, run baseline+expanded", "Matched coverage receipt", "ABACUS B0 owner"),
    ("adversarial_penetration", "ABACUS W29 fault injectors", "Fault-oracle pairs/JUnit identities",
     "Negative, reverse, A-B-A, fail-closed tests", "Detected faults and branch deltas", "MIP reviewer"),
    ("cross_module_integration", "ABACUS/CODEX/QPS owner repos", "Pinned sender+receiver evidence",
     "Verify both sides without authority transfer", "Receiver handshake/DEFER", "CODEX MYCELIUM/QPS owner"),
    ("platform_runner_reach", "GitHub Actions native runners", "OS/Python/source/attempt/job identity",
     "Four cells; separate queue/run/failure evidence", "Cell-specific terminal receipts", "Runner owner"),
    ("causal_defect_detection", "BD/security/engineering owners", "First-red logs + source discriminators",
     "Reproduce, classify, negative retest", "Candidate root and owner HOLD", "Authorized causal-root reviewer"),
)


def require(p, msg):
    if not p:
        raise ValueError(msg)


def serialize(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")


def sha256(value):
    return hashlib.sha256(value).hexdigest()


def ordered_layers(nodes, edges):
    indegree = {n["id"]: 0 for n in nodes}
    nxt = defaultdict(set)
    for edge in edges:
        if edge["kind"] in EXECUTABLE and edge["to"] not in nxt[edge["from"]]:
            nxt[edge["from"]].add(edge["to"])
            indegree[edge["to"]] += 1
    remaining, layers = set(indegree), []
    while remaining:
        ready = sorted(x for x in remaining if indegree[x] == 0)
        require(bool(ready), "SPINE_EXECUTABLE_CYCLE")
        layers.append(ready)
        for node in ready:
            remaining.remove(node)
            for target in nxt[node]:
                indegree[target] -= 1
    return layers


def validate(data):
    require(isinstance(data, dict) and data.get("schema") == SCHEMA, "SCHEMA")
    g = data.get("governance", {})
    require(g.get("merge_admission") == "HOLD" and
            g.get("mutation_enabled") is False and
            g.get("authority_transfer") is False and
            g.get("formal_root_closures") is None and
            g.get("authenticated_dispatch") is None, "UNAUTHORIZED_PROMOTION")
    require(data.get("population") == "SELECTED_NATIVE_JOBS_NOT_FULL_FLEET",
            "OVERCLAIMED_FLEET")
    heads = data.get("source_heads")
    require(isinstance(heads, dict) and
            set(heads) == {"GBOGEB/ABACUS", "GBOGEB/CODEX"} and
            all(type(x) is str and bool(SHA.fullmatch(x)) for x in heads.values()),
            "INVALID_EXACT_MAIN_HEAD")
    lanes = data.get("lanes")
    require(isinstance(lanes, list) and len(lanes) >= 4, "MISSING_PARALLEL_LANES")
    lids = [x.get("id") for x in lanes]
    require(len(set(lids)) == len(lids) and all(type(x) is str and x for x in lids),
            "DUPLICATE_LANE")
    scope_owner = {}
    for lane in lanes:
        require(lane.get("axis") in AXES and
                lane.get("repo") in {"GBOGEB/ABACUS", "GBOGEB/CODEX", "GBOGEB/cryoplant-project"},
                "UNOWNED_LANE")
        require(lane.get("state") in {"CANDIDATE_COMMITTED_UNVERIFIED",
                                      "SOURCE_VERIFIED_NOT_RECEIVER",
                                      "OWNER_ACTION_REQUIRED"},
                "FALSE_LANE_ACCEPTANCE")
        require(lane.get("native_complete") is None and
                lane.get("root_closed") is None and
                lane.get("formal_credit") == 0, "FAKE_COMPLETION")
        require(type(lane.get("origin")) is str and lane["origin"].startswith("https://github.com/"),
                "MISSING_PROTO_ORIGIN")
        require(type(lane.get("source_ref")) is str and lane["source_ref"].startswith("https://github.com/"),
                "MISSING_SOURCE_REF")
        paths = lane.get("changed_paths")
        require(type(paths) is list, "MISSING_CHANGED_PATHS")
        for path in paths:
            require(type(path) is str and path and PATH.fullmatch(path) and
                    not path.startswith("/") and ".." not in Path(path).parts,
                    "UNSAFE_PATH")
            key = (lane["repo"], path.lower())
            require(key not in scope_owner, "WRITER_SCOPE_COLLISION")
            scope_owner[key] = lane["id"]
        require(type(lane.get("acceptance")) is str and lane["acceptance"], "MISSING_ACCEPTANCE")
    obs = data.get("observed_jobs")
    require(isinstance(obs, list) and len(obs) > 0, "NATIVE_DENOMINATOR_UNKNOWN")
    keys = set()
    for row in obs:
        require(row.get("lane") in lids, "ORPHAN_JOB")
        require(type(row.get("run_id")) is int and row["run_id"] > 0
                and type(row.get("job_id")) is int and row["job_id"] > 0
                and type(row.get("attempt")) is int and row["attempt"] > 0,
                "INVALID_NATIVE_ID")
        require(type(row.get("sha")) is str and bool(SHA.fullmatch(row["sha"])),
                "UNPINNED_JOB_HEAD")
        require(row.get("conclusion") in {"success", "failure"} and
                row.get("status") == "completed", "FORGED_TERMINAL_SUCCESS")
        require(type(row.get("cohort")) is str and row["cohort"] and
                type(row.get("cell")) is str and row["cell"], "UNKNOWN_COHORT")
        require(row.get("first_red") is None if row["conclusion"] == "success" else
                type(row.get("first_red")) is str and bool(row["first_red"]),
                "INCONSISTENT_FIRST_RED")
        require(row.get("source_level") == "NATIVE_JOB_STEPS",
                "UNVERIFIED_NATIVE_INPUT")
        key = (row["repo"], row["run_id"], row["attempt"], row["job_id"])
        require(key not in keys, "DUPLICATE_NATIVE_JOB")
        keys.add(key)
        require(row["repo"] in ("GBOGEB/ABACUS", "GBOGEB/CODEX"),
                "NATIVE_PRIVATE_QPS_PROOF_FORBIDDEN")
    for lane in lanes:
        require(type(lane.get("candidate_sha")) is str and
                bool(SHA.fullmatch(lane["candidate_sha"])) if lane["state"] == "CANDIDATE_COMMITTED_UNVERIFIED"
                else lane.get("candidate_sha") is None, "INVALID_CANDIDATE_SHA")
    require(data.get("downstream_owner_gates") ==
            ["ABACUS#1860", "CODEX#977", "QPS#1959"], "GATE_OMISSION")
    return True


def graph(data):
    validate(data)
    nodes = [
        {"id":"spine:fanin","kind":"FANIN","state":"READ_ONLY"},
        {"id":"spine:admission","kind":"GATE","state":"HOLD"},
        {"id":"spine:codex","kind":"CONSUMER","state":"NOT_AUTHORIZED_TO_EXECUTE"},
        {"id":"spine:qps","kind":"CONSUMER","state":"DEFER"},
    ]
    edges = []
    def edge(a,b,k,source,level):
        edges.append({"from":a,"to":b,"kind":k,"source_ref":source,"evidence":level})
    edge("spine:fanin","spine:admission","GATE_HOLD","https://github.com/GBOGEB/ABACUS/issues/1860","DECLARED")
    edge("spine:admission","spine:codex","GATE_HOLD","https://github.com/GBOGEB/CODEX/issues/977","DECLARED")
    edge("spine:admission","spine:qps","GATE_HOLD","https://github.com/GBOGEB/cryoplant-project/issues/1959","DECLARED")
    for lane in data["lanes"]:
        p="lane:"+lane["id"]+":"
        stages=["origin","candidate","tests","native","receipt","consumer"]
        for stage in stages:
            nodes.append({"id":p+stage,"kind":{
                "origin":"ORIGIN","candidate":"CANDIDATE","tests":"TEST",
                "native":"RUNNER","receipt":"RECEIPT","consumer":"CONSUMER"}[stage],
                "owner":lane["repo"],"state":lane["state"],"source_ref":lane["source_ref"]})
        for a,b in zip(stages,stages[1:]):
            edge(p+a,p+b,"REQUIRES",lane["source_ref"],"DECLARED")
        edge(p+"consumer","spine:fanin","FAN_IN",lane["source_ref"],"DECLARED")
        # Native predecessor job observations always trace to the historical
        # origin; they must not prove the unqualified candidate.
        for row in [x for x in data["observed_jobs"] if x["lane"] == lane["id"]]:
            nid="native:"+str(row["job_id"])
            nodes.append({"id":nid,"kind":"JOB","owner":row["repo"],
                          "source_ref":row["source_ref"],"state":row["conclusion"],
                          "sha":row["sha"],"run_id":row["run_id"],
                          "job_id":row["job_id"]})
            edge(nid,p+"origin","OBSERVED",row["source_ref"],"NATIVE_JOB_STEPS")
    ids=[n["id"] for n in nodes]
    require(len(ids)==len(set(ids)), "DUPLICATE_GRAPH_NODE")
    idset=set(ids)
    assert all(e["from"] in idset and e["to"] in idset for e in edges)
    layers=ordered_layers(nodes,edges)
    return {"schema":"codepurple.mycelium.w30.graph.v1",
            "nodes":nodes,"edges":edges,"layers":layers,
            "owner_gate":"HOLD","authority_transfer":False,
            "source_digest":sha256(serialize(data))}


def pressure(g):
    children=defaultdict(set)
    for e in g["edges"]:
        if e["kind"] in EXECUTABLE:
            children[e["from"]].add(e["to"])
    out={}
    for n in g["nodes"]:
        if n["kind"]!="ORIGIN":
            continue
        start=n["id"]
        pending=list(children[start]); seen=set()
        while pending:
            x=pending.pop()
            if x==start or x in seen:
                continue
            seen.add(x)
            pending.extend(children[x]-seen)
        out[start]={"direct_dependents":len(children[start]),
                    "reachable_unique_nodes":len(seen),
                    "affected_ids":sorted(seen),
                    "accepted_causal_unblocks":None}
    return out


def metrics(data, g):
    cohort=defaultdict(list)
    for j in data["observed_jobs"]:
        cohort[j["cohort"]].append(j)
    census=[]
    for name in sorted(cohort):
        entries=cohort[name]
        census.append({"cohort":name,"job_denominator":len(entries),
                       "native_success":sum(j["conclusion"]=="success" for j in entries),
                       "native_failure":sum(j["conclusion"]=="failure" for j in entries),
                       "job_ids":sorted(x["job_id"] for x in entries),
                       "source_sha":list(sorted(set(x["sha"] for x in entries))),
                       "selection":"PINNED_OBSERVED_JOBS_ONLY_NOT_WHOLE_FLEET"})
    lanes=[]
    for lane in data["lanes"]:
        ls=[j for j in data["observed_jobs"] if j["lane"] == lane["id"]]
        red={r["first_red"] for r in ls if r["first_red"] is not None}
        lanes.append({"id":lane["id"],"axis":lane["axis"],"origin":lane["origin"],
                      "changed_files":len(lane["changed_paths"]),
                      "observed_native_job_instances":len(ls),
                      "observed_distinct_first_red_strings":len(red),
                      "observed_failed_cells":len({j["cell"] for j in ls
                                                  if j["conclusion"] == "failure"}),
                      "stage":lane["state"],"candidate_native_success":None,
                      "candidate_native_denominator":None,
                      "formal_root_closures":None,
                      "acceptance":lane["acceptance"]})
    old=cohort.get("AB_W29_N_MINUS_1", [])
    new=cohort.get("AB_W29_N", [])
    by_cell={j["cell"]:j for j in old}
    comparable=len(old)==4 and len(new)==4 and set(by_cell)=={j["cell"] for j in new}
    advanced=(sum(STAGE[j["first_red_stage"]]>STAGE[by_cell[j["cell"]]["first_red_stage"]]
                  for j in new) if comparable else None)
    return {"schema":"codepurple.mycelium.w30.metrics.v1",
            "source_digest":sha256(serialize(data)),
            "reference_graph":{"nodes":len(g["nodes"]),"edges":len(g["edges"]),
                               "dag_layers":len(g["layers"]),
                               "directed_density_pct":round(100*len(g["edges"])/
                                    (len(g["nodes"])*(len(g["nodes"])-1)),4),
                               "downstream_pressure":pressure(g)},
            "independent_cohorts":census,"lanes":lanes,
            "temporal_w29":{"n_minus_1_run":39151512739,
                            "n_run":39154971255,
                            "paired_matrix_cells":4 if comparable else None,
                            "first_red_stage_advanced_cells":advanced,
                            "interpretation":"DESCRIPTIVE_FIRST_RED_DISPLACEMENT_ONLY_NOT_ROOT_CLOSURE"},
            "future":{"n_plus_1_targets":"REQUIRES_TERMINAL_EXACT_CANDIDATE_HEAD",
                      "accepted_root_closures":None,
                      "cross_repo_receiver_pairs":None,
                      "governed_merges":None,
                      "consecutive_comparable_epochs":None},
            "governance":{"admission":"HOLD","authority_transfer":False,
                          "merge_status_not_equivalent_to_admission":True}}


def sipoc(data):
    validate(data)
    return {"schema":"codepurple.mycelium.w30.sipoc.v1",
            "rows":[dict(zip(("axis","supplier","input","process","output","consumer"), row))
                    for row in SIPOC],
            "merge_admission":"HOLD","independent_denominators":True}


def render(report, model):
    rows=[]
    for lane in report["lanes"]:
        rows.append("<tr><td>"+html.escape(lane["id"])+
                    "</td><td>"+html.escape(lane["axis"])+
                    "</td><td>"+str(lane["observed_native_job_instances"])+
                    "</td><td>"+str(lane["observed_failed_cells"])+
                    "</td><td>"+html.escape(lane["stage"])+
                    "</td></tr>")
    SIP=("\n".join("<tr>"+''.join("<td>"+html.escape(str(r[k]))+"</td>" for k in
                        ("axis","supplier","input","process","output","consumer"))+"</tr>"
                  for r in model["rows"]))
    return ("<!doctype html><html lang='en'><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>CODE PURPLE W30 Parallel SPINE</title>"
            "<style>body{font:15px system-ui,sans-serif;margin:auto;max-width:1280px;"
            "padding:24px;background:#101a29;color:#ecf0f6}h1{font-size:26px}"
            "p,small{color:#b4c6d8}.cards{display:grid;grid-template-columns:"
            "repeat(auto-fit,minmax(180px,1fr));gap:12px}article{background:#1b2a3d;"
            "border:1px solid #36506b;border-radius:12px;padding:16px}"
            "b{font-size:27px}table{width:100%;border-collapse:collapse;font-size:13px}"
            "th,td{padding:10px 8px;text-align:left;border-bottom:1px solid #385168}"
            "th{color:#a7cfe2}div.scroll{overflow-x:auto}"
            "</style><h1>CODE PURPLE · Parallel SPINE / SIPOC / DAG W30</h1>"
            "<p>Read-only selected native observations · noncompensating gates · MERGE ADMISSION HOLD</p>"
            "<div class='cards'><article><b>"+str(report["reference_graph"]["nodes"])+
            "</b><p>source-bound graph nodes</p></article>"
            "<article><b>"+str(report["reference_graph"]["edges"])+
            "</b><p>typed graph edges</p></article>"
            "<article><b>"+str(report["reference_graph"]["dag_layers"])+
            "</b><p>executable DAG layers</p></article>"
            "<article><b>"+str(report["temporal_w29"]["first_red_stage_advanced_cells"])+
            "/4</b><p>W29 first-red stage displaced</p></article></div>"
            "<h2>Disjoint execution lanes</h2><div class='scroll'><table><thead>"
            "<tr><th>Lane</th><th>Growth axis</th><th>Historical jobs</th>"
            "<th>Failed unique cells</th><th>Candidate status</th></tr></thead>"
            "<tbody>"+''.join(rows)+"</tbody></table></div>"
            "<h2>Five-row SIPOC</h2><div class='scroll'><table>"
            "<tr><th>Axis</th><th>Supplier</th><th>Input</th><th>Process</th>"
            "<th>Output</th><th>Consumer</th></tr>"+SIP+"</table></div>"
            "<p>Exact heads, native attempts, edge provenance and denominators:"
            " see the linked JSON/DAG bundle. This viewer cannot authorize merges"
            " or cross-repository execution.</p></html>\n")


def build(data, output: Path, *, head, run_id=None, attempt=None):
    require(type(head) is str and bool(SHA.fullmatch(head)), "NOT_PINNED_CANDIDATE")
    for val in (run_id, attempt):
        require(val is None or type(val) is int and val > 0,"BAD_NATIVE_ATTEMPT")
    g=graph(data)
    m=metrics(data,g)
    s=sipoc(data)
    output.mkdir(parents=True,exist_ok=True)
    blobs={"W30_SPINE_GRAPH.json":serialize(g),"W30_SPINE_METRICS.json":serialize(m),
           "W30_SIPOC.json":serialize(s),"W30_VIEWER.html":render(m,s).encode("utf-8")}
    for name, raw in blobs.items():
        (output/name).write_bytes(raw)
    receipt={"schema":"codepurple.mycelium.w30.receipt.v1","head_sha":head,
             "run_id":run_id,"attempt":attempt,"source_digest":sha256(serialize(data)),
             "scope":"SELECTED_NATIVE_NOT_GLOBAL","admission":"HOLD",
             "authority_transfer":False,"dispatch_authorized":False,
             "formal_root_closure":None,
             "files":{name:sha256(raw) for name,raw in sorted(blobs.items())}}
    (output/"W30_SHA256.json").write_bytes(serialize(receipt))
    return receipt


def verify(output: Path, head):
    d=json.loads((output/"W30_SHA256.json").read_bytes())
    require(d.get("head_sha")==head and d.get("admission")=="HOLD" and
            d.get("authority_transfer") is False and
            d.get("dispatch_authorized") is False and
            d.get("formal_root_closure") is None, "FALSE_RECEIPT_AUTHORITY")
    require(set(d.get("files", {})) ==
            {"W30_SPINE_GRAPH.json","W30_SPINE_METRICS.json","W30_SIPOC.json","W30_VIEWER.html"},
            "MISSING_OR_EXTRA_FILES")
    for name, want in d["files"].items():
        require((output/name).is_file() and
                sha256((output/name).read_bytes())==want,"DIGEST_DRIFT:"+name)
    return d


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--head",required=True)
    p.add_argument("--run-id",type=int)
    p.add_argument("--attempt",type=int)
    p.add_argument("--verify-only",action="store_true")
    a=p.parse_args()
    if not a.verify_only:
        build(json.loads(a.input.read_text(encoding="utf-8")),a.out,
              head=a.head,run_id=a.run_id,attempt=a.attempt)
    print(json.dumps(verify(a.out,a.head),sort_keys=True))


if __name__=="__main__":
    main()
