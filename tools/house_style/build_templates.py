"""Build the QPS house templates from a CODEX Word master.

Usage: python3 tools/house_style/build_templates.py <Word master .docx> <authoritative deck .pptx> [outdir]
  e.g. Full_VCR_Handover_master.docx ~/Downloads/QPS_MTBF_WCS_DMAIC_v7.pptx   (outdir defaults to templates/)

Outputs
  QPS_House_starter.docx  Word reference doc (styles, numbering, corporate header/footer, empty body)
  QPS_House.dotx          same, as a Word template
  QPS_House.pptx          SCK CEN 2020 slide master (all layouts, no slides, no ECM identity of the source deck)
  QPS_House.potx          same, as a PowerPoint template
  QPS_House.source.txt    source deck name, size and SHA-256 of this local build
"""
import datetime as dt
import hashlib
import os
import sys
import zipfile
from pathlib import Path

import docx
from pptx import Presentation

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE / "templates"

try:
    from . import qps_post
except ImportError:  # run as a script
    sys.path.insert(0, str(HERE))
    import qps_post

# The deck the slide master is cut from (see README "Authoritative references").
REFERENCE_DECK = ("QPS_MTBF_WCS_DMAIC_v7.pptx", "c31553f29d7c590c748165cd3d5b882e9cb69f849c372aa6d2078c786b1a4556")


def swap_content_type(src, dst, old, new):
    zin = zipfile.ZipFile(src)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            data = zin.read(it.filename)
            if it.filename == "[Content_Types].xml":
                data = data.replace(old, new)
            zout.writestr(it, data)


def build_word(master, out):
    d = docx.Document(master)
    body = d.element.body
    for el in list(body):
        if not el.tag.endswith("sectPr"):
            body.remove(el)
    starter = os.path.join(out, "QPS_House_starter.docx")
    d.save(starter)
    swap_content_type(starter, os.path.join(out, "QPS_House.dotx"),
                      b"wordprocessingml.document.main+xml", b"wordprocessingml.template.main+xml")


def name_furniture(master):
    """Name the reference / ISC / footer text boxes of one slide master so the post-processor can fill them."""
    boxes = sorted((s for s in master.shapes if s.shape_type == 17), key=lambda s: (s.left, s.top))
    if not any(qps_post.furniture_role(s) for s in boxes):
        return  # e.g. the Alexandria integration master: ECM field boxes only
    for shp in boxes:
        txt = shp.text_frame.text.strip()
        if txt.startswith("ISC"):
            shp.name = "QPS ISC"
        elif txt.startswith("SCK CEN/"):
            shp.name = "QPS Ref"
        elif "[" not in txt:
            shp.name = "QPS Footer"


def build_slides(deck, out):
    """Corporate slide template = the SCK CEN 2020 master from an authoritative deck, slides removed."""
    p = Presentation(deck)
    ids = p.slides._sldIdLst
    for sid in list(ids):
        p.part.drop_rel(sid.rId)
        ids.remove(sid)
    # Name the furniture on every master (decks can use the same-named layouts of masters 2-4), and clear
    # the source deck's document reference so no deck built on the template shows it.
    for m in p.slide_masters:
        name_furniture(m)
    for _, role, shp in qps_post.furniture(p):
        if role == "ref":
            qps_post._set_text(shp, "SCK CEN/")
    qps_post.scrub_identity(p)
    # Google Slides exports substitute fonts (e.g. Quattrocento Sans); point them back at the theme font.
    for part in list(p.slide_masters) + [lay for mm in p.slide_masters for lay in mm.slide_layouts]:
        qps_post.normalise_fonts(part.element)
    pptx_path = os.path.join(out, "QPS_House.pptx")
    p.save(pptx_path)
    swap_content_type(pptx_path, os.path.join(out, "QPS_House.potx"),
                      b"presentationml.presentation.main+xml", b"presentationml.template.main+xml")
    return record_source(deck, out)


def record_source(deck, out):
    """Write QPS_House.source.txt (deck name, size, SHA-256) and say whether it is the recorded reference deck."""
    sha = hashlib.sha256(Path(deck).read_bytes()).hexdigest()
    name = os.path.basename(deck)
    Path(out, "QPS_House.source.txt").write_text(
        f"source deck: {name}\nbytes: {os.path.getsize(deck)}\nsha256: {sha}\n"
        f"built: {dt.datetime.now(tz=dt.UTC).isoformat(timespec='seconds')}\n", encoding="utf-8")
    if sha != REFERENCE_DECK[1]:
        print(f"WARNING: {name} (sha256 {sha[:12]}…) is not the recorded reference deck "
              f"{REFERENCE_DECK[0]} ({REFERENCE_DECK[1][:12]}…)", file=sys.stderr)
    return sha


if __name__ == "__main__":
    master, deck = sys.argv[1], sys.argv[2]
    outdir = sys.argv[3] if len(sys.argv) > 3 else str(TEMPLATES)
    os.makedirs(outdir, exist_ok=True)
    build_word(master, outdir)
    build_slides(deck, outdir)
