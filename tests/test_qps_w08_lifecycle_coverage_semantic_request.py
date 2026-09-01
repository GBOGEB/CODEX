from pathlib import Path

import json
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "qps_w08_workstream_coverage.schema.json"
REQUEST = ROOT / "feedback" / "qps_w08_lifecycle_coverage_semantic_request.yaml"


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
    item = workstreams["items"]
    assert item["properties"]["authority"]["const"] == "QPS_child"
    assert item["properties"]["credit_allowed"]["const"] is False


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
