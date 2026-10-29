"""Coverage wave 11 (L3): DMAIC phase-map validator, federation governance
health-check and QPS perpetual-control aggregator (all repo paths patched to
``tmp_path``)."""
from __future__ import annotations

import json

import pytest
import yaml

from tests.coverage_waves._loader import load

PHASE = "scripts/validate_dmaic_phase_map.py"
FEDGOV = "scripts/check_federation_governance.py"
PERP = "scripts/qps_perpetual_control.py"


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# ---------------------------------------------------------------- DMAIC phase map
PHASE_MAP = {
    "dmaic_phases": {
        "DEFINE": {"incubator_categories": ["INCUBATOR"], "incubator_themes": ["scope"]},
        "MEASURE": {"incubator_categories": ["ANALYSIS"], "incubator_themes": ["metrics"]},
    },
    "routing_rules": [{"action": "assign_default_phase", "default_phase": "MEASURE"}],
    "validation": {"allowed_phases": ["DEFINE", "MEASURE"]},
}


def test_routing_index_and_resolution():
    m = load(PHASE)
    idx = m._build_routing_index(PHASE_MAP)
    assert idx["__default__"] == "MEASURE"
    assert m.resolve_phase("ANALYSIS", "metrics", idx) == "MEASURE"
    assert m.resolve_phase("INCUBATOR", "zzz", idx) == "DEFINE"
    assert m.resolve_phase("zzz", "scope", idx) == "DEFINE"
    assert m.resolve_phase("zzz", "zzz", idx) == "MEASURE"
    assert m._build_routing_index({})["__default__"] == "DEFINE"


def _tree(tmp_path, tuples, phase_map=PHASE_MAP):
    inc = tmp_path / "inc"
    inc.mkdir()
    for name, body in tuples.items():
        _write(inc / name, body)
    pmap = _write(tmp_path / "map.yml", yaml.safe_dump(phase_map))
    return inc, pmap


def test_validate_passes_and_writes_report(tmp_path, capsys):
    m = load(PHASE)
    inc, pmap = _tree(tmp_path, {"a.yml": "category: ANALYSIS\ntheme: metrics\n",
                                 "session_tuple_schema.yml": "category: X\n"})
    report = tmp_path / "r" / "report.json"
    assert m.validate(inc, pmap, report) == 0
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["status"] == "passed" and data["totals"]["tuples_total"] == 1
    assert data["results"][0]["phase"] == "MEASURE"
    assert "PASS: 1 tuple(s)" in capsys.readouterr().out


def test_validate_failures_and_report(tmp_path, capsys):
    m = load(PHASE)
    pmap = dict(PHASE_MAP, validation={"allowed_phases": ["DEFINE"]})
    inc, pmap_path = _tree(tmp_path, {"bad.yml": "a: [1\n", "missing.yaml": "category: ANALYSIS\n",
                                      "out.yml": "category: ANALYSIS\ntheme: metrics\n",
                                      "ok.yml": "category: INCUBATOR\ntheme: scope\n"}, pmap)
    report = tmp_path / "rep.json"
    assert m.validate(inc, pmap_path, report) == 1
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["status"] == "failed" and data["totals"]["unresolved_total"] == 3
    assert data["actual_percent"] == 25.0 and data["convergence_delta"] == -75.0
    err = capsys.readouterr().err
    assert "YAML parse error" in err and "missing required fields" in err and "unknown phase 'MEASURE'" in err


def test_validate_empty_and_missing_map(tmp_path, capsys):
    m = load(PHASE)
    inc, pmap = _tree(tmp_path, {})
    report = tmp_path / "e.json"
    assert m.validate(inc, pmap, report) == 0
    assert json.loads(report.read_text(encoding="utf-8"))["status"] == "no-tuples"
    assert m.validate(inc, pmap) == 0
    assert m.validate(inc, tmp_path / "none.yml") == 1
    assert "phase map not found" in capsys.readouterr().err


def test_validate_allowed_defaults_to_declared_phases(tmp_path):
    m = load(PHASE)
    pmap = {k: v for k, v in PHASE_MAP.items() if k != "validation"}
    inc, path = _tree(tmp_path, {"a.yml": "category: INCUBATOR\ntheme: scope\n"}, pmap)
    assert m.validate(inc, path) == 0


def test_phase_main_and_repo_map(tmp_path):
    m = load(PHASE)
    inc, pmap = _tree(tmp_path, {"a.yml": "category: ANALYSIS\ntheme: metrics\n"})
    assert m.main(["--incubator-dir", str(inc), "--phase-map", str(pmap)]) == 0
    assert m.main([]) == 0


# ---------------------------------------------------------------- federation governance
def _fedgov_root(tmp_path, monkeypatch, m, *, manifest="codex:\n  a: 1\nabacus:\n  b: 2\n", parser_src="x = 1\n",
                 schema="{}"):
    for rel, _ in m.REAL_CODE:
        _write(tmp_path / rel, "x")
    if parser_src is not None:
        _write(tmp_path / "federation_runtime/engines/governance_parser.py", parser_src)
    else:
        (tmp_path / "federation_runtime/engines/governance_parser.py").unlink()
    _write(tmp_path / "federation_runtime/schema/governance_header.schema.json", schema)
    if manifest is not None:
        _write(tmp_path / "bridge_manifest.yaml", manifest)
    else:
        (tmp_path / "bridge_manifest.yaml").unlink()
    monkeypatch.setattr(m, "ROOT", tmp_path)


def test_fedgov_pass(tmp_path, monkeypatch, capsys):
    m = load(FEDGOV)
    _fedgov_root(tmp_path, monkeypatch, m)
    _write(tmp_path / "output/federation_bridge/x", "x")
    assert m.main() == 0
    assert "RESULT: PASS" in capsys.readouterr().out


def test_fedgov_every_failure(tmp_path, monkeypatch, capsys):
    m = load(FEDGOV)
    _fedgov_root(tmp_path, monkeypatch, m, manifest="# codex: only a comment\nabacus: 1\n",
                 parser_src="def broken(:\n", schema="{not json")
    (tmp_path / m.REAL_CODE[2][0]).unlink()
    assert m.main() == 1
    out = capsys.readouterr().out
    assert "SYNTAX ERROR" in out and "JSON ERROR" in out
    assert "does not define a 'codex:' key" in out and "MISSING  [real]" in out


def test_fedgov_helpers_missing_files(tmp_path, monkeypatch):
    m = load(FEDGOV)
    _fedgov_root(tmp_path, monkeypatch, m, manifest=None, parser_src=None)
    assert m._validate_governance_parser()[0].startswith("  MISSING  governance parser")
    assert m._validate_bridge_manifest()[0].startswith("  MISSING  bridge_manifest.yaml")
    assert m._check_paths([("nope.txt", "d")], "x") == ["  MISSING  [x] nope.txt  (d)"]


def test_fedgov_repo_passes():
    assert load(FEDGOV).main() == 0


# ---------------------------------------------------------------- perpetual control
@pytest.mark.parametrize(
    ("doc", "ok"),
    [
        (None, False), ({}, False), ({"status": "ACCEPT"}, True), ({"probe_status": "ACCEPT"}, True),
        ({"dov_status": "PASS"}, True), ({"execution": {"probe_status": "ACCEPT"}}, True),
        ({"execution": {"dov_status": "PASS"}}, True), ({"execution": "x", "status": "NO"}, False),
    ],
)
def test_perpetual_accepted(doc, ok):
    assert load(PERP).accepted(doc) is ok


def test_perpetual_load_and_find(tmp_path):
    m = load(PERP)
    assert m.load_json(tmp_path / "none.json") is None
    assert m.load_json(_write(tmp_path / "bad.json", "{x")) is None
    _write(tmp_path / "a" / "x.json", '{"n": 1}')
    _write(tmp_path / "b" / "x.json", '{"n": 2}')
    assert m.find_named(tmp_path, "x.json") == {"n": 2}
    assert m.find_named(tmp_path / "missing", "x.json") is None


def _perp_env(tmp_path, monkeypatch, m, seeds_ok=True, family=(), mcp=None):
    seeds = tmp_path / "seeds"
    evidence = tmp_path / "evidence"
    for name in ("A", "B"):
        body = {"status": "ACCEPT" if seeds_ok else "NO", "receipt_id": name, "workflow": {"run_id": 1},
                "execution": {"executor_workflow_sha": "e", "real_probe_steps": 3}, "source": {"exact_sha": "s"}}
        _write(seeds / f"QPS_FEDERATED_LLDB_W1F_{name}_ACCEPT.json", json.dumps(body))
    for fname in family:
        extra = {"source_exact_sha": "x", "session": {"stack_frames": 4}} if fname == "lldb_dap_live.json" else {}
        _write(evidence / "run1" / fname, json.dumps(dict({"status": "ACCEPT"}, **extra)))
    if mcp is not None:
        _write(evidence / "run1" / "lldb_mcp_live.json", json.dumps(mcp))
    monkeypatch.setattr(m, "SEEDS", seeds)
    monkeypatch.setattr(m, "OUT", tmp_path / "out")
    return evidence


FAMILY = ("lldb_dap_live.json", "docker_remote_lldb.json", "debugpy_live.json", "js_debug_live.json")


def test_perpetual_full_terminal_pass(tmp_path, monkeypatch, capsys):
    m = load(PERP)
    ev = _perp_env(tmp_path, monkeypatch, m, family=FAMILY, mcp={"status": "ACCEPT"})
    monkeypatch.setattr("sys.argv", ["p", "--evidence-root", str(ev), "--repo-local-runner-recovered"])
    assert m.main() == 0
    status = json.loads((tmp_path / "out" / "perpetual_control_status.json").read_text(encoding="utf-8"))
    assert status["federated_perpetual_control"] == "CONTROL"
    assert status["terminal_global_perpetual_debug_dov"] == "PASS"
    assert status["heartbeat"]["count"] == 3 and status["burndown"] == []
    assert json.loads(capsys.readouterr().out)["schema"] == "qps.perpetual.control.v2"


def test_perpetual_withheld_with_burndown(tmp_path, monkeypatch, capsys):
    m = load(PERP)
    ev = _perp_env(tmp_path, monkeypatch, m, seeds_ok=False, family=FAMILY[:1], mcp={"status": "DEFER"})
    monkeypatch.setattr("sys.argv", ["p", "--evidence-root", str(ev)])
    assert m.main() == 2
    status = json.loads(capsys.readouterr().out)
    assert status["federated_perpetual_control"] == "WITHHELD"
    ids = {b["id"]: b["state"] for b in status["burndown"]}
    assert ids["BD03-EXT-RUNNER-001"] == "WITHHELD_EXTERNAL"
    assert ids["BD-RUNTIME-LLDB-MCP"] == "DEFER_TOOLCHAIN" and ids["BD-RUNTIME-DEBUGPY"] == "OPEN"
    assert status["heartbeat"]["count"] == 1


def test_perpetual_control_without_terminal(tmp_path, monkeypatch, capsys):
    m = load(PERP)
    ev = _perp_env(tmp_path, monkeypatch, m, family=FAMILY)
    monkeypatch.setattr("sys.argv", ["p", "--evidence-root", str(ev)])
    assert m.main() == 0
    status = json.loads(capsys.readouterr().out)
    assert status["terminal_global_perpetual_debug_dov"] == "WITHHELD"
    assert status["terminal_requirements"]["live_lldb_mcp"] is False
