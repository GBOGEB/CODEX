"""scripts/osv_sarif_summary.py turns OSV SARIF into annotations and a summary table."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

SARIF = {
    "version": "2.1.0",
    "runs": [{
        "tool": {"driver": {"name": "osv-scanner", "rules": [
            {"id": "GHSA-aaaa-bbbb-cccc", "shortDescription": {"text": "Example package: path traversal"}},
        ]}},
        "results": [
            {"ruleId": "GHSA-aaaa-bbbb-cccc", "level": "warning",
             "message": {"text": "Package 'example@1.0.0' is vulnerable to 'GHSA-aaaa-bbbb-cccc'."},
             "locations": [{"physicalLocation": {"artifactLocation": {"uri": "requirements.txt"}, "region": {"startLine": 3}}}]},
            {"ruleId": "GHSA-dddd-eeee-ffff", "message": {"text": "multi\nline"}},
        ],
    }],
}


def _mod():
    spec = importlib.util.spec_from_file_location("osv_sarif_summary", REPO_ROOT / "scripts/osv_sarif_summary.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_findings_are_extracted_with_rule_summary_and_location():
    rows = _mod().findings(SARIF)
    assert [r["id"] for r in rows] == ["GHSA-aaaa-bbbb-cccc", "GHSA-dddd-eeee-ffff"]
    assert rows[0]["file"] == "requirements.txt" and rows[0]["line"] == "3"
    assert rows[0]["summary"] == "Example package: path traversal"
    assert rows[1]["file"] == "" and rows[1]["message"] == "multi line"


def test_main_emits_valid_workflow_commands_and_summary(tmp_path, capsys, monkeypatch):
    (tmp_path / "results.sarif").write_text(json.dumps(SARIF), encoding="utf-8")
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    assert _mod().main([str(tmp_path)]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0] == "::notice title=OSV findings::2 finding(s) in 1 SARIF file(s)"
    assert out[1] == "::warning file=requirements.txt,line=3,title=OSV GHSA-aaaa-bbbb-cccc::Example package: path traversal"
    assert out[2] == "::warning title=OSV GHSA-dddd-eeee-ffff::multi line"
    assert "| GHSA-aaaa-bbbb-cccc | `requirements.txt` |" in summary.read_text(encoding="utf-8")


def test_missing_sarif_is_reported_not_silent(tmp_path, capsys):
    assert _mod().main([str(tmp_path / "absent")]) == 0
    assert "no SARIF file found" in capsys.readouterr().out
