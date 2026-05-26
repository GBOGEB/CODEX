from pathlib import Path

import yaml

from orchestrate_g6 import CONVERGENCE_KPIS_PATH, WAVE_PROGRESSION_PATH, _load_wave_series, run_g6_attestation_loop


def test_load_wave_series_reads_governed_manifests() -> None:
    claimed_waves, actual_waves = _load_wave_series()

    with WAVE_PROGRESSION_PATH.open("r", encoding="utf-8") as handle:
        wave_progression = yaml.safe_load(handle) or {}
    with CONVERGENCE_KPIS_PATH.open("r", encoding="utf-8") as handle:
        convergence = yaml.safe_load(handle) or {}

    expected_claimed = {
        item["wave"]: float(item["completion"]) / 100.0
        for item in wave_progression["waves"]
    }
    expected_actual = {
        wave: float(completion) / 100.0
        for wave, completion in convergence["convergence_kpis"]["progression"].items()
    }
    common_waves = sorted(set(expected_claimed) & set(expected_actual))

    assert len(claimed_waves) == len(actual_waves)
    assert claimed_waves == [expected_claimed[wave] for wave in common_waves]
    assert actual_waves == [expected_actual[wave] for wave in common_waves]


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
    assert "default-src 'self'" in dashboard
    assert "base-uri 'none'" in dashboard
    assert "object-src 'none'" in dashboard
    assert "frame-ancestors 'none'" in dashboard
    assert result["attestation_hash"] in dashboard
