from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
VALUE = ROOT / "mission_control" / "mycelium" / "executable_value_contract.yaml"
REX = ROOT / "mission_control" / "mycelium" / "rex_observability_contract.yaml"

def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_executable_value_contract():
    data = load(VALUE)
    assert data["hierarchy"][0] == "GM"
    assert data["dimensions"]["vertical"]["edge"] == "contributes_to_gm"
    assert data["dimensions"]["horizontal"]["edge"] == "serves_horizontal_mission"
    assert data["lifecycle"] == [
        "IMPLEMENT","TEST","PROVE","REGISTER","CONNECT","CONSUME","OBSERVE_VALUE","CONTROL"
    ]
    assert "PIPELINE_INTEGRATION_COVERAGE" in data["metrics"]
    assert "VALUE_EDGE_COVERAGE" in data["metrics"]
    assert data["tested_orphan"]["state"] == "TESTED_ORPHAN"

def test_rex_is_ambient_pre_and_post_execution_control():
    data = load(REX)
    assert data["pre_execution_rex"]["enabled"] is True
    assert data["post_execution_rex"]["enabled"] is True
    assert "LOOKUP_EXACT_SIGNATURE" in data["pre_execution_rex"]["sequence"]
    assert "LOOKUP_SAME_GM" in data["pre_execution_rex"]["sequence"]
    assert "UPDATE_RECURRENCE_CLASS" in data["post_execution_rex"]["sequence"]
    assert "reuse_success_rate" in data["metrics"]["reuse"]
    assert "recurrence_rate_by_signature" in data["metrics"]["recurrence"]
    assert data["ui"]["omnipresent_badge"] is True

def test_improvement_prefers_reuse_before_new():
    data = load(REX)
    order = data["improvement_strategy"]["preferred_order"]
    assert order[0] == "REUSE_EXISTING_CODE_METHOD_PROCESS"
    assert "APPLY_3P_STAR_IF_PRIORITY_OR_PROOF_PATH_NEEDS_REFINEMENT" in order
    assert "APPLY_MIP_IF_MODERNIZE_INNOVATE_PERPETUATE_VALUE_NEEDS_REFINEMENT" in order
    assert "APPLY_DMAIC_IF_MEASURED_PROCESS_GAP_OR_RECURRENCE_REQUIRES_IMPROVEMENT" in order
    assert order[-1] == "CREATE_NEW_ONLY_IF_NO_CONTROLLED_REUSABLE_PATTERN_EXISTS"

def test_rex_graph_edges_cover_reuse_and_missions():
    data = load(REX)
    edges = set(data["graph_edges"])
    required = {
        "learned_from","similar_to","recurs_as","fixed_by","prevented_by","reuses",
        "contributes_to_gm","serves_horizontal_mission"
    }
    assert required <= edges


def test_rex_updates_on_material_execution_and_findings():
    data = load(REX)
    policy = data["update_policy"]
    assert policy["mode"] == "EVENT_DRIVEN_WITH_PERIODIC_ROLLUP"
    triggers = set(policy["immediate_event_triggers"])
    required = {
        "TASK_EXECUTED", "FIRST_RED_OBSERVED", "DEFECT_OR_GAP_DISCOVERED",
        "REPAIR_VERIFIED", "REVIEW_FINDING", "PRIOR_METHOD_REUSED",
        "RECURRENCE_OBSERVED", "CONTROL_ESCAPE_OBSERVED"
    }
    assert required <= triggers
    assert policy["freshness"]["stale_if_material_events_unabsorbed"] is True
    assert policy["provisional_state"]["state"] == "OBSERVED_PENDING_VERIFICATION"
    assert "PR_MERGE" in policy["periodic_rollup"]["triggers"]
