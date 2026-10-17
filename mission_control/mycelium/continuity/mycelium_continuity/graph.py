"""MYCELIUM continuity graph: additive, owner-preserving, read-only projections.

A typed universal reference graph may contain cycles. Only SIPOC_DEPENDENCY is
admissible to the executable DAG planner. A DECLARED edge never becomes proof.
"""
from __future__ import annotations
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from typing import Any
import hashlib
import json
import re

SHA = re.compile(r"[0-9a-f]{40}\Z")
KINDS = {"SIPOC_DEPENDENCY", "OWNED_BY", "FEDERATION_BRIDGE", "REFERENCE", "PROOF", "SUPPLIES", "TEMPORAL_SUCCESSOR", "REVERSE_PRESSURE", "PROPOSED_CONSUMER"}
BINDINGS = {"DECLARED", "HISTORICAL", "OBSERVED", "RECEIPT_BOUND", "ACCEPTED"}
LAYERS = {"SIPOC", "FEDERATION", "GOLDEN_THREAD", "BD", "TEMPORAL", "CONTROL", "ATOMS"}
MODES = {"OBSERVE", "NATIVE_PROVE", "MUTATION_PROPOSAL"}


def canonical_bytes(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()


def sha256(data: Any) -> str:
    return hashlib.sha256(canonical_bytes(data)).hexdigest()


def require(test: bool, message: str) -> None:
    if not test:
        raise ValueError(message)


def full_sha(value: str) -> bool:
    return type(value) is str and bool(SHA.fullmatch(value))


def make_node(id: str, title: str, kind: str, layer: str, *, owner: str, source: str, evidence: str = "DECLARED", **kw) -> dict:
    return {"id": id, "title": title, "kind": kind, "layer": layer, "owner": owner, "source": source,
            "evidence": evidence, **kw}


def make_edge(source: str, target: str, kind: str, layer: str, *, binding: str, source_ref: str, **kw) -> dict:
    return {"from": source, "to": target, "kind": kind, "layer": layer, "binding": binding,
            "source_ref": source_ref, **kw}


def validate_graph(g: dict) -> dict:
    require(g.get("schema") == "code-purple.mycelium.graph.v2", "graph schema")
    require(g.get("authority_transfer") is False and g.get("dispatch_authorized") is False, "authority escalation")
    nodes, edges = g.get("nodes"), g.get("edges")
    require(isinstance(nodes, list) and isinstance(edges, list), "missing graph arrays")
    ids = [n.get("id") for n in nodes]
    require(all(type(i) is str and i for i in ids) and len(ids) == len(set(ids)), "duplicate/invalid node")
    ni = {n["id"]: n for n in nodes}
    for node in nodes:
        require(node.get("layer") in LAYERS, "invalid node layer")
        require(node.get("evidence") in BINDINGS, "invalid node evidence")
        require(type(node.get("source")) is str and bool(node["source"]), "orphan node missing source")
        require(type(node.get("owner")) is str and bool(node["owner"]), "node without owner")
        if node.get("source_sha") is not None:
            require(full_sha(node["source_sha"]), "invalid pinned node SHA")
    keys = []
    for e in edges:
        require(e.get("from") in ni and e.get("to") in ni, "dangling graph edge")
        require(e.get("from") != e.get("to"), "self edge")
        require(e.get("kind") in KINDS and e.get("layer") in LAYERS, "untyped graph edge")
        require(e.get("binding") in BINDINGS, "illegal graph proof class")
        require(type(e.get("source_ref")) is str and bool(e["source_ref"]), "edge without provenance")
        if e["binding"] in {"RECEIPT_BOUND", "ACCEPTED"}:
            require(type(e.get("proof_ref")) is str and bool(e["proof_ref"]), "unproven receipt edge")
        if e["binding"] == "ACCEPTED":
            require(e.get("owner_acceptance") is True and type(e.get("reviewer")) is str and bool(e["reviewer"]), "forged acceptance")
        if e["kind"] == "SIPOC_DEPENDENCY":
            require(ni[e["from"]]["kind"] == ni[e["to"]]["kind"] == "SIPOC_INSTANCE", "SIPOC edge must join instances")
        keys.append((e["from"], e["to"], e["kind"], e["layer"]))
    require(len(set(keys)) == len(keys), "duplicate semantic edge")
    # Execution graph must be acyclic; other typed reference layers may cycle.
    schedule = schedule_sipoc(nodes, edges)
    return {"nodes": len(nodes), "edges": len(edges), "sipoc_nodes": len([n for n in nodes if n["kind"] == "SIPOC_INSTANCE"]),
            "sipoc_edges": len([e for e in edges if e["kind"] == "SIPOC_DEPENDENCY"]), "waves": schedule,
            "bindings": dict(Counter(e["binding"] for e in edges))}


def schedule_sipoc(nodes: list[dict], edges: list[dict]) -> list[list[str]]:
    active = {n["id"] for n in nodes if n.get("kind") == "SIPOC_INSTANCE"}
    graph = defaultdict(set)
    indegree = {n: 0 for n in active}
    for e in edges:
        if e.get("kind") != "SIPOC_DEPENDENCY":
            continue
        a, b = e["from"], e["to"]
        require(a in active and b in active, "external SIPOC edge")
        if b not in graph[a]:
            graph[a].add(b)
            indegree[b] += 1
    waves = []
    remaining = set(active)
    while remaining:
        ready = sorted(n for n in remaining if indegree[n] == 0)
        require(bool(ready), "cycle in executable SIPOC DAG")
        waves.append(ready)
        for n in ready:
            remaining.remove(n)
            for child in graph[n]:
                indegree[child] -= 1
    return waves


def components(nodes: list[dict], edges: list[dict], *, bound_only: bool = False) -> list[list[str]]:
    ids = {n["id"] for n in nodes}
    neighbor = {i: set() for i in ids}
    for e in edges:
        if bound_only and e["binding"] not in {"OBSERVED", "RECEIPT_BOUND", "ACCEPTED"}:
            continue
        neighbor[e["from"]].add(e["to"])
        neighbor[e["to"]].add(e["from"])
    groups = []
    unseen = set(ids)
    while unseen:
        start = min(unseen)
        seen, todo = set(), [start]
        while todo:
            n = todo.pop()
            if n in seen: continue
            seen.add(n)
            todo += list(neighbor[n] - seen)
        unseen -= seen
        groups.append(sorted(seen))
    return sorted(groups, key=lambda x: (-len(x), x[0]))


def project_metrics(g: dict, legacy: dict) -> dict:
    s = validate_graph(g)
    legacy_node_ids = {"sipoc:N1:" + x["id"] for x in legacy["instances"]}
    legacy_edges = {("sipoc:N1:" + x["from"], "sipoc:N1:" + x["to"]) for x in legacy["edges"]}
    curr_nodes = {n["id"] for n in g["nodes"]}
    curr_edges = {(e["from"], e["to"]) for e in g["edges"] if e["kind"] == "SIPOC_DEPENDENCY"}
    require(legacy_node_ids <= curr_nodes, "historical SIPOC branch pruned without disposition")
    require(legacy_edges <= curr_edges, "historical SIPOC edge pruned without disposition")
    legacy_prs = {(r["repo"], r["pr"]) for r in legacy["prs"]}
    observed_prs = {(n.get("repository"), n.get("number")) for n in g["nodes"] if n["kind"] == "PR" and n.get("historical")}
    require(legacy_prs <= observed_prs, "historical PR lineage dropped")
    ordered = s["waves"]
    known = {"HISTORICAL", "OBSERVED", "RECEIPT_BOUND", "ACCEPTED"}
    return {"schema":"code-purple.mycelium.metrics.v2", "nodes":s["nodes"], "edges":s["edges"],
            "legacy_sipoc_retention":{"numerator":len(legacy_node_ids),"denominator":len(legacy["instances"])},
            "legacy_edge_retention":{"numerator":len(legacy_edges),"denominator":len(legacy["edges"])},
            "legacy_pr_retention":{"numerator":len(legacy_prs),"denominator":len(legacy_prs)},
            "node_growth_vs_n1":s["nodes"] - len(legacy["instances"]),
            "edge_growth_vs_n1":s["edges"] - len(legacy["edges"]),
            "typed_bindings":s["bindings"],"sipoc_waves":ordered,
            "components_all":len(components(g["nodes"],g["edges"])),
            "components_receipt_observed":len(components(g["nodes"],g["edges"],bound_only=True)),
            "scope_defined_node_provenance":{"numerator":sum(bool(n.get("source")) for n in g["nodes"]),"denominator":s["nodes"]},
            "graph_evidence_edge_fraction":{"numerator":sum(e["binding"] in known for e in g["edges"]),"denominator":s["edges"],"scope":"LOCAL_PROJECTION_EDGES_ONLY"},
            "whole_fleet_reach":None,"native_debug_penetration":None,"matched_statistical_uplift":None,
            "accepted_causal_root_closures":None,"eligible_fleet_denominator":None}