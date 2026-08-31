#!/usr/bin/env python3
"""Fail-closed validator for the QPS multi-format artifact lineage contract."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import yaml


REQUIRED_OUTPUTS = {"Excel", "HTML", "DOCX", "PPTX", "PDF", "Markdown"}
REQUIRED_CONTROLS = {"content_hash", "semantic_hash", "freshness", "qa_status", "evidence_coverage"}


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def validate_contract(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    build = data.get("build_model", {})
    outputs = build.get("outputs", [])
    output_names = [entry.get("artifact_type") for entry in outputs if isinstance(entry, dict)]
    required_outputs = build.get("required_outputs", [])

    if (
        not isinstance(required_outputs, list)
        or not all(isinstance(value, str) and value for value in required_outputs)
        or set(required_outputs) != REQUIRED_OUTPUTS
        or len(required_outputs) != len(REQUIRED_OUTPUTS)
    ):
        errors.append(f"required_outputs must list each of {sorted(REQUIRED_OUTPUTS)} exactly once")
    if set(output_names) != REQUIRED_OUTPUTS or len(output_names) != len(REQUIRED_OUTPUTS):
        errors.append("outputs must define each required artifact exactly once")
    if build.get("peer_artifacts_may_depend_on_each_other") is not False:
        errors.append("peer artifact dependencies must be disabled")
    shared_parent = build.get("shared_parent")
    for entry in outputs:
        if not isinstance(entry, dict):
            errors.append("each output must be an object")
            continue
        if entry.get("parent") != shared_parent:
            errors.append(f"{entry.get('artifact_type')} must branch from {shared_parent}")
        if set(entry.get("required_controls", [])) != REQUIRED_CONTROLS:
            errors.append(f"{entry.get('artifact_type')} has incomplete output controls")

    baseline = data.get("evidence_baseline", {})
    try:
        rtm = int(baseline.get("rtm_nodes", 0))
        offer = int(baseline.get("offer_nodes", 0))
        edges = int(baseline.get("crosswalk_edges", 0))
        reviewed = int(baseline.get("reviewed_edges", 0))
        reviewed_edge_coverage = float(baseline.get("reviewed_edge_coverage", -1))
    except (TypeError, ValueError):
        errors.append("evidence_baseline numeric fields must be numbers")
        rtm = offer = edges = reviewed = 0
        reviewed_edge_coverage = -1.0
    if not math.isclose(reviewed_edge_coverage, _ratio(reviewed, edges), rel_tol=1e-9):
        errors.append("reviewed_edge_coverage does not match reviewed_edges/crosswalk_edges")

    pca = data.get("pca_screening", {})
    canonical = rtm + offer
    screened = int(pca.get("screened_nodes", 0))
    retained = int(pca.get("retained_pc_count", 0))
    disclosed = int(pca.get("disclosed_dominant_loading_vectors", 0))
    if int(pca.get("canonical_nodes", -1)) != canonical:
        errors.append("PCA canonical_nodes must equal RTM + OFFER nodes")
    if not math.isclose(float(pca.get("node_coverage", -1)), _ratio(screened, canonical), rel_tol=1e-9):
        errors.append("PCA node_coverage is inconsistent")
    if not math.isclose(sum(float(v) for v in pca.get("explained_variance_ratio", {}).values()), 1.0, rel_tol=1e-9):
        errors.append("PCA explained variance ratios must sum to 1")
    if not math.isclose(float(pca.get("dominant_loading_disclosure_coverage", -1)), _ratio(disclosed, retained), rel_tol=1e-9):
        errors.append("dominant loading disclosure coverage is inconsistent")

    gate = data.get("completion_gate", {})
    receipt = gate.get("current_build_receipt")
    coverage = gate.get("binary_release_coverage")
    claim = gate.get("completion_claim_allowed")
    if claim and (not receipt or coverage != 1.0):
        errors.append("completion cannot be claimed without a complete build receipt")
    if not receipt and data.get("status") != "HOLD_PENDING_BUILD_RECEIPT":
        errors.append("missing build receipt requires HOLD_PENDING_BUILD_RECEIPT")
    return errors


def validate_file(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        return ["contract root must be an object"]
    return validate_contract(data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    errors = validate_file(args.path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"PASS: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

