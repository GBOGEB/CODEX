"""Coverage wave 12 (L3): PPTX slide-preview generator and the W111 / gg_MATH
receipt gates (real-repo PASS paths read-only, tamper paths on tmp copies)."""
from __future__ import annotations

import copy
import json

import pytest

from tests.coverage_waves._loader import load, run_main

SLIDES = "src/tools/slide_preview_generator.py"
NORM = "scripts/normalize_qps_w111_dow_return.py"
BRIDGE111 = "scripts/validate_qps_w111_power_utility_bridge.py"
GGMATH = "scripts/validate_gg_math_temporal_pca_knowledge_atom.py"


# ---------------------------------------------------------------- slide preview generator
def _deck(tmp_path):
    pptx = pytest.importorskip("pptx")
    prs = pptx.Presentation()
    s1 = prs.slides.add_slide(prs.slide_layouts[0])
    s1.shapes.title.text = "QPLANT OVERVIEW"
    s2 = prs.slides.add_slide(prs.slide_layouts[1])
    s2.shapes.title.text = "Scope <draft>"
    s2.placeholders[1].text = "- item one"
    s3 = prs.slides.add_slide(prs.slide_layouts[5])
    s3.shapes.title.text = "Plain notes"
    prs.slides.add_slide(prs.slide_layouts[6])
    path = tmp_path / "deck.pptx"
    prs.save(str(path))
    return path


def test_extract_slides_style_hints(tmp_path):
    m = load(SLIDES)
    slides = m.extract_slides(_deck(tmp_path))
    assert [s["n"] for s in slides] == [1, 2, 3, 4]
    assert slides[0]["style_hint"] == {"bg": "#f0f8ff", "is_title": True}
    assert slides[1]["bullets"] == 1 and slides[1]["style_hint"]["bg"] == "#ffffff"
    assert slides[2]["style_hint"]["bg"] == "#fafafa" and slides[3]["texts"] == []
    assert len(m.extract_slides(_deck(tmp_path), limit=2)) == 2


def test_digital_twins_and_html(tmp_path):
    m = load(SLIDES)
    slides = [{"n": 1, "texts": ["T <x>", "a", "b", "c", "d", "e"], "shape_count": 2, "bullets": 0,
               "style_hint": {"bg": "#fff"}},
              {"n": 2, "texts": [], "shape_count": 0, "bullets": 0}]
    twins = m.build_digital_twins([dict(slides[0])])
    assert twins[0]["summary"] == ["T <x>", "a", "b"] and twins[0]["slide"] == 1
    out = tmp_path / "p.html"
    m.write_html_preview(slides, out)
    html = out.read_text(encoding="utf-8")
    assert "Slide Preview (2 slides)" in html and "T &lt;x&gt;" in html and "<x>" not in html
    assert html.count("class='para'") == 4 and "background:#ffffff" in html


def test_slides_main_writes_three_artifacts(tmp_path, capsys):
    m = load(SLIDES)
    deck = _deck(tmp_path)
    out = tmp_path / "out"
    assert m.main(["--pptx", str(deck), "--outdir", str(out), "--limit", "3"]) == 0
    assert len(json.loads((out / "slide_texts.json").read_text(encoding="utf-8"))) == 3
    assert (out / "slide_digital_twins.json").is_file() and (out / "slide_preview.html").is_file()
    assert capsys.readouterr().out.count("WROTE:") == 3


def test_slides_presentation_fallback_raises(monkeypatch):
    import builtins
    import sys

    real_import = builtins.__import__

    def no_pptx(name, *a, **k):
        if name == "pptx" or name.startswith("pptx."):
            raise ImportError("no pptx")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", no_pptx)
    monkeypatch.delitem(sys.modules, "l3cw_src_tools_slide_preview_generator_nopptx", raising=False)
    import importlib.util

    from tests.coverage_waves._loader import ROOT
    spec = importlib.util.spec_from_file_location("l3cw_src_tools_slide_preview_generator_nopptx",
                                                  ROOT / SLIDES)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with pytest.raises(ImportError, match="python-pptx is required"):
        mod.Presentation("x")


# ---------------------------------------------------------------- W111 DOW return normalizer
def _dow(m):
    return json.loads(m.DEFAULT_DOW.read_text(encoding="utf-8"))


def test_w111_normalize_repo_receipt():
    m = load(NORM)
    res = m.normalize(_dow(m), "abc")
    assert res["semantic_normalization"] == "PASS_NO_NUMERIC_MUTATION"
    assert res["dow_receipt_file_sha256"] == "abc" and res["payload_digest_preserved"] is True
    assert res["output_payload_sha256"] == res["input_payload_sha256"] == m.EXPECTED_PAYLOAD_SHA256


@pytest.mark.parametrize(
    ("path", "value", "message"),
    [
        (("authority_scope",), "GLOBAL", "authority scope mismatch"),
        (("engineering_promotion_forbidden",), False, "promotion guard missing"),
        (("source_contract", "source_ssot_git_blob_sha"), "x", "child SSOT identity mismatch"),
        (("source_contract", "keb_receipt_verified"), False, "did not verify KEB receipt"),
        (("invCOP_screen", "unreconciled_electrical_kW"), 1.0, "residual changed"),
        (("baseload", "status"), "IDENTIFIED", "baseload must remain DEFER"),
        (("pca", "status"), "PASS", "PCA must remain deferred"),
        (("independent_thermophysical_crosscheck", "isothermal_relative_delta"), 0.5, "isothermal crosscheck"),
        (("independent_thermophysical_crosscheck", "isentropic_model_difference_class"), "X",
         "model-form classification changed"),
    ],
)
def test_w111_normalize_rejects_tamper(path, value, message):
    m = load(NORM)
    dow = copy.deepcopy(_dow(m))
    node = dow
    for key in path[:-1]:
        node = node.setdefault(key, {})
    node[path[-1]] = value
    with pytest.raises(AssertionError, match=message):
        m.normalize(dow, "x")


def test_w111_normalize_helpers_and_main(tmp_path, capsys):
    m = load(NORM)
    with pytest.raises(ValueError, match="must be a JSON object"):
        m.load_json(_write(tmp_path / "a.json", "[1]"))
    m.require(True, "never")
    out = tmp_path / "o" / "n.json"
    with pytest.raises(SystemExit) as exc:
        run_main(NORM, ["--output", str(out)])
    assert exc.value.code == 0
    assert json.loads(out.read_text(encoding="utf-8"))["receipt_id"] == "KEB-W111-POWER-UTILITY-RETURN"
    assert "numeric_mutation=false" in capsys.readouterr().out
    bad = _write(tmp_path / "bad.json", "{}")
    with pytest.raises(SystemExit) as exc:
        run_main(NORM, ["--input", str(bad), "--output", str(out)])
    assert exc.value.code == 1
    assert "NORMALIZATION=FAIL" in capsys.readouterr().err


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# ---------------------------------------------------------------- W111 bridge validator
def test_w111_bridge_repo_pass_and_receipt(tmp_path, monkeypatch, capsys):
    m = load(BRIDGE111)
    monkeypatch.setattr("sys.argv", ["v", "--receipt", str(tmp_path / "r" / "rec.json")])
    assert m.main() == 0
    rec = json.loads((tmp_path / "r" / "rec.json").read_text(encoding="utf-8"))
    assert rec["payload_digest_preserved"] is True and rec["dispatch_target"] == "GBOGEB/ABACUS"
    monkeypatch.setattr("sys.argv", ["v"])
    assert m.main() == 0
    assert capsys.readouterr().out.count("QPS_W111_KEB_BRIDGE_VALIDATION=PASS") == 2


def test_w111_bridge_helpers():
    m = load(BRIDGE111)
    assert m.atom_map({"atoms": [{"id": 1, "v": "a"}]}) == {"1": {"id": 1, "v": "a"}}
    assert m.atom_map({}) == {}
    a = m.canonical_payload_sha256({"b": 1, "a": 2})
    assert a == m.canonical_payload_sha256({"a": 2, "b": 1}) and len(a) == 64


def test_w111_bridge_tampered_manifest_fails(tmp_path, monkeypatch, capsys):
    m = load(BRIDGE111)
    manifest = tmp_path / "m.yaml"
    manifest.write_text(m.MANIFEST.read_text(encoding="utf-8").replace("GBOGEB/CODEX", "someone/else", 1),
                        encoding="utf-8")
    monkeypatch.setattr(m, "MANIFEST", manifest)
    monkeypatch.setattr("sys.argv", ["v"])
    with pytest.raises(AssertionError):
        m.main()
    monkeypatch.setattr(m, "MANIFEST", _write(tmp_path / "list.yaml", "- 1\n"))
    with pytest.raises(AssertionError, match="manifest must be a mapping"):
        m.main()


def test_w111_bridge_main_guard_pass(capsys):
    with pytest.raises(SystemExit) as exc:
        run_main(BRIDGE111)
    assert exc.value.code == 0
    assert "payload_digest_preserved=true" in capsys.readouterr().out


# ---------------------------------------------------------------- gg_MATH knowledge atom
def test_ggmath_repo_pass(tmp_path, capsys):
    m = load(GGMATH)
    out = tmp_path / "o" / "r.json"
    with pytest.raises(SystemExit) as exc:
        run_main(GGMATH, ["--source-sha", "deadbeef", "--out", str(out)])
    assert exc.value.code == 0
    rec = json.loads(out.read_text(encoding="utf-8"))
    assert rec["source_control_sha"] == "deadbeef" and rec["authority_transfer"] is False
    assert rec["result"] == "PASS_REAL_KEB_KNOWLEDGE_ATOM_WITH_INDEPENDENT_NUMERIC_DOW"
    assert capsys.readouterr().out.strip() == rec["result"]
    with pytest.raises(SystemExit, match="boom"):
        m.require(False, "boom")


@pytest.mark.parametrize(
    ("key", "value", "message"),
    [("keb_item_id", "BAD", "invalid keb_item_id"), ("keb_item_id", "KEB-ITEM-0009", "unexpected atom id"),
     ("source_pr", 99, "source PR drift"), ("object_type", "X", "not a knowledge atom")],
)
def test_ggmath_tampered_atom(tmp_path, monkeypatch, key, value, message):
    m = load(GGMATH)
    atom = json.loads(m.ATOM.read_text(encoding="utf-8"))
    atom[key] = value
    monkeypatch.setattr(m, "ATOM", _write(tmp_path / "atom.json", json.dumps(atom)))
    monkeypatch.setattr("sys.argv", ["v", "--source-sha", "s", "--out", str(tmp_path / "o.json")])
    with pytest.raises(SystemExit, match=message):
        m.main()


def test_ggmath_missing_fields(tmp_path, monkeypatch):
    m = load(GGMATH)
    monkeypatch.setattr(m, "ATOM", _write(tmp_path / "atom.json", "{}"))
    monkeypatch.setattr("sys.argv", ["v", "--source-sha", "s", "--out", str(tmp_path / "o.json")])
    with pytest.raises(SystemExit, match="missing required fields"):
        m.main()
