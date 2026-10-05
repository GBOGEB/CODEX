from __future__ import annotations

import json
from collections import defaultdict, deque
from itertools import pairwise
from pathlib import Path
from typing import Any

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
MC = ROOT / "mission_control" / "mycelium"
CONTRACT = MC / "executable_integration_value_contract.yaml"
REGISTRY = MC / "executable_integration_registry.yaml"
SCHEMA = MC / "schemas" / "executable_integration_registry.schema.json"
REPORT = MC / "executable_value_report.json"
PAGES_REPORT = ROOT / "docs" / "data" / "missioncontrol_executable_value_report.json"

REQUIRED_PATH_ROLES = (
    "UPSTREAM_SOURCE",
    "EXECUTABLE_OR_CONFIG",
    "EXECUTION",
    "OUTPUT_OR_EVIDENCE",
    "DOWNSTREAM_CONSUMER",
)
CONSUMER_TYPES = {"CONSUMER", "CONTROL_STATE"}
OUTCOME_TYPES = {"OUTCOME", "CONTROL_STATE", "CONSUMER"}


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a mapping")
    return data


def inventory(contract: dict[str, Any]) -> list[str]:
    migration = contract["migration"]
    extensions = set(migration["extensions"])
    assets: set[str] = set()
    for root_name in migration["census_roots"]:
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in extensions:
                assets.add(path.relative_to(ROOT).as_posix())
    return sorted(assets)


def connected_nodes(registry: dict[str, Any]) -> tuple[dict[str, int], dict[str, int]]:
    incoming: dict[str, int] = defaultdict(int)
    outgoing: dict[str, int] = defaultdict(int)
    for edge in registry.get("edges", []):
        outgoing[edge["from"]] += 1
        incoming[edge["to"]] += 1
    return incoming, outgoing


def reachable(
    start: str,
    adjacency: dict[str, list[tuple[str, dict[str, Any]]]],
    predicate,
) -> bool:
    seen = {start}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for nxt, edge in adjacency.get(current, []):
            if nxt in seen:
                continue
            if predicate(nxt, edge):
                return True
            seen.add(nxt)
            queue.append(nxt)
    return False


def roles_contain_required_sequence(roles: list[str]) -> bool:
    cursor = 0
    for role in roles:
        if cursor < len(REQUIRED_PATH_ROLES) and role == REQUIRED_PATH_ROLES[cursor]:
            cursor += 1
    return cursor == len(REQUIRED_PATH_ROLES)


def path_is_real(
    path: dict[str, Any],
    edges: set[tuple[str, str]],
    node_map: dict[str, dict[str, Any]],
) -> bool:
    nodes = path["nodes"]
    roles = path.get("roles", [])
    if len(nodes) != len(roles):
        return False
    if not roles_contain_required_sequence(roles):
        return False
    if not all((a, b) in edges for a, b in pairwise(nodes)):
        return False
    terminal = node_map.get(nodes[-1], {})
    return roles[-1] == "DOWNSTREAM_CONSUMER" and terminal.get("type") in CONSUMER_TYPES


def validate_registry(
    contract: dict[str, Any], registry: dict[str, Any], schema: dict[str, Any]
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    jsonschema.Draft202012Validator(schema).validate(registry)

    allowed_nodes = set(contract["node_types"])
    allowed_edges = set(contract["edge_types"])
    scopes = contract["value_scopes"]
    nodes = registry["nodes"]
    ids = [node["id"] for node in nodes]
    if len(ids) != len(set(ids)):
        errors.append("duplicate executable node id")
    node_map = {node["id"]: node for node in nodes}
    incoming, outgoing = connected_nodes(registry)

    for node in nodes:
        if node["type"] not in allowed_nodes:
            errors.append(f"unknown executable node type: {node['type']} for {node['id']}")
        if node["value_scope"] not in scopes:
            errors.append(f"unknown value scope: {node['value_scope']} for {node['id']}")
        if not node["tested"]:
            errors.append(f"value scope requires tested=true: {node['id']}")

    edge_pairs: set[tuple[str, str]] = set()
    federation_nodes: set[str] = set()
    adjacency: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    for edge in registry["edges"]:
        if edge["type"] not in allowed_edges:
            errors.append(f"unknown executable edge type: {edge['type']}")
        if edge["from"] not in node_map or edge["to"] not in node_map:
            errors.append(f"orphan executable edge endpoint: {edge}")
            continue
        edge_pairs.add((edge["from"], edge["to"]))
        adjacency[edge["from"]].append((edge["to"], edge))
        if edge["type"] == "FEDERATES" or edge.get("cross_repository"):
            if not edge.get("evidence"):
                errors.append(f"federation edge lacks evidence: {edge['from']}->{edge['to']}")
            federation_nodes.update((edge["from"], edge["to"]))

    executed_path_nodes: set[str] = set()
    invalid_paths: list[str] = []
    for path in registry["integration_paths"]:
        real = path_is_real(path, edge_pairs, node_map)
        if not real:
            invalid_paths.append(path["id"])
            errors.append(
                f"integration path lacks required roles/edges/terminal consumer: {path['id']}"
            )
        if path["executed"]:
            if not real:
                continue
            if not path["evidence"]:
                errors.append(f"executed integration path lacks evidence: {path['id']}")
            else:
                executed_path_nodes.update(path["nodes"])

    tested_orphans: list[str] = []
    library_reference: list[str] = []
    for node in nodes:
        node_id = node["id"]
        edge_count = incoming[node_id] + outgoing[node_id]
        downstream = outgoing[node_id]
        if node["tested"] and edge_count == 0 and downstream == 0:
            if node.get("intentional_no_consumer"):
                library_reference.append(node_id)
            else:
                tested_orphans.append(node_id)
        if node["current_state"] == "PIPELINE_INTEGRATED" and node_id not in executed_path_nodes:
            errors.append(f"PIPELINE_INTEGRATED claim lacks executed traversal: {node_id}")

        rank = scopes[node["value_scope"]]["rank"]
        value_evidence = node.get("value_evidence", [])
        if rank >= 1 and downstream == 0 and node["type"] not in OUTCOME_TYPES:
            errors.append(f"{node['value_scope']} claim lacks downstream edge: {node_id}")
        if rank >= 2:
            if not value_evidence:
                errors.append(f"{node['value_scope']} claim lacks value evidence: {node_id}")
            repo_reachable = reachable(
                node_id,
                adjacency,
                lambda target, edge: bool(edge.get("evidence"))
                and node_map[target].get("outcome_scope") in {
                    "REPOSITORY", "PROJECT", "FEDERATION", "RECURSIVE_CONTROL"
                },
            )
            if not repo_reachable and node.get("outcome_scope") not in {
                "REPOSITORY", "PROJECT", "FEDERATION", "RECURSIVE_CONTROL"
            }:
                errors.append(f"{node['value_scope']} claim lacks evidenced repository outcome path: {node_id}")
        if rank >= 3:
            project_reachable = reachable(
                node_id,
                adjacency,
                lambda target, edge: bool(edge.get("evidence"))
                and node_map[target].get("outcome_scope") in {
                    "PROJECT", "FEDERATION", "RECURSIVE_CONTROL"
                },
            )
            if not project_reachable and node.get("outcome_scope") not in {
                "PROJECT", "FEDERATION", "RECURSIVE_CONTROL"
            }:
                errors.append(f"{node['value_scope']} claim lacks evidenced project outcome path: {node_id}")
        if rank >= 4 and node_id not in federation_nodes:
            errors.append(f"{node['value_scope']} claim lacks federation edge: {node_id}")
        if rank >= 5:
            if not node.get("recursive_control_effect", False):
                errors.append(f"{node['value_scope']} claim lacks recursive control effect: {node_id}")
            control_reachable = reachable(
                node_id,
                adjacency,
                lambda target, edge: bool(edge.get("evidence"))
                and node_map[target].get("outcome_scope") == "RECURSIVE_CONTROL",
            )
            if not control_reachable and node.get("outcome_scope") != "RECURSIVE_CONTROL":
                errors.append(f"{node['value_scope']} claim lacks evidenced recursive control path: {node_id}")

    assets = inventory(contract)
    registered_paths = {node["path"] for node in nodes}
    unregistered = sorted(set(assets) - registered_paths)
    report = {
        "schema_version": "0.2",
        "authority_class": "DERIVED_CONTROL_PROJECTION",
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
        "lifecycle": contract["lifecycle"]["implementation"],
        "recursive_execution_loop": contract["lifecycle"]["recursive_execution"],
        "registered_node_count": len(nodes),
        "registered_edge_count": len(registry["edges"]),
        "declared_integration_path_count": len(registry["integration_paths"]),
        "executed_integration_path_count": sum(
            1 for p in registry["integration_paths"] if p["executed"]
        ),
        "tested_orphans": tested_orphans,
        "library_reference_only": library_reference,
        "inventory": {
            "census_roots": contract["migration"]["census_roots"],
            "asset_count": len(assets),
            "registered_asset_count": len(set(assets) & registered_paths),
            "unregistered_asset_count": len(unregistered),
            "unregistered_assets": unregistered,
            "global_integration_complete": (
                len(unregistered) == 0
                and not tested_orphans
                and not invalid_paths
                and bool(executed_path_nodes)
            ),
        },
        "value_scope_counts": {
            scope: sum(1 for node in nodes if node["value_scope"] == scope)
            for scope in scopes
        },
        "control": {
            "migration_enforcement": contract["migration"]["enforcement"],
            "tested_orphan_queue_required": bool(tested_orphans),
            "registration_debt_queue_required": bool(unregistered),
            "pipeline_integrated_requires_executed_traversal": True,
            "value_claims_require_evidenced_outcome_paths": True,
            "no_authority_transfer": True,
        },
    }
    return errors, report


def main() -> int:
    contract = load_yaml(CONTRACT)
    registry = load_yaml(REGISTRY)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors, report = validate_registry(contract, registry, schema)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    REPORT.write_text(payload, encoding="utf-8")
    PAGES_REPORT.parent.mkdir(parents=True, exist_ok=True)
    PAGES_REPORT.write_text(payload, encoding="utf-8")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "Executable integration/value: "
        f"{report['registered_node_count']} nodes / "
        f"{report['registered_edge_count']} edges / "
        f"{report['inventory']['unregistered_asset_count']} unregistered assets / "
        f"{len(report['tested_orphans'])} tested orphans"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
