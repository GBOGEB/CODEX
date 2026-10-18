"""The GISTAU Ch15 deck is generated from committed sources and kept current."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

from slides.deck_orchestrator import (
    normalize_deck,
    render_html_deck,
    render_markdown_deck,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTENT = REPO_ROOT / "slides/src/gistau_ch15/deck_content.yaml"
STYLE = REPO_ROOT / "slides/src/gistau_ch15/deck_style.css"
GENERATED = REPO_ROOT / "docs/qps-slide-system/generated/gistau-ch15-validated-model"


def _builder():
    spec = importlib.util.spec_from_file_location("build_gistau_deck_content", REPO_ROOT / "tools/build_gistau_deck_content.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_deck_content_is_current_with_its_sources():
    assert CONTENT.read_text(encoding="utf-8") == _builder().render(), "regenerate: python tools/build_gistau_deck_content.py"


def test_generated_html_and_markdown_are_current():
    deck = normalize_deck(yaml.safe_load(CONTENT.read_text(encoding="utf-8")))
    assert GENERATED.with_suffix(".html").read_text(encoding="utf-8") == render_html_deck(deck, STYLE.read_text(encoding="utf-8"))
    assert GENERATED.with_suffix(".md").read_text(encoding="utf-8") == render_markdown_deck(deck)


def test_every_deck_slide_is_registered():
    deck = yaml.safe_load(CONTENT.read_text(encoding="utf-8"))
    registry = yaml.safe_load((REPO_ROOT / "MANIFEST/MASTER_SLIDE_REGISTRY.yaml").read_text(encoding="utf-8"))
    ids = {s["slide_id"]: s for s in registry["slides"] if s.get("deck_id") == deck["metadata"]["deck_id"]}
    assert len(ids) == len(deck["slides"])
    for i, slide in enumerate(deck["slides"], 1):
        assert ids[f"GISTAU-{i:04d}"]["title"] == slide["title"]


def test_deck_carries_no_open_item_as_passing():
    deck = yaml.safe_load(CONTENT.read_text(encoding="utf-8"))
    gate = yaml.safe_load((REPO_ROOT / "governance/physics/CH15_CANONICAL_VALIDATION.yaml").read_text(encoding="utf-8"))
    checklist = {row["id"]: row["result"] for s in deck["slides"] if s["section"] == "VALIDATION" for row in s.get("checklist", []) if "result" in row}
    builder = _builder()
    for eid in gate.get("source_check_required", {}) or {}:
        assert checklist[builder.EXAMPLE_NAMES.get(eid, eid)] == "open (source check)"
    text = CONTENT.read_text(encoding="utf-8")
    for e in (gate.get("book_errata", {}) or {}).values():
        assert f"cell {e['cell']}" in text  # an erratum is shown, never silently dropped
