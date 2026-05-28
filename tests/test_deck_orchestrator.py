from pathlib import Path

import json

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
