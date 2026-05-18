from gistau_ch15.properties.frontier_runner import FrontierEngineeringRunner



def test_frontier_engineering_runner_executes():
    runner = FrontierEngineeringRunner(output_directory="outputs/test_frontier")

    report = runner.run()

    assert "backend_comparison_rows" in report
    assert "refprop_validation_rows" in report
    assert "wetness_validation_rows" in report
    assert "cryogenic_expander_replay" in report
    assert "uncertainty_summary" in report



def test_frontier_runner_produces_heatmap_rows():
    runner = FrontierEngineeringRunner(output_directory="outputs/test_frontier_heatmap")

    report = runner.run()

    assert report["backend_heatmap_matrix"]
