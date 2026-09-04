import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "qps_w08_workstream_coverage.schema.json"
REQUEST = ROOT / "feedback" / "qps_w08_lifecycle_coverage_semantic_request.yaml"
PR_HEAD_AHT = ROOT / "feedback" / "qps_w08_pr_head_aht_control_snapshot.yaml"

EXPECTED_WORKSTREAM_IDS = {
    "W08-REVIEW",
    "W08-COVERAGE",
    "W08-OFFER",
    "W08-ADR-OCD",
    "W08-COST",
    "W08-RAMS",
    "W08-INTERFACES",
    "W08-SUPPORT",
    "W08-3D",
    "W08-SAFETY",
    "W08-CYBER",
    "W08-CONTROLS",
    "W08-EXCLUSIONS",
    "W08-CODES",
    "W08-DELIVERABLES",
    "W08-LIFECYCLE",
    "W08-SPARES-RCM",
}


def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_schema_requires_child_authority_and_no_credit_controls():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["properties"]["document_id"]["const"] == "QPS_W08_WORKSTREAM_COVERAGE_BASELINE"
    assert schema["properties"]["authority"]["const"] == "QPS_child"
    controls = schema["properties"]["controls"]["properties"]
    assert controls["safety_non_compensating"]["const"] is True
    assert controls["no_missing_evidence_zero_imputation"]["const"] is True
    assert controls["no_parent_self_promotion"]["const"] is True
    assert controls["technical_default_rank_separate_from_cost_views"]["const"] is True
    workstreams = schema["properties"]["workstreams"]
    assert workstreams["minItems"] == 17
    assert workstreams["maxItems"] == 17
    assert workstreams["uniqueItems"] is True
    required_ids = {
        rule["contains"]["properties"]["workstream_id"]["const"]
        for rule in workstreams["allOf"]
    }
    assert required_ids == EXPECTED_WORKSTREAM_IDS
    item = workstreams["items"]
    assert item["properties"]["authority"]["const"] == "QPS_child"
    assert item["properties"]["credit_allowed"]["const"] is False
    assert set(item["properties"]["workstream_id"]["enum"]) == EXPECTED_WORKSTREAM_IDS
    assert item["properties"]["name"]["minLength"] == 1
    assert item["properties"]["owner"]["minLength"] == 1
    assert item["properties"]["lifecycle_phase"]["minLength"] == 1
    assert item["properties"]["gap_status"]["enum"] == [
        "BASELINE_PENDING",
        "ZERO_COVERAGE_DECLARED",
        "UNKNOWN_OR_PARTIAL",
        "SOURCE_DISCOVERED",
        "SOURCE_SUPPORTED",
        "PARTIAL_BOUND",
        "VALIDATED_DISPOSITIONED",
        "CLOSED_ACCEPTED",
    ]


def test_semantic_request_is_candidate_only_and_sanitized():
    data = load_yaml(REQUEST)
    controls = data["control_boundary"]
    assert controls["parent_role"] == "candidate_semantic_schema_ci_support_only"
    assert controls["child_authority_required"] is True
    assert controls["confidential_bidder_payload_allowed"] is False
    assert controls["parent_credit_promotion_allowed"] is False
    assert controls["formal_completion_delta"] == 0
    assert controls["bidder_compliance_delta"] == 0
    assert controls["missing_values_zero_imputation_allowed"] is False
    assert data["return_contract"]["sanitized_only"] is True
    assert data["return_contract"]["no_credit_statement_required"] is True


def test_semantic_checks_cover_taxonomy_safety_ranking_and_html_boundary():
    data = load_yaml(REQUEST)
    checks = {row["check_id"] for row in data["semantic_checks"]}
    assert checks == {
        "S01_TAXONOMY_COMPLETENESS",
        "S02_SAFETY_NON_COMPENSATING",
        "S03_NO_ZERO_IMPUTATION",
        "S04_PARENT_CANDIDATE_ONLY",
        "S05_RANK_POPULATION_SEPARATION",
        "S06_REQUIRED_FIELDS",
        "S07_HTML_PRESENTATION_BOUNDARY",
    }
    required = set(data["expected_return_fields"])
    assert {"finding_id", "workstream_id", "check_id", "recommended_child_disposition", "no_credit_statement"} <= required


def test_pr_head_aht_snapshot_embeds_failed_check_threshold():
    snapshot = load_yaml(PR_HEAD_AHT)
    assert snapshot["pull_request"] == "GBOGEB/CODEX#330"
    assert snapshot["head_sha"] == "3479d8926d0c3a64e0ef396126025bbb76937940"
    assert snapshot["status"] == "THRESHOLD_BREACHED"
    assert snapshot["evidence_class"] == "SOURCE-SUPPORTED"
    assert snapshot["threshold_policy"]["threshold_reached"] is True
    assert snapshot["aht_statistics_bridge"]["method"] == "classify_failed_check_threshold"
    assert snapshot["measure"]["failed_checks"] == 5
    assert snapshot["measure"]["blocker_checks"] == 5
    assert snapshot["measure"]["total_decisive_checks"] == 25
    assert snapshot["control"]["completion_credit_allowed"] is False
