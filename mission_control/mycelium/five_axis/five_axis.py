"""Read-only five-axis growth frontier projection for CODEX MYCELIUM.

Not a new source of truth, native run query, scheduler, root-closure ledger or
merge admission authority. Frozen selected-population snapshots only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

SCHEMA = "codepurple.mycelium.five-axis.snapshot.v1"
AXES = ("source_coverage", "adversarial_penetration", "cross_module_integration",
        "platform_runner_reach", "causal_defect_detection")
KINDS = {"ISSUE", "SOURCE", "PR", "RUN", "CHECK", "FINDING", "GATE", "CONSUMER"}
EDGE_KINDS = {"TRACES_TO", "PROOF", "BLOCKS", "REQUIRES", "REFERENCE"}
ORDER_EDGES = {"TRACES_TO", "PROOF", "BLOCKS", "REQUIRES"}
EVIDENCE = {"SOURCE_REPORTED", "NATIVE_JOB_STEPS", "NATIVE_RUN_METADATA",
            "DECLARED_DEPENDENCY", "NOT_QUALIFIED"}
SHA = re.compile(r"[0-9a-f]{40}\Z")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("utf-8")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def topo(nodes: list[dict], edges: list[dict]) -> list[list[str]]:
    """Cycle-check the ordered dependency projection; references may cycle."""
    ids = {n["id"] for n in nodes}
    incoming = {node: 0 for node in ids}
    downstream = defaultdict(set)
    for e in edges:
        if e["kind"] in ORDER_EDGES and e["to"] not in downstream[e["from"]]:
            downstream[e["from"]].add(e["to"])
            incoming[e["to"]] += 1
    result, left = [], set(ids)
    while left:
        ready = sorted(k for k in left if incoming[k] == 0)
        require(bool(ready), "EXECUTABLE_DAG_CYCLE")
        result.append(ready)
        for item in ready:
            left.remove(item)
            for dependent in downstream[item]:
                incoming[dependent] -= 1
    return result


def _count_pair(metric: dict, ids: set[str]) -> None:
    require(type(metric) is dict, "MISSING_METRIC")
    require(type(metric.get("unit")) is str and bool(metric["unit"]), "MISSING_UNIT")
    n, d = metric.get("numerator"), metric.get("denominator")
    require((n is None) == (d is None), "PARTIAL_DENOMINATOR")
    if n is not None:
        require(type(n) is int and type(d) is int and d > 0 and 0 <= n <= d,
                "FORGED_OR_INVALID_DENOMINATOR")
        require(metric.get("evidence") in ids, "MEASURED_WITHOUT_SOURCE_NODE")
        require(metric.get("evidence_level") in EVIDENCE - {"DECLARED_DEPENDENCY", "NOT_QUALIFIED"},
                "DECLARATION_IS_NOT_MEASUREMENT")
        require(type(metric.get("source_ref")) is str and bool(metric["source_ref"]),
                "MEASURED_WITHOUT_PROOF_REF")
    else:
        require(metric.get("evidence") is None and metric.get("evidence_level") is None,
                "UNKNOWN_WITH_FABRICATED_PROOF")


def validate(data: dict) -> list[list[str]]:
    require(type(data) is dict and data.get("schema") == SCHEMA, "INVALID_SCHEMA")
    guard = data.get("authority", {})
    require(guard.get("merge_admission") == "HOLD" and
            guard.get("mutation_enabled") is False and
            guard.get("authority_transfer") is False and
            guard.get("formal_root_closures") is None,
            "UNAUTHORIZED_PROMOTION")
    require(data.get("population") == "SELECTED_SOURCE_BOUND_PILOT_NOT_FLEET",
            "UNDEFINED_OR_OVERCLAIMED_POPULATION")
    heads = data.get("source_heads")
    require(type(heads) is dict and set(heads) == {"GBOGEB/ABACUS", "GBOGEB/CODEX"},
            "SOURCE_FLEET_IDENTITY")
    for sha in heads.values():
        require(type(sha) is str and bool(SHA.fullmatch(sha)), "INVALID_SOURCE_SHA")
    nodes, edges = data.get("nodes"), data.get("edges")
    require(type(nodes) is list and type(edges) is list and len(nodes) > 0,
            "MISSING_TOPOLOGY")
    ids = [n.get("id") for n in nodes]
    require(all(type(x) is str and x for x in ids) and len(ids) == len(set(ids)),
            "DUPLICATE_OR_INVALID_NODE")
    by_id = {n["id"]: n for n in nodes}
    for n in nodes:
        require(n.get("kind") in KINDS and type(n.get("owner")) is str and n["owner"],
                "UNTYPED_OR_UNOWNED_NODE")
        require(type(n.get("source_ref")) is str and n["source_ref"].startswith("https://github.com/"),
                "UNTRACEABLE_NODE")
        if "sha" in n:
            require(type(n["sha"]) is str and bool(SHA.fullmatch(n["sha"])),
                    "INVALID_NODE_SHA")
    seen = set()
    for e in edges:
        require(e.get("from") in by_id and e.get("to") in by_id and
                e["from"] != e["to"], "DANGLING_OR_SELF_EDGE")
        require(e.get("kind") in EDGE_KINDS and type(e.get("source_ref")) is str and
                e["source_ref"].startswith("https://github.com/"),
                "UNTYPED_OR_UNTRACEABLE_EDGE")
        require(e.get("evidence_level") in EVIDENCE, "UNTYPED_EDGE_EVIDENCE")
        key = (e["from"], e["to"], e["kind"])
        require(key not in seen, "DUPLICATE_EDGE")
        seen.add(key)
        # A declared edge can guide planning but cannot masquerade as a native proof.
        if e["kind"] == "PROOF":
            require(e["evidence_level"] in {"NATIVE_JOB_STEPS", "NATIVE_RUN_METADATA"},
                    "DECLARED_PROOF_EDGE")
    for n in nodes:
        if n["kind"] == "FINDING":
            require(any(e["to"] == n["id"] and e["kind"] == "TRACES_TO" and
                        by_id[e["from"]]["kind"] in {"PR", "ISSUE"} for e in edges),
                    "FINDING_WITHOUT_SOURCE_ORIGIN")
    axes = data.get("axes")
    require(type(axes) is list and [a.get("id") for a in axes] == list(AXES),
            "FIVE_AXIS_CONTRACT")
    for axis in axes:
        require(type(axis.get("question")) is str and bool(axis["question"]),
                "AXIS_WITHOUT_OBJECTIVE")
        _count_pair(axis.get("primary"), set(ids))
        signals = axis.get("signals")
        require(type(signals) is list and len(signals) > 0, "AXIS_WITHOUT_SIGNALS")
        for signal in signals:
            _count_pair(signal, set(ids))
        require(type(axis.get("acceptance")) is str and bool(axis["acceptance"]),
                "AXIS_WITHOUT_ACCEPTANCE")
    return topo(nodes, edges)


def exposure(data: dict, start: str) -> dict:
    """Reach is a declared/observed dependency exposure, not causal proof."""
    successors = defaultdict(set)
    for e in data["edges"]:
        if e["kind"] in {"TRACES_TO", "BLOCKS", "REQUIRES"}:
            successors[e["from"]].add(e["to"])
    seen, pending = set(), list(successors[start])
    while pending:
        x = pending.pop()
        if x in seen or x == start:
            continue
        seen.add(x)
        pending.extend(successors[x] - seen)
    indexed = {n["id"]: n for n in data["nodes"]}
    return {"direct_dependents": len(successors[start]),
            "downstream_unique_nodes": len(seen),
            "downstream_consumer_nodes": sum(indexed[x]["kind"] == "CONSUMER" for x in seen),
            "affected_ids": sorted(seen),
            "causal_credit": None}


def project(data: dict) -> dict:
    waves = validate(data)
    nodes, edges = data["nodes"], data["edges"]
    metrics = []
    for axis in data["axes"]:
        p = axis["primary"]
        entry = {"id": axis["id"], "question": axis["question"],
                 "unit": p["unit"], "numerator": p["numerator"],
                 "denominator": p["denominator"],
                 "percent": None if p["denominator"] is None else
                 round(100 * p["numerator"] / p["denominator"], 4),
                 "state": "UNKNOWN" if p["denominator"] is None else "BOUNDED_NATIVE_OBSERVATION",
                 "signals": axis["signals"], "acceptance": axis["acceptance"]}
        metrics.append(entry)
    return {
        "schema": "codepurple.mycelium.five-axis.metrics.v1",
        "population": data["population"], "source_heads": data["source_heads"],
        "source_digest": digest(canonical(data)), "merge_admission": "HOLD",
        "formal_root_closures": None,
        "axes": metrics,
        "graph": {"nodes": len(nodes), "edges": len(edges),
                  "typed_edge_fraction": {"numerator": len(edges), "denominator": len(edges)},
                  "source_traceable_nodes": {"numerator": sum(bool(n.get("source_ref")) for n in nodes),
                                             "denominator": len(nodes)},
                  "dependency_layers": len(waves),
                  "directed_density_pct": round(100 * len(edges) / (len(nodes)*(len(nodes)-1)), 4)
                  if len(nodes) > 1 else 0,
                  "blocker_pressure": {
                      n["id"]: exposure(data, n["id"]) for n in nodes
                      if n["kind"] in {"ISSUE", "FINDING"}
                  }},
        "comparison_rule": "SAME_SOURCE_SHA_SELECTION_CONFIG_TOOL_ELIGIBLE_DENOMINATOR_ONLY",
        "stability": {"consecutive_comparable_waves": None,
                      "n_plus_one_equals_n_converged": None},
    }


def sipoc(data: dict) -> dict:
    validate(data)
    return {"schema": "codepurple.mycelium.five-axis.sipoc.v1", "admission": "HOLD",
            "rows": [
                {"axis": a["id"], "supplier": "ABACUS/CODEX source-owning CI or owner",
                 "input": a["primary"]["unit"] + " and exact provenance",
                 "process": "Pin -> validate -> compare -> fault inject -> remeasure",
                 "output": "Noncompensating evidence and dependency pressure",
                 "consumer": "CODEX MYCELIUM (read-only); ABACUS/QPS retain authority"}
                for a in data["axes"]]}


def write_bundle(data: dict, out: Path, *, candidate_head: str,
                 run_id: int | None = None, attempt: int | None = None) -> dict:
    require(type(candidate_head) is str and bool(SHA.fullmatch(candidate_head)),
            "CANDIDATE_HEAD_NOT_PINNED")
    for name, value in (("run_id", run_id), ("attempt", attempt)):
        require(value is None or type(value) is int and value > 0,
                "INVALID_" + name.upper())
    metrics = project(data)
    out.mkdir(parents=True, exist_ok=True)
    files = {
        "FIVE_AXIS_METRICS.json": canonical(metrics),
        "FIVE_AXIS_DAG.json": canonical({"schema": "codepurple.mycelium.five-axis.dag.v1",
                                        "nodes": data["nodes"], "edges": data["edges"],
                                        "layers": topo(data["nodes"], data["edges"]),
                                        "admission": "HOLD"}),
        "FIVE_AXIS_SIPOC.json": canonical(sipoc(data)),
    }
    for name, raw in files.items():
        (out / name).write_bytes(raw)
    receipt = {"schema": "codepurple.mycelium.five-axis.sha256.v1",
               "candidate_head": candidate_head,
               "observed_run_id": run_id, "observed_attempt": attempt,
               "snapshot_source_digest": digest(canonical(data)),
               "evidence_class": "READ_ONLY_PROJECTION_NOT_NATIVE_COVERAGE_PROOF",
               "admission": "HOLD", "authority_transfer": False,
               "files": {name: digest(raw) for name, raw in sorted(files.items())}}
    (out / "FIVE_AXIS_SHA256.json").write_bytes(canonical(receipt))
    return receipt


def verify_bundle(out: Path, candidate_head: str) -> dict:
    r = json.loads((out / "FIVE_AXIS_SHA256.json").read_text(encoding="utf-8"))
    require(r.get("candidate_head") == candidate_head and
            r.get("admission") == "HOLD" and r.get("authority_transfer") is False,
            "RECEIPT_IDENTITY_OR_AUTHORITY")
    require(set(r.get("files", {})) ==
            {"FIVE_AXIS_METRICS.json", "FIVE_AXIS_DAG.json", "FIVE_AXIS_SIPOC.json"},
            "MISSING_OR_EXTRA_RECEIPT_FILES")
    for name, expected in r["files"].items():
        require((out / name).is_file() and
                digest((out / name).read_bytes()) == expected,
                "HASH_DRIFT:" + name)
    require(json.loads((out / "FIVE_AXIS_METRICS.json").read_text())["merge_admission"] == "HOLD",
            "METRICS_PROMOTION")
    return r


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--candidate-head", required=True)
    parser.add_argument("--run-id", type=int)
    parser.add_argument("--attempt", type=int)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        write_bundle(data, args.out, candidate_head=args.candidate_head,
                     run_id=args.run_id, attempt=args.attempt)
    print(json.dumps(verify_bundle(args.out, args.candidate_head), sort_keys=True))


if __name__ == "__main__":
    main()
