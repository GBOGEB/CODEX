from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import generate_human_outputs as generator


def test_calc_core_conversion_is_stable() -> None:
    row = generator.calc(1e-8)

    assert row["q_si_pa_m3_s"] == 1e-09
    assert row["g_day"] == pytest.approx(1.4188355677445835e-07)
    assert row["g_year_99_8000h"] == pytest.approx(4.682157373557125e-05)
    assert json.dumps({"q_si_pa_m3_s": generator.calc(1e-9)["q_si_pa_m3_s"]}) == '{"q_si_pa_m3_s": 1e-10}'


def test_git_and_timestamp_fallbacks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HUMAN_GIT_HASH", raising=False)
    monkeypatch.delenv("HUMAN_GENERATED_AT", raising=False)
    monkeypatch.delenv("SOURCE_DATE_EPOCH", raising=False)
    monkeypatch.setattr(generator, "run_git", lambda *_args: None)

    assert generator.git_value() == "unknown"
    assert generator.generated_at_value() == "unknown"


def test_write_outputs_generates_docs_with_docs_nav(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path
    monkeypatch.setattr(generator, "ROOT", root)
    monkeypatch.setattr(generator, "OUT", root / "outputs")
    monkeypatch.setattr(generator, "HTML", root / "outputs" / "html")
    monkeypatch.setattr(generator, "JSON_DIR", root / "outputs" / "json")
    monkeypatch.setattr(generator, "TRACE", root / "traceability")
    monkeypatch.setattr(generator, "DOCS", root / "docs")
    monkeypatch.setenv("HUMAN_GENERATED_AT", "2026-05-09T00:00:00Z")
    monkeypatch.setenv("HUMAN_GIT_HASH", "abc1234")
    monkeypatch.delenv("HUMAN_INCLUDE_RUNTIME_METADATA", raising=False)

    generator.write_outputs()

    calculations = json.loads((root / "outputs" / "json" / "calculation_inputs_outputs.json").read_text())
    assert calculations["generated_at"] == "2026-05-09T00:00:00Z"
    assert calculations["git"] == "abc1234"
    assert calculations["rows"][0]["q_si_pa_m3_s"] == 1e-10

    docs_index = (root / "docs" / "HUMAN.index.html").read_text()
    assert "../outputs/html/01_EXECUTIVE_SUMMARY.html" in docs_index

    plot_page = (root / "outputs" / "html" / "04_PLOTS_AND_VISUAL_EVIDENCE.html").read_text()
    assert "<svg" in plot_page
    assert "cdn.plot.ly" not in plot_page
    assert not (root / "outputs" / "json" / "runtime_metadata.json").exists()
