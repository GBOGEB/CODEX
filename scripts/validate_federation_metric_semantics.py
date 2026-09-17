#!/usr/bin/env python3
"""Validate the governed semantic status of federation metrics.

This validator deliberately does not invent primitive GETI/PCI formulas. It proves
what current CODEX can support: per-repo scalar presence, deterministic weighted
aggregation, and presentation-only dashboard bands. Primitive semantic promotion
remains forbidden until a separate provenance contract is supplied.
"""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "controls" / "FEDERATION_METRIC_SEMANTICS_v1.json"
ROLLUP_IMPL = ROOT / "src" / "qplant_presentation_engine" / "federation_rollup.py"
DASHBOARD_IMPL = ROOT / "dashboards" / "w008_governance_dashboard.py"
ROLLUP_RECORD = ROOT / "metrics" / "federation" / "federation_rollup.json"


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"Expected JSON object: {path}")
    return payload


def main() -> int:
    contract = _load_json(CONTRACT_PATH)
    rollup_module = _load_module("leg5_federation_rollup", ROLLUP_IMPL)
    dashboard_module = _load_module("leg5_governance_dashboard", DASHBOARD_IMPL)

    expected_metrics = set(rollup_module.SCALAR_METRICS)
    contract_metrics = contract["metrics"]
    assert set(contract_metrics) == expected_metrics

    for metric_name in expected_metrics:
        definition = contract_metrics[metric_name]
        assert definition["current_semantic_status"] == "AGGREGATE_ONLY"
        assert definition["primitive_formula"] is None
        assert definition["primitive_population_contract"] is None
        assert definition["promotion_to_semantically_bound_allowed"] is False
        required = set(definition["required_for_promotion"])
        assert {
            "primitive_definition",
            "accepted_input_population",
            "formula_and_version",
            "source_provenance",
            "range_and_missing_evidence_semantics",
            "executable_regeneration_receipt",
        } <= required

    weights = rollup_module.DEFAULT_WEIGHTS
    members = rollup_module.MEMBERS
    assert math.isclose(sum(weights.values()), 1.0, rel_tol=0.0, abs_tol=1e-9)
    assert set(weights) == set(members)

    repo_metrics: dict[str, dict] = {}
    for member in members:
        path = ROOT / "metrics" / "repo" / f"{member.lower()}_metrics.json"
        payload = _load_json(path)
        metrics = payload.get("metrics", payload)
        assert isinstance(metrics, dict), f"metrics object missing for {member}"
        for metric_name in expected_metrics:
            assert metric_name in metrics, f"{member} missing {metric_name}"
            value = metrics[metric_name]
            assert isinstance(value, (int, float)), f"{member}.{metric_name} not numeric"
        assert 0.0 <= float(metrics["geti"]) <= 1.0
        assert 0.0 <= float(metrics["pci"]) <= 1.0
        repo_metrics[member] = payload

    computed = rollup_module.FederationRollup().aggregate(repo_metrics)
    current_rollup = _load_json(ROLLUP_RECORD)
    recorded = current_rollup.get("aggregated", current_rollup)
    for metric_name in expected_metrics:
        assert math.isclose(
            float(computed[metric_name]),
            float(recorded[metric_name]),
            rel_tol=0.0,
            abs_tol=1e-6,
        ), f"rollup mismatch for {metric_name}"

    bands = contract["dashboard_status_bands"]
    assert bands["semantic_class"] == "PRESENTATION_ONLY"
    assert bands["control_authority"] is False
    assert dashboard_module._federation_status(0.80, 0.80)[0] == "HEALTHY"
    assert dashboard_module._federation_status(0.70, 0.70)[0] == "DEGRADED"
    assert dashboard_module._federation_status(0.69, 0.80)[0] == "CRITICAL"

    receipt = {
        "schema": "federation-metric-semantics-validation/1.0",
        "status": "PASS",
        "semantic_status": {
            metric_name: contract_metrics[metric_name]["current_semantic_status"]
            for metric_name in sorted(expected_metrics)
        },
        "aggregated_values": {
            metric_name: computed[metric_name] for metric_name in sorted(expected_metrics)
        },
        "dashboard_status_bands": "PRESENTATION_ONLY",
        "promotion_to_semantically_bound": "WITHHELD_UNBOUND_PRIMITIVES",
        "formal_credit_delta": 0,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
