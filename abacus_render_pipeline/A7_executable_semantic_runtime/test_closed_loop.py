from closed_loop import run


def test_real_ledgers_form_valid_closed_loop():
    result = run()
    assert result["status"] == "PASS"
    assert result["schema_errors"] == []
    # TUP-0009 replay + TUP-0010 renderer acceptance extend the original 8-tuple seed.
    assert result["completeness"]["tuple_count"] == 10
    assert result["completeness"]["parentage_valid"] is True
    assert len(result["branch_dag"]["nodes"]) == 10
    assert len(result["branch_dag"]["edges"]) == 9
    assert result["runtime"]["state"]["replay_ready"] is True


if __name__ == "__main__":
    test_real_ledgers_form_valid_closed_loop()
    print("A7 real-ledger closed-loop tests: PASS")
