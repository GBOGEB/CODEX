from closed_loop import run


def test_real_ledgers_form_valid_closed_loop():
    result = run()
    assert result["status"] == "PASS"
    assert result["schema_errors"] == []
    # TUP-0013 closes the visual snapshot receipt frontier.
    assert result["completeness"]["tuple_count"] == 13
    assert result["completeness"]["parentage_valid"] is True
    assert len(result["branch_dag"]["nodes"]) == 13
    assert len(result["branch_dag"]["edges"]) == 12
    assert result["runtime"]["state"]["replay_ready"] is True


if __name__ == "__main__":
    test_real_ledgers_form_valid_closed_loop()
    print("A10 real-ledger closed-loop tests: PASS")
