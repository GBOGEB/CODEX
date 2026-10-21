from closed_loop import DATA, check_branch_dag, derive_branch_dag, load_json, run


def forest():
    return [
        {"id": "TUP-0001", "parent": None, "branch": "a", "theme": "t", "progress": "active"},
        {"id": "TUP-0002", "parent": "TUP-0001", "branch": "a", "theme": "t", "progress": "active"},
        {"id": "TUP-0003", "parent": None, "branch": "b", "theme": "t", "progress": "active"},
        {"id": "TUP-0004", "parent": "TUP-0003", "branch": "b", "theme": "t", "progress": "active"},
    ]


def test_real_ledgers_form_valid_closed_loop():
    result = run()
    assert result["status"] == "PASS"
    assert result["schema_errors"] == []
    # TUP-0014 extends the closed loop with Pages ownership stabilization.
    assert result["completeness"]["tuple_count"] == 14
    assert result["completeness"]["parentage_valid"] is True
    assert len(result["branch_dag"]["nodes"]) == 14
    assert len(result["branch_dag"]["edges"]) == 13
    assert result["runtime"]["state"]["replay_ready"] is True
    dag_result = check_branch_dag(load_json(DATA / "semantic_tuple_ledger.json")["tuples"], result["branch_dag"])
    assert dag_result["pass"] is True
    assert dag_result["roots"] == ["TUP-0001"]


def test_multi_root_forest_passes_dag_check():
    tuples = forest()
    result = check_branch_dag(tuples, derive_branch_dag(tuples))
    assert result["pass"] is True
    assert result["roots"] == ["TUP-0001", "TUP-0003"]
    assert result["expected_edges"] == 2


def test_dag_without_root_fails():
    tuples = forest()
    tuples[0]["parent"] = "TUP-0002"
    tuples[2]["parent"] = "TUP-0004"
    result = check_branch_dag(tuples, derive_branch_dag(tuples))
    assert result["pass"] is False
    assert result["roots"] == []


def test_dag_missing_edge_fails():
    tuples = forest()
    dag = derive_branch_dag(tuples)
    dag["edges"] = dag["edges"][:-1]
    assert check_branch_dag(tuples, dag)["pass"] is False


if __name__ == "__main__":
    test_real_ledgers_form_valid_closed_loop()
    test_multi_root_forest_passes_dag_check()
    test_dag_without_root_fails()
    test_dag_missing_edge_fails()
    print("A10.2 real-ledger closed-loop tests: PASS")
