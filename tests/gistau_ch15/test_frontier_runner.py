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


def test_frontier_runner_reports_unavailable_refprop_and_hepak(monkeypatch, tmp_path):
    from gistau_ch15.properties.backend_selector import BackendAvailability
    from gistau_ch15.properties.compare import BackendTier
    from gistau_ch15.properties.fallback_helium import FallbackHeliumBackend
    from gistau_ch15.properties import frontier_runner as runner_module

    def _fake_selector():
        return (
            {"fallback": FallbackHeliumBackend()},
            [
                BackendAvailability("fallback", BackendTier.FALLBACK, True, "deterministic"),
                BackendAvailability("coolprop", BackendTier.COOLPROP, False, "not installed"),
                BackendAvailability("refprop", BackendTier.REFPROP, False, "ctREFPROP missing"),
                BackendAvailability("hepak", BackendTier.HEPAK, False, "HEPAK missing"),
            ],
        )

    monkeypatch.setattr(runner_module, "select_available_backends", _fake_selector)
    report = FrontierEngineeringRunner(output_directory=str(tmp_path)).run()

    assert all(row["backend_name"] == "refprop" for row in report["refprop_validation_rows"])
    assert all(row["status"] == "backend_unavailable_or_failed" for row in report["refprop_validation_rows"])
    assert all(row["backend_name"] == "hepak" for row in report["wetness_validation_rows"])
    assert all(row["status"] == "backend_unavailable_or_failed" for row in report["wetness_validation_rows"])
