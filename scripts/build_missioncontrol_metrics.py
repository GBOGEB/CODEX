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


def source_identity_is_measured(row: dict[str, Any]) -> bool:
    """Return True only when an exact source-head identity is actually measured."""
    status = str(row.get("status", "")).upper()
    identity = str(row.get("identity_status", "")).upper()
    return bool(row.get("head_sha")) and (
        identity == STATUS_MEASURED or status == "MEASURED_CHAT_CONNECTOR"
    )


def canonical_number(value: float, digits: int = 2) -> int | float:
    """Round deterministically and collapse integral floats to integers."""
    rounded = round(float(value), digits)
    return int(rounded) if rounded.is_integer() else rounded


def ratio_metric(num: float | None, den: float | None) -> dict[str, Any]:
    if num is None or den in (None, 0):
        return {"status": STATUS_WITHHELD, "value": None}
    return {"status": STATUS_DERIVED, "value": canonical_number(100.0 * float(num) / float(den))}


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
        "value": canonical_number(score * 100.0),
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



def executable_value_census(graph: dict[str, Any]) -> dict[str, Any]:
    """Classify executable graph nodes from explicit graph/runtime evidence only."""
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    candidates = [
        node for node in nodes
        if node.get("type") in {"workflow", "script", "executable", "config"}
    ]
    rows: list[dict[str, Any]] = []
    for node in candidates:
        node_id = node.get("id")
        meta = node.get("meta", {})
        incoming = [edge for edge in edges if edge.get("to") == node_id]
        outgoing = [edge for edge in edges if edge.get("from") == node_id]
        tested = bool(
            meta.get("exact_head_run")
            or meta.get("proof_ref")
            or any(edge.get("type") in {"proves", "validates"} for edge in incoming)
        )
        gm_linked = any(
            edge.get("type") == "contributes_to_gm"
            for edge in incoming + outgoing
        )
        horizontal_linked = any(
            edge.get("type") == "serves_horizontal_mission"
            for edge in incoming + outgoing
        )
        downstream = [
            edge for edge in outgoing
            if edge.get("type") in {"consumes", "feeds", "produces_for"}
        ]
        upstream = [
            edge for edge in incoming
            if edge.get("type") in {"consumes", "feeds", "produces_for"}
        ]
        pipeline_integrated = bool(tested and upstream and downstream)
        value_edges = [
            edge for edge in incoming + outgoing
            if edge.get("type") in {
                "contributes_to_gm", "serves_horizontal_mission",
                "consumes", "feeds", "produces_for",
            }
        ]
        tested_orphan = bool(
            tested
            and not pipeline_integrated
            and not gm_linked
            and not horizontal_linked
            and not downstream
        )
        rows.append({
            "id": node_id,
            "type": node.get("type"),
            "tested": tested,
            "pipeline_integrated": pipeline_integrated,
            "gm_linked": gm_linked,
            "horizontal_linked": horizontal_linked,
            "downstream_consumer_count": len(downstream),
            "value_edge_count": len(value_edges),
            "state": "TESTED_ORPHAN" if tested_orphan else (
                "PIPELINE_INTEGRATED" if pipeline_integrated else
                "TESTED_ONLY" if tested else "WITHHELD"
            ),
        })

    total = len(rows)
    tested_count = sum(row["tested"] for row in rows)
    integrated_count = sum(row["pipeline_integrated"] for row in rows)
    value_linked_count = sum(row["value_edge_count"] > 0 for row in rows)
    gm_count = sum(row["gm_linked"] for row in rows)
    horizontal_count = sum(row["horizontal_linked"] for row in rows)
    orphan_count = sum(row["state"] == "TESTED_ORPHAN" for row in rows)
    return {
        "status": STATUS_DERIVED if total else STATUS_WITHHELD,
        "population": total,
        "classification_basis": (
            "explicit graph edges and exact runtime/proof metadata only; "
            "filenames and labels do not imply consumers or value"
        ),
        "metrics": {
            "TEST_PROOF_COVERAGE": ratio_metric(tested_count, total),
            "PIPELINE_INTEGRATION_COVERAGE": ratio_metric(integrated_count, total),
            "VALUE_EDGE_COVERAGE": ratio_metric(value_linked_count, total),
            "TESTED_ORPHAN_COUNT": {
                "status": STATUS_DERIVED if total else STATUS_WITHHELD,
                "value": orphan_count if total else None,
            },
            "GM_LINK_COVERAGE": ratio_metric(gm_count, total),
            "HORIZONTAL_MISSION_LINK_COVERAGE": ratio_metric(horizontal_count, total),
        },
        "nodes": rows,
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
        if "family_progress" in record:
            metric["family_progress"] = record["family_progress"]
        if "mechanical_progress" in record:
            metric["mechanical_progress"] = record["mechanical_progress"]
        if "campaign" in record:
            metric["campaign"] = record["campaign"]
        if "workers" in record:
            metric["workers"] = record["workers"]

        chi = record.get("code_health_inputs", {})
        keys = ("qa_gate_health", "test_health", "lint_health", "debug_health")
        measured = {k: float(chi[k]) for k in keys if isinstance(chi.get(k), (int, float))}
        if measured:
            metric["code_health"] = {
                "status": STATUS_DERIVED,
                "value": canonical_number(sum(measured.values()) / len(measured)),
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
        "executable_value": executable_value_census(graph),
        "guards": {
            "same_graph_multiple_projections": True,
            "no_synthetic_scores": True,
            "analytics_create_no_formal_or_engineering_credit": True,
        },
    }



def apply_source_status_overlay(
    snapshot: dict[str, Any],
    source_status: dict[str, Any],
) -> None:
    """Overlay newer measured remote-source evidence without provenance loss.

    When source-status reports a genuinely newer measured value, it supersedes
    the stale observation. When the measured value is unchanged, the overlay is
    monotonic: it may add exact source identity/current-head evidence, but it
    must not erase richer governed provenance or reinterpret a slice baseline
    as the historical baseline.
    """
    sources = {
        str(row.get("id")): row
        for row in source_status.get("sources", [])
        if isinstance(row, dict) and row.get("id")
    }
    abacus = sources.get("abacus")
    if not abacus:
        return

    evidence_job = (
        f"ABACUS job {abacus['census_job']}"
        if abacus.get("census_job") is not None
        else None
    )
    evidence_pr = (
        f"#{abacus['census_pr']}"
        if abacus.get("census_pr") is not None
        else None
    )
    census_run = abacus.get("census_workflow_run")

    dab_mech = snapshot.setdefault("nodes", {}).setdefault("dab_mech", {})
    if abacus.get("W293") is not None:
        previous_mechanical = dict(dab_mech.get("mechanical_progress", {}))
        previous_residual = previous_mechanical.get("residual_w293")
        changed_measurement = previous_residual != abacus["W293"]
        if changed_measurement:
            mechanical: dict[str, Any] = {
                "status": STATUS_MEASURED,
                "slice": f"{evidence_pr} census" if evidence_pr else "typed remote census",
            }
        else:
            mechanical = previous_mechanical
            mechanical["status"] = STATUS_MEASURED

        mechanical["residual_w293"] = abacus["W293"]
        mechanical["residual_status"] = abacus.get(
            "w293_postmerge_status", STATUS_MEASURED
        )
        mechanical["repository_total_flake8"] = abacus.get("census_total")
        if evidence_job and (changed_measurement or not mechanical.get("evidence_job")):
            mechanical["evidence_job"] = evidence_job
        if census_run is not None and (
            changed_measurement or mechanical.get("evidence_run") is None
        ):
            mechanical["evidence_run"] = census_run
        if evidence_pr and (changed_measurement or not mechanical.get("evidence_pr")):
            mechanical["evidence_pr"] = evidence_pr
        if abacus.get("census_artifact_id") is not None:
            mechanical["artifact_id"] = abacus["census_artifact_id"]
        if abacus.get("census_artifact_sha256"):
            mechanical["artifact_sha256"] = abacus["census_artifact_sha256"]
        dab_mech["mechanical_progress"] = mechanical

    family_names = (
        "E999", "F821", "F601", "F811",
        "F841", "E722", "E731", "E741",
    )
    measured = {
        family: abacus[family]
        for family in family_names
        if isinstance(abacus.get(family), int)
    }
    if measured:
        dab_hard = snapshot.setdefault("nodes", {}).setdefault("dab_hard", {})
        previous = {
            str(row.get("family")): dict(row)
            for row in dab_hard.get("family_progress", [])
            if isinstance(row, dict) and row.get("family")
        }
        rows: list[dict[str, Any]] = []
        slice_baselines = abacus.get("family_slice_baselines", {})
        pending = {
            str(row.get("family")): row
            for row in abacus.get("pending_independent_lanes", [])
            if isinstance(row, dict) and row.get("family")
        }
        existing_order = [
            str(row.get("family"))
            for row in dab_hard.get("family_progress", [])
            if isinstance(row, dict) and row.get("family") in measured
        ]
        ordered_families = existing_order + [
            family
            for family in family_names
            if family in measured and family not in existing_order
        ]
        for family in ordered_families:
            value = measured[family]
            row = previous.get(family, {"family": family})
            prior_value = row.get("measured_postmerge")
            changed_measurement = prior_value != value

            if isinstance(slice_baselines, dict) and family in slice_baselines:
                slice_baseline = slice_baselines[family]
                if changed_measurement or "baseline" not in row:
                    row["baseline"] = slice_baseline

            row["measured_postmerge"] = value
            row["status"] = STATUS_MEASURED
            if family == "E999" and value > 0 and abacus.get("source_bound_hold"):
                row["state"] = "SOURCE_BOUND_HOLD"
                if changed_measurement or not row.get("note"):
                    row["note"] = (
                        "sole remaining E999 is source-bound: "
                        + str(abacus["source_bound_hold"])
                    )
            elif value == 0:
                row["state"] = "CLOSED"
            else:
                row["state"] = "MEASURED_RESIDUAL"

            pending_row = pending.get(family)
            if pending_row and value > 0:
                row["state"] = f"MEASURED_RESIDUAL_ACTIVE_PR{pending_row.get('pr')}"
                row["active_pr"] = pending_row.get("pr")
                expected = pending_row.get("expected_only")
                if isinstance(expected, dict) and family in expected:
                    row["expected_only"] = expected[family]

            baseline = row.get("baseline")
            if isinstance(baseline, (int, float)):
                row["delta_from_baseline"] = value - baseline

            if evidence_pr:
                if changed_measurement:
                    if row.get("evidence_pr") and row.get("evidence_pr") != evidence_pr:
                        row["repair_evidence_pr"] = row["evidence_pr"]
                    row["measurement_pr"] = evidence_pr
                    if not row.get("evidence_pr"):
                        row["evidence_pr"] = evidence_pr
                elif not row.get("measurement_pr"):
                    row["measurement_pr"] = evidence_pr
            if evidence_job:
                if changed_measurement or not row.get("measurement_job"):
                    row["measurement_job"] = evidence_job
                if changed_measurement or not row.get("evidence_job"):
                    row["evidence_job"] = evidence_job
            rows.append(row)
        dab_hard["family_progress"] = rows

    latest: dict[str, Any] = {
        "source": abacus.get("repository", "GBOGEB/ABACUS"),
        "source_sha": abacus.get("measured_return_source_sha") or abacus.get("head_sha"),
        "current_source_sha": abacus.get("head_sha"),
        "evidence": abacus.get("evidence_ref"),
        "status": abacus.get("w293_postmerge_status", STATUS_MEASURED),
        "census_run": abacus.get("census_workflow_run"),
        "census_job": abacus.get("census_job"),
        "artifact_id": abacus.get("census_artifact_id"),
        "total": abacus.get("census_total"),
    }
    for family in family_names + ("W293",):
        if isinstance(abacus.get(family), int):
            latest[family] = abacus[family]
    pending_lanes = [
        row for row in abacus.get("pending_independent_lanes", [])
        if isinstance(row, dict)
    ]
    if pending_lanes:
        row = pending_lanes[0]
        expected = row.get("expected_only")
        latest["active_unmeasured"] = {
            "pr": row.get("pr"),
            "family": row.get("family"),
            "expected_only": (
                expected.get(row.get("family"))
                if isinstance(expected, dict)
                else expected
            ),
        }
    snapshot["latest_remote_return"] = latest


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
        apply_source_status_overlay(snapshot, source_status)
        sources = source_status.get("sources", [])
        fresh_metadata = sum(
            1
            for row in sources
            if str(row.get("status", "")).upper()
            in {"FRESH", "MEASURED_CHAT_CONNECTOR"}
        )
        measured_identity = sum(1 for row in sources if source_identity_is_measured(row))
        if sources:
            snapshot.setdefault("nodes", {}).setdefault("repo_codex", {})["docking"] = {
                "status": STATUS_DERIVED,
                "value": canonical_number(100.0 * measured_identity / len(sources)),
                "fresh_sources": fresh_metadata,
                "measured_identity_sources": measured_identity,
                "identity_withheld_sources": len(sources) - measured_identity,
                "declared_sources": len(sources),
                "basis": "exact-head identity coverage; repository metadata freshness reported separately",
            }
    if PORT_REGISTRY.exists():
        port_registry = json.loads(PORT_REGISTRY.read_text(encoding="utf-8"))
        ports = [p for p in port_registry.get("ports", []) if p.get("declared")]
        probed = [p for p in ports if str(p.get("probe_status", "")).upper() in {"PASS", "SUCCESS", "GREEN"}]
        snapshot.setdefault("nodes", {}).setdefault("repo_codex", {})["ports"] = (
            {
                "status": STATUS_DERIVED,
                "value": canonical_number(100.0 * len(probed) / len(ports)),
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
    payload = json.dumps(snapshot, indent=2, sort_keys=False) + "\n"
    OUT.write_text(payload, encoding="utf-8")
    PAGES_OUT.parent.mkdir(parents=True, exist_ok=True)
    PAGES_OUT.write_text(payload, encoding="utf-8")
    print(f"MissionControl metrics snapshot: {snapshot['graph']['node_count']} nodes / {snapshot['graph']['edge_count']} edges")


if __name__ == "__main__":
    main()
