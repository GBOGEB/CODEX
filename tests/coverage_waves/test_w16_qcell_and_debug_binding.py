"""Coverage wave 16 (L3): QCELL v0.7.7 visual-control check and receipt emitter,
plus the QPS debug-runtime KEB binding consumer.

The real tracked QCELL artifacts are read only; tamper paths use tmp copies.
``defusedxml`` (absent in CI) is shimmed with the stdlib parser.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import types
import xml.etree.ElementTree as StdET

import pytest

from tests.coverage_waves._loader import ROOT, load

QDIR = ROOT / "qcell_svg_model" / "v0_7_7"
CHECK = QDIR / "scripts" / "check_qcell_visual_control.py"
EMIT = "qcell_svg_model/v0_7_7/scripts/emit_qcell_visual_receipt.py"
DEBUG = "runtime/debug/qps_debug_federation_consumer.py"
SHA = "a" * 40


@pytest.fixture
def check_mod(monkeypatch):
    shim = types.ModuleType("defusedxml")
    shim.ElementTree = StdET
    monkeypatch.setitem(sys.modules, "defusedxml", shim)
    monkeypatch.setitem(sys.modules, "defusedxml.ElementTree", StdET)
    spec = importlib.util.spec_from_file_location("l3cw_qcell_check_visual_control", CHECK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- visual control check
def test_qcell_check_passes_on_tracked_artifacts(check_mod, capsys):
    assert check_mod.main() == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "PASS" and out["forbidden_overlaps"] == 0 and out["engineering_promotion_authority"] is False


def test_qcell_overlap_helper(check_mod):
    a = {"x": 0, "y": 0, "w": 10, "h": 10}
    assert check_mod.overlaps(a, {"x": 5, "y": 5, "w": 10, "h": 10}) is True
    assert check_mod.overlaps(a, {"x": 10, "y": 0, "w": 5, "h": 5}) is False


def _svg_variant(tmp_path, monkeypatch, mod, old, new):
    text = mod.SVG.read_text(encoding="utf-8")
    assert old in text, old
    p = tmp_path / "q.svg"
    p.write_text(text.replace(old, new), encoding="utf-8")
    monkeypatch.setattr(mod, "SVG", p)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ('id="outerHeatRev"', 'id="gone1"'),
        ('id="heatArrowInner"', 'id="gone2"'),
        ('class="txt small white"', 'class="txt small"'),
        ('fill="#0618aa"', 'fill="#000001"'),
    ],
)
def test_qcell_check_rejects_svg_tamper(check_mod, tmp_path, monkeypatch, capsys, old, new):
    _svg_variant(tmp_path, monkeypatch, check_mod, old, new)
    with pytest.raises(SystemExit) as exc:
        check_mod.main()
    assert exc.value.code == 1
    assert "REJECT:" in capsys.readouterr().out


def test_qcell_check_rejects_missing_artifact_and_overlap(check_mod, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(check_mod, "HTML", QDIR / "docs" / "l3_never_created.html")
    with pytest.raises(SystemExit):
        check_mod.main()
    monkeypatch.setattr(check_mod, "HTML", QDIR / "docs" / "index.html")
    boxes = json.loads(check_mod.BOXES.read_text(encoding="utf-8"))
    excl = [b for b in boxes["boxes"] if b.get("class") == "exclusive"]
    excl[1].update(x=excl[0]["x"], y=excl[0]["y"])
    p = tmp_path / "boxes.json"
    p.write_text(json.dumps(boxes), encoding="utf-8")
    monkeypatch.setattr(check_mod, "BOXES", p)
    with pytest.raises(SystemExit):
        check_mod.main()
    assert "forbidden exclusive-box overlaps" in capsys.readouterr().out


# ---------------------------------------------------------------- receipt emitter
def _render_dirs(tmp_path, html_override=None):
    a, b = tmp_path / "a", tmp_path / "b"
    for d in (a, b):
        d.mkdir()
        shutil.copyfile(QDIR / "svg" / "qcell_main_v0_7_7.svg", d / "qcell_main_v0_7_7.svg")
        shutil.copyfile(QDIR / "docs" / "index.html", d / "index.html")
    if html_override is not None:
        (b / "index.html").write_text(html_override, encoding="utf-8")
    return a, b


def test_emit_receipt_pass(tmp_path, monkeypatch, capsys):
    m = load(EMIT)
    a, b = _render_dirs(tmp_path)
    out = tmp_path / "o" / "r.json"
    monkeypatch.setattr("sys.argv", ["e", "--producer-sha", SHA, "--render-a-dir", str(a), "--render-b-dir", str(b),
                                     "--out", str(out)])
    assert m.main() == 0
    rec = json.loads(out.read_text(encoding="utf-8"))
    assert rec["producer_sha"] == SHA and rec["collision_state"] == "PASS" and rec["render_determinism"] == "PASS"
    assert rec["svg_sha256"] == m.sha256_text(m.read_text(a / "qcell_main_v0_7_7.svg"))
    assert json.loads(capsys.readouterr().out) == rec


@pytest.mark.parametrize(
    ("sha", "html", "message"),
    [("ABC", None, "40-character lowercase"), (SHA, "<html>different</html>", "not byte-identical")],
)
def test_emit_receipt_rejects(tmp_path, monkeypatch, capsys, sha, html, message):
    m = load(EMIT)
    a, b = _render_dirs(tmp_path, html)
    monkeypatch.setattr("sys.argv", ["e", "--producer-sha", sha, "--render-a-dir", str(a), "--render-b-dir", str(b),
                                     "--out", str(tmp_path / "r.json")])
    with pytest.raises(SystemExit) as exc:
        m.main()
    assert exc.value.code == 1 and message in capsys.readouterr().err


def test_emit_receipt_rejects_policy_and_drift(tmp_path, monkeypatch, capsys):
    import yaml
    m = load(EMIT)
    model = yaml.safe_load(m.SSOT.read_text(encoding="utf-8"))
    model["main_policy"]["big_teaching_arrows_default_visible"] = True
    ssot = tmp_path / "ssot.yaml"
    ssot.write_text(yaml.safe_dump(model), encoding="utf-8")
    monkeypatch.setattr(m, "SSOT", ssot)
    a, b = _render_dirs(tmp_path)
    monkeypatch.setattr("sys.argv", ["e", "--producer-sha", SHA, "--render-a-dir", str(a), "--render-b-dir", str(b),
                                     "--out", str(tmp_path / "r.json")])
    with pytest.raises(SystemExit):
        m.main()
    assert "big teaching arrows must remain OFF" in capsys.readouterr().err
    monkeypatch.setattr(m, "SSOT", QDIR / "src" / "qcell_main_v0_7_7.yaml")
    for d in (a, b):
        (d / "qcell_main_v0_7_7.svg").write_text("<svg/>", encoding="utf-8")
    with pytest.raises(SystemExit):
        m.main()
    assert "differs from tracked canonical SVG" in capsys.readouterr().err


def test_emit_collision_state_rejects_overlap(tmp_path, monkeypatch, capsys):
    m = load(EMIT)
    boxes = json.loads(m.BOXES.read_text(encoding="utf-8"))
    excl = [b for b in boxes["boxes"] if b.get("class") == "exclusive"]
    excl[1].update(x=excl[0]["x"], y=excl[0]["y"])
    p = tmp_path / "boxes.json"
    p.write_text(json.dumps(boxes), encoding="utf-8")
    monkeypatch.setattr(m, "BOXES", p)
    with pytest.raises(SystemExit):
        m.collision_state()
    assert "forbidden exclusive-box overlap" in capsys.readouterr().err


# ---------------------------------------------------------------- QPS debug binding consumer
GOOD_ENVELOPE = {"producer": "GBOGEB/cryoplant-project", "status": "ACCEPT", "exact_head_sha": "abc",
                 "envelope_sha256": "e", "minimum_victory_condition": {"runtime_steps_gt_zero": True,
                                                                     "recursive_audit_pass": True}}
GOOD_FED = {"source": {"repository": "GBOGEB/cryoplant-project", "exact_sha": "s", "payload_hash_match": True},
            "execution": {"real_probe_steps": 5, "probe_status": "ACCEPT", "dov_status": "PASS"},
            "adapter": {"surface_present": True, "surface_state": "READY", "surface_probe_returncode": 0},
            "authority_guards": {"qps_repo_local_runner_gate": "WITHHELD_EXTERNAL"}, "receipt_sha256": "r"}


def test_debug_evaluate_repo_local():
    m = load(DEBUG)
    ok = m.evaluate_repo_local(GOOD_ENVELOPE)
    assert ok["accept"] is True and ok["checks"]["repo_local_runner_recovered"] is True
    bad = m.evaluate_repo_local(dict(GOOD_ENVELOPE, exact_head_sha="UNKNOWN"))
    assert bad["accept"] is False and bad["checks"]["exact_head_sha_present"] is False


def test_debug_evaluate_federated_direct_and_durable():
    m = load(DEBUG)
    durable = m.evaluate_federated(GOOD_FED)
    assert durable["accept"] is True and durable["source_receipt_sha256"] == "r"
    direct = dict(GOOD_FED)
    direct.pop("execution")
    direct.update(real_probe_steps=1, probe_status="ACCEPT", dov_status="PASS", original_receipt_sha256="o")
    res = m.evaluate_federated(direct)
    assert res["accept"] is True and res["source_receipt_sha256"] == "o"
    gated = dict(GOOD_FED, authority_guards={})
    assert m.evaluate_federated(gated)["accept"] is False
    assert m.evaluate_federated({})["checks"]["runtime_steps_gt_zero"] is False


def test_debug_load_json_from_file_env_or_none(tmp_path, monkeypatch):
    m = load(DEBUG)
    p = tmp_path / "e.json"
    p.write_text('{"a": 1}', encoding="utf-8")
    assert m.load_json(p, "L3_UNUSED") == {"a": 1}
    monkeypatch.setenv("L3_ENV_JSON", '{"b": 2}')
    assert m.load_json(tmp_path / "missing.json", "L3_ENV_JSON") == {"b": 2}
    monkeypatch.delenv("L3_ENV_JSON")
    assert m.load_json(None, "L3_ENV_JSON") is None


@pytest.mark.parametrize(
    ("argv", "env", "status", "mode"),
    [
        (["--federated-receipt"], None, "ACCEPT", "FEDERATED_EXACT_PAYLOAD"),
        (["--envelope"], None, "ACCEPT", "QPS_REPO_LOCAL"),
        ([], None, "DEFER", "NONE"),
    ],
)
def test_debug_main_writes_binding(tmp_path, monkeypatch, capsys, argv, env, status, mode):
    m = load(DEBUG)
    monkeypatch.setattr(m, "OUT", tmp_path / "gen")
    monkeypatch.delenv("QPS_FEDERATED_DEBUG_RECEIPT_JSON", raising=False)
    monkeypatch.delenv("QPS_DEBUG_ENVELOPE_JSON", raising=False)
    args = list(argv)
    if argv == ["--federated-receipt"]:
        p = tmp_path / "f.json"
        p.write_text(json.dumps(GOOD_FED), encoding="utf-8")
        args.append(str(p))
    elif argv == ["--envelope"]:
        p = tmp_path / "e.json"
        p.write_text(json.dumps(GOOD_ENVELOPE), encoding="utf-8")
        args.append(str(p))
    monkeypatch.setattr("sys.argv", ["d", *args])
    assert m.main() == 0
    binding = json.loads((tmp_path / "gen" / "qps_debug_keb_binding.json").read_text(encoding="utf-8"))
    assert binding["status"] == status and binding["evidence_mode"] == mode
    assert binding["authority_guards"]["engineering_authority_transfer"] is False
    assert len(binding["binding_sha256"]) == 64 and json.loads(capsys.readouterr().out)["status"] == status
