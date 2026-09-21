from semantic_substrate.validators import validate_semantic_substrate as v


def test_find_undocumented_terms_flags_missing_semantic_terms():
    declared = {'semantic_governance', 'tuple'}
    scanned = {'semantic_governance', 'semantic_drift_daemon', 'other_token'}

    result = v.find_undocumented_terms(declared, scanned)
    assert result == ['semantic_drift_daemon']


def test_find_undocumented_terms_ignores_non_semantic_tokens():
    declared = {'semantic_governance'}
    scanned = {'semantic_governance', 'runtime_loop', 'tuple_registry'}

    result = v.find_undocumented_terms(declared, scanned)
    assert result == []


def test_keb_semantic_vocabulary_terms_are_declared():
    declared = v.load_declared_terms()
    assert "semantic_change" in declared
    assert "semantic_debt_delta" in declared
