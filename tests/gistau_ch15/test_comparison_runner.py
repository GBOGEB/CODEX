from gistau_ch15.properties.backend_selector import select_available_backends
from gistau_ch15.properties.comparison_runner import ComparisonRunner


def test_comparison_runner_emits_required_row_schema():
    backends, availability = select_available_backends()
    rows = ComparisonRunner().run_worked_example_comparisons(backends, availability)

    assert rows
    required_keys = {
        "example_id",
        "tuple_id",
        "backend_name",
        "backend_tier",
        "reference_tier",
        "quantity",
        "backend_value",
        "reference_value",
        "absolute_delta",
        "relative_delta",
        "unit",
        "status",
        "notes",
    }
    assert required_keys.issubset(rows[0].keys())


def test_comparison_runner_includes_mapped_and_pending_rows():
    backends, availability = select_available_backends()
    rows = ComparisonRunner().run_worked_example_comparisons(backends, availability)

    statuses = {row["status"] for row in rows}
    assert "mapping_pending" in statuses
    assert "outside_tolerance" in statuses or "within_tolerance" in statuses
