import copy

from closed_loop import DATA, load_json
from lineage_lock import check_append_only, extend_lock, lock_entries, run


def fixture():
    return [
        {"id": "TUP-0001", "parent": None, "branch": "root", "theme": "t1", "intent": "i1", "progress": "active"},
        {"id": "TUP-0002", "parent": "TUP-0001", "branch": "root", "theme": "t2", "intent": "i2", "progress": "active"},
    ]


def test_committed_lock_matches_real_ledger():
    result = run()
    assert result["status"] == "PASS"
    assert result["errors"] == []
    tuples = load_json(DATA / "semantic_tuple_ledger.json")["tuples"]
    assert result["locked_count"] == len(tuples)
    assert result["appended"] == []


def test_appended_tuple_extends_lock():
    tuples = fixture()
    locked = lock_entries(tuples)
    tuples.append({"id": "TUP-0003", "parent": "TUP-0002", "branch": "root", "theme": "t3", "intent": "i3"})
    result = check_append_only(tuples, locked)
    assert result["status"] == "PASS"
    assert result["appended"] == ["TUP-0003"]
    assert [entry["id"] for entry in extend_lock(tuples, locked)] == ["TUP-0001", "TUP-0002", "TUP-0003"]


def test_progress_may_evolve():
    tuples = fixture()
    locked = lock_entries(tuples)
    evolved = copy.deepcopy(tuples)
    evolved[0]["progress"] = "complete"
    evolved[0]["todo"] = "nothing left"
    assert check_append_only(evolved, locked)["status"] == "PASS"


def test_rewritten_identity_fails():
    tuples = fixture()
    locked = lock_entries(tuples)
    tuples[1]["parent"] = None
    result = check_append_only(tuples, locked)
    assert result["status"] == "FAIL"
    assert result["errors"] == ["locked tuple TUP-0002 identity fields were rewritten"]


def test_deleted_tuple_fails():
    tuples = fixture()
    locked = lock_entries(tuples)
    result = check_append_only(tuples[:1], locked)
    assert result["status"] == "FAIL"
    assert result["errors"] == ["locked tuple TUP-0002 was deleted"]


def test_inserted_tuple_fails():
    tuples = fixture()
    locked = lock_entries(tuples)
    tuples.insert(1, {"id": "TUP-0009", "parent": "TUP-0001", "branch": "root", "theme": "t", "intent": "i"})
    result = check_append_only(tuples, locked)
    assert result["status"] == "FAIL"
    assert "position 2: locked TUP-0002 replaced or reordered by TUP-0009" in result["errors"]


def test_extend_refuses_to_rewrite_history():
    tuples = fixture()
    locked = lock_entries(tuples)
    tuples[0]["intent"] = "rewritten"
    try:
        extend_lock(tuples, locked)
    except ValueError as exc:
        assert "TUP-0001" in str(exc)
    else:
        raise AssertionError("extend_lock accepted rewritten history")


if __name__ == "__main__":
    test_committed_lock_matches_real_ledger()
    test_appended_tuple_extends_lock()
    test_progress_may_evolve()
    test_rewritten_identity_fails()
    test_deleted_tuple_fails()
    test_inserted_tuple_fails()
    test_extend_refuses_to_rewrite_history()
    print("A7.3 lineage lock tests: PASS")
