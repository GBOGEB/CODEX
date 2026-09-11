import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "governance" / "qps_triage" / "KEB_CONTRACT_v1.json"


def _load():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_keb_authority_ceiling_is_fail_closed():
    data = _load()
    authority = data["authority"]
    assert data["repo"] == "GBOGEB/CODEX"
    assert authority["may_mutate_qps_engineering_truth"] is False
    assert authority["may_mutate_qps_compliance"] is False
    assert authority["may_mutate_qps_negotiation"] is False


def test_keb_receipt_requires_exact_execution_identity():
    data = _load()
    required = set(data["required_receipt_fields"])
    assert {"producer_pr", "producer_head_sha", "executed_steps", "result", "receipt_sha256"} <= required
    runtime = data["runtime_gate"]
    assert runtime["pass_requires_executed_steps_gt_zero"] is True
    assert runtime["pass_requires_exact_head_sha"] is True
    assert runtime["pass_requires_receipt_digest"] is True
    assert runtime["merge_is_not_runtime_pass"] is True


def test_keb_has_dow_and_child_reentry_path():
    data = _load()
    surfaces = data["repo_surfaces"]
    assert surfaces["semantic_vocabulary"] == "PIPELINE/GLOSSARY.yaml"
    assert data["predecessor"]["dow_consumer_pr"] == 1107
    assert data["promotion_rule"].startswith("KEB evidence may support")
    assert data["result_enum"] == ["PASS", "FAIL", "DEFER"]


def test_repo_deep_files_exist():
    data = _load()
    for key in ("prompt_sequence", "federation_activity", "semantic_vocabulary", "repo_deep_handoff"):
        assert (ROOT / data["repo_surfaces"][key]).exists(), key
