from governance.w84_source_eligibility import REQUIRED, validate


def test_missing_atoms_are_not_semantically_eligible():
    receipt = validate({"atoms": []})
    assert receipt["semantic_provenance_pass"] is False
    assert receipt["required_child_action"] == "REMAIN_SOURCE_RECOVERY"
    assert receipt["engineering_credit_delta"] == 0


def test_exact_source_bound_atoms_pass_without_credit():
    payload = {
        "atoms": [
            {
                "atom_id": atom_id,
                "state": "ACCEPTED_SOURCE_BOUND",
                "source_locator": f"source://{atom_id}",
                "source_sha256": "b" * 64,
            }
            for atom_id in sorted(REQUIRED)
        ]
    }
    receipt = validate(payload)
    assert receipt["semantic_provenance_pass"] is True
    assert receipt["required_child_action"] == "ROUNDTRIP_TO_DOW"
    assert receipt["engineering_credit_delta"] == 0
