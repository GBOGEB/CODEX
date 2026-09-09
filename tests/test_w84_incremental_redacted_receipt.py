from governance.w84_incremental_redacted_receipt import validate


def base_receipt():
    return {
        "child_repo": "GBOGEB/cryoplant-project",
        "child_commit_sha": "a" * 40,
        "atom_id": "LB-02-BFLOW",
        "child_atom_eligible": True,
        "source_locator_present": True,
        "source_sha256_valid": True,
        "child_gate_digest_sha256": "b" * 64,
        "child_package_digest_sha256": "c" * 64,
    }


def test_incremental_redacted_receipt_passes_without_private_data():
    result = validate(base_receipt())
    assert result["incremental_semantic_provenance_pass"] is True
    assert result["required_action"] == "ROUNDTRIP_ATOM_TO_DOW"
    assert result["engineering_credit_delta"] == 0


def test_private_source_fields_fail_closed():
    receipt = base_receipt()
    receipt["source_locator"] = "private.pdf#page=1"
    result = validate(receipt)
    assert result["incremental_semantic_provenance_pass"] is False
    assert result["private_fields_copied"] == ["source_locator"]
