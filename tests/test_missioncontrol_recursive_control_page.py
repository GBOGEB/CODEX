"""Source-contract checks for the read-only recursive control entry page."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "docs/missioncontrol_recursive_control.html"
PROJECTION = ROOT / "docs/data/missioncontrol_recursive_control_projection.json"


def _html() -> str:
    return HTML.read_text(encoding="utf-8")


def _catalogue() -> list[dict]:
    match = re.search(r'<script type="application/json" id="catalogue">(.*?)</script>', _html(), re.DOTALL)
    assert match, "catalogue block missing"
    return json.loads(match.group(1))


def test_page_loads_the_pages_copy_of_the_projection() -> None:
    html = _html()
    assert "fetch(path" in html
    assert "'data/missioncontrol_recursive_control_projection.json'" in html
    assert "'data/mycelium_kpi_measurement.json'" in html
    assert PROJECTION.is_file()


def test_every_codex_catalogue_path_exists() -> None:
    entries = _catalogue()
    assert len({e["path"] for e in entries}) == len(entries)
    for entry in entries:
        assert entry["repo"] in {"CODEX", "HUB"}
        if entry["repo"] == "CODEX":
            assert (ROOT / entry["path"]).exists(), entry["path"]


def test_catalogue_covers_every_local_projection_input() -> None:
    paths = {e["path"] for e in _catalogue() if e["repo"] == "CODEX"}
    projection = json.loads(PROJECTION.read_text(encoding="utf-8"))
    for item in projection["inputs"]:
        if item["origin"] == "LOCAL":
            assert item["path"] in paths, item["path"]


def test_page_is_read_only_and_self_contained() -> None:
    html = _html()
    assert "<title>" in html and "<h1>" in html and "aria-label=" in html
    assert re.search(r"<script[^>]+src=", html) is None
    assert re.search(r"fetch\(['\"]https?:", html) is None
    assert "method:" not in html and "POST" not in html
    assert "never writes" in html and "UNKNOWN" in html


def test_page_states_both_access_routes() -> None:
    html = _html()
    assert "https://gbogeb.github.io/CODEX/missioncontrol_recursive_control.html" in html
    assert "https://github.com/GBOGEB/CODEX" in html
    assert "explorer.exe" in html and "http.server" in html


def test_launchpad_links_the_entry_page() -> None:
    launchpad = (ROOT / "docs/missioncontrol_federated_launchpad.html").read_text(encoding="utf-8")
    assert 'href="missioncontrol_recursive_control.html"' in launchpad
