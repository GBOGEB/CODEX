"""GISTAU book navigator and Chapter 3 page: current with their sources, complete, and correctly mapped."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def _tool():
    spec = importlib.util.spec_from_file_location("render_gistau_book", REPO_ROOT / "tools/render_gistau_book.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_committed_pages_are_current():
    tool = _tool()
    assert tool.OUT_BOOK.read_text(encoding="utf-8") == tool.render_book()
    assert tool.OUT_CH3.read_text(encoding="utf-8") == tool.render_ch3()


def test_every_ch3_benchmark_and_open_item_is_shown():
    data = json.loads((REPO_ROOT / "docs/gistau-ch3/data/claude_cycle_benchmarks.json").read_text(encoding="utf-8"))
    page = (REPO_ROOT / "docs/gistau-ch3/index.html").read_text(encoding="utf-8")
    for b in data["benchmarks"]:
        assert f"id='{b['benchmark_id']}'" in page
    for item in data["open_items"]:
        assert item["id"] in page


def test_page_offsets_match_the_source_manifest():
    book = yaml.safe_load((REPO_ROOT / "GISTAU/sources/master/source_manifest.yaml").read_text(encoding="utf-8"))["original_book"]
    for chapter, key in (("ch3_basic_thermodynamic_cycles", "ch3"), ("ch15_cryo_tool_box", "ch15")):
        b_lo, b_hi = (int(x) for x in book["chapters"][chapter]["book_pages"].split("-"))
        p_lo, p_hi = (int(x) for x in book["chapters"][chapter]["pdf_pages"].split("-"))
        assert (p_lo - b_lo, p_hi - b_hi) == (book["pdf_page_offset"][key],) * 2
    # Fig. 15.31 is on book p. 638 = PDF p. 673 (checked against the original PDF in #1120).
    assert _tool()._pdf_page(638, book["pdf_page_offset"]["ch15"]) == 673


def test_navigator_links_both_chapters_and_keeps_other_sources_apart():
    page = (REPO_ROOT / "docs/gistau/index.html").read_text(encoding="utf-8")
    assert "href='../gistau-ch3/index.html'" in page and "href='../gistau-ch15/index.html'" in page
    assert "Not this book: Chapter 3 Final.pdf" in page
    for target in ("docs/index.html", "docs/gistau-ch15/index.html"):
        assert "gistau/index.html" in (REPO_ROOT / target).read_text(encoding="utf-8")


def test_ch15_l1_summary_comes_from_the_record():
    record = json.loads((REPO_ROOT / "docs/gistau-ch15/data/l1_validation_results.json").read_text(encoding="utf-8"))["record"]
    gate = yaml.safe_load((REPO_ROOT / "governance/physics/CH15_CANONICAL_VALIDATION.yaml").read_text(encoding="utf-8"))
    n_q = sum(1 for r in record["rows"] if r["example_id"] in gate["checked"])
    page = (REPO_ROOT / "docs/gistau/index.html").read_text(encoding="utf-8")
    assert f"/{len(gate['checked'])} examples · " in page and f"/{n_q} values" in page
