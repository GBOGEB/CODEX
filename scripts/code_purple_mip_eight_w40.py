"""Read-only CODE PURPLE MIP eight-section appraisal and path-disjoint proposal.

MIP = Modernize / Innovate / Perpetuate (CODEX MIP/README.md).
Measures *only* native evidence supplied in the frozen ledger. Reports a
workflow elapsed-time proxy separately from runner-minute cost. This never
dispatches work, changes GitHub, authenticates QPS, or grants admission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SCHEMA = "codepurple.mip.eight-section-assessment.v1"
OUT_SCHEMA = "codepurple.mip.eight-section-eval.v1"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")
PATH = re.compile(r"[a-zA-Z0-9_.\-/]+\Z")
DECISIONS = {
    "RECONCILE", "SUPERSEDE", "PARK_AND_RESCOUT", "MAINTAIN",
    "HOLD_RELEASE", "DEFER_DISPATCH", "FEDERATION_DEFER", "OWNER_HOLD"
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":")) + "\n").encode()


def path_key(value: object) -> str:
    require(type(value) is str and bool(PATH.fullmatch(value))
            and not value.startswith("/")
            and all(p not in ("", ".", "..") for p in value.split("/")),
            "UNSAFE_OR_AMBIGUOUS_PATH")
    return value.casefold()


def validate(data: object) -> dict:
    require(type(data) is dict and data.get("schema") == SCHEMA, "UNTRUSTED_SCHEMA")
    require(data.get("method", {}).get("expansion")
            == ["Modernize", "Innovate", "Perpetuate"], "MIP_METHOD_DRIFT")
    require(data.get("method", {}).get("qualified_global_dov") == "WITHHELD",
            "MIP_FALSE_DOV")
    g = data.get("governance", {})
    require(g.get("merge_admission") == "HOLD" and g.get("auto_merge") is False
            and g.get("security_waiver") is False
            and g.get("remote_dispatch") is False
            and g.get("formal_root_closures") is None
            and g.get("verified_independent_human_review") is False
            and g.get("blocked_red_canary") is None, "MIP_AUTHORITY_PROMOTION")
    src = data.get("sources", {})
    require(set(src) == {"ABACUS", "CODEX", "QPS"}, "MIP_SOURCE_OWNER")
    for r in ("ABACUS", "CODEX"):
        require(type(src[r].get("main_sha")) is str
                and SHA40.fullmatch(src[r]["main_sha"]), "UNKNOWN_PUBLIC_HEAD")
    require(src["QPS"].get("main_sha") is None
            and src["QPS"].get("owner_receipt") == "DEFER_PRIVATE",
            "PRIVATE_QPS_NOT_PUBLIC")
    sections = data.get("sections")
    require(type(sections) is list and len(sections) == 8
            and sorted(x.get("id") for x in sections) == list(range(1, 9)),
            "EIGHT_SECTION_POPULATION")
    for x in sections:
        require(x.get("decision") in DECISIONS
                and x.get("priority") in {"P0", "P1", "P2"}
                and type(x.get("source_prs")) is list
                and all(type(p) is int and p > 0 for p in x["source_prs"])
                and all(type(x.get(name)) is str and x[name].strip()
                        for name in ("modernize", "innovate", "perpetuate",
                                     "next", "acceptance", "alternate")),
                "MIP_SECTION_INCOMPLETE")
    require(sections[1]["decision"] == "SUPERSEDE"
            and sections[2]["decision"] == "PARK_AND_RESCOUT",
            "NO_DOUBLE_COUNT_PLATEAU")
    n = data.get("native", {})
    w = n.get("source_w38", {})
    require(w.get("repo") == "GBOGEB/ABACUS"
            and w.get("pr") == 2289
            and type(w.get("head")) is str and SHA40.fullmatch(w["head"])
            and type(w.get("source_sha256")) is str
            and SHA64.fullmatch(w["source_sha256"])
            and w.get("result") == "SUCCESS"
            and w.get("admitted") is False
            and w.get("global_main_delta") is None, "W38_NATIVE_SCOPE")
    b, e = w.get("baseline", {}), w.get("expanded", {})
    require(all(type(row.get(k)) is int and row[k] >= 0 for row in (b, e)
                for k in ("branches", "statements", "eligible_branches",
                          "eligible_statements")), "UNMATCHED_SOURCE_DENOMINATORS")
    require(b["eligible_branches"] == e["eligible_branches"] == 36
            and b["eligible_statements"] == e["eligible_statements"] == 97
            and b["branches"] == 21 and e["branches"] == 36
            and b["statements"] == 63 and e["statements"] == 97,
            "W38_MEASURED_INVARIANT")
    require(type(w.get("elapsed_workflow_seconds")) is int
            and w["elapsed_workflow_seconds"] > 0, "UNKNOWN_WORKFLOW_ELAPSED")
    route = n.get("route_w38", {})
    require(route.get("pr") == 2288
            and route.get("actual_route_yield") is None
            and route.get("productive_skip_count") is None,
            "ROUTE_UNPROVEN_SUPPRESSION")
    for key, pr in (("browser_w37", 1115), ("primary_w39", 1117)):
        r = n.get(key, {})
        require(r.get("pr") == pr and r.get("result") == "SUCCESS"
                and type(r.get("head")) is str and SHA40.fullmatch(r["head"]),
                "NATIVE_UI_PROOF_MISSING")
    require(data.get("phase_gates", {}).get("global_admission") == "HOLD"
            and data["phase_gates"].get("perpetuate", "").startswith("WITHHELD"),
            "MIP_GLOBAL_PROMOTION")

    require(data.get("parallel_path_epoch") == "SOURCE_DIFF_READBACK_FROZEN_AS_OF_2026_10_19",
            "UNPINNED_PATH_CENSUS")
    lanes = data.get("parallel_lanes")
    require(type(lanes) is list and len(lanes) >= 4
            and len({l["id"] for l in lanes}) == len(lanes)
            and len({(l["repo"], l["pr"]) for l in lanes}) == len(lanes),
            "INVALID_DISJOINT_LANES")
    for lane in lanes:
        require(lane.get("path_evidence_class") ==
                "FROZEN_GITHUB_PR_CHANGED_FILENAMES_NOT_ACTIVE_LEASE",
                "PATH_SNAPSHOT_NOT_RUNNER_LOCK")
        require(lane.get("repo") in {"GBOGEB/ABACUS", "GBOGEB/CODEX"}
                and type(lane.get("pr")) is int and lane["pr"] > 0,
                "INVALID_LANE_OWNER")
        p = lane.get("paths")
        require(type(p) is list and bool(p)
                and len(set(path_key(x) for x in p)) == len(p),
                "INVALID_LANE_PATHS")

    collisions = []
    for i, a in enumerate(lanes):
        for other in lanes[i+1:]:
            if a["repo"] != other["repo"]:
                continue
            for f in a["paths"]:
                u = path_key(f)
                for gpath in other["paths"]:
                    v = path_key(gpath)
                    if u == v or u.startswith(v+"/") or v.startswith(u+"/"):
                        collisions.append([a["id"], other["id"], f, gpath])
    require(not collisions, "PATH_COLLISION_REQUIRES_SERIALIZATION")
    return data


def evaluate(data: dict, *, candidate_head: str, raw_sha256: str) -> dict:
    validate(data)
    require(type(candidate_head) is str and SHA40.fullmatch(candidate_head),
            "UNPINNED_CANDIDATE_HEAD")
    require(type(raw_sha256) is str and SHA64.fullmatch(raw_sha256),
            "INVALID_SOURCE_RECEIPT")
    w = data["native"]["source_w38"]
    baseline, expanded = w["baseline"], w["expanded"]
    branch_delta = expanded["branches"] - baseline["branches"]
    statement_delta = expanded["statements"] - baseline["statements"]
    proxy = round(60 * branch_delta / w["elapsed_workflow_seconds"], 3)
    decisions = []
    for item in data["sections"]:
        decisions.append({
            "id": item["id"], "priority": item["priority"],
            "decision": item["decision"], "owner": item["owner"],
            "evidence_class": ("EXACT_SHA_LOCAL_MODULE_ONLY"
                               if item["id"] in (2, 3) else
                               "DECLARED_WITH_FROZEN_OWNER_OBSERVATIONS"),
            "automatic_dispatch": False,
        })
    return {
        "schema": OUT_SCHEMA, "candidate_head": candidate_head,
        "source_json_sha256": raw_sha256,
        "mip": ["Modernize", "Innovate", "Perpetuate"],
        "eight_section_denominator": 8,
        "decisions": decisions,
        "measured_existing_source": {
            "distinct_source_files": 1,
            "new_branches": branch_delta,
            "new_statements": statement_delta,
            "branch_ratio_baseline": round(baseline["branches"] / 36, 6),
            "branch_ratio_expanded": round(expanded["branches"] / 36, 6),
            "statement_ratio_baseline": round(baseline["statements"] / 97, 6),
            "statement_ratio_expanded": round(expanded["statements"] / 97, 6),
            "native_workflow_elapsed_seconds": w["elapsed_workflow_seconds"],
            "native_branches_per_workflow_elapsed_minute_proxy": proxy,
            "runner_busy_minutes": None,
            "source_sha256": w["source_sha256"],
            "current_main_global_coverage_delta": None,
            "eligible_causal_root_closure_count": None,
        },
        "source_path_disjoint": True,
        "path_disjoint_evidence_class": "FROZEN_PR_DIFF_NOT_A_LEASE",
        "live_current_pr_diff_verified": False,
        "parallel_lanes_declared": len(data["parallel_lanes"]),
        "actual_free_worker_capacity": None,
        "dispatch_permitted": False,
        "code_purple_merge_admission": "HOLD",
        "mip_programme_dov": "WITHHELD",
        "technical_mip_outcome": "LOCAL_MODERNIZE_AND_INNOVATE_PROVEN_PERPETUATE_UNQUALIFIED",
        "confidence": "MEASURED_LOCAL_AND_DECLARED_CROSS_LANE_NOT_GLOBAL",
        "missing_perpetuate_evidence": [
            "three_distinct_repository_SHA_self_index_receipts",
            "executed_verified_produce_or_self_heal_candidate",
            "effective_repo_branch_rules_plus_human_review_plus_red_canary",
            "authenticated_QPS_owner_receiver_roundtrip"
        ],
        "security_waiver": False,
        "authority_transfer": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, required=True)
    parser.add_argument("--candidate-head", required=True)
    parser.add_argument("--out", type=Path, required=True)
    a = parser.parse_args()
    raw = a.register.read_bytes()
    receipt = evaluate(json.loads(raw), candidate_head=a.candidate_head,
                       raw_sha256=hashlib.sha256(raw).hexdigest())
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_bytes(canonical(receipt))
    print(json.dumps({
        "source_branch_gain": receipt["measured_existing_source"]["new_branches"],
        "source_statement_gain": receipt["measured_existing_source"]["new_statements"],
        "parallel_path_disjoint": receipt["source_path_disjoint"],
        "admission": receipt["code_purple_merge_admission"],
        "mip_dov": receipt["mip_programme_dov"],
    }))


if __name__ == "__main__":
    main()
