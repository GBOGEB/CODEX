"""Coverage wave 13 (L3): read-only repo validators (W259 method cards, W285,
CTaxonomy, MASTER contract, QPS W04/W05 receipts, W101 immutable stage,
governance snapshot, authority integrity, workflow registration guard).

Real-repo PASS paths are asserted read-only; failure paths use tmp copies.
"""
from __future__ import annotations

import hashlib
import json

import pytest
import yaml

from tests.coverage_waves._loader import ROOT, load, run_main

SRC259 = "scripts/validate_w259_p4_method_cards_source_receipt.py"
ATOM259 = "scripts/validate_w259_p4_method_cards_knowledge_atom.py"
W285 = "scripts/validate_w285_federation_depth_semantics.py"
CTAX = "scripts/validate_ctaxonomy_semantic_contract.py"
MASTER = "scripts/validate_master_contract_ssot.py"
W04 = "tools/validate_qps_w04_keb_receipt.py"
W05 = "tools/validate_qps_w05_bidder_eval_keb.py"
W101 = "triage/w101_validate_immutable_binary_stage.py"
SNAP = "scripts/emit_governance_snapshot.py"
AUTH = "scripts/check_authority_integrity.py"
WFGUARD = "tools/validators/workflow_registration_guard.py"


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _tampered_json(tmp_path, src, mutate):
    data = json.loads(src.read_text(encoding="utf-8"))
    mutate(data)
    return _write(tmp_path / src.name, json.dumps(data))


# ---------------------------------------------------------------- W259 method cards
def test_w259_source_receipt_pass(tmp_path, capsys):
    out = tmp_path / "o" / "r.json"
    run_main(SRC259, ["--out", str(out)])
    assert out.is_file() and capsys.readouterr().out.strip().startswith("{")


def test_w259_source_receipt_tamper(tmp_path, monkeypatch):
    m = load(SRC259)
    with pytest.raises(SystemExit, match="FAIL: boom"):
        m.require(False, "boom")
    assert len(m.bundle_digest()) == 64
    data = json.loads(m.RECEIPT.read_text(encoding="utf-8"))
    first = next(iter(data))
    monkeypatch.setattr(m, "RECEIPT", _tampered_json(tmp_path, m.RECEIPT, lambda d: d.pop(first)))
    monkeypatch.setattr("sys.argv", ["v", "--out", str(tmp_path / "o.json")])
    with pytest.raises((SystemExit, KeyError)):
        m.main()


def test_w259_knowledge_atom_pass_and_tamper(tmp_path, monkeypatch, capsys):
    out = tmp_path / "a.json"
    run_main(ATOM259, ["--out", str(out)])
    assert json.loads(out.read_text(encoding="utf-8")) and capsys.readouterr().out
    m = load(ATOM259)
    first = next(iter(json.loads(m.ATOM.read_text(encoding="utf-8"))))
    monkeypatch.setattr(m, "ATOM", _tampered_json(tmp_path, m.ATOM, lambda d: d.pop(first)))
    monkeypatch.setattr("sys.argv", ["v", "--out", str(tmp_path / "b.json")])
    with pytest.raises((SystemExit, KeyError)):
        m.main()


# ---------------------------------------------------------------- W285
def test_w285_pass_and_tamper(tmp_path, monkeypatch, capsys):
    m = load(W285)
    assert m.validate() is True
    run_main(W285)
    assert "PASS" in capsys.readouterr().out
    monkeypatch.setattr(m, "P", _tampered_json(tmp_path, m.P, lambda d: d.update(schema="other")))
    with pytest.raises(ValueError, match="schema mismatch"):
        m.validate()


# ---------------------------------------------------------------- CTaxonomy
def test_ctaxonomy_pass_and_failures(tmp_path, monkeypatch, capsys):
    m = load(CTAX)
    real = ROOT / m.PATH
    monkeypatch.setattr(m, "PATH", real)
    assert m.main() == 0
    data = yaml.safe_load(real.read_text(encoding="utf-8"))
    data["required_active_ids"] = ["PLOC"]
    data["validation"] = {}
    data["receipt"] = {"engineering_credit_delta": 1}
    monkeypatch.setattr(m, "PATH", _write(tmp_path / "c.yaml", yaml.safe_dump(data)))
    assert m.main() == 1
    out = capsys.readouterr().out
    assert "KEB_CTAXONOMY_CONTRACT=PASS" in out and "required_active_ids mismatch" in out
    assert out.count("missing fail-closed rule") == 6 and "authority guard violated" in out


@pytest.mark.xfail(
    strict=True,
    reason=(
        "production_defect: scripts/validate_ctaxonomy_semantic_contract.py reads its contract via a "
        "cwd-relative Path, so running it from any directory other than the repo root raises "
        "FileNotFoundError (CLAUDE.md: resolve paths from the repo root via pathlib)"
    ),
)
def test_ctaxonomy_runs_outside_repo_root(tmp_path, monkeypatch):
    m = load(CTAX)
    monkeypatch.chdir(tmp_path)
    assert m.main() == 0


# ---------------------------------------------------------------- MASTER contract SSOT
def test_master_contract_pass_and_fail(tmp_path, capsys):
    m = load(MASTER)
    m.validate(m.DEFAULT_SCHEMA, m.DEFAULT_SSOT)
    assert "Validated" in capsys.readouterr().out
    bad = _write(tmp_path / "bad.yaml", "not_a_contract: true\n")
    with pytest.raises(SystemExit, match="MASTER SSOT validation failed"):
        m.validate(m.DEFAULT_SCHEMA, bad)
    assert m.load_yaml(_write(tmp_path / "x.yaml", "a: 1\n")) == {"a": 1}


def test_master_contract_main(monkeypatch, capsys):
    m = load(MASTER)
    monkeypatch.setattr("sys.argv", ["v"])
    m.main()
    assert "Validated" in capsys.readouterr().out


# ---------------------------------------------------------------- QPS W04 receipt
W04_FIXTURE = ROOT / "tests/fixtures/qps_w04_keb_receipt_fixture.yaml"


def test_w04_fixture_and_main(capsys):
    m = load(W04)
    assert m.validate(m.load(W04_FIXTURE)) == []
    assert m.main(["prog", str(W04_FIXTURE)]) == 0
    assert "satisfies QPS W04" in capsys.readouterr().out


def _root_receipt(m):
    r = {k: "x" for k in m.REQUIRED}
    r.update(correlation_id=m.CORR, authority_boundary="QPS_child_disposes", requested_operations=["op"],
             executed_operations=["op"], parent_commit_sha="a" * 40,
             semantic_domains_for_regression=sorted(m.DOMAINS),
             operation_status={"op": {"executed": True, "status": "PASS", "mechanic_path": "p"}})
    r.pop("output_hash")
    payload = json.dumps(r, sort_keys=True, separators=(",", ":")).encode()
    r["output_hash"] = hashlib.sha256(payload).hexdigest()
    return r


def test_w04_root_receipt_rules():
    m = load(W04)
    good = _root_receipt(m)
    assert m.validate(good) == []
    bad = dict(good, parent_commit_sha="short", operation_status={"op": {"executed": False}},
               semantic_domains_for_regression=[], correlation_id="x", authority_boundary="",
               executed_operations=["op"], requested_operations=["other"])
    del bad["run_id"]
    errs = " | ".join(m.validate(bad))
    for needle in ("correlation_id mismatch", "child authority boundary missing", "operation mismatch",
                   "missing runtime fields: run_id", "parent_commit_sha must be resolved",
                   "semantic regression domains incomplete", "lacks executed PASS mechanic", "output_hash mismatch"):
        assert needle in errs
    assert "operation_status must be a mapping" in m.validate(dict(good, operation_status=[]))
    assert m.validate({"example_valid_receipt": 3}) == ["receipt missing or not a mapping"]
    wrapped = m.validate({"example_valid_receipt": {"correlation_id": m.CORR}, "semantic_domains_for_regression": []})
    assert "fixture semantic domains incomplete" in wrapped


def test_w04_load_and_main_errors(tmp_path, capsys):
    m = load(W04)
    with pytest.raises(ValueError):
        m.load(_write(tmp_path / "l.yaml", "- 1\n"))
    bad = _write(tmp_path / "b.yaml", yaml.safe_dump({"correlation_id": "x"}))
    assert m.main(["prog", str(bad)]) == 1
    assert "ERROR: correlation_id mismatch" in capsys.readouterr().err


# ---------------------------------------------------------------- QPS W05 receipt
def _w05(m, **over):
    r = {k: "x" for k in m.REQUIRED}
    r.update(correlation_id="QPS-FED-W05-BIDDER-EVAL", parent_repository="GBOGEB/CODEX", requested_operations=["a"],
             executed_operations=["a"], child_disposition_placeholder="UNSET",
             typed_semantic_findings=[{"qps_authority": False, "disposition_unset": True}])
    r.update(over)
    return r


@pytest.mark.parametrize(
    ("over", "message"),
    [
        ({"correlation_id": "x"}, "wrong correlation"),
        ({"parent_repository": "x/y"}, "wrong parent repository"),
        ({"executed_operations": []}, "operation mismatch"),
        ({"child_disposition_placeholder": "ACCEPT"}, "self-disposition prohibited"),
        ({"typed_semantic_findings": []}, "no semantic findings"),
        ({"typed_semantic_findings": [{"qps_authority": True}]}, "claims QPS authority"),
        ({"typed_semantic_findings": [{"qps_authority": False}]}, "must remain unset"),
    ],
)
def test_w05_rejects(tmp_path, monkeypatch, over, message):
    m = load(W05)
    p = _write(tmp_path / "r.yaml", yaml.safe_dump(_w05(m, **over)))
    monkeypatch.setattr("sys.argv", ["v", str(p)])
    with pytest.raises(SystemExit, match=message):
        m.main()


def test_w05_pass_and_shape_errors(tmp_path, monkeypatch, capsys):
    m = load(W05)
    p = _write(tmp_path / "r.yaml", yaml.safe_dump(_w05(m)))
    monkeypatch.setattr("sys.argv", ["v", str(p)])
    assert m.main() == 0 and "W05 KEB RECEIPT VALIDATION PASSED" in capsys.readouterr().out
    for text, message in (("- 1\n", "not a mapping"), ("a: 1\n", "missing fields")):
        monkeypatch.setattr("sys.argv", ["v", str(_write(tmp_path / "x.yaml", text))])
        with pytest.raises(SystemExit, match=message):
            m.main()


# ---------------------------------------------------------------- W101 immutable stage
def test_w101_missing_and_mismatch(tmp_path, monkeypatch, capsys):
    m = load(W101)
    monkeypatch.chdir(tmp_path)
    stage = tmp_path / "stage"
    names = list(m.EXPECTED)
    _write(stage / names[0], "wrong bytes")
    monkeypatch.setattr("sys.argv", ["v", str(stage)])
    assert m.main() == 3
    rec = json.loads((tmp_path / "out" / "W101_IMMUTABLE_STAGE_RECEIPT.json").read_text(encoding="utf-8"))
    assert rec["status"] == "DEFER_IMMUTABLE_INPUT_STAGE" and rec["passed"] == 0
    assert rec["files"][names[0]]["state"] == "HASH_MISMATCH" and rec["files"][names[1]]["state"] == "MISSING"
    assert json.loads(capsys.readouterr().out)["required"] == 4


def test_w101_all_pass_with_matching_hashes(tmp_path, monkeypatch):
    m = load(W101)
    monkeypatch.chdir(tmp_path)
    expected = {}
    for i in range(4):
        p = _write(tmp_path / "stage" / f"f{i}.xlsx", f"payload {i}")
        expected[p.name] = m.sha256(p)
    monkeypatch.setattr(m, "EXPECTED", expected)
    monkeypatch.setattr("sys.argv", ["v", str(tmp_path / "stage")])
    assert m.main() == 0
    monkeypatch.setattr("sys.argv", ["v"])
    assert m.main() == 3


# ---------------------------------------------------------------- governance snapshot
@pytest.mark.parametrize(
    ("raw", "expected"),
    [("ruff=success", ("ruff", "passed")), (" t = FAILURE ", ("t", "failed")), ("x=skipped", ("x", "skipped"))],
)
def test_snapshot_parse_check(raw, expected):
    assert load(SNAP)._parse_check(raw) == expected


def test_snapshot_parse_check_rejects():
    with pytest.raises(ValueError, match="expected name=status"):
        load(SNAP)._parse_check("nonsense")


def test_snapshot_main(tmp_path, monkeypatch):
    m = load(SNAP)
    monkeypatch.setenv("GITHUB_SHA", "abc")
    out = tmp_path / "r" / "s.json"
    assert m.main(["--check", "a=success", "--check", "b=passed", "--out", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "passed" and data["sha"] == "abc" and len(data["checks"]) == 2
    assert m.main(["--check", "a=success", "--check", "b=failure", "--out", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["status"] == "failed"
    assert m.main(["--out", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["status"] == "failed"


# ---------------------------------------------------------------- authority integrity
def test_authority_integrity_repo_pass(capsys):
    assert load(AUTH).main() == 0
    assert "AUTHORITY_INTEGRITY_PASS" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("text", "message"),
    [
        (None, "manifest.yaml missing"),
        ("authorities: {}\n", "registry missing or empty"),
        ("authorities:\n  a: 1\n", "is not a mapping"),
        ("authorities:\n  a: {authority_class: x}\n", "has no logical_id"),
        ("authorities:\n  a: {logical_id: L, authority_class: nope}\n", "invalid authority_class"),
    ],
)
def test_authority_integrity_failures(tmp_path, monkeypatch, text, message):
    m = load(AUTH)
    manifest = tmp_path / "manifest.yaml"
    if text is not None:
        _write(manifest, text)
    monkeypatch.setattr(m, "MANIFEST", manifest)
    with pytest.raises(SystemExit, match=message):
        m.main()


# ---------------------------------------------------------------- workflow registration guard
@pytest.mark.parametrize(
    ("name", "text", "needle"),
    [
        ("w.yml", 'name: x\n"on": push\njobs:\n  a: {runs-on: x}\n', None),
        ("w.yml", "on: push\njobs:\n  a: {}\n", "must be quoted"),
        ("validate.yml", '"on": push\nx: &governance_paths [a]\njobs:\n  a: {}\n', "anchors are not admitted"),
        ("w.yml", '"on": [push\n', "YAML parse failed"),
        ("w.yml", "- 1\n", "root must be a mapping"),
        ("w.yml", "name: x\njobs:\n  a: {}\n", "no string 'on' key"),
        ("w.yml", '"on": push\njobs: {}\n', "no jobs mapping"),
    ],
)
def test_workflow_guard_check(tmp_path, name, text, needle):
    errors = load(WFGUARD).check(_write(tmp_path / name, text))
    if needle is None:
        assert errors == []
    else:
        assert any(needle in e for e in errors)


def test_workflow_guard_main(tmp_path, monkeypatch, capsys):
    m = load(WFGUARD)
    monkeypatch.setattr(m, "TARGETS", [ROOT / t for t in m.TARGETS])
    assert m.main() == 0
    monkeypatch.setattr(m, "TARGETS", [_write(tmp_path / "bad.yml", "on: x\n")])
    assert m.main() == 1
    out = capsys.readouterr().out
    assert "PASS " in out and "FAIL " in out
