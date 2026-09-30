#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "mission_control" / "mycelium" / "interaction_graph.json"
OBS = ROOT / "mission_control" / "mycelium" / "control_observations.json"
OUT = ROOT / "mission_control" / "mycelium" / "metrics_snapshot.json"
PAGES_OUT = ROOT / "docs" / "data" / "missioncontrol_metrics.json"
LOG_ANALYSIS = ROOT / "mission_control" / "mycelium" / "log_analysis.json"
SOURCE_STATUS = ROOT / "mission_control" / "mycelium" / "source_status.json"
PORT_REGISTRY = ROOT / "mission_control" / "mycelium" / "port_registry.json"

STATUS_MEASURED = "MEASURED"
STATUS_DERIVED = "DERIVED_FROM_MEASURED"
STATUS_WITHHELD = "WITHHELD"


def ratio_metric(num: float | None, den: float | None) -> dict[str, Any]:
    if num is None or den in (None, 0):
        return {"status": STATUS_WITHHELD, "value": None}
    return {"status": STATUS_DERIVED, "value": round(100.0 * float(num) / float(den), 2)}


def pressure_metric(inputs: dict[str, Any], weights: dict[str, float]) -> dict[str, Any]:
    normalized = {
        "urgency": inputs.get("urgency"),
        "criticality": inputs.get("criticality"),
        "downstream_blocks": None if inputs.get("downstream_blocks") is None else min(float(inputs["downstream_blocks"]) / 5.0, 1.0),
        "unblock_value": inputs.get("unblock_value"),
        "proof_deficit": inputs.get("proof_deficit"),
        "age": None if inputs.get("age_days") is None else min(float(inputs["age_days"]) / 30.0, 1.0),
    }
    present = {k: float(v) for k, v in normalized.items() if v is not None and k in weights}
    if not present:
        return {"status": STATUS_WITHHELD, "value": None, "coverage": 0.0}
    total_weight = sum(float(weights[k]) for k in present)
    score = sum(present[k] * float(weights[k]) for k in present) / total_weight
    return {
        "status": STATUS_DERIVED,
        "value": round(score * 100.0, 2),
        "coverage": round(len(present) / len(weights), 3),
        "used_inputs": sorted(present),
        "missing_inputs": sorted(set(weights) - set(present)),
    }


def bt_rank(outcomes: list[dict[str, Any]], iterations: int = 100) -> dict[str, Any]:
    if not outcomes:
        return {"status": STATUS_WITHHELD, "reason": "no observed pairwise outcomes", "ranking": []}
    names = sorted({str(x["winner"]) for x in outcomes} | {str(x["loser"]) for x in outcomes})
    idx = {name: i for i, name in enumerate(names)}
    wins = [0.0] * len(names)
    games = [[0.0] * len(names) for _ in names]
    for row in outcomes:
        i, j = idx[str(row["winner"])], idx[str(row["loser"])]
        count = float(row.get("count", 1))
        wins[i] += count
        games[i][j] += count
        games[j][i] += count
    strength = [1.0] * len(names)
    for _ in range(iterations):
        new = strength[:]
        for i in range(len(names)):
            denom = 0.0
            for j in range(len(names)):
                if i == j or games[i][j] == 0:
                    continue
                denom += games[i][j] / max(strength[i] + strength[j], 1e-12)
            new[i] = wins[i] / denom if denom > 0 and wins[i] > 0 else 1e-9
        s = sum(new)
        strength = [v / s for v in new] if s else strength
    ranking = sorted(
        ({"item": names[i], "strength": round(strength[i], 6)} for i in range(len(names))),
        key=lambda x: x["strength"],
        reverse=True,
    )
    return {"status": STATUS_DERIVED, "ranking": ranking}


def pca_projection(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if len(rows) < 3:
        return {"status": STATUS_WITHHELD, "reason": "fewer than 3 complete observations"}
    feature_names = sorted(set.intersection(*(set(r.get("features", {})) for r in rows)))
    if len(feature_names) < 2:
        return {"status": STATUS_WITHHELD, "reason": "fewer than 2 common numeric features"}
    matrix = []
    for row in rows:
        values = [row.get("features", {}).get(k) for k in feature_names]
        if any(v is None or not isinstance(v, (int, float)) for v in values):
            return {"status": STATUS_WITHHELD, "reason": "incomplete numeric feature matrix"}
        matrix.append([float(v) for v in values])
    try:
        import numpy as np
    except Exception:
        return {"status": STATUS_WITHHELD, "reason": "numpy unavailable"}
    x = np.asarray(matrix, dtype=float)
    std = x.std(axis=0, ddof=1)
    if np.any(std == 0):
        return {"status": STATUS_WITHHELD, "reason": "zero-variance feature present"}
    z = (x - x.mean(axis=0)) / std
    cov = np.cov(z, rowvar=False)
    vals, vecs = np.linalg.eigh(cov)
    order = np.argsort(vals)[::-1]
    vals = vals[order]
    vecs = vecs[:, order]
    explained = vals / vals.sum()
    return {
        "status": STATUS_DERIVED,
        "features": feature_names,
        "explained_variance_ratio": [round(float(v), 6) for v in explained.tolist()],
        "components": [[round(float(v), 6) for v in col] for col in vecs.T.tolist()],
        "interpretation_guard": "component order is diagnostic variance, not priority or importance",
    }


def build_snapshot(graph: dict[str, Any], obs: dict[str, Any]) -> dict[str, Any]:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    n, e = len(nodes), len(edges)
    urls = sum(1 for node in nodes if node.get("url"))
    proof_edges = sum(1 for edge in edges if edge.get("type") in {"proves", "validates"})
    blockers = sum(1 for edge in edges if edge.get("type") == "blocks")

    projections: dict[str, dict[str, int]] = {}
    for view in ("engineering", "control", "observability"):
        vnodes = [x for x in nodes if view in x.get("meta", {}).get("views", [])]
        vids = {x["id"] for x in vnodes}
        vedges = [x for x in edges if (view in x.get("views", [])) or (x.get("from") in vids and x.get("to") in vids)]
        projections[view] = {"nodes": len(vnodes), "edges": len(vedges)}

    node_metrics: dict[str, Any] = {}
    weights = obs.get("pressure_weights", {})
    for node_id, record in obs.get("nodes", {}).items():
        metric: dict[str, Any] = {}
        qa = record.get("qa")
        if qa:
            metric["qa"] = ratio_metric(qa.get("passed_required_gates"), qa.get("executed_required_gates"))
            metric["qa"]["evidence"] = qa.get("evidence", [])
        pressure = record.get("pressure_inputs")
        if pressure is not None:
            metric["pressure"] = pressure_metric(pressure, weights)
        metric["maturity"] = record.get("maturity", {"status": STATUS_WITHHELD, "value": None})
        metric["dmaic"] = record.get("dmaic", {"status": STATUS_WITHHELD})
        metric["logs"] = record.get("logs", {"status": STATUS_WITHHELD})
        metric["docking"] = record.get("docking", {"status": STATUS_WITHHELD})
        metric["ports"] = record.get("ports", {"status": STATUS_WITHHELD})

        chi = record.get("code_health_inputs", {})
        keys = ("qa_gate_health", "test_health", "lint_health", "debug_health")
        measured = {k: float(chi[k]) for k in keys if isinstance(chi.get(k), (int, float))}
        if measured:
            metric["code_health"] = {
                "status": STATUS_DERIVED,
                "value": round(sum(measured.values()) / len(measured), 2),
                "coverage": round(len(measured) / len(keys), 3),
                "used_inputs": sorted(measured),
                "missing_inputs": sorted(set(keys) - set(measured)),
            }
        else:
            metric["code_health"] = {"status": STATUS_WITHHELD, "value": None, "inputs": chi}
        node_metrics[node_id] = metric

    return {
        "schema_version": "0.1",
        "snapshot_at": obs.get("snapshot_at"),
        "evidence_policy": obs.get("evidence_policy"),
        "graph": {
            "node_count": n,
            "edge_count": e,
            "density": round(e / (n * (n - 1)), 6) if n > 1 else 0.0,
            "link_coverage_pct": round(100.0 * urls / n, 2) if n else 0.0,
            "proof_edge_count": proof_edges,
            "block_edge_count": blockers,
        },
        "projections": projections,
        "nodes": node_metrics,
        "pca": pca_projection(obs.get("pca_rows", [])),
        "bradley_terry": bt_rank(obs.get("pairwise_outcomes", [])),
        "guards": {
            "same_graph_multiple_projections": True,
            "no_synthetic_scores": True,
            "analytics_create_no_formal_or_engineering_credit": True,
        },
    }


def main() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    obs = json.loads(OBS.read_text(encoding="utf-8"))
    if LOG_ANALYSIS.exists():
        log_analysis = json.loads(LOG_ANALYSIS.read_text(encoding="utf-8"))
        for node_id, summary in log_analysis.get("nodes", {}).items():
            obs.setdefault("nodes", {}).setdefault(node_id, {})["logs"] = summary
    snapshot = build_snapshot(graph, obs)
    if SOURCE_STATUS.exists():
        source_status = json.loads(SOURCE_STATUS.read_text(encoding="utf-8"))
        sources = source_status.get("sources", [])
        fresh = sum(1 for row in sources if str(row.get("status", "")).upper() in {"FRESH", "MEASURED_CHAT_CONNECTOR"})
        if sources:
            snapshot.setdefault("nodes", {}).setdefault("repo_codex", {})["docking"] = {
                "status": STATUS_DERIVED,
                "value": round(100.0 * fresh / len(sources), 2),
                "fresh_sources": fresh,
                "declared_sources": len(sources),
                "basis": "source registry freshness/identity observation",
            }
    if PORT_REGISTRY.exists():
        port_registry = json.loads(PORT_REGISTRY.read_text(encoding="utf-8"))
        ports = [p for p in port_registry.get("ports", []) if p.get("declared")]
        probed = [p for p in ports if str(p.get("probe_status", "")).upper() in {"PASS", "SUCCESS", "GREEN"}]
        snapshot.setdefault("nodes", {}).setdefault("repo_codex", {})["ports"] = (
            {
                "status": STATUS_DERIVED,
                "value": round(100.0 * len(probed) / len(ports), 2),
                "probed_ports": len(probed),
                "declared_ports": len(ports),
            }
            if ports and probed
            else {
                "status": STATUS_WITHHELD,
                "value": None,
                "probed_ports": len(probed),
                "declared_ports": len(ports),
                "reason": "no governed port probe has passed yet",
            }
        )
    payload = json.dumps(snapshot, indent=2, sort_keys=True) + "\n"
    OUT.write_text(payload, encoding="utf-8")
    PAGES_OUT.parent.mkdir(parents=True, exist_ok=True)
    PAGES_OUT.write_text(payload, encoding="utf-8")
    print(f"MissionControl metrics snapshot: {snapshot['graph']['node_count']} nodes / {snapshot['graph']['edge_count']} edges")


if __name__ == "__main__":
    main()
