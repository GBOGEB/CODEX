import json
from pathlib import Path

from scripts.classify_executable_registration_debt import classify


def _write_report(path: Path, assets: list[str]) -> None:
    path.write_text(
        json.dumps({"inventory": {"unregistered_assets": assets}}),
        encoding="utf-8",
    )


def _write_workflow(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_path_filter_only_is_not_operational_consumer(tmp_path: Path) -> None:
    report = tmp_path / "report.json"
    workflows = tmp_path / "workflows"
    tests = tmp_path / "tests"
    tests.mkdir()
    _write_report(report, ["scripts/example.py"])
    (tests / "test_example.py").write_text("", encoding="utf-8")
    _write_workflow(
        workflows / "example.yml",
        """
on:
  pull_request:
    paths:
      - scripts/example.py
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - run: echo no-consumer
""",
    )
    payload = classify(report, workflows, tests)
    row = payload["candidates"][0]
    assert row["test_evidence"] is True
    assert row["operational_edge"] is False
    assert row["classification"] == "TESTED_ORPHAN"


def test_run_step_is_operational_consumer(tmp_path: Path) -> None:
    report = tmp_path / "report.json"
    workflows = tmp_path / "workflows"
    tests = tmp_path / "tests"
    tests.mkdir()
    _write_report(report, ["scripts/example.py"])
    _write_workflow(
        workflows / "example.yml",
        """
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - run: python scripts/example.py
""",
    )
    payload = classify(report, workflows, tests)
    row = payload["candidates"][0]
    assert row["operational_edge"] is True
    assert row["downstream_consumer"] == "github_actions"
    assert row["classification"] == "PIPELINE_INTEGRATION_CANDIDATE"


def test_test_asset_is_reference_only(tmp_path: Path) -> None:
    report = tmp_path / "report.json"
    workflows = tmp_path / "workflows"
    tests = tmp_path / "tests"
    workflows.mkdir()
    tests.mkdir()
    _write_report(report, ["tests/test_example.py"])
    payload = classify(report, workflows, tests)
    assert payload["candidates"][0]["classification"] == "LIBRARY_REFERENCE_ONLY"


def test_unknown_asset_remains_unresolved(tmp_path: Path) -> None:
    report = tmp_path / "report.json"
    workflows = tmp_path / "workflows"
    tests = tmp_path / "tests"
    workflows.mkdir()
    tests.mkdir()
    _write_report(report, ["scripts/unknown.py"])
    payload = classify(report, workflows, tests)
    assert payload["candidates"][0]["classification"] == "UNRESOLVED_REGISTRATION_DEBT"


def test_source_report_tracks_actual_override(tmp_path: Path) -> None:
    report = tmp_path / "custom-report.json"
    workflows = tmp_path / "workflows"
    tests = tmp_path / "tests"
    workflows.mkdir()
    tests.mkdir()
    _write_report(report, [])
    payload = classify(report, workflows, tests)
    assert payload["source_report"] == str(report.resolve())
