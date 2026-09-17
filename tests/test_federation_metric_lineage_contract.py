"""Currentness tests for the federation metric semantic-lineage contract.

These tests deliberately distinguish arithmetic aggregation from primitive metric
meaning.  A weighted rollup can be numerically reproducible while the upstream
semantic formula that produced each repository scalar remains unbound.
"""
from __future__ import annotations

import json
from pathlib import Path

from src.qplant_presentation_engine.federation_rollup import (
    DEFAULT_WEIGHTS,
    MEMBERS,
    FederationRollup,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "metrics" / "federation" / "federation_metric_lineage_v1.json"
ROLLUP_PATH = ROOT / "metrics" / "federation" / "federation_rollup.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _repo_metrics_from_rollup(rollup: dict) -> dict[str, dict]:
    return {
        row["member"]: {
            "geti": row["geti"],
            "pci": row["pci"],
            "expansion_factor": row["expansion_factor"],
            "forward_pca": {
                "convergence_score": row["forward_pca"],
                "variance_explained": [0, 0, 0, 0, 0],
            },
            "backward_pca": {
                "regression_score": row["backward_pca"],
                "variance_explained": [0, 0, 0, 0, 0],
            },
        }
        for row in rollup["repo_summaries"]
    }


def test_contract_population_matches_runtime_rollup_constants() -> None:
    contract = _load(CONTRACT_PATH)
    population = contract["population"]

    assert population["members"] == list(MEMBERS)
    assert population["weights"] == DEFAULT_WEIGHTS
    assert abs(sum(population["weights"].values()) - 1.0) < 1e-12
    assert population["missing_member_policy"] == "FAIL_CLOSED"


def test_current_scalar_rollup_is_reproducible_from_bound_population() -> None:
    contract = _load(CONTRACT_PATH)
    rollup = _load(ROLLUP_PATH)
    metrics = _repo_metrics_from_rollup(rollup)
    computed = FederationRollup(weights=contract["population"]["weights"]).aggregate(metrics)

    for key in ("geti", "pci", "expansion_factor"):
        assert computed[key] == rollup["aggregated"][key]
        assert contract["metrics"][key]["aggregate_formula_version"] == "federation_rollup.py:v1"
        assert contract["metrics"][key]["current_disposition"] == "AGGREGATE_ONLY"


def test_primitive_semantics_are_explicitly_unbound_not_inferred() -> None:
    contract = _load(CONTRACT_PATH)

    for key in ("geti", "pci", "expansion_factor"):
        metric = contract["metrics"][key]
        assert metric["primitive_semantic_formula"] is None
        assert metric["primitive_semantic_state"] == "UNBOUND_UPSTREAM"
        assert metric["current_disposition"] == "AGGREGATE_ONLY"


def test_dashboard_status_is_display_only_and_fail_closed_for_control_authority() -> None:
    contract = _load(CONTRACT_PATH)
    bands = contract["status_bands"]
    currentness = contract["currentness"]

    assert bands["authority"] == "DISPLAY_DERIVED_ONLY"
    assert bands["missing_or_unbound_semantics_policy"] == "WITHHOLD_STATUS"
    assert currentness["health_status_authority"] == "WITHHELD_UNTIL_PRIMITIVE_SEMANTICS_BOUND"
    assert currentness["primitive_metric_semantics"] == "WITHHELD_UNBOUND_UPSTREAM"
    assert currentness["canonical_gt_credit"] == "NONE"
    assert currentness["runtime_gold_compensation"] is False


def test_contract_cannot_claim_health_authority_while_any_primitive_semantics_unbound() -> None:
    contract = _load(CONTRACT_PATH)
    any_unbound = any(
        metric["primitive_semantic_state"] != "BOUND"
        for metric in contract["metrics"].values()
    )

    assert any_unbound is True
    assert contract["currentness"]["health_status_authority"].startswith("WITHHELD")
    assert contract["status_bands"]["authority"] != "CONTROL_AUTHORITY"
