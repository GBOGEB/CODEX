from runtime import reconstruct, validate


def fixture():
    tuples = [
        {"id": "TUP-0001", "branch": "root"},
        {"id": "TUP-0002", "branch": "canonical_convergence"},
        {"id": "TUP-0003", "branch": "option_b_overlay_first"},
    ]
    invariants = [
        {"id": "INV-001", "statement": "generated outputs are non-canonical"},
        {"id": "INV-002", "statement": "semantic colours transform by theme"},
    ]
    debt = [
        {"id": "DEBT-001", "status": "open"},
        {"id": "DEBT-002", "status": "closed"},
    ]
    return tuples, invariants, debt


def test_reconstruction_is_idempotent():
    args = fixture()
    assert reconstruct(*args) == reconstruct(*args)


def test_expected_state():
    state = reconstruct(*fixture())
    assert state.latest_tuple == "TUP-0003"
    assert state.tuple_count == 3
    assert state.invariant_count == 2
    assert state.open_debt_count == 1
    assert state.replay_ready is True
    assert validate(state)["status"] == "PASS"


if __name__ == "__main__":
    test_reconstruction_is_idempotent()
    test_expected_state()
    print("A7 semantic runtime tests: PASS")
