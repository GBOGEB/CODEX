import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import render_portal_tiles as rpt


def test_checked_in_portal_matches_ssot():
    assert rpt.main(["--check"]) == 0


def test_traceability_is_computed_from_chain_status():
    trace = {"chains": [{"status": "complete"}, {"status": "partial"}, {"status": "complete"}, {"status": "partial"}]}
    tile = rpt.traceability_tile(trace)
    assert ">50%<" in tile
    assert "2 of 4 chains complete" in tile
    assert "status partial" in tile


def test_traceability_all_complete_is_ready():
    tile = rpt.traceability_tile({"chains": [{"status": "complete"}]})
    assert ">100%<" in tile and "status ready" in tile


def test_traceability_without_chains_does_not_invent_a_number():
    assert ">n/a<" in rpt.traceability_tile({})


def test_release_readiness_is_labelled_declared():
    runtime = {
        "runtime": {"version": "W007", "generated_on": "2026-06-05"},
        "coverage_metrics": {"release_readiness_percent": 72},
    }
    tile = rpt.readiness_tile(runtime)
    assert ">72%<" in tile
    assert "declared W007 2026-06-05, not measured" in tile


def test_render_requires_markers():
    try:
        rpt.render("<html></html>", {}, {})
    except SystemExit as exc:
        assert "markers not found" in str(exc)
    else:
        raise AssertionError("render() accepted a page without markers")


def test_render_replaces_only_the_marked_block():
    page = f"<p>before</p>{rpt.BEGIN}old{rpt.END}<p>after</p>"
    out = rpt.render(page, {"artifact_counts": {"ssot_models": 3}}, {"chains": [{"status": "partial"}]})
    assert out.startswith("<p>before</p>") and out.endswith("<p>after</p>")
    assert "old" not in out and ">0%<" in out
