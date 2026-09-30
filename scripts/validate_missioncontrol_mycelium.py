#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "mission_control" / "mycelium" / "control_manifest.yaml"
GRAPH = ROOT / "mission_control" / "mycelium" / "interaction_graph.json"
PAGES_GRAPH = ROOT / "docs" / "data" / "missioncontrol_interaction_graph.json"
HTML = ROOT / "docs" / "missioncontrol_mycelium.html"
INDEX = ROOT / "docs" / "index.html"
METRICS = ROOT / "mission_control" / "mycelium" / "metrics_snapshot.json"
PAGES_METRICS = ROOT / "docs" / "data" / "missioncontrol_metrics.json"
HISTORY = ROOT / "mission_control" / "mycelium" / "progress_history.json"
LOG_ANALYSIS = ROOT / "mission_control" / "mycelium" / "log_analysis.json"


def validate() -> list[str]:
    errors: list[str] = []
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    pages_graph = json.loads(PAGES_GRAPH.read_text(encoding="utf-8"))
    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    pages_metrics = json.loads(PAGES_METRICS.read_text(encoding="utf-8"))

    if graph != pages_graph:
        errors.append("Pages graph materialization differs from canonical graph")
    if metrics != pages_metrics:
        errors.append("Pages metrics materialization differs from canonical metrics")

    allowed_nodes = set(manifest["graph_contract"]["node_types"])
    allowed_edges = set(manifest["graph_contract"]["edge_types"])
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    ids = [n.get("id") for n in nodes]

    if len(ids) != len(set(ids)):
        errors.append("duplicate graph node id")

    node_ids = set(ids)
    for node in nodes:
        if node.get("type") not in allowed_nodes:
            errors.append(f"unknown node type: {node.get('type')} for {node.get('id')}")
        if not node.get("state"):
            errors.append(f"node without state: {node.get('id')}")

    for node in nodes:
        url = node.get("url")
        if isinstance(url, str) and url.startswith("../"):
            errors.append(f"Pages-unsafe graph URL: {node.get('id')} -> {url}")

    for edge in edges:
        if edge.get("type") not in allowed_edges:
            errors.append(f"unknown edge type: {edge.get('type')}")
        if edge.get("from") not in node_ids or edge.get("to") not in node_ids:
            errors.append(f"orphan edge endpoint: {edge}")

    html = HTML.read_text(encoding="utf-8")
    for panel in manifest["layout"]["panels"]:
        if f'data-panel="{panel["id"]}"' not in html:
            errors.append(f"missing UI panel: {panel['id']}")

    if "../mission_control/" in html:
        errors.append("Pages HTML reaches outside docs tree")
    if "data/missioncontrol_interaction_graph.json" not in html:
        errors.append("Pages HTML is not bound to materialized graph")
    if "missioncontrol_mycelium.html" not in INDEX.read_text(encoding="utf-8"):
        errors.append("Pages index does not link MissionControl Mycelium")

    for required_node in {"codex_bd_queue", "current_next", "user_steer", "epic_cryoplant", "topic_2k_refrigeration", "qps_triage_b", "dow_b_pressure_drop", "repo_cryoplant_project"}:
        if required_node not in node_ids:
            errors.append(f"missing interaction-control node: {required_node}")

    invariant = manifest.get("projection_invariant", {})
    if invariant.get("id") != "THIS_IS_THE_WAY" or invariant.get("one_graph_multiple_projections") is not True:
        errors.append("THIS_IS_THE_WAY projection invariant is not bound")
    if metrics.get("guards", {}).get("same_graph_multiple_projections") is not True:
        errors.append("metrics do not preserve same-graph projection guard")
    if not HISTORY.exists() or not LOG_ANALYSIS.exists():
        errors.append("progress/log control surfaces missing")

    for layout_mode in {"2x3", "3x2", "golden_focus", "single_focus"}:
        if layout_mode not in set(manifest.get("layout", {}).get("selectable_modes", [])):
            errors.append(f"missing selectable layout mode: {layout_mode}")

    for ui_token in {"golden-focus", "single-focus", 'id="focus"', 'id="projection"', 'id="graphFilter"', 'id="edgeInspect"', "CODEX BD queue", "External split-repo router", "THIS IS THE WAY", 'id="metricRows"', 'id="progressRows"'}:
        if ui_token not in html:
            errors.append(f"missing enhanced UI contract token: {ui_token}")

    if manifest.get("authority_transfer") is not False:
        errors.append("authority_transfer must remain false")
    if manifest.get("formal_credit_delta") != 0:
        errors.append("formal_credit_delta must remain zero")
    if manifest.get("engineering_authority") is not False:
        errors.append("CODEX UI must not self-promote engineering authority")

    return errors


if __name__ == "__main__":
    found = validate()
    if found:
        for item in found:
            print(f"ERROR: {item}")
        raise SystemExit(1)
    print("MissionControl Mycelium validation: PASS")
