import copy

from branch_evolution import evaluate, run


def fixture():
    tuples = [
        {"id": "TUP-0001", "parent": None, "branch": "root"},
        {"id": "TUP-0002", "parent": "TUP-0001", "branch": "canonical_convergence"},
        {"id": "TUP-0003", "parent": "TUP-0001", "branch": "option_b_overlay_first"},
        {"id": "TUP-0004", "parent": "TUP-0003", "branch": "comparison"},
    ]
    competition = {
        "id": "COMP-001",
        "fork": "TUP-0001",
        "alternatives": ["TUP-0002", "TUP-0003"],
        "status": "open",
        "winner": None,
        "evidence": [],
    }
    return tuples, competition


def converged(competition, winner="TUP-0003", evidence=("TUP-0004",)):
    result = copy.deepcopy(competition)
    result.update({"status": "converged", "winner": winner, "evidence": list(evidence)})
    return result


def test_real_ledger_keeps_competing_branches_explicit():
    result = run()
    assert result["status"] == "PASS"
    assert result["errors"] == []
    assert result["fork_points"]["TUP-0001"] == ["TUP-0002", "TUP-0003"]
    assert result["open_competitions"] == ["COMP-001"]
    assert result["competing_branches"] == ["canonical_convergence", "option_b_overlay_first"]
    assert "TUP-0014" in result["frontier"]


def test_evaluation_is_idempotent():
    tuples, competition = fixture()
    assert evaluate(tuples, [competition]) == evaluate(tuples, [competition])


def test_open_competition_passes():
    tuples, competition = fixture()
    result = evaluate(tuples, [competition])
    assert result["status"] == "PASS"
    assert result["frontier"] == ["TUP-0002", "TUP-0004"]


def test_evidenced_convergence_passes():
    tuples, competition = fixture()
    result = evaluate(tuples, [converged(competition)])
    assert result["status"] == "PASS"
    assert result["converged_competitions"] == ["COMP-001"]
    assert result["competing_branches"] == []


def test_convergence_without_evidence_fails():
    tuples, competition = fixture()
    result = evaluate(tuples, [converged(competition, evidence=())])
    assert result["status"] == "FAIL"
    assert result["errors"] == ["COMP-001 converged without evidence"]


def test_evidence_must_descend_from_fork():
    tuples, competition = fixture()
    result = evaluate(tuples, [converged(competition, evidence=("TUP-0001",))])
    assert result["status"] == "FAIL"
    assert "COMP-001 evidence TUP-0001 is not a tuple descending from fork TUP-0001" in result["errors"]


def test_winner_must_be_an_alternative():
    tuples, competition = fixture()
    result = evaluate(tuples, [converged(competition, winner="TUP-0004")])
    assert result["status"] == "FAIL"
    assert "COMP-001 converged winner TUP-0004 is not one of its alternatives" in result["errors"]


def test_open_competition_cannot_name_winner():
    tuples, competition = fixture()
    competition["winner"] = "TUP-0002"
    result = evaluate(tuples, [competition])
    assert result["status"] == "FAIL"


def test_deleting_losing_branch_fails():
    tuples, competition = fixture()
    pruned = [item for item in tuples if item["id"] != "TUP-0002"]
    result = evaluate(pruned, [converged(competition)])
    assert result["status"] == "FAIL"
    assert "COMP-001 alternative TUP-0002 is not in the tuple ledger" in result["errors"]


def test_alternatives_must_share_the_fork():
    tuples, competition = fixture()
    competition["alternatives"] = ["TUP-0002", "TUP-0004"]
    result = evaluate(tuples, [competition])
    assert result["status"] == "FAIL"
    assert "COMP-001 alternative TUP-0004 does not branch from fork TUP-0001" in result["errors"]


def test_missing_fields_fail():
    tuples, competition = fixture()
    del competition["evidence"]
    result = evaluate(tuples, [competition])
    assert result["status"] == "FAIL"
    assert result["errors"] == ["competition[0] missing fields: evidence"]


if __name__ == "__main__":
    test_real_ledger_keeps_competing_branches_explicit()
    test_evaluation_is_idempotent()
    test_open_competition_passes()
    test_evidenced_convergence_passes()
    test_convergence_without_evidence_fails()
    test_evidence_must_descend_from_fork()
    test_winner_must_be_an_alternative()
    test_open_competition_cannot_name_winner()
    test_deleting_losing_branch_fails()
    test_alternatives_must_share_the_fork()
    test_missing_fields_fail()
    print("A7.1 branch evolution tests: PASS")
