import copy

from handover_seed import build_seed, next_seed, run, verify_seed


def fixture():
    tuple_doc = {
        "tuples": [
            {"id": "TUP-0001", "parent": None, "branch": "root", "todo": "fork"},
            {"id": "TUP-0002", "parent": "TUP-0001", "branch": "a", "todo": "compare"},
            {"id": "TUP-0003", "parent": "TUP-0001", "branch": "b", "todo": "build"},
        ]
    }
    governance = {
        "invariants": [{"id": "INV-001", "statement": "lineage is preserved"}],
        "semantic_debt": [
            {"id": "DEBT-001", "status": "open", "topic": "x", "next_action": "do x"},
            {"id": "DEBT-002", "status": "closed", "topic": "y", "next_action": "done"},
        ],
        "branch_competition": [
            {"id": "COMP-001", "fork": "TUP-0001", "alternatives": ["TUP-0002", "TUP-0003"],
             "status": "open", "winner": None, "evidence": []},
        ],
    }
    return tuple_doc, governance


def test_committed_seed_is_current():
    result = run()
    assert result["status"] == "PASS", result["errors"]
    assert "TUP-0014" in result["resume_from"]


def test_seed_is_idempotent():
    tuple_doc, governance = fixture()
    assert build_seed(tuple_doc, governance) == build_seed(tuple_doc, governance)


def test_seed_carries_resume_state():
    seed = build_seed(*fixture())
    assert seed["parent_seed_sha256"] is None
    assert [item["id"] for item in seed["resume_from"]] == ["TUP-0002", "TUP-0003"]
    assert seed["open_competitions"] == ["COMP-001"]
    assert seed["competing_branches"] == ["a", "b"]
    assert [item["id"] for item in seed["open_debt"]] == ["DEBT-001"]
    assert seed["state"]["latest_tuple"] == "TUP-0003"
    assert verify_seed(seed, *fixture()) == []


def test_next_pulse_chains_onto_previous_seed():
    tuple_doc, governance = fixture()
    first = build_seed(tuple_doc, governance)
    resume = first["resume_from"][1]["id"]
    tuple_doc["tuples"].append({"id": "TUP-0004", "parent": resume, "branch": "b", "todo": "ship"})
    second = next_seed(tuple_doc, governance, first)
    assert second["parent_seed_sha256"] == first["seed_sha256"]
    assert [item["id"] for item in second["resume_from"]] == ["TUP-0002", "TUP-0004"]
    assert second["state"]["tuple_count"] == first["state"]["tuple_count"] + 1
    assert verify_seed(second, tuple_doc, governance) == []
    # Unchanged ledgers are a fixed point: the next pulse keeps the same seed.
    assert next_seed(tuple_doc, governance, second) is second


def test_stale_seed_fails():
    tuple_doc, governance = fixture()
    seed = build_seed(tuple_doc, governance)
    governance["semantic_debt"][0]["status"] = "closed"
    errors = verify_seed(seed, tuple_doc, governance)
    assert len(errors) == 1 and errors[0].startswith("seed is stale")


def test_tampered_seed_fails():
    tuple_doc, governance = fixture()
    seed = copy.deepcopy(build_seed(tuple_doc, governance))
    seed["open_debt"] = []
    errors = verify_seed(seed, tuple_doc, governance)
    assert "seed_sha256 does not match seed content" in errors
    assert "seed content does not match the state reconstructed from the ledgers" in errors


if __name__ == "__main__":
    test_committed_seed_is_current()
    test_seed_is_idempotent()
    test_seed_carries_resume_state()
    test_next_pulse_chains_onto_previous_seed()
    test_stale_seed_fails()
    test_tampered_seed_fails()
    print("A7.4 handover seed tests: PASS")
