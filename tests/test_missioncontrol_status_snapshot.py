import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "mission_control" / "mycelium" / "snapshots" / "status_bd_snapshot_v01.json"
PAGES = ROOT / "docs" / "data" / "missioncontrol_status_snapshot_v01.json"
HTML = ROOT / "docs" / "missioncontrol_status_snapshot.html"
JS = ROOT / "docs" / "assets" / "missioncontrol" / "status-snapshot.js"


def test_snapshot_projection_is_frozen_and_pages_safe() -> None:
    canonical = json.loads(CANON.read_text(encoding="utf-8"))
    pages = json.loads(PAGES.read_text(encoding="utf-8"))
    assert canonical == pages
    assert canonical["renderer_type"] == "HTML_CONTENT_AS_SLIDE"
    assert canonical["template"] == "STATUS_BD_SNAPSHOT"
    assert canonical["snapshot_state"] == "MATERIALIZED_VIEW"
    assert canonical["snapshot_sha"]
    assert canonical["footer"]["authority_transfer"] is False
    assert canonical["footer"]["formal_credit_delta"] == 0
    assert canonical["footer"]["engineering_credit_delta"] == 0
    assert len(canonical["source_inputs"]) >= 4
    assert all(row["blob_sha"] for row in canonical["source_inputs"])


def test_status_snapshot_has_required_slide_contract() -> None:
    html = HTML.read_text(encoding="utf-8")
    js = JS.read_text(encoding="utf-8")
    for token in (
        "<title>MissionControl · Status / BD Snapshot</title>",
        'id="title"',
        'id="laneRows"',
        'id="evidence"',
        'id="interpretation"',
        'id="footer"',
        "aspect-ratio:16/9",
        "@media(max-width:620px)",
        "viewport",
    ):
        assert token in html
    assert "data/missioncontrol_status_snapshot_v01.json" in js
    assert "cache:'no-store'" in js
    assert "snapshot_state" in js
    assert "authority_transfer" in js
    assert "formal_credit_delta" in js
    assert "engineering_credit_delta" in js
    assert "../mission_control/" not in html
    assert "../mission_control/" not in js


def test_snapshot_renderer_is_read_only() -> None:
    js = JS.read_text(encoding="utf-8")
    forbidden = ("method:'POST'", 'method:"POST"', "git push", "contents: write", "pull-requests: write")
    assert all(token not in js for token in forbidden)
