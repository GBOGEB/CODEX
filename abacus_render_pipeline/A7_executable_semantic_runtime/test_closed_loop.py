from closed_loop import run


def test_real_ledgers_form_valid_closed_loop():
    result = run()
    assert result["status"] == "PASS"
    assert result["schema_errors"] == []
    # TUP-0011 adds the content-addressed renderer execution receipt frontier.
    assert result["completeness"]["tuple_count"] == 11
    assert result["completeness"]["parentage_valid"] is True
    assert len(result["branch_dag"]["nodes"]) == 11
    assert len(result["branch_dag"]["edges"]) == 10
    assert result["runtime"]["state"]["replay_ready"] is True


if __name__ == "__main__":
    test_real_ledgers_form_valid_closed_loop()
    print("A8 real-ledger closed-loop tests: PASS")
