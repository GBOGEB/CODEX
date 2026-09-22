import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "federation/qps/W328_BT2_SOURCE_TOLERANCE_KEB_REVIEW.json"


def load_receipt():
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def test_w328_binds_exact_merged_child():
    data = load_receipt()
    assert data["child"]["repository"] == "GBOGEB/cryoplant-project"
    assert data["child"]["pr"] == 1630
    assert data["child"]["exact_head"] == "ce179022b125b862ed5d144e72601c0236af7169"
    assert data["child"]["merge_sha"] == "f0882dec84b6ff8621f778e56f25086263fbd511"


def test_w328_preserves_source_semantics():
    data = load_receipt()["semantic_contract"]
    assert data["population_rule"] == "minimum_not_exact"
    assert data["future_rows"]["allowed"] is True
    assert data["future_rows"]["require_installed_or_future"] == "future"
    assert data["reverse_cumulative"]["recompute_from_per_qcell_rows"] is True
    assert data["flow"]["source_bound_zero_allowed"] is True
    assert data["mass_balance"]["nonzero_residual_requires_source_tolerance"] is True
    assert data["mass_balance"]["tolerance_must_be_finite_nonnegative"] is True
    assert data["mass_balance"]["residual_absolute_value_must_be_within_tolerance"] is True


def test_w328_parent_cannot_promote_child_truth():
    data = load_receipt()
    assert data["authority_transfer"] is False
    assert data["formal_credit_delta"] == 0
    assert data["non_compensation"]["physical_conversion_delta"] == 0
    assert data["return_contract"]["child_disposition_required_for_any_engineering_state_change"] is True
