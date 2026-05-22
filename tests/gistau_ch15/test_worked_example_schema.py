from gistau_ch15.validation.worked_example_runner import SUPPORTED_EXAMPLE_IDS, WorkedExampleRunner


def test_worked_examples_include_required_pr_g_bindings():
    examples = WorkedExampleRunner().load_worked_examples()
    ids = {example["example_id"] for example in examples}
    assert SUPPORTED_EXAMPLE_IDS.issubset(ids)


def test_worked_examples_reference_tiers_present():
    examples = WorkedExampleRunner().load_worked_examples()
    sample = next(example for example in examples if example["example_id"] in SUPPORTED_EXAMPLE_IDS)
    assert "primary_reference_tier" in sample
    assert "expected_outputs" in sample
