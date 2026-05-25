from __future__ import annotations

import json
from pathlib import Path

import pytest
import requests

import orchestrate_g3
import pr_generator
from helium_refrigeration_core import CryogenicHeliumEngine


def test_compute_exergy_efficiency_bounds() -> None:
    engine = CryogenicHeliumEngine()

    assert (
        engine.compute_exergy_efficiency(
            mass_flow=1.0,
            enthalpy_in=100.0,
            enthalpy_out=130.0,
            entropy_in=1.0,
            entropy_out=1.1,
            power_kw=0.0,
        )
        == 0.0
    )
    assert (
        engine.compute_exergy_efficiency(
            mass_flow=10.0,
            enthalpy_in=100.0,
            enthalpy_out=220.0,
            entropy_in=1.0,
            entropy_out=1.1,
            power_kw=0.5,
        )
        == 1.0
    )


def test_covariance_and_variance_metrics() -> None:
    engine = CryogenicHeliumEngine()
    claimed = [1.0, 2.0, 3.0]
    actual = [1.0, 2.0, 3.0]

    assert engine.calculate_covariance(claimed, actual) == pytest.approx(1.0)
    assert engine.calculate_anova_variance(claimed, actual) == pytest.approx(0.0)
    assert engine.calculate_covariance([1.0], [1.0]) == 0.0
    assert engine.calculate_anova_variance([1.0], [1.0]) == 0.0


def test_compute_exergy_efficiency_uses_kw_units() -> None:
    engine = CryogenicHeliumEngine()
    efficiency = engine.compute_exergy_efficiency(
        mass_flow=2.0,
        enthalpy_in=100.0,
        enthalpy_out=1100.0,
        entropy_in=1.0,
        entropy_out=1.0,
        power_kw=2.0,
    )
    assert efficiency == pytest.approx(1.0)


def test_compile_g3_dashboard_notes_missing_anchors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    matrix = {
        "tuples": [
            {
                "component_id": "G3-TUPLE-ONE",
                "scope": "Scope One",
                "upstream": {"repo": "gbogeb/codex", "file_path": "exists.md"},
                "downstream": {"file_path": "downstream/one.py"},
            },
            {
                "component_id": "G3-TUPLE-TWO",
                "scope": "Scope Two",
                "upstream": {"repo": "gbogeb/codex", "file_path": "missing.md"},
                "downstream": {"file_path": "downstream/two.py"},
            },
        ]
    }
    (tmp_path / "exists.md").write_text("ok", encoding="utf-8")
    (tmp_path / "g3_deep_matrix.json").write_text(json.dumps(matrix), encoding="utf-8")
    monkeypatch.setattr(orchestrate_g3, "__file__", str(tmp_path / "orchestrate_g3.py"))

    orchestrate_g3.compile_g3_dashboard()

    readme = (tmp_path / "outputs" / "html" / "README.md").read_text(encoding="utf-8")
    files_html = (tmp_path / "outputs" / "html" / "files.html").read_text(encoding="utf-8")
    assert "- [ ] Add or correct upstream anchor: `missing.md`" in readme
    assert "G3-TUPLE-ONE" in files_html


def test_compile_g3_dashboard_escapes_matrix_values(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    matrix = {
        "tuples": [
            {
                "component_id": "<script>alert(1)</script>",
                "scope": "Scope & \"quoted\"",
                "upstream": {"repo": "gbogeb/codex", "file_path": "a b/<tag>.md"},
                "downstream": {"file_path": "downstream/<bad>.py"},
            }
        ]
    }
    (tmp_path / "g3_deep_matrix.json").write_text(json.dumps(matrix), encoding="utf-8")
    monkeypatch.setattr(orchestrate_g3, "__file__", str(tmp_path / "orchestrate_g3.py"))

    orchestrate_g3.compile_g3_dashboard()

    files_html = (tmp_path / "outputs" / "html" / "files.html").read_text(encoding="utf-8")
    assert "<script>alert(1)</script>" not in files_html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in files_html
    assert "Scope &amp; &quot;quoted&quot;" in files_html
    assert "a%20b/%3Ctag%3E.md" in files_html
    assert "downstream/&lt;bad&gt;.py" in files_html


def test_issue_g3_pull_request_handles_transport_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "dummy")

    def _raise_request_exception(*_args, **_kwargs):
        raise requests.RequestException("network down")

    monkeypatch.setattr(pr_generator.requests, "post", _raise_request_exception)
    assert (
        pr_generator.issue_g3_pull_request(
            "gbogeb/codex", "branch", "title", "body"
        )
        is False
    )
