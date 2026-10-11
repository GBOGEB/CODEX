"""House-style post-processing and QA gate (tools/house_style)."""
from pathlib import Path

import pytest

docx = pytest.importorskip("docx")
pytest.importorskip("pptx")

from tools.house_style import qps_post, qps_qa

ROOT = Path(__file__).resolve().parents[1]
STARTER = ROOT / "tools" / "house_style" / "templates" / "QPS_House_starter.docx"


class Meta:
    title = "VCR Handover Summary"
    subtitle = "Handover report"
    project = "MINERVA - Cryoplant - QPS - VCR"
    author = "Test Author"
    ref = "SCK CEN/12345678"
    third_party_ref = ""
    version = "0.1"
    status = "Draft"
    classification = "Restricted"
    date = "2026-10-11"
    short = False


def _house_doc(tmp_path, heading="Requirements"):
    d = docx.Document(str(STARTER))
    d.add_paragraph(heading, style="Heading 1")
    d.add_paragraph("Body text.")
    t = d.add_table(rows=2, cols=2)
    t.cell(0, 0).text, t.cell(0, 1).text = "ID", "Item"
    src = tmp_path / "src.docx"
    d.save(str(src))
    return src


def test_bare_starter_document_is_not_publishable(tmp_path):
    rep = qps_qa.check_docx(str(_house_doc(tmp_path)))
    rules = {i["rule"] for i in rep.items if i["level"] == "FAIL"}
    assert not rep.ok
    assert {"front matter", "title page", "header/footer"} <= rules


def test_post_adds_minerva_front_matter_and_footer_fields(tmp_path):
    out = tmp_path / "out.docx"
    qps_post.post_docx(str(_house_doc(tmp_path)), str(out), Meta, keep=True)
    rep = qps_qa.check_docx(str(out))
    assert rep.ok, rep.markdown()
    texts = [p.text for p in docx.Document(str(out)).paragraphs]
    for heading in qps_qa.FRONT_MATTER:
        assert heading in texts
    assert "SCK CEN Ref.: SCK CEN/12345678" in texts


def test_fix_strips_typed_heading_numbers_and_off_palette_colour(tmp_path):
    d = docx.Document(str(STARTER))
    d.add_paragraph("2. Quality Controls", style="Heading 1")
    run = d.add_paragraph().add_run("red text")
    run.font.color.rgb = docx.shared.RGBColor(0xFF, 0x00, 0x00)
    src = tmp_path / "src.docx"
    d.save(str(src))
    out = tmp_path / "fixed.docx"
    qps_post.post_docx(str(src), str(tmp_path / "staged.docx"), Meta, keep=True)
    qps_qa.fix_docx(str(tmp_path / "staged.docx"), str(out), Meta)
    rep = qps_qa.check_docx(str(out))
    assert rep.ok, rep.markdown()
    fixed = docx.Document(str(out))
    assert "Quality Controls" in [p.text for p in fixed.paragraphs]


@pytest.mark.parametrize("value,ok", [("562873", True), ("984A9C", True), ("EEE4F5", True),
                                      ("333333", True), ("FF0000", False), ("1D7A5F", False)])
def test_palette_rules(value, ok):
    assert qps_qa.colour_ok(value) is ok


def test_nearest_palette_colour():
    assert qps_qa.nearest("003366") == "034694"


@pytest.mark.skipif(not Path(qps_post.PPTX_REF).exists(), reason="corporate slide master is built locally")
def test_foreign_deck_is_rehosted_and_publishable(tmp_path):
    from pptx import Presentation
    src = tmp_path / "foreign.pptx"
    prs = Presentation()
    s = prs.slides.add_slide(prs.slide_layouts[1])
    s.shapes.title.text = "Scope"
    s.placeholders[1].text = "One\nTwo"
    prs.save(str(src))
    out = tmp_path / "out.pptx"
    qps_qa.fix_pptx(str(src), str(out), Meta)
    assert qps_qa.check_pptx(str(out)).ok
