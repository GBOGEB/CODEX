from semantic_substrate.validators.validate_semantic_substrate import load_declared_terms


TRIAGE_RECEIPT_TERMS = {
    "semantic_checks_pass",
    "semantic_checks_run",
    "semantic_provenance_result",
}


def test_triage_receipt_terms_are_declared():
    declared = load_declared_terms()
    missing = TRIAGE_RECEIPT_TERMS - declared
    assert not missing, f"Undeclared TRIAGE receipt terms: {sorted(missing)}"
