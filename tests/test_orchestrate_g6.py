from pathlib import Path

from orchestrate_g6 import _load_wave_series, run_g6_attestation_loop


def test_load_wave_series_reads_governed_manifests() -> None:
    claimed_waves, actual_waves = _load_wave_series()

    assert len(claimed_waves) == len(actual_waves)
    assert claimed_waves[0] == 1.0
    assert actual_waves[0] == 0.12
    assert claimed_waves[-1] == 0.52
    assert actual_waves[-1] == 0.71


def test_run_g6_attestation_loop_writes_outputs_html_without_touching_readme(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs" / "html"
    repo_readme = Path(__file__).resolve().parents[1] / "README.md"
    readme_before = repo_readme.read_text(encoding="utf-8")

    result = run_g6_attestation_loop(output_dir=output_dir)

    readme_after = repo_readme.read_text(encoding="utf-8")
    assert readme_after == readme_before

    assert set(result["output_paths"]) == {"files", "dashboard", "slides", "summary"}
    for output_path in result["output_paths"].values():
        assert Path(output_path).exists()

    dashboard = (output_dir / "g6_dashboard.html").read_text(encoding="utf-8")
    assert "Content-Security-Policy" in dashboard
    assert result["attestation_hash"] in dashboard
