from semantic_acceptance_gate import evaluate
from semantic_delta_replay import run as run_replay


def test_replay_exact_sequence():
    result = run_replay()
    assert result["status"] == "PASS"
    assert result["final_state"]["exact_TUP_0001_to_TUP_0008"] is True
    assert result["final_state"]["visited_count"] >= 8


def test_renderer_acceptance_requires_reconstructability():
    result = evaluate(render_validation_passed=True)
    assert result["status"] == "PASS"
    assert result["semantic_promotions_allowed"] is True
    assert all(result["checks"].values())


def test_renderer_failure_blocks_promotion():
    result = evaluate(render_validation_passed=False)
    assert result["status"] == "FAIL"
    assert result["semantic_promotions_allowed"] is False


if __name__ == "__main__":
    test_replay_exact_sequence()
    test_renderer_acceptance_requires_reconstructability()
    test_renderer_failure_blocks_promotion()
    print("A7.1 semantic replay and acceptance tests: PASS")
