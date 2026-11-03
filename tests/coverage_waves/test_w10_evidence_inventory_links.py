"""Coverage wave 10 (L3): OCR evidence runtime, multi-format inventory V2,
docs link checker and QPS/DOW/KEB bridge-row validator.
"""
from __future__ import annotations

import hashlib
import json

import pytest
import yaml

from tests.coverage_waves._loader import load, run_main

OCR = "src/evidence/ocr_evidence_runtime_v1.py"
INV = "src/inventory/multiformat_inventory_v2.py"
LINKS = "scripts/check_links.py"
ROWS = "scripts/validate_bridge_rows.py"


def _write(path, text, mode="t"):
    path.parent.mkdir(parents=True, exist_ok=True)
    if mode == "b":
        path.write_bytes(text)
    else:
        path.write_text(text, encoding="utf-8")
    return path


# ---------------------------------------------------------------- OCR evidence runtime
def _asset(m, fmt, **kw):
    return m.EvidenceAsset("a", "p", fmt, 1, "h", **kw)


@pytest.mark.parametrize(
    ("fmt", "kw", "decision", "conf"),
    [
        ("DWG", {}, "defer_dwg_render", 0.0),
        ("SVG", {"semantic_vector_confidence": 0.8}, "skip", 0.8),
        ("DRAWIO", {"semantic_vector_confidence": 0.5}, "conditional", 0.5),
        ("PDF", {"embedded_text_chars": 80}, "skip", 0.85),
        ("PDF", {"embedded_text_chars": 10}, "required", 0.65),
        ("IMAGE", {"raster_confidence": 0.7}, "conditional", 0.7),
        ("HTML", {}, "conditional", 0.5),
    ],
)
def test_ocr_decisions(fmt, kw, decision, conf):
    m = load(OCR)
    side = m.OCREvidenceRuntime().decide_ocr(_asset(m, m.EvidenceFormat[fmt], **kw))
    assert side.decision.value == decision and side.confidence == conf


def test_ocr_promotion_rules():
    m = load(OCR)
    rt = m.OCREvidenceRuntime()
    D = m.OCRDecision
    assert rt.may_promote_ocr(m.OCRSidecar("a", D.REQUIRED, 0.95)) is True
    assert rt.may_promote_ocr(m.OCRSidecar("a", D.REQUIRED, 0.90)) is False
    assert rt.may_promote_ocr(m.OCRSidecar("a", D.SKIP, 0.99)) is False
    assert rt.may_promote_ocr(m.OCRSidecar("a", D.CONDITIONAL, 0.99, warnings=["w"])) is False


def test_ocr_lineage_and_json():
    m = load(OCR)
    rt = m.OCREvidenceRuntime()
    asset = _asset(m, m.EvidenceFormat.PDF, embedded_text_chars=0)
    side = m.OCRSidecar("a", m.OCRDecision.REQUIRED, 0.95)
    lin = rt.build_lineage(asset, side)
    assert lin.derived_artifacts == ["ocr_sidecar"] and side.promoted_to_authoritative is True
    skip = rt.build_lineage(asset, m.OCRSidecar("a", m.OCRDecision.SKIP, 1.0))
    assert skip.derived_artifacts == [] and skip.evidence_primary is True
    data = json.loads(rt.to_json(lin))
    assert data["sidecar"]["decision"] == "required" and data["preservation_policy"] == "preserve_full_frame"


def test_ocr_asset_from_path(tmp_path):
    m = load(OCR)
    pdf = _write(tmp_path / "d" / "x.PDF", b"%PDF-1", "b")
    a = m.OCREvidenceRuntime.asset_from_path(pdf, root=tmp_path)
    digest = hashlib.sha256(b"%PDF-1").hexdigest()
    assert (a.source_format, a.sha256, a.asset_id, a.size_bytes) == (m.EvidenceFormat.PDF, digest, digest[:16], 6)
    assert a.path.replace("\\", "/") == "d/x.PDF"
    odd = m.OCREvidenceRuntime.asset_from_path(_write(tmp_path / "y.bin", b"z", "b"))
    assert odd.source_format == m.EvidenceFormat.UNKNOWN and odd.path == str(tmp_path / "y.bin")


@pytest.mark.xfail(
    strict=True,
    reason=(
        "production_defect: OCREvidenceRuntime.asset_from_path maps the file extension straight onto "
        "EvidenceFormat values, so .png/.jpg files (enum value 'image') become UNKNOWN and lose the "
        "image-is-primary-evidence OCR policy"
    ),
)
def test_ocr_png_is_classified_as_image(tmp_path):
    m = load(OCR)
    a = m.OCREvidenceRuntime.asset_from_path(_write(tmp_path / "skid.png", b"\x89PNG", "b"))
    assert a.source_format == m.EvidenceFormat.IMAGE


def test_ocr_main_demo(capsys):
    run_main(OCR)
    data = json.loads(capsys.readouterr().out)
    assert data["sidecar"]["decision"] == "conditional" and data["sidecar"]["promoted_to_authoritative"] is False


# ---------------------------------------------------------------- multi-format inventory
def test_inventory_scan_records_tags_and_duplicates(tmp_path):
    m = load(INV)
    _write(tmp_path / "QPLANT-WCS-floor-plan.svg", "<svg><title>PCW  loop</title><text>MIS interlock</text></svg>")
    _write(tmp_path / "copy" / "dup.svg", "<svg><title>PCW  loop</title><text>MIS interlock</text></svg>")
    _write(tmp_path / "page.html", "<html><script>x()</script><style>p{}</style><p>HVAC  roof routing</p></html>")
    _write(tmp_path / "plain.svg", "<svg/>")
    _write(tmp_path / "skip.txt", "ignored")
    for name in ("a.pptx", "b.xlsx", "c.docx", "d.pdf", "e.png", "f.vsdx", "g.drawio", "h.dwg"):
        _write(tmp_path / name, name)
    inv = m.MultiFormatInventoryV2(tmp_path)
    recs = {r.path.replace("\\", "/"): r for r in inv.scan()}
    assert "skip.txt" not in recs and len(recs) == 12
    svg = recs["QPLANT-WCS-floor-plan.svg"]
    assert svg.summary == "PCW loop; MIS interlock" and svg.extractor == "svg_text_nodes"
    assert {"QPLANT", "WCS", "PCW", "MIS"} <= set(svg.category_tags) and svg.drawing_type == "Floor plan"
    assert svg.naming_group == "QPLANT_WCS_FLOOR_PLAN"
    assert svg.duplicate_group is not None and svg.duplicate_group == recs["copy/dup.svg"].duplicate_group
    assert recs["page.html"].summary == "HVAC roof routing" and recs["page.html"].drawing_type == "Roof routing"
    assert recs["plain.svg"].summary.startswith("SVG found, no title")
    assert recs["h.dwg"].extractor == "dwg_render_then_ocr_contract" and recs["a.pptx"].duplicate_group is None
    payload = json.loads(inv.to_json(list(recs.values())))
    assert payload["schema"] == "edcp.multiformat_inventory.v2" and len(payload["records"]) == 12


def test_inventory_helpers():
    m = load(INV)
    I = m.MultiFormatInventoryV2
    assert I._naming_group("a b") == "UNGROUPED"
    assert I._naming_group("one two three four five") == "ONE_TWO_THREE_FOUR"
    assert I._classify_drawing_type("nothing here") is None
    assert I._classify_tags("no tags") == []
    assert m.BaseExtractor().extract_summary(None).startswith("Extraction not implemented")
    assert I(m.Path(".")) ._plugin_for(m.Path("x.unknown")) is None


@pytest.mark.xfail(
    strict=True,
    reason=(
        "production_defect: multiformat_inventory_v2 DRAWING_TYPE_PATTERNS matches 'PID' without word "
        "boundaries (case-insensitive), so names like 'rapid_prototype' are classified as P&ID drawings"
    ),
)
def test_inventory_rapid_is_not_a_pid():
    m = load(INV)
    assert m.MultiFormatInventoryV2._classify_drawing_type("rapid_prototype.pdf") is None


@pytest.mark.xfail(
    strict=True,
    reason=(
        "production_defect: multiformat_inventory_v2 tags on path.name, where underscores are word characters, "
        "so \bQPLANT\b-style patterns never match underscore-delimited names such as QPLANT_WCS_layout.pdf "
        "(the underscore-free name_text it computes is only used for naming groups)"
    ),
)
def test_inventory_tags_underscore_delimited_names(tmp_path):
    m = load(INV)
    _write(tmp_path / "QPLANT_WCS_layout.pdf", "x")
    (rec,) = m.MultiFormatInventoryV2(tmp_path).scan()
    assert {"QPLANT", "WCS"} <= set(rec.category_tags)


def test_inventory_main(tmp_path, capsys):
    _write(tmp_path / "x.pdf", "pdf")
    run_main(INV, [str(tmp_path)])
    assert json.loads(capsys.readouterr().out)["records"][0]["extension"] == ".pdf"


# ---------------------------------------------------------------- check_links (runs against cwd)
def test_check_links_passes_on_clean_tree(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / "docs" / "index.html", '<a href="sub/p.html#x">p</a><img src="img.png">'
                                             '<a href="https://e.com">e</a><a href="#top">t</a>'
                                             '<a href="/sub/p.html">abs</a><a href="../outputs/r.html">o</a>'
                                             '<a href="?q=1">q</a>')
    _write(tmp_path / "docs" / "sub" / "p.html", "<p/>")
    _write(tmp_path / "docs" / "img.png", "x")
    _write(tmp_path / "outputs" / "r.html", "x")
    _write(tmp_path / "docs" / "notes.md", "[a](sub/p.html) ![b](img.png)")
    _write(tmp_path / "docs" / "cfg.yaml", "page_url: docs/sub/p.html\nlogo_path: ./img.png\nname: plain\n"
                                          "root_file: /docs/index.html\nweird_link: x.css:\n")
    _write(tmp_path / "docs" / "s.css", "a{background:url(img.png)}")
    _write(tmp_path / "README.md", "[d](docs/index.html)")
    run_main(LINKS)
    assert "link check passed" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("rel", "text", "needle"),
    [
        ("docs/a.html", '<a href="missing.html">x</a>', "broken link"),
        ("docs/a.html", '<a href="../secret.txt">x</a>', "link escapes docs root"),
        ("docs/a.html", '<a href="../../../outside.html">x</a>', "link escapes docs root"),
        ("docs/a.md", "[x](nope.md)", "broken link"),
        ("docs/a.md", "[x](../../../../escape.md)", "link escapes repo root"),
        ("docs/a.yml", "doc_path: missing/page.html\n", "broken link"),
        ("docs/a.yml", "doc_path: ../nope.md\n", "broken link"),
        ("docs/a.css", "b{background:url(gone.css)}", "broken link"),
        ("docs/a.md", "[x](/abs/missing.md)", "broken link"),
    ],
)
def test_check_links_reports(tmp_path, monkeypatch, rel, text, needle):
    work = tmp_path / "repo"
    work.mkdir()
    monkeypatch.chdir(work)
    _write(work / rel, text)
    with pytest.raises(SystemExit, match=needle):
        run_main(LINKS)


# ---------------------------------------------------------------- bridge rows
def _rows():
    lineage = {"chat_session": "c", "originating_prompt": "p", "created_by": "me"}
    q = {k: "v" for k in load(ROWS).REQUIRED["qps_rows"]}
    q.update(lineage=lineage, receipt_binding={"source_pr": "1", "source_sha": "s", "file_digest": "d"})
    d = {k: "v" for k in load(ROWS).REQUIRED["dow_rows"]}
    d["lineage"] = lineage
    k = {x: "v" for x in load(ROWS).REQUIRED["keb_rows"]}
    k["lineage"] = lineage
    return {"qps_rows": [q], "dow_rows": [d], "keb_rows": [k]}


@pytest.mark.parametrize(
    ("value", "allow", "missing"),
    [(None, True, True), ("  ", True, True), ("tbd", False, True), ("TBD", True, False), (0, False, False)],
)
def test_is_missing(value, allow, missing):
    assert load(ROWS).is_missing(value, allow) is missing


def test_bridge_rows_validators():
    m = load(ROWS)
    assert m.validate_lineage("r", "x") == ["r: lineage must be a mapping"]
    assert m.validate_lineage("r", {"chat_session": "TBD"})[0] == "r: lineage.chat_session is required"
    assert m.validate_receipt_binding("r", 3, True) == ["r: receipt_binding must be a mapping"]
    assert len(m.validate_receipt_binding("r", {"source_pr": "TBD"}, allow_tbd=True)) == 2
    assert m.validate_group("qps_rows", "x", True) == ["qps_rows: must be a list"]
    errs = m.validate_group("dow_rows", ["junk", {"dow_item_id": "TBD"}], allow_tbd=False)
    assert errs[0] == "dow_rows[0]: row must be a mapping" and "dow_rows[1]: dow_item_id is required" in errs


def test_bridge_rows_main_draft_and_strict(tmp_path, monkeypatch, capsys):
    m = load(ROWS)
    data = _rows()
    good = _write(tmp_path / "g.yaml", yaml.safe_dump(data))
    monkeypatch.setattr("sys.argv", ["v", str(good)])
    assert m.main() == 0
    data["dow_rows"][0]["reason"] = "TBD"
    tbd = _write(tmp_path / "t.yaml", yaml.safe_dump(data))
    monkeypatch.setattr("sys.argv", ["v", str(tbd)])
    assert m.main() == 0
    monkeypatch.setattr("sys.argv", ["v", str(tbd), "--strict"])
    assert m.main() == 1
    out = capsys.readouterr().out
    assert "draft mode" in out and "- dow_rows[0]: reason is required" in out
    with pytest.raises(ValueError):
        m.load_yaml(_write(tmp_path / "l.yaml", "- 1\n"))
    assert m.load_yaml(_write(tmp_path / "e.yaml", "")) == {}


def test_bridge_rows_repo_sample_draft_mode():
    m = load(ROWS)
    data = m.load_yaml(m.Path(__file__).resolve().parents[2] / "ssot/bridge_rows/sample_qps_dow_keb_receipts.yaml")
    errs = [e for g in ("qps_rows", "dow_rows", "keb_rows") for e in m.validate_group(g, data.get(g), True)]
    assert errs == []
