from pathlib import Path

import json
import pytest

from slides.deck_orchestrator import build_deck_assets, load_deck_content, normalize_deck


FIXTURE_DIR = Path("slides/src/qps_cybersecurity")


def test_normalize_deck_assigns_fixed_ids_and_sections():
    content = load_deck_content(FIXTURE_DIR / "deck_content.yaml")
    deck = normalize_deck(content)

    assert deck["deck_id"] == "qps-cybersecurity-ad07-slide-deck-2"
    assert len(deck["slides"]) == 4
    assert deck["slides"][1]["id"] == "QPS_CYBERSECURITY_AD07_SLIDE_DECK_2_002"
    assert deck["slides"][1]["section"] == "APPENDIX"


def test_build_deck_assets_emits_html_markdown_and_abacus_manifest(tmp_path):
    result = build_deck_assets(
        content_path=FIXTURE_DIR / "deck_content.yaml",
        css_path=FIXTURE_DIR / "deck_style.css",
        output_dir=tmp_path,
    )

    artifact_kinds = {artifact.kind for artifact in result.artifacts}
    assert artifact_kinds == {"html", "markdown"}
    assert result.manifest_path.exists()

    html_path = tmp_path / "qps-cybersecurity-ad07-slide-deck-2.html"
    markdown_path = tmp_path / "qps-cybersecurity-ad07-slide-deck-2.md"
    assert "Cybersecurity Framework" in html_path.read_text(encoding="utf-8")
    assert "RTM-321" in markdown_path.read_text(encoding="utf-8")

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["slide_count"] == 4
    assert manifest["abacus_controls"]["fixed_and_locked_status"] is True
    assert manifest["abacus_controls"]["rtm_appendix_present"] is True
    assert {item["path"] for item in manifest["artifacts"]} == {
        "qps-cybersecurity-ad07-slide-deck-2.html",
        "qps-cybersecurity-ad07-slide-deck-2.md",
    }


def test_build_deck_assets_uses_source_date_epoch_for_manifest_timestamp(tmp_path, monkeypatch):
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "0")
    result = build_deck_assets(
        content_path=FIXTURE_DIR / "deck_content.yaml",
        css_path=FIXTURE_DIR / "deck_style.css",
        output_dir=tmp_path,
    )

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["generated_at"] == "1970-01-01T00:00:00+00:00"


def test_build_deck_assets_rejects_unsupported_formats(tmp_path):
    with pytest.raises(ValueError, match="Unsupported format"):
        build_deck_assets(
            content_path=FIXTURE_DIR / "deck_content.yaml",
            css_path=FIXTURE_DIR / "deck_style.css",
            output_dir=tmp_path,
            formats=("html", "pdf"),
        )


def test_build_deck_assets_rejects_invalid_source_date_epoch(tmp_path, monkeypatch):
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "not-an-int")
    with pytest.raises(ValueError, match="SOURCE_DATE_EPOCH must be an integer Unix timestamp"):
        build_deck_assets(
            content_path=FIXTURE_DIR / "deck_content.yaml",
            css_path=FIXTURE_DIR / "deck_style.css",
            output_dir=tmp_path,
        )


def test_build_deck_assets_preserves_acronym_casing_in_rendered_headings(tmp_path):
    build_deck_assets(
        content_path=FIXTURE_DIR / "deck_content.yaml",
        css_path=FIXTURE_DIR / "deck_style.css",
        output_dir=tmp_path,
    )

    html_text = (tmp_path / "qps-cybersecurity-ad07-slide-deck-2.html").read_text(encoding="utf-8")
    markdown_text = (tmp_path / "qps-cybersecurity-ad07-slide-deck-2.md").read_text(encoding="utf-8")
    assert "<h3>RTM Map</h3>" in html_text
    assert "### RTM Map" in markdown_text
