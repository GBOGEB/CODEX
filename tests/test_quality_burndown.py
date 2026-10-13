import json
import subprocess
import sys


def test_burndown_comparison(tmp_path):
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps({"source_sha": "old", "diagnostics": [
        {"tool": "ruff", "path": "a.py", "rule": "F821", "message": "undefined", "line": 3}]}))
    current = tmp_path / "ruff.json"
    current.write_text("[]")
    output = tmp_path / "receipt.json"
    result = subprocess.run(
        [sys.executable, "scripts/quality_burndown.py", "--ruff", str(current),
         "--baseline", str(baseline), "--out", str(output), "--source-sha", "new"],
        capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    receipt = json.loads(output.read_text())
    assert receipt["comparison"]["resolved"] == 1
    assert receipt["comparison"]["new"] == 0
    assert receipt["comparison"]["net_reduction"] == 1
    assert receipt["comparison"]["same_source"] is False
    assert receipt["admission"] == "advisory"


def test_pyright_rule_and_line(tmp_path):
    report = tmp_path / "pyright.json"
    report.write_text(json.dumps({"generalDiagnostics": [{
        "file": "b.py", "rule": "reportUndefinedVariable",
        "severity": "error", "message": "missing", "range": {"start": {"line": 4}}
    }]}))
    output = tmp_path / "receipt.json"
    result = subprocess.run(
        [sys.executable, "scripts/quality_burndown.py", "--pyright", str(report),
         "--out", str(output)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    receipt = json.loads(output.read_text())
    assert receipt["current"]["by_rule"]["pyright:reportUndefinedVariable"] == 1
    assert receipt["diagnostics"][0]["line"] == 5


def test_line_shift_does_not_claim_resolution(tmp_path):
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps({"source_sha": "sha0", "diagnostics": [
        {"tool": "ruff", "path": "scripts/example.py",
         "rule": "F821", "message": "Undefined name \`foo\`", "line": 5}
    ]}))
    ruff = tmp_path / "ruff.json"
    ruff.write_text(json.dumps([{"filename": str(tmp_path / "scripts/example.py"),
        "code": "F821", "message": "Undefined name \`foo\`",
        "location": {"row": 10}}]))
    output = tmp_path / "out.json"
    result = subprocess.run([
        sys.executable, "scripts/quality_burndown.py",
        "--ruff", str(ruff), "--repo-root", str(tmp_path),
        "--baseline", str(baseline), "--out", str(output),
    ], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    delta = json.loads(output.read_text())["comparison"]
    assert delta["resolved"] == 0
    assert delta["new"] == 0
    assert delta["net_reduction"] == 0
