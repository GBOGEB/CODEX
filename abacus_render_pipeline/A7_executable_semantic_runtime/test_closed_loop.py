from closed_loop import run


def test_real_ledgers_form_valid_closed_loop():
    result = run()
    assert result["status"] == "PASS"
    assert result["schema_errors"] == []
    assert result["completeness"]["tuple_count"] == 8
    assert result["completeness"]["parentage_valid"] is True
    assert len(result["branch_dag"]["nodes"]) == 8
    assert len(result["branch_dag"]["edges"]) == 7
    assert result["runtime"]["state"]["replay_ready"] is True


if __name__ == "__main__":
    test_real_ledgers_form_valid_closed_loop()
    print("A7 real-ledger closed-loop tests: PASS")
