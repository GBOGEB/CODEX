"""Read-only federated DAG -> existing Mycelium graph contract crosswalk.

Only proposed graph nodes and DECLARED edges are emitted. This adapter never
turns workflow metadata, staged plans or graph paths into RECEIPT_BOUND,
ACCEPTED, worker launch, root closure, or engineering evidence.
"""
from __future__ import annotations

import json
from pathlib import Path

OWNERS = {
    "CODEX": "GBOGEB/CODEX",
    "ABACUS": "GBOGEB/ABACUS",
    "QPS": "GBOGEB/pipeline-automation-hub",
    "CRYO": "GBOGEB/cryoplant-project",
    "FEDERATION": "GBOGEB/CODEX",
}
SHA_FIELDS = {"CODEX", "ABACUS"}


def build(data: dict) -> dict:
    assert data["schema_version"] == "missioncontrol.federated_dag.v1"
    assert data["snapshot"]["mutation_enabled"] is False
    assert data["snapshot"]["P0_admission"] == "HOLD"
    assert data["snapshot"]["first_correctly_admitted_main_merge"] is None
    nodes: list[dict] = []
    ids: set[str] = set()
    for item in data["nodes"]:
        ident = "federated:w1:" + item["id"]
        if ident in ids:
            raise ValueError("duplicate node")
        ids.add(ident)
        nodes.append({
            "id": ident,
            "title": item["label"],
            "kind": "SIPOC_INSTANCE" if any(e["kind"] == "dependency" and item["id"] in (e["from"], e["to"]) for e in data["edges"]) else "REFERENCE",
            "layer": "SIPOC" if any(e["kind"] == "dependency" and item["id"] in (e["from"], e["to"]) for e in data["edges"]) else "FEDERATION",
            "owner": OWNERS[item["repo"]],
            "source": item["url"],
            "evidence": "DECLARED",
            "state": item["state"],
            "authority": "REMOTE" if item["repo"] not in ("CODEX", "FEDERATION") else "LOCAL_PROJECTION",
        })
    edges: list[dict] = []
    for e in data["edges"]:
        kind = {"dependency": "SIPOC_DEPENDENCY",
                "reference": "REFERENCE",
                "feedback": "REVERSE_PRESSURE",
                "evidence": "PROPOSED_CONSUMER"}[e["kind"]]
        edges.append({
            "from": "federated:w1:" + e["from"],
            "to": "federated:w1:" + e["to"],
            "kind": kind,
            "layer": "SIPOC" if kind == "SIPOC_DEPENDENCY" else "FEDERATION",
            "binding": "DECLARED",
            "source_ref": "docs/data/missioncontrol_federated_dag_v1.json",
        })
    return {
        "schema": "code-purple.mycelium.graph.v2",
        "authority_transfer": False,
        "dispatch_authorized": False,
        "nodes": nodes, "edges": edges,
        "crosswalk_class": "DECLARED_DAG_PROJECTION_ONLY",
        "master_dags_canonical_path": None,
        "master_dags_resolution": "UNKNOWN_PENDING_OWNER_CANONICAL_SOURCE",
        "native_rex_receipts_accepted": None,
        "first_admitted_main_merge": None,
        "coverage_delta": None,
        "bd_root_delta": None,
        "external_runtime_qualifier": "mission_control/mycelium/continuity/mycelium_continuity/native_bridge.py",
        "existing_graph_validator": "mission_control/mycelium/continuity/mycelium_continuity/graph.py",
    }


def main() -> None:
    source = Path("docs/data/missioncontrol_federated_dag_v1.json")
    graph = build(json.loads(source.read_text(encoding="utf-8")))
    from mission_control.mycelium.continuity.mycelium_continuity.graph import validate_graph
    report = validate_graph(graph)
    output = Path("artifacts/mc-federated-qa/mycelium-crosswalk.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
