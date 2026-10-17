"""Lossless N1 -> typed N7 MYCELIUM overlay, without source-authority mutation."""
from __future__ import annotations
from collections import Counter
from pathlib import Path
from .graph import make_node, make_edge, validate_graph, project_metrics, full_sha, require

LEGACY_SOURCE = "archive:CODE_PURPLE_MYCELIUM_CONVERGENCE_N1_20261016(1).zip#mesh.json"
REPOS = {
    "GBOGEB/CODEX": "CODEX_UI_GOVERNANCE",
    "GBOGEB/pipeline-automation-hub": "MISSIONCONTROL_FEDERATION",
    "GBOGEB/ABACUS": "ABACUS_SOURCE_OWNER",
    "GBOGEB/cryoplant-project": "QPS_CHILD_ENGINEERING",
    "GBOGEB/gg_MATH": "METHOD_RESEARCH_ONLY",
}
N7_PROCESSES = [
    ("S-N7-FREEZE", "S", "Source freeze and immutable N1 custody", []),
    ("I-N7-VERIFY", "I", "Readback and source/gate classification", ["S-N7-FREEZE"]),
    ("P-N7-AUDIT", "P", "Design intent/value/prune audit", ["I-N7-VERIFY"]),
    ("P-N7-TOPOLOGY", "P", "Typed federation, DAG and SIPOC expansion", ["I-N7-VERIFY"]),
    ("P-N7-GOLDEN", "P", "Golden Thread proof and bitemporal projection", ["I-N7-VERIFY"]),
    ("P-N7-VISUAL", "P", "Read-only six-panel visual testflight", ["I-N7-VERIFY"]),
    ("O-N7-ASSEMBLE", "O", "Lossless continuation ZIP and QA receipts", ["P-N7-AUDIT", "P-N7-TOPOLOGY", "P-N7-GOLDEN", "P-N7-VISUAL"]),
    ("C-N7-HOLD", "C", "Independent acceptance and recursive next pulse", ["O-N7-ASSEMBLE"]),
]


def build_graph(original: dict, observed: dict, verified_native_digest: str | None = None) -> dict:
    require(original.get("schema") == "code-purple.mesh-projection.v1", "N1 input not canonical mesh projection")
    require(original.get("admission") == "HOLD" and original.get("dispatch") == "STAGED_NOT_LAUNCHED", "N1 authority mismatch")
    require(observed.get("schema") == "code-purple.source-readback.v1", "missing source readback")
    require(observed.get("authorization", {}).get("dispatch_authorized") is False, "dispatch would be authorized")
    require(observed["authorization"].get("merge_authorized") is False, "merge would be authorized")
    require(observed["authorization"].get("accepted_causal_root_closures") is None, "false root closure")
    nodes, edges = [], []
    seen = set()

    def n(id, title, kind, layer, *, owner, source, evidence="DECLARED", **kw):
        require(id not in seen, "duplicate node during ingest")
        seen.add(id)
        nodes.append(make_node(id, title, kind, layer, owner=owner, source=source, evidence=evidence, **kw))
        return id

    def e(a,b,kind,layer,*,binding="DECLARED",source_ref=LEGACY_SOURCE,**kw):
        edges.append(make_edge(a,b,kind,layer,binding=binding,source_ref=source_ref,**kw))

    # Source owners are stable identities. GitHub branch heads are observation-specific facts.
    reads = observed.get("repositories", [])
    require(len(reads) == 5 and {r.get("repo") for r in reads} == set(REPOS), "five-repo census mismatch")
    for row in reads:
        require(full_sha(row.get("sha")), "source head is not an exact SHA")
        repo = row["repo"]
        n("repo:"+repo, repo, "REPOSITORY", "FEDERATION",owner=REPOS[repo],source="https://github.com/"+repo,
          evidence="OBSERVED",source_sha=row["sha"],branch=row["branch"],protected=row.get("protected"),
          observed_on=observed["observed_on"])

    # Source contracts are references only, never imported as an alternate SSOT.
    contracts = observed.get("source_contracts", [])
    require(len(contracts)>=6, "missing federation owner contracts")
    for item in contracts:
        key="contract:"+item["authority"]
        owner = item["repository"]
        src = item["path"]
        n(key,item["role"],"CONTRACT","FEDERATION",owner=item["authority"],source=src,
          evidence="OBSERVED" if item.get("verified") == "CONNECTOR_FILE_READBACK" else "DECLARED",
          repository=owner,git_blob_sha=item.get("git_blob_sha"))
        e("repo:"+owner,key,"OWNED_BY","FEDERATION",binding="OBSERVED",source_ref=src)

    # The historical N1 SIPOC graph is byte-for-byte preserved as a branch.
    legacy_ids = [x["id"] for x in original.get("instances", [])]
    require(len(legacy_ids) == 8 and len(set(legacy_ids)) == 8, "N1 8-instance baseline drift")
    for instance in original["instances"]:
        key="sipoc:N1:"+instance["id"]
        owner=instance["repo"]
        n(key,instance["id"]+" | "+instance["incarnation"],"SIPOC_INSTANCE","SIPOC",
          owner=owner,source=LEGACY_SOURCE,evidence="HISTORICAL",legacy_id=instance["id"],
          epoch="N1",role=instance["sipoc_role"],mode=instance["mode"],
          source_sha=instance["source_sha"], root_candidate_not_authoritative=instance.get("root_id"),
          state=instance.get("state"), owner_issue=instance.get("owner_issue"))
        e(key,"repo:"+owner,"OWNED_BY","FEDERATION",binding="HISTORICAL")
    for edge in original["edges"]:
        e("sipoc:N1:"+edge["from"],"sipoc:N1:"+edge["to"],"SIPOC_DEPENDENCY","SIPOC",binding="HISTORICAL")

    # New N7 branch never rewrites N1 dependencies or confuses proposals with execution.
    for id,role,title,deps in N7_PROCESSES:
        n("sipoc:N7:"+id, title, "SIPOC_INSTANCE", "SIPOC",owner="GBOGEB/CODEX",
          source="code-purple.mycelium.continuity.v2", evidence="DECLARED",epoch="N7",role=role,
          mode="OBSERVE",state="PROPOSED_READONLY",max_parallel=3)
        e("sipoc:N7:"+id,"contract:CODEX_UI_GOVERNANCE","OWNED_BY","FEDERATION",
          source_ref="mission_control/mycelium/control_manifest.yaml")
        for dep in deps:
            e("sipoc:N7:"+dep,"sipoc:N7:"+id,"SIPOC_DEPENDENCY","SIPOC",
              source_ref="code-purple.mycelium.continuity.v2")
    e("sipoc:N1:C-ADMISSION","sipoc:N7:S-N7-FREEZE","TEMPORAL_SUCCESSOR","TEMPORAL",
      binding="HISTORICAL",source_ref="original:N1 + N7 declared continuity")

    # Historical PRs are carried forward as historical leaves, not silently refreshed.
    pri = original.get("prs", [])
    require(len(pri) == 22, "legacy 22 PR records unexpectedly missing")
    for row in pri:
        repo = row["repo"]
        key=f"pr:historical:{repo}#{row['pr']}"
        n(key,f"{repo} #{row['pr']} | {row.get('title','historical')}","PR","TEMPORAL",
          owner=repo,source=row.get("url") or LEGACY_SOURCE,evidence="HISTORICAL",historical=True,
          repository=repo,number=row["pr"],source_sha=row["head_sha"],
          historical_state=row.get("state"), snapshot_on=original.get("source_snapshot_date"))
        if repo in REPOS:
            e(key,"repo:"+repo,"OWNED_BY","FEDERATION",binding="HISTORICAL")

    # Canonical CPQ ledger is a remote authority, not a new root register.
    cpq=observed.get("cpq_statuses", [])
    require(len(cpq)==18 and len({c["id"] for c in cpq})==18,"CPQ census mismatch")
    allowed={"ACTIVE","TODO","DONE","UNKNOWN_NEEDS_READER","CONTROL","SUPERSEDED","INVALIDATED"}
    for x in cpq:
        require(x["state"] in allowed,"invalid CPQ lifecycle")
        key="cpq:"+x["id"]
        n(key,x["id"]+" | "+x["state"],"BD_ITEM","BD",owner="MISSIONCONTROL_BD",
          source="mission-control/federation-atlas/CODE_PURPLE_BD_QUEUE_v1.json",evidence="OBSERVED",
          lifecycle=x["state"],canonical_id=x["id"],root_acceptance=None)
        e(key,"contract:MISSIONCONTROL_BD","OWNED_BY","BD",binding="OBSERVED",
          source_ref="mission-control/federation-atlas/CODE_PURPLE_BD_QUEUE_v1.json")
    e("cpq:CPQ-010","cpq:CPQ-013","REFERENCE","BD",binding="OBSERVED",
      source_ref="mission-control/federation-atlas/CODE_PURPLE_BD_QUEUE_v1.json#CPQ-013",relation="DEPENDS_ON")
    e("cpq:CPQ-013","cpq:CPQ-010","REVERSE_PRESSURE","BD",binding="DECLARED",
      source_ref="mission-control/federation-atlas/CPQ_N4_BURNDOWN_CHARTER.md",relation="BLOCKER_RETURN")

    n("gate:P0_ADMISSION","P0 governed admission HOLD","GATE","CONTROL",
      owner="INDEPENDENT_REVIEW_AND_SECURITY",source="https://github.com/GBOGEB/ABACUS/issues/1860",
      evidence="OBSERVED",status="HOLD")
    n("gate:CODEX_MUTATION","CODEX remote mutation disabled","GATE","CONTROL",
      owner="CODEX_EXECUTION_GOVERNANCE",source="mission_control/mycelium/execution_gateway_contract.yaml",
      evidence="OBSERVED",status="DENY")
    n("gate:QPS_ACCEPTANCE","QPS child semantic acceptance independent","GATE","CONTROL",
      owner="QPS_CHILD_ENGINEERING",source="mission-control/golden-thread/GOLDEN_THREAD_ARCHITECTURE_BDQ_v2.yaml",
      evidence="DECLARED",status="DEFER")
    n("gate:REVIEW","Independent reviewer required","GATE","CONTROL",
      owner="INDEPENDENT_REVIEWER",source="https://github.com/GBOGEB/ABACUS/issues/1860",
      evidence="DECLARED",status="HOLD")
    for child in ["contract:ABACUS_BD_LDAB","contract:CODEX_EXECUTION_GOVERNANCE","contract:MISSIONCONTROL_GOLDEN_THREAD"]:
        e(child,"gate:P0_ADMISSION","REFERENCE","CONTROL",binding="DECLARED",
          source_ref=observed["sources"][0])
    e("contract:CODEX_EXECUTION_GOVERNANCE","gate:CODEX_MUTATION","REFERENCE","CONTROL",binding="OBSERVED",
      source_ref="mission_control/mycelium/execution_gateway_contract.yaml")
    e("contract:MISSIONCONTROL_GOLDEN_THREAD","gate:QPS_ACCEPTANCE","FEDERATION_BRIDGE","FEDERATION",
      binding="DECLARED",source_ref="mission-control/golden-thread/GOLDEN_THREAD_ARCHITECTURE_BDQ_v2.yaml")
    e("contract:MISSIONCONTROL_SIPOC","contract:CODEX_UI_GOVERNANCE","FEDERATION_BRIDGE","FEDERATION",
      binding="DECLARED",source_ref="mission-control/gogreen/SIPOC_INSTANCE_DAG.md")
    e("contract:CODEX_UI_GOVERNANCE","contract:MISSIONCONTROL_GOLDEN_THREAD","PROPOSED_CONSUMER","FEDERATION",
      binding="DECLARED",source_ref="mission_control/mycelium/control_manifest.yaml")
    e("contract:MISSIONCONTROL_GOLDEN_THREAD","contract:CODEX_UI_GOVERNANCE","REFERENCE","FEDERATION",
      binding="DECLARED",source_ref="mission-control/golden-thread/README.md")

    for pr in observed.get("pull_requests", []):
        key=f"pr:observed:{pr['repo']}#{pr['number']}"
        require(full_sha(pr["head_sha"]) and full_sha(pr["merge_commit_sha"]),"PR identity missing")
        src=f"https://github.com/{pr['repo']}/pull/{pr['number']}"
        n(key,f"PR #{pr['number']} | {pr['state']}","PR","TEMPORAL",owner=pr["repo"],source=src,
          evidence="OBSERVED",repository=pr["repo"],number=pr["number"],source_sha=pr["head_sha"],
          merged_at=pr["merged_at"],merge_commit_sha=pr["merge_commit_sha"])
        e(key,"repo:"+pr["repo"],"OWNED_BY","FEDERATION",binding="OBSERVED",source_ref=src)
        job=f"run:GitHub:{pr['native_workflow_run_id']}"
        runsrc=f"https://github.com/{pr['repo']}/actions/runs/{pr['native_workflow_run_id']}"
        n(job,f"Native Method Atlas #{pr['native_workflow_run_id']} ({pr['native_workflow_outcome']})",
          "WORKFLOW_RUN","GOLDEN_THREAD",owner=pr["repo"],source=runsrc,
          evidence="OBSERVED",source_sha=pr["head_sha"],conclusion=pr["native_workflow_outcome"])
        e(key,job,"PROOF","GOLDEN_THREAD",binding="OBSERVED",source_ref=runsrc)
        if pr["native_workflow_outcome"] == "failure":
            fail="atom:CPQ-003-NATIVE-RED"
            n(fail,"CPQ-003 browser native first-red","ATOM","ATOMS",owner=pr["repo"],source=runsrc,
              evidence="OBSERVED",status="FAIL",source_sha=pr["head_sha"])
            e(job,fail,"PROOF","GOLDEN_THREAD",binding="OBSERVED",source_ref=runsrc)
            e(fail,"cpq:CPQ-003","REVERSE_PRESSURE","BD",binding="OBSERVED",source_ref=runsrc)
        if pr.get("native_artifact_id"):
            artifact=f"artifact:GitHub:{pr['native_artifact_id']}"
            digest=pr["native_artifact_sha256"]
            require(len(digest)==64 and all(v in "0123456789abcdef" for v in digest),"invalid artifact digest")
            verified=(pr.get('native_artifact_byte_verified') is True and verified_native_digest == digest)
            native_class='RECEIPT_BOUND' if verified else 'OBSERVED'
            edge_class='RECEIPT_BOUND' if verified else 'DECLARED'
            n(artifact,"Native Method Atlas artifact (verified or remote claim)","ARTIFACT","GOLDEN_THREAD",
              owner=pr["repo"],source=runsrc,
              evidence=native_class,artifact_sha256=digest,artifact_id=pr["native_artifact_id"],
              locally_verified=verified,
              source_sha=pr["head_sha"])
            e(job,artifact,"PROOF","GOLDEN_THREAD",binding=edge_class,source_ref=runsrc,
              **({"proof_ref":"sha256:"+digest} if verified else {"relation":"REMOTE_METADATA_DIGEST_ONLY"}))
            e(artifact,"cpq:CPQ-003","SUPPLIES","GOLDEN_THREAD",binding=edge_class,
              source_ref=runsrc,**({"proof_ref":"sha256:"+digest} if verified else {}),relation="TEST_EVIDENCE_NOT_CLOSURE")
            e(artifact,"cpq:CPQ-010","SUPPLIES","GOLDEN_THREAD",binding=edge_class,
              source_ref=runsrc,**({"proof_ref":"sha256:"+digest} if verified else {}),relation="HISTORICAL_REPLAY_NOT_CONTROL")
            e(artifact,"gate:P0_ADMISSION","REFERENCE","CONTROL",binding="DECLARED",source_ref=runsrc)
    # Atomic work/release state: every atom has an explicit owner/consumer and evidence limit.
    atoms = [
      ("atom:N1-ORIGINAL", "Immutable original N1 archive", "HISTORICAL"),
      ("atom:SIPOC-IDENTITY", "N1 to N7 SIPOC identity preservation", "DECLARED"),
      ("atom:CANONICAL-CPQ", "Current 18-row CPQ status readback", "OBSERVED"),
      ("atom:CODEX-DEFAULT-DENY", "CODEX gateway default-deny source contract", "OBSERVED"),
      ("atom:GLOBAL-COVERAGE", "Broad scope coverage denominator UNKNOWN", "DECLARED"),
      ("atom:LLDB-SESSION", "Authentic debugger session receipt UNKNOWN", "DECLARED"),
      ("atom:INDEPENDENT-REVIEW", "Independent approval not obtained", "DECLARED"),
      ("atom:RECURSIVE-NEXT", "Next pulse retains immutable ancestors", "DECLARED"),
    ]
    for id,title,bind in atoms:
        n(id,title,"ATOM","ATOMS",owner="CODEX_UI_GOVERNANCE",source="code-purple.mycelium.continuity.v2",evidence=bind,
          status="UNKNOWN" if "UNKNOWN" in title else "REVIEW")
        e(id,"contract:CODEX_UI_GOVERNANCE","OWNED_BY","FEDERATION",binding="DECLARED",source_ref="mission_control/mycelium/control_manifest.yaml")
    e("atom:CANONICAL-CPQ","cpq:CPQ-010","REFERENCE","BD",binding="OBSERVED",source_ref="mission-control/federation-atlas/CODE_PURPLE_BD_QUEUE_v1.json")
    e("atom:LLDB-SESSION","contract:ABACUS_BD_LDAB","PROPOSED_CONSUMER","GOLDEN_THREAD",source_ref="https://github.com/GBOGEB/ABACUS/issues/1929")
    e("atom:GLOBAL-COVERAGE","gate:P0_ADMISSION","REFERENCE","CONTROL",source_ref="code-purple.mycelium.continuity.v2")
    e("atom:RECURSIVE-NEXT","sipoc:N7:S-N7-FREEZE","REFERENCE","TEMPORAL",source_ref="code-purple.mycelium.continuity.v2")

    g={"schema":"code-purple.mycelium.graph.v2","lineage":"N1_IMMUTABLE_PLUS_N7_READONLY_FEDERATION",
       "authority_transfer":False,"dispatch_authorized":False,"admission":"HOLD",
       "canonical_authority":{"CODEX":"mission_control/mycelium/control_manifest.yaml",
                             "SIPOC":"mission-control/gogreen/sipoc_instances.py",
                             "GOLDEN_THREAD":"mission-control/golden-thread/golden_thread.py",
                             "ABACUS_BD":"https://github.com/GBOGEB/ABACUS/issues/1929",
                             "MC_BD":"mission-control/federation-atlas/CODE_PURPLE_BD_QUEUE_v1.json"},
       "nodes":nodes,"edges":edges,"historical_source":LEGACY_SOURCE,
       "snapshots":{"n1":original.get("source_snapshot_date"),"readback":observed.get("observed_on")}}
    validate_graph(g)
    project_metrics(g,original)
    return g